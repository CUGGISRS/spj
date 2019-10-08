# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 10:01:46 2019

@author: yuanz
"""

import arcpy
import sys
from arcpy.sa import *
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
##############
IN_DEM=sys.argv[1]#地形起伏——高程  #输入数据
VAR_GEO=sys.argv[2] #0/1
VAR_FBL=sys.argv[3] #不要大于5000
OUTPUTPATH =sys.argv[4] 
OUTPUTNAME = sys.argv[5]
###########
#IN_DEM='E:\spj\data\dixingqifu\dem_wgs84.tif'#地形起伏——高程  #输入数据
#VAR_GEO="1" #0/1
#VAR_FBL="200" #不要大于5000
#OUTPUTPATH ="D:\\map\\" 
#OUTPUTNAME = "dxqf"

if int(VAR_GEO)==1:#地理坐标系0/1
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
def calc_gridRA(gridLength,DEM,ppd):
    nbr=NbrRectangle(gridLength,gridLength,'CELL') #邻域分析的窗口大小
    rasterMax=BlockStatistics(DEM,nbr,'MAXIMUM')
    rasterMin=BlockStatistics(DEM,nbr,'MINIMUM')
    RA=rasterMax-rasterMin
    RA.save(ppd)
RAMean=calc_gridRA(VAR_R,IN_DEM,OUTPUTPATH+OUTPUTNAME+".tif")
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")