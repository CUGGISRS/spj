# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 17:50:44 2019

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
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
###############################
PATH=sys.argv[1]#PATH="D:\\test\\data\\ql4\\"
IN_DZ=sys.argv[2]#IN_DZ="dizhenzaihai.tif"
IN_TD=sys.argv[3]#IN_TD="生物多样性用地数据.shp"
IN_CLIP=sys.argv[4]#IN_CLIP="clipper.shp"
VAR_GEO=sys.argv[5]#VAR_GEO="1" #0/1
VAR_FBL=sys.argv[6]#VAR_FBL="20" #不要大于5000
IN_XZQQ=sys.argv[7]
OUTPUTPATH=sys.argv[8]
OUTPUTNAME=sys.argv[9]#OUTPUTNAME="diejiajieguo"
###############################
#PATH="E:\\spj\\data\\ql4\\"
#IN_DZ="dizhenzaihai.tif"
#IN_TD="生物多样性用地数据.shp"
#IN_CLIP="clipper.shp"
#VAR_GEO="1" #0/1
#VAR_FBL="20" #不要大于5000
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH='D:\\map\\'
#OUTPUTNAME="diejiajieguo"
#######################
env.workspace=PATH[:-1]
##################################
#重采样像元大小设定
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
##########################
exp=Con(IN_DZ, IN_DZ, "", "VALUE = 1")
exp.save('dz.tif')
ex='"DLMC" = \'农村居民点\' '
arcpy.Select_analysis(IN_TD, "td.shp", ex)
arcpy.RasterToPolygon_conversion ('dz.tif', "dizhi.shp")
arcpy.Intersect_analysis (["dizhi.shp", "td.shp"],"jg.shp" )
arcpy.Clip_analysis("jg.shp", IN_CLIP, OUTPUTPATH+OUTPUTNAME+".shp")
arcpy.Delete_management('dz.tif')
arcpy.Delete_management("td.shp")
arcpy.Delete_management("dizhi.shp")
arcpy.Delete_management("jg.shp")
arcpy.TableToExcel_conversion (OUTPUTPATH+OUTPUTNAME+".shp",OUTPUTPATH+OUTPUTNAME+".xls")
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".shp", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.CheckInExtension('Spatial')
arcpy.CheckInExtension('3D')