# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 17:46:04 2019

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
PATH=sys.argv[1]#PATH="D:\\test\\data\\ql3\\"
IN_STBH=sys.argv[2]#IN_STBH="shengtaijicheng.tif"   #生态保护
IN_CZ=sys.argv[3]#IN_CZ="town_jicheng.tif"
IN_TD=sys.argv[4]#IN_TD="生物多样性用地数据.shp"
IN_CLIP=sys.argv[5]#IN_CLIP="clipper.shp"
VAR_GEO=sys.argv[6]#VAR_GEO="1" #0/1
VAR_FBL=sys.argv[7]#VAR_FBL="20" #不要大于5000
IN_XZQQ=sys.argv[8]
OUTPUTPATH=sys.argv[9]
OUTPUTNAME=sys.argv[10]#OUTPUTNAME="diejiajieguo"
###############################
#PATH="E:\\spj\\data\\ql3\\"
#IN_STBH="shengtaijicheng.tif"   #生态保护
#IN_CZ="town_jicheng.tif"
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
exp=Con(IN_STBH, IN_STBH, "", "VALUE = 1")
exp.save('st.tif')
exp=Con(IN_CZ, IN_CZ, "", "VALUE = 5")
exp.save('cz.tif')
ex='"DLMC" = \'现状城镇用地\' '
arcpy.Select_analysis(IN_TD, "td.shp", ex)
arcpy.RasterToPolygon_conversion ('st.tif', "shengtai.shp")
arcpy.RasterToPolygon_conversion ('cz.tif', "chengzhen.shp")
arcpy.Intersect_analysis (["shengtai.shp", "td.shp","chengzhen.shp"],"jg.shp" )
arcpy.Clip_analysis("jg.shp", IN_CLIP, OUTPUTPATH+OUTPUTNAME+".shp")
arcpy.Delete_management('st.tif')
arcpy.Delete_management('cz.tif')
arcpy.Delete_management("td.shp")
arcpy.Delete_management("shengtai.shp")
arcpy.Delete_management("chengzhen.shp")
arcpy.Delete_management("jg.shp")
arcpy.TableToExcel_conversion (OUTPUTPATH+OUTPUTNAME+".shp",OUTPUTPATH+OUTPUTNAME+".xls")
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".shp", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.CheckInExtension('Spatial')
arcpy.CheckInExtension('3D')
