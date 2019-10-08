# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 09:11:22 2019

@author: 赵晓旭
城镇功能指向的水资源评价
评价因子：水资源总量模数，用水总量控制指标模数
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
#####################################
#HARDCODE
#PATH=sys.argv[1]
#IN_XZQ=sys.argv[2]   #行政区矢量图斑中有字段名为[ZJYL]，[ZJYL]字段为用水总量
#IN_CLIP=sys.argv[3]   #研究区范围
#
#VAR_A=sys.argv[4]  #0:用水总量控制指标模数  1:水资源总量模数
#VAR_GEO=sys.argv[5]     #0/1
#VAR_FBL=sys.argv[6]    #分辨率
#
#VAR_SWaterLow = sys.argv[7]  #省级---水资源较低可利用下限，单位m³/km²
#VAR_SWaterMid = sys.argv[8]  #省级---水资源中等可利用下限，单位m³/km²
#VAR_SWaterHigh = sys.argv[9]  #省级---水资源较高可利用下限，单位m³/km²
#VAR_SWaterHighest = sys.argv[10]  #省级---水资源高可利用下限，单位m³/km²
#
#VAR_XWaterLow = sys.argv[11]  #市县级---水资源较低可利用下限，单位m³/km²
#VAR_XWaterMid = sys.argv[12]  #市县级---水资源中等可利用下限，单位m³/km²
#VAR_XWaterHigh = sys.argv[13]  #市县级---水资源较高可利用下限，单位m³/km²
#VAR_XWaterHighest = sys.argv[14]  #市县级---水资源高可利用下限，单位m³/km²
#IN_XZQQ=sys.argv[15]
#OUTPUTPATH = sys.argv[16]
#OUTPUTNAME=sys.argv[17]    #输出数据名称
#####################################
PATH="E:\\spj\\data\\town_func_w\\"
IN_XZQ="XZQ_Xian.shp"
IN_CLIP="clipper.shp"
VAR_A="0"  #0:用水总量控制指标模数  1:水资源总量模数
VAR_GEO="1" #0/1
VAR_FBL="300" #分辨率
VAR_SWaterLow = "50000"  #省级---水资源较低可利用下限，单位m³/km²
VAR_SWaterMid = "100000"  #省级---水资源中等可利用下限，单位m³/km²
VAR_SWaterHigh = "200000"  #省级---水资源较高可利用下限，单位m³/km²
VAR_SWaterHighest = "500000"  #省级---水资源高可利用下限，单位m³/km²
VAR_XWaterLow = "30000"  #市县级---水资源较低可利用下限，单位m³/km²
VAR_XWaterMid = "80000"  #市县级---水资源中等可利用下限，单位m³/km²
VAR_XWaterHigh = "130000"  #市县级---水资源较高可利用下限，单位m³/km²
VAR_XWaterHighest = "250000"  #市县级---水资源高可利用下限，单位m³/km²
IN_XZQQ='E:\\spj\\data\\town_func_w\\XZQ_WGS84.shp'
OUTPUTPATH = "D:\\map\\"
OUTPUTNAME="town_shui"
##################################
env.workspace = PATH[:-1]
SWaterLow = int(VAR_SWaterLow)
SWaterMid = int(VAR_SWaterMid)
SWaterHigh = int(VAR_SWaterHigh)
SWaterHighest = int(VAR_SWaterHighest)

XWaterLow = int(VAR_XWaterLow)
XWaterMid = int(VAR_XWaterMid)
XWaterHigh = int(VAR_XWaterHigh)
XWaterHighest = int(VAR_XWaterHighest)
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
####################################
def fj(a,b=[]):
    if a<SWaterLow:
        b.append(5)
    elif SWaterLow<=a<SWaterMid:
        b.append(4)
    elif SWaterMid<=a<SWaterHigh:
        b.append(3)
    elif SWaterHigh<=a<SWaterHighest:
        b.append(2)
    else:
        b.append(1)
    return b
def fj2(a,b=[]):
    if a<XWaterLow:
        b.append(5)
    elif XWaterLow<=a<XWaterMid:
        b.append(4)
    elif XWaterMid<=a<VAR_XWaterHigh:
        b.append(3)
    elif VAR_XWaterHigh<=a<XWaterHighest:
        b.append(2)
    else:
        b.append(1)
    return b
#################################
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
####################################
list1=[]
list2=[]
cursor = arcpy.da.SearchCursor(IN_XZQ, ["ZJYL","SHAPE@AREA"])
for row in cursor:
    list1.append(row[0])
    list2.append(row[1]/1000000)    
#print list1,list2    
func = lambda x,y:x/y
result = list(map(func,list1,list2))
if int(VAR_A)==1: 
    for i in result:
         t=fj(i)
elif int(VAR_A)==0:
    for i in result:
         t=fj2(i) 
else :
    print"there is no choice here"   
#print t
cursor2 = arcpy.UpdateCursor(IN_XZQ)
try:
    arcpy.DeleteField_management(IN_XZQ, 'ysdj')
    arcpy.AddField_management(IN_XZQ, 'ysdj', "LONG")   #创建aaa列，用来放置1，2，3，4，5
except:
    arcpy.AddField_management(IN_XZQ, 'ysdj', "LONG")  # 创建aaa列，用来放置1，2，3，4，5
i = 0
for my_row in cursor2:
    my_row.setValue('ysdj', t[i])
    cursor2.updateRow(my_row)
    i += 1
del cursor
del cursor2
arcpy.FeatureToRaster_conversion(IN_XZQ,'ysdj','xzq.tif',VAR_FBL)
arcpy.Clip_management('xzq.tif',"",OUTPUTPATH+OUTPUTNAME+'.tif',IN_CLIP,"", "ClippingGeometry")
##########################
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
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.DeleteField_management(IN_XZQ, "ysdj")
arcpy.Delete_management('xzq.tif')
#####################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
     StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_nong_cheng_shui_5J.clr")
arcpy.CheckInExtension("Spatial")
arcpy.CheckInExtension("3D")
