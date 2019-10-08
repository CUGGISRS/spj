# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 13:34:08 2019

"""
from __future__ import division
import arcpy
import math
from arcpy import env
from arcpy.sa import *
import sys
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
##############################
PATH = sys.argv[1] 
IN_XZZB= sys.argv[2] 
IN_NIR = sys.argv[3]      
IN_RED = sys.argv[4] 
IN_NDVI = sys.argv[5]     
IN_ZB = sys.argv[6]  
VAR_NDVI1 = sys.argv[7]      
VAR_NDVI2 = sys.argv[8]      
VAR_NDVI3 = sys.argv[9]     
VAR_NDVI4 = sys.argv[10]      
VAR_NDVI5 = sys.argv[11]
OUTPUTPATH =  sys.argv[12]     
OUTPUTNAME = sys.argv[13]
OUTPUTNAME1 = sys.argv[14]
###############################################
#PATH='D:\\test\\data\\st_stbc\\'
#IN_XZZB="0"
#IN_NIR='NIR20.tif'      
#IN_RED='RED20.tif' 
#IN_NDVI=""     
#IN_ZB="STXT_wgs84.shp"  
#VAR_NDVI1="0.1"      
#VAR_NDVI2="0.3"      
#VAR_NDVI3="0.5"      
#VAR_NDVI4="0.7"     
#VAR_NDVI5="0.9"
#OUTPUTPATH="E:\\spj\\data\\st_stbc\\"    
#OUTPUTNAME ="shpjg"
#OUTPUTNAME1 ="tifjg"
###############################################
env.workspace=PATH[:-1]
#########################################
if int(IN_XZZB)==0:
    try:
        arcpy.Delete_management('nir.tif')
        arcpy.Float_3d(IN_NIR,'nir.tif') 
    except:  
        arcpy.Float_3d(IN_NIR,'nir.tif')
    try:
        arcpy.Delete_management('red.tif')
        arcpy.Float_3d(IN_RED,'red.tif') 
    except:  
        arcpy.Float_3d(IN_RED,'red.tif')
    NIR=arcpy.Raster('nir.tif')
    RED=arcpy.Raster('red.tif')
    nd=(NIR-RED)/(NIR+RED)
    nd.save("ndvi.tif")
    exp=Con(IsNull("ndvi.tif"),0,"ndvi.tif")
    exp.save(OUTPUTPATH+OUTPUTNAME1+".tif")
else:
    exp=Con(IsNull(IN_NDVI),0,IN_NDVI)
    exp.save(OUTPUTPATH+OUTPUTNAME1+".tif")
outReclass = arcpy.sa.Reclassify(OUTPUTPATH+OUTPUTNAME1+".tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_NDVI1),1],[float(VAR_NDVI1),float(VAR_NDVI2),2],[float(VAR_NDVI2),float(VAR_NDVI3),3],[float(VAR_NDVI3),float(VAR_NDVI4),4],[float(VAR_NDVI4),float(VAR_NDVI5),5],[float(VAR_NDVI5),1,6]]),'NODATA')
outReclass.save("ndvire.tif")
arcpy.RasterToPolygon_conversion("ndvire.tif", "ndvig.shp", "NO_SIMPLIFY", "VALUE")
arcpy.Intersect_analysis (["ndvig.shp",IN_ZB] , OUTPUTPATH+OUTPUTNAME+".shp")
######################################
arcpy.Delete_management('nir.tif')
arcpy.Delete_management('red.tif')
#arcpy.Delete_management("ndvi.tif")
arcpy.Delete_management("ndvire.tif")
arcpy.Delete_management("ndvig.shp")
######################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")