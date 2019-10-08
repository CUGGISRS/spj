# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 10:15:12 2019

@author: yuanz
"""

from __future__ import division
import arcpy
from arcpy import env
from arcpy.sa import *
import sys
import pandas as pd
import os
import RasterTableToTxtAndExcel
import StaticticsByXZQ
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
#####################################
PATH=sys.argv[1]
IN_FB=sys.argv[2]    #风暴潮灾txt文本数据
IN_CLIP=sys.argv[3]   #研究范围
VAR_GEO=sys.argv[4]     #0/1 空间坐标系 1---地理坐标系 0---投影坐标系
VAR_FBL=sys.argv[5]   #分辨率 空间分辨率
VAR_WXXLow = sys.argv[6]    #风暴潮灾较低危险性下限，默认2.0
VAR_WXXMid = sys.argv[7]    #风暴潮灾较高危险性下限，默认3.5
VAR_WXXHigh = sys.argv[8]    #风暴潮灾高危险性下限，默认7.0
IN_XZQQ=sys.argv[9]
OUTPUTPATH = sys.argv[10]
OUTPUTNAME=sys.argv[11]    #输出数据名称
#####################################
#PATH='E:\\spj\\data\\town_zaihai_fb\\'
#IN_FB=PATH+"fengbaochao.xls"
#IN_CLIP="clipper.shp"
#VAR_GEO="1" #0/1
#VAR_FBL="200" #分辨率
#VAR_WXXLow = "2.0"   #风暴潮灾较低危险性下限，默认2.0
#VAR_WXXMid = "3.5"    #风暴潮灾较高危险性下限，默认3.5
#VAR_WXXHigh = "7.0"   #风暴潮灾高危险性下限，默认7.0
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="town_fengbaochao"
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
#################################
def xlsx_to_csv_pd(xlsxpath,csvpath):
    data_xls = pd.read_excel(xlsxpath, index_col=0)
    data_xls.to_csv(csvpath, encoding='utf-8')
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
#####################################
env.workspace=PATH[:-1]
MIFBC="fbc.shp"
in_fb_csv = PATH+"fengbaochao.csv"
#IN_FB=PATH+FB
WXXLow = float(VAR_WXXLow)
WXXMid = float(VAR_WXXMid)
WXXHigh = float(VAR_WXXHigh)
######################################
if IN_FB.endswith(".txt") or IN_FB.endswith(".csv"):
    pass
if IN_FB.endswith(".xls") or IN_FB.endswith(".xlsx"):
    if __name__ == '__main__':
                xlsx_to_csv_pd(IN_FB,in_fb_csv)
                IN_FB = in_fb_csv
createFC = arcpy.CreateFeatureclass_management(env.workspace,MIFBC, "POINT", "", "", "")
arcpy.AddField_management(env.workspace + "/" + MIFBC, "xdsd", "FLOAT")
arcpy.AddField_management(env.workspace + "/" + MIFBC,  "lon", "FLOAT")
arcpy.AddField_management(env.workspace + "/" + MIFBC,  "lat", "FLOAT")
arcpy.AddField_management(env.workspace + "/" + MIFBC,  "YEAR", "FLOAT")
iflds = ["xdsd","YEAR", "lon","lat", "SHAPE@XY"]
iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIFBC, iflds)
count = 1
for ln in open(IN_FB, 'r').readlines():
           lnstrip = ln.strip()
           if count > 1:
               dataList = ln.split(",")
               lat = dataList[2]
               lon = dataList[1]
               y = dataList[4]
               xdsd = dataList[5]
               ivals = [xdsd, y, float(lon), float(lat),(float(lon), float(lat))]
               iCur.insertRow(ivals)
           count += 1
print('Finish Projection:',MIFBC)
del iCur
chazhi(MIFBC, "xdsd", "krigfb.tif",CC)
arcpy.Clip_management("krigfb.tif","","clipfb.tif",IN_CLIP,"0", "ClippingGeometry")
outReclass = arcpy.sa.Reclassify("clipfb.tif", "Value", arcpy.sa.RemapRange([[-10000,WXXLow,4],[WXXLow,WXXMid,3],[WXXMid,WXXHigh,2],[WXXHigh,50000,1]]))
outReclass.save(OUTPUTPATH+OUTPUTNAME+".tif")
#######################################
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
        return u"较低"
    elif a == 4:
        return u"低"

  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")

#############################################
arcpy.Delete_management(MIFBC)
arcpy.Delete_management("krigfb.tif")
arcpy.Delete_management("clipfb.tif")
if os.path.exists(in_fb_csv) == True:
    os.remove(in_fb_csv)
###########################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
      StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_fengbaochao_4J.clr")
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")