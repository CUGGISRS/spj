# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 17:25:07 2019

@author: yuanz
"""
from __future__ import division
import arcpy
from arcpy import env
from arcpy.sa import *
import sys
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
###########################
# #person test
PATH=sys.argv[1]#PATH="D:\\test\\data\\town_envi_w\\"
VAR=sys.argv[2]#VAR="1" #0是方法一，1是方法二
IN_RL=sys.argv[3]#IN_RL="shuihuanjing.tif"
IN_ND=sys.argv[4]#IN_ND="年均水质目标浓度.tif"
IN_DB=sys.argv[5]#IN_DB="地表水资源量.tif"
IN_CLIP=sys.argv[6]#IN_CLIP="clipper.shp"
VAR_GEO=sys.argv[7]
VAR_FBL=sys.argv[8]
VAR_D=sys.argv[9]#VAR_D="20"
VAR_M=sys.argv[10]#VAR_M="200"
VAR_H=sys.argv[11]#VAR_H="3000"
VAR_O=sys.argv[12]#VAR_O="5000"
IN_XZQQ=sys.argv[13]
OUTPUTPATH = sys.argv[14]
OUTPUTNAME=sys.argv[15]#OUTPUTNAME="town_shuihuanjing"
###########################
# #person test
#PATH="E:\\spj\\data\\town_envi_w\\"
#VAR="1" #0是方法一，1是方法二
#IN_RL="shuihuanjing.tif"
#IN_ND="年均水质目标浓度.tif"
#IN_DB="地表水资源量.tif"
#IN_CLIP="clipper.shp"
#VAR_GEO="1" #0/1
#VAR_FBL="150" #分辨率
#VAR_D="20"
#VAR_M="200"
#VAR_H="3000"
#VAR_O="5000"
#IN_XZQQ='XZQ_WGS84.shp'
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="town_shuihuanjing"
#####################################
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
env.workspace = PATH[:-1]
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
if int(VAR)==0:
    outReclass2 = arcpy.sa.Reclassify(IN_RL, "Value", arcpy.sa.RemapRange([[0,float(VAR_D),5],[float(VAR_D),float(VAR_M),4],[float(VAR_M),float(VAR_H),3],[float(VAR_H),float(VAR_O),2],[float(VAR_O),11000000000,1]]),'NODATA')
    outReclass2.save(OUTPUTPATH+OUTPUTNAME+".tif")
else:
    f=arcpy.Raster(IN_ND)*arcpy.Raster(IN_DB)
    f.save("shuizhi.tif")
    outReclass2 = arcpy.sa.Reclassify("shuizhi.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_D),5],[float(VAR_D),float(VAR_M),4],[float(VAR_M),float(VAR_H),3],[float(VAR_H),float(VAR_O),2],[float(VAR_O),11000000000,1]]),'NODATA')
    outReclass2.save(OUTPUTPATH+OUTPUTNAME+".tif")
    arcpy.Delete_management("shuizhi.tif")
#################################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"高"
    elif a == 2:
        return u"较高"   
    elif a == 3:
        return u"一般"
    elif a == 4:
        return u"较低"
    elif a == 5:
        return u"低"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")

#######################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
     StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_tu_huan_5J.clr")
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
    