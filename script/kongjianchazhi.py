# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 09:19:35 2019

@author: yuanz
"""
import arcpy
from arcpy.sa import *
import sys
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
##############################
INPUTFILE=sys.argv[1]
IN_FIELDS=sys.argv[2]
VAR_GEO=sys.argv[3]
VAR_FBL=sys.argv[4]
OUTPUTPATH=sys.argv[5]
OUTPUTNAME=sys.argv[6]
###############################
#INPUTFILE="E:\\spj\\data\\chazhi\\dw2.shp"
#IN_FIELDS= "bfb"
#VAR_GEO="1" #0/1   1地理坐标系  0投影坐标系
#VAR_FBL="150"
#OUTPUTPATH="D:\\map\\"
#OUTPUTNAME="chazhi"
###########################
if int(VAR_GEO)==1:#地理坐标系
    VAR_FBL=0.0000101*int(VAR_FBL)
else:#投影坐标系
    VAR_FBL=int(VAR_FBL)
CC="%f"%(VAR_FBL)
def krig(a,b,c,CC): #空间插值
    rows = arcpy.da.SearchCursor(a,['FID'])
    for row in rows:
         y= row[0]
    del rows,row
    if y>=12:
        p="Variable %d"%(12)
    else:
        p="Variable %d"%(y-1)
    arcpy.Kriging_3d(a, b, c, "Spherical",CC,p) 
    return b
def chazhi(a,b,d,CC,y=[]):
    cursor = arcpy.da.SearchCursor(a, [b])
    for row in cursor:
         y.append(row[0])
    del row,cursor
    if len(set(y))==1:
            arcpy.Idw_3d(a, b, d,CC)
    else:
            krig(a, b, d,CC)
    
chazhi(INPUTFILE, IN_FIELDS, OUTPUTPATH+OUTPUTNAME+".tif",CC)
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")