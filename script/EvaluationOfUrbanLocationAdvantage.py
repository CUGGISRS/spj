# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 09:32:14 2019

@author: 赵晓旭
区位：省级区位优势度评价/市县层面优势度评价
"""
from __future__ import division
import arcpy
from arcpy import env
from arcpy.sa import *
import sys
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput=True
#####################################
PATH=sys.argv[1]
VAR_S=sys.argv[2]  #0=省级 1=市县
IN_SHENG=sys.argv[3] #省级到达中心城市时间（分钟）-tif
IN_SHI=sys.argv[4] #市级达到中心城市时间（分钟）-tif
IN_CLIP=sys.argv[5] #研究范围-shp
VAR_GEO=sys.argv[6]
VAR_FBL=sys.argv[7]
VAR_SSJHighest = sys.argv[8] #到达市县时间---高可达 20分钟
VAR_SSJHigh = sys.argv[9] #到达市县时间---较高可达 40分钟
VAR_SSJMid = sys.argv[10] #到达市县时间---高可达 60分钟
VAR_SSJLow = sys.argv[11] #到达市县时间---高可达 90分钟
VAR_SHSJHighest = sys.argv[12]  # 到达省级的时间---高可达 60分钟
VAR_SHSJHigh = sys.argv[13]  # 到达省级的时间---高可达 120分钟
VAR_SHSJMid = sys.argv[14]  # 到达省级的时间---高可达 210分钟
VAR_SHSJLow = sys.argv[15]  # 到达省级的时间---高可达 300分钟
IN_XZQQ=sys.argv[16] 
OUTPUTPATH = sys.argv[17] 
OUTPUTNAME= sys.argv[18]
#####################################
#PATH="E:\\spj\\data\\town_quwei\\"
#VAR_S="1"  #0=省级 1=市县
#IN_SHENG="shengji.tif"
#IN_SHI="shixian.tif"  #"shixian.tif"
#IN_CLIP="clipper.shp"
#VAR_GEO="1" #0/1
#VAR_FBL="150" #分辨率
#VAR_SHSJHighest = "60"  # 到达省级的时间---高可达 60分钟
#VAR_SHSJHigh = "120"  # 到达省级的时间---高可达 120分钟
#VAR_SHSJMid = "210"  # 到达省级的时间---高可达 210分钟
#VAR_SHSJLow = "300"  # 到达省级的时间---高可达 300分钟
#VAR_SSJHighest = "20" #到达市县时间---高可达 20分钟
#VAR_SSJHigh = "40" #到达市县时间---较高可达 40分钟
#VAR_SSJMid = "60" #到达市县时间---高可达 60分钟
#VAR_SSJLow = "90" #到达市县时间---高可达 90分钟
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="town_quwei"
#####################################
env.workspace=PATH[:-1]
####################################
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
################################
if int(VAR_S)==0:
      Z = arcpy.sa.Reclassify(IN_SHENG, "Value", arcpy.sa.RemapRange([[0,float(VAR_SHSJHighest),1],[float(VAR_SHSJHighest),float(VAR_SHSJHigh),2],[float(VAR_SHSJHigh),float(VAR_SHSJMid),3],[float(VAR_SHSJMid),float(VAR_SHSJLow),4],[float(VAR_SHSJLow),100000,5]]),'NODATA')
      Z.save("sheng.tif")
      arcpy.Clip_management("sheng.tif","",OUTPUTPATH+OUTPUTNAME+".tif",IN_CLIP,"", "ClippingGeometry")
else:
      Z = arcpy.sa.Reclassify(IN_SHI, "Value", arcpy.sa.RemapRange([[0,float(VAR_SSJHighest),1],[float(VAR_SSJHighest),float(VAR_SSJHigh),2],[float(VAR_SSJHigh),float(VAR_SSJMid),3],[float(VAR_SSJMid),float(VAR_SSJLow),4],[float(VAR_SSJLow),10000,5]]),'NODATA')
      Z.save("shi.tif")
      arcpy.Clip_management("shi.tif","",OUTPUTPATH+OUTPUTNAME+".tif",IN_CLIP,"", "ClippingGeometry")
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"好"
    elif a == 2:
        return u"较好"   
    elif a == 3:
        return u"一般"
    elif a == 4:
        return u"较差"
    elif a == 5:
        return u"差"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management("sheng.tif")
arcpy.Delete_management("shi.tif")
#######################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
      StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_tu_huan_5J.clr")
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")