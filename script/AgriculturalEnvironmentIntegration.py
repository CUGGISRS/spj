# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 13:38:31 2019

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
##############################################
PATH =sys.argv[1]
IN_st=sys.argv[2]
IN_qt=sys.argv[3]
IN_CLIP=sys.argv[4]
VAR_GEO=sys.argv[5]
VAR_FBL=sys.argv[6]
IN_XZQQ=sys.argv[7]
OUTPUTPATH = sys.argv[8]
OUTPUTNAME=sys.argv[9]
#PATH = 'E:\\spj\\data\\agri_envi\\'
#IN_st="huanjingpingjia_st.tif"
#IN_qt="huanjingpingjia_qita.tif"
#IN_CLIP="clipper.shp"
#VAR_GEO="1" #0/1
#VAR_FBL="150" #不要大于5000
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="ny_huanjingjicheng"
########################################
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
env.workspace=PATH[:-1]#工作环境
h=arcpy.Raster(IN_st)+arcpy.Raster(IN_qt)
h.save(OUTPUTPATH+OUTPUTNAME+'.tif')
########################################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"高"
    elif a == 3:
        return u"中"
    elif a == 5:
        return u"低"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
if arcpy.Exists("tihuan.tif"):
    arcpy.Delete_management("tihuan.tif")
if arcpy.Exists("tihuan1.tif"):
    arcpy.Delete_management("tihuan1.tif")    
##############################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_nong_huan_3J.clr")
##################################
arcpy.CheckInExtension('Spatial')
arcpy.CheckInExtension('3D')