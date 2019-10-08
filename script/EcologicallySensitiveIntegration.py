# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 17:58:56 2019

@author: yuanz
"""
from __future__ import division
import arcpy
import math
import sys
import numpy as np
from arcpy import env
from arcpy.sa import *
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
###############################
PATH=sys.argv[1]#PATH="D:\\test\\data\\st_mg_jc\\"
IN_HAQS=sys.argv[2]#IN_HAQS="haianqinshi.tif"   #海岸侵蚀
IN_SMH=sys.argv[3]#IN_SMH="shimohua.tif"       #石漠化
IN_STLS=sys.argv[4]#IN_STLS="shuituliushi.tif"  #水土流失
IN_TDSH=sys.argv[5]#IN_TDSH="tudishahu.tif"     #土地沙化
IN_CLIP=sys.argv[6]#IN_CLIP="clipper.shp"
VAR_GEO=sys.argv[7]#VAR_GEO="1" #0/1
VAR_FBL=sys.argv[8]#VAR_FBL="20" #不要大于5000
IN_XZQQ=sys.argv[9]
OUTPUTPATH = sys.argv[10]
OUTPUTNAME=sys.argv[11]#OUTPUTNAME="st_mingan_jicheng"
###############################
#PATH="E:\\spj\\data\\st_mg_jc\\"
#IN_HAQS=""   #海岸侵蚀
#IN_SMH=""       #石漠化shimohua.tif
#IN_STLS="shuituliushi.tif"  #水土流失
#IN_TDSH=""     #土地沙化
#IN_CLIP="clipper.shp"
#VAR_GEO="1" #0/1
#VAR_FBL="20" #不要大于5000
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="st_mg_jc"
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
if IN_HAQS=="99999":
    IN_HAQS = create_raster(5,IN_CLIP,VAR_FBL,"tihuan.tif")
if IN_SMH=="99999":
    IN_SMH =  create_raster(5,IN_CLIP,VAR_FBL,"tihuan1.tif")
if IN_STLS=="99999":
    IN_STLS = create_raster(5,IN_CLIP,VAR_FBL,"tihuan2.tif")
if IN_TDSH=="99999":
    IN_TDSH =  create_raster(5,IN_CLIP,VAR_FBL,"tihuan3.tif")
################################
arcpy.RasterToPolygon_conversion (Int(IN_HAQS), "haqsshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_SMH), "smhshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_STLS), "stlsshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_TDSH), "tdshshp.shp")
arcpy.Intersect_analysis (["haqsshp.shp","smhshp.shp", "stlsshp.shp","tdshshp.shp"],"stmgshp.shp" ) 
cursor = arcpy.da.SearchCursor("stmgshp.shp" , ["GRIDCODE","GRIDCODE_1","GRIDCODE_2","GRIDCODE_3"])
mg=[]
for row in cursor: 
    mg.append(max([row[0],row[1],row[2],row[3]]))
del row,cursor
try:
    arcpy.DeleteField_management("stmgshp.shp", 'base1')
    arcpy.AddField_management("stmgshp.shp", 'base1', "SHORT")  
except:              
    arcpy.AddField_management("stmgshp.shp", 'base1', "SHORT")
cursor1 = arcpy.UpdateCursor("stmgshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('base1', mg[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row 
arcpy.FeatureToRaster_conversion("stmgshp.shp", "base1", "stmg.tif",CC)
arcpy.Clip_management("stmg.tif","",OUTPUTPATH+OUTPUTNAME+'.tif',IN_CLIP,"", "ClippingGeometry")
#####################################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"极敏感"
    if a == 3:
        return u"高度敏感"
    else:
        return u'一般敏感'"""
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management("haqsshp.shp")
arcpy.Delete_management("smhshp.shp")
arcpy.Delete_management("stlsshp.shp")
arcpy.Delete_management("tdshshp.shp")
arcpy.Delete_management("stmgshp.shp" )
arcpy.Delete_management("stmg.tif" )
if arcpy.Exists("tihuan1.tif"):
    arcpy.Delete_management("tihuan1.tif")
if arcpy.Exists("tihuan.tif"):
    arcpy.Delete_management("tihuan.tif")
if arcpy.Exists("tihuan2.tif"):
    arcpy.Delete_management("tihuan2.tif")
if arcpy.Exists("tihuan3.tif"):
    arcpy.Delete_management("tihuan3.tif")
##################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
     StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_mingan_3J.clr")
#arcpy.ApplySymbologyFromLayer_management(OUTPUTPATH+OUTPUTNAME+".tif", "C:/yz_spj/clr/Month4_mingan_3J.lyr")                                
##################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
