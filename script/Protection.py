# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 17:54:17 2019

@author: yuanz
"""
import arcpy
import math
import sys
import numpy as np
from arcpy import env
from arcpy.sa import *
import RasterTableToTxtAndExcel
import StaticticsByXZQ
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
###############################
PATH= sys.argv[1]#PATH="D:\\test\\data\\st_fw_jc\\"
IN_FFGC= sys.argv[2]#IN_FFGC="fangfenggusha.tif"  #防风固沙
IN_STBC= sys.argv[3]#IN_STBC="shuitubaochi.tif"   #水土保持
IN_SYHY= sys.argv[4]#IN_SYHY="shuiyuanhanyang.tif"#水源涵养
IN_SW= sys.argv[5]#IN_SW="shengwuduoyangxing.tif" #生物多样性维护
IN_HAFH= sys.argv[6]#IN_HAFH="haianfanghu.tif"     #海岸防护
IN_CLIP= sys.argv[7]#IN_CLIP="clipper.shp"
VAR_GEO= sys.argv[8]#VAR_GEO="1" #0/1
VAR_FBL= sys.argv[9]#VAR_FBL="20" #不要大于5000
IN_XZQQ = sys.argv[10]
OUTPUTPATH = sys.argv[11]
OUTPUTNAME= sys.argv[12]#OUTPUTNAME="st_fuwu_jicheng"
###############################
#PATH="E:\\spj\\data\\st_zy_jc\\"
#IN_CLIP="clipper.shp"
#IN_FFGC="fangfenggusha.tif"  #防风固沙
#IN_STBC="shuitubaochi.tif"   #水土保持
#IN_SYHY="shuiyuanhanyang.tif"#水源涵养
#IN_SW="shengwuduoyangxing.tif" #生物多样性维护
#IN_HAFH=""     #海岸防护 #haianfanghu.tif
#VAR_GEO="1" #0/1
#VAR_FBL="20" #不要大于5000
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="st_zy_jc"
###############################
#重采样像元大小设定
FBLL=int(VAR_FBL)
if int(VAR_GEO)==1:#地理坐标系
    VAR_FBL=0.0000101*int(VAR_FBL)
else:#投影坐标系
    VAR_FBL=int(VAR_FBL)
CC="%f"%(VAR_FBL)
if int(VAR_FBL)<30:
    VAR_R=15  #邻域统计栅格数
elif 30<=int(VAR_FBL)<50:
    VAR_R=12
elif 50<=int(VAR_FBL)<100:
    VAR_R=9
else:
    VAR_R=3
def create_raster(constantValue,IN_CLIP,VAR_FBL,tihuan):
    desc=arcpy.Describe(IN_CLIP)
    extent=desc.extent
    xmin=float(extent.XMin) #x的最小坐标
    xmax=float(extent.XMax)
    ymin=float(extent.YMin)
    ymax=float(extent.YMax)
    outConstRaster = CreateConstantRaster(constantValue, "INTEGER",VAR_FBL,Extent(xmin,ymin,xmax,ymax))
    outConstRaster.save(tihuan)
    return tihuan
#################################
env.workspace=PATH[:-1]
###################################
if IN_FFGC=="99999":
    IN_FFGC = create_raster(5,IN_CLIP,VAR_FBL,"tihuan.tif")
if IN_STBC=="99999":
    IN_STBC = create_raster(5,IN_CLIP,VAR_FBL,"tihuan1.tif")
if IN_SYHY=="99999":
    IN_SYHY = create_raster(5,IN_CLIP,VAR_FBL,"tihuan2.tif")
if IN_SW =="99999":
    IN_SW = create_raster(5,IN_CLIP,VAR_FBL,"tihuan3.tif")
if IN_HAFH=="99999":
    IN_HAFH = create_raster(5,IN_CLIP,VAR_FBL,"tihuan4.tif")
##################################
arcpy.RasterToPolygon_conversion (Int(IN_FFGC), "ffgsshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_STBC), "stbcshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_SYHY), "syhyshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_SW), "swdyxshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_HAFH), "hafhshp.shp")
arcpy.Intersect_analysis (["ffgsshp.shp","stbcshp.shp", "syhyshp.shp","swdyxshp.shp","hafhshp.shp"],"stfwshp.shp" ) 
cursor = arcpy.da.SearchCursor("stfwshp.shp" , ["GRIDCODE","GRIDCODE_1","GRIDCODE_2","GRIDCODE_3","GRIDCODE_4"])
fw=[]
for row in cursor: 
    fw.append(max([row[0],row[1],row[2],row[3],row[4]]))
del row,cursor
try:
    arcpy.DeleteField_management("stfwshp.shp", 'base')
    arcpy.AddField_management("stfwshp.shp", 'base', "SHORT") 
except:  
    arcpy.AddField_management("stfwshp.shp", 'base', "SHORT")
cursor1 = arcpy.UpdateCursor("stfwshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('base', fw[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row 
arcpy.FeatureToRaster_conversion("stfwshp.shp", "base", "stfw.tif",CC)
arcpy.Clip_management("stfw.tif","",OUTPUTPATH+OUTPUTNAME+'.tif',IN_CLIP,"", "ClippingGeometry")
####################################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"极重要"
    if a == 3:
        return u"高度重要"
    else:
        return u'一般重要'"""
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management("ffgs.tif")
arcpy.Delete_management("stbc.tif")
arcpy.Delete_management("syhy.tif")
arcpy.Delete_management("stfw.tif")
arcpy.Delete_management("ffgsshp.shp")
arcpy.Delete_management("stbcshp.shp")
arcpy.Delete_management("syhyshp.shp" )
arcpy.Delete_management("swdyxshp.shp")
arcpy.Delete_management("stfwshp.shp")
arcpy.Delete_management("hafhshp.shp")
if arcpy.Exists("tihuan1.tif"):
    arcpy.Delete_management("tihuan1.tif")
if arcpy.Exists("tihuan.tif"):
    arcpy.Delete_management("tihuan.tif")
if arcpy.Exists("tihuan2.tif"):
    arcpy.Delete_management("tihuan2.tif")
if arcpy.Exists("tihuan3.tif"):
    arcpy.Delete_management("tihuan3.tif")
if arcpy.Exists("tihuan4.tif"):
    arcpy.Delete_management("tihuan4.tif")
############################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
      StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_fuwu_3J.clr")
#arcpy.ApplySymbologyFromLayer_management(fin,  "C:/yz_spj/clr/Month4_fuwu_3J.lyr")                             
###########################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")