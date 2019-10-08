# -*- coding: utf-8 -*-
import arcpy
import math
import sys
import os
import numpy as np
from arcpy import env
from arcpy.sa import *
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
###############################
PATH=sys.argv[1]#PATH="D:\\test\\data\\st_jc\\"
IN_FW=sys.argv[2]#IN_FW="st_fuwu_jicheng.tif"
IN_MG=sys.argv[3]#IN_MG="st_mingan_jicheng.tif"
IN_CLIP=sys.argv[4]#IN_CLIP="clipper.shp"
VAR_GEO=sys.argv[5]#VAR_GEO="1" #0/1
VAR_FBL=sys.argv[6]#VAR_FBL="20" #不要大于5000
IN_XZQQ=sys.argv[7]
OUTPUTPATH=sys.argv[8]
OUTPUTNAME=sys.argv[9]#OUTPUTNAME="shengtaijicheng"
###############################
#PATH="E:\\spj\\data\\st_jc\\"
#IN_FW="st_fuwu_jicheng.tif"
#IN_MG=""
#IN_CLIP="clipper.shp"
#VAR_GEO="1" #0/1
#VAR_FBL="20" #不要大于5000
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH="D:\\map\\"
#OUTPUTNAME="st_jc"
##################################
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
#############################################
if IN_FW =="99999":
    IN_FW = create_raster(5,IN_CLIP,VAR_FBL,"tihuan.tif")
if IN_MG =="99999":
    IN_MG =  create_raster(5,IN_CLIP,VAR_FBL,"tihuan1.tif")
##################################
arcpy.RasterToPolygon_conversion (Int(IN_FW), "stfwshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_MG), "stmgshp.shp")
arcpy.Intersect_analysis (["stfwshp.shp","stmgshp.shp"],"stjcshp.shp" )
cursor = arcpy.da.SearchCursor("stjcshp.shp", ["GRIDCODE","GRIDCODE_1"])
new=[]
for row in cursor:
	   if row[0]==1:
			new.append(1)
	   elif row[0]==3:
			if row[1]==1:
				new.append(1)
			elif 3<=row[1]<=5:
				new.append(3)
	   elif row[0]==5:
			   if row[1]==1:
				  new.append(1)
			   elif row[1]==3:
				  new.append(3)
			   elif row[1]==5:
				  new.append(5)
#print new
del row,cursor
arcpy.AddField_management("stjcshp.shp", 'jc', "SHORT")
cursor1 = arcpy.UpdateCursor("stjcshp.shp")
i = 0
for my_row in cursor1:
	my_row.setValue('jc', new[i])
	cursor1.updateRow(my_row)
	i += 1
del cursor1,my_row  
arcpy.FeatureToRaster_conversion("stjcshp.shp", "jc", "jc.tif",CC)
arcpy.Clip_management("jc.tif","",OUTPUTPATH+OUTPUTNAME+'.tif',IN_CLIP,"", "ClippingGeometry")
###########################################
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
arcpy.Delete_management("stfwshp.shp")
arcpy.Delete_management("stmgshp.shp" )
arcpy.Delete_management("stjcshp.shp")
arcpy.Delete_management("jc.tif")
if arcpy.Exists("tihuan1.tif"):
    arcpy.Delete_management("tihuan1.tif")
if arcpy.Exists("tihuan.tif"):
    arcpy.Delete_management("tihuan.tif")
######################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
      StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month7_jicheng_3J.clr")
#arcpy.ApplySymbologyFromLayer_management(OUTPUTPATH+OUTPUTNAME+".tif", "C:/yz_spj/clr/Month4_mingan_3J.lyr")                               
#####################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
