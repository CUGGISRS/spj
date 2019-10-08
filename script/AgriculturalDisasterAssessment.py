# -*- coding: utf-8 -*-
from __future__ import division
import arcpy
import sys
from arcpy import env
from arcpy.sa import *
import RasterTableToTxtAndExcel
import StaticticsByXZQ
import os
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
######################################
#PATH=sys.argv[1]#PATH="D:\\test\\data\\agri_func_zaihai\\zaihaizhenghe\\"
#IN_JY=sys.argv[2]#JY="jiangyuzaihai.tif"  #降雨灾害
#IN_GW=sys.argv[3]#GW="gaowenzaihai.tif"    #高温灾害
#IN_DW=sys.argv[4]#DW="diwenzaihai.tif"   #低温灾害
#IN_DF=sys.argv[5]#DF="dafengzaihai.tif"  #大风灾害
#IN_GH=sys.argv[6]#GH="ganhanzaihai.tif"  #干旱灾害
#IN_CLIP=sys.argv[7]
#VAR_GEO=sys.argv[8]
#VAR_FBL=sys.argv[9]
#VAR_1=sys.argv[10]#VAR_1="0.2"     #降雨权重系数
#VAR_2=sys.argv[11]#VAR_2="0.1"   #高温权重系数
#VAR_3=sys.argv[12]#VAR_3="0.25"   #低温权重系数
#VAR_4=sys.argv[13]#VAR_4="0.15"   #大风权重系数
#VAR_5=sys.argv[14]#VAR_5="0.3"    #干旱权重系数
###灾害整合的重分类
#VAR_ZH1=sys.argv[15]#VAR_ZH1="1"    #1~1.8 为高
#VAR_ZH2=sys.argv[16]#VAR_ZH2="1.8"   #1.8~2.6   为较高
#VAR_ZH3=sys.argv[17]#VAR_ZH3="2.6"   #2.6~3.4   为中等
#VAR_ZH4=sys.argv[18]#VAR_ZH4="3.4"   #3.4~4.2   为较低
#VAR_ZH5=sys.argv[19]#VAR_ZH5="4.2"  #4.2~5     为低
#VAR_ZH6=sys.argv[20]#VAR_ZH6="5"
#IN_XZQQ=sys.argv[21]
#OUTPUTPATH = sys.argv[22]
#OUTPUTNAME=sys.argv[23]#OUTPUTNAME="zaihai"   #输出
######################################
PATH="E:\\spj\\data\\agri_func_zaihai\\zaihaizhenghe\\"
IN_JY="jiangyuzaihai.tif"  #降雨灾害  #
IN_GW="99999"    #高温灾害
IN_DW="99999"   #低温灾害
IN_DF="dafengzaihai.tif"  #大风灾害
IN_GH="99999"  #干旱灾害
IN_CLIP="clipper.shp"
VAR_GEO="1" #0/1
VAR_FBL="150" #不要大于5000
VAR_1="0.2"     #降雨权重系数
VAR_2="0.1"   #高温权重系数
VAR_3="0.25"   #低温权重系数
VAR_4="0.15"   #大风权重系数
VAR_5="0.3"    #干旱权重系数
 #灾害整合的重分类
VAR_ZH1="1"    #1~1.8 为高
VAR_ZH2="1.8"   #1.8~2.6   为较高
VAR_ZH3="2.6"   #2.6~3.4   为中等
VAR_ZH4="3.4"   #3.4~4.2   为较低
VAR_ZH5="4.2"  #4.2~5     为低
VAR_ZH6="5"
IN_XZQQ='E:\\spj\\data\\agri_func_zaihai\\zaihaizhenghe\\XZQ_WGS84.shp'
OUTPUTPATH="D:\\map\\"
OUTPUTNAME="ttttt"   #输出
#####################################
env.workspace=PATH[:-1]
###################################
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
####################################
if IN_JY == "99999":
    VAR_1="0"
    IN_JY = create_raster(5,IN_CLIP,VAR_FBL,"tihuan.tif")
if IN_GW == "99999":
    VAR_2="0"
    IN_GW = create_raster(5,IN_CLIP,VAR_FBL,"tihuan1.tif")
if IN_DW == "99999":
    VAR_3="0"
    IN_DW = create_raster(5,IN_CLIP,VAR_FBL,"tihuan2.tif")
if IN_DF == "99999":
    VAR_4="0"
    IN_DF = create_raster(5,IN_CLIP,VAR_FBL,"tihuan3.tif")
if IN_GH == "99999":
    VAR_5="0"
    IN_GH = create_raster(5,IN_CLIP,VAR_FBL,"tihuan4.tif")
f=float(VAR_1)*arcpy.Raster(IN_JY)+float(VAR_2)*arcpy.Raster(IN_GW)+float(VAR_3)*arcpy.Raster(IN_DW)+float(VAR_4)*arcpy.Raster(IN_DF)+float(VAR_5)*arcpy.Raster(IN_GH)
f.save("ff.tif")

#################################
outReclass2 = arcpy.sa.Reclassify("ff.tif", "Value", arcpy.sa.RemapRange([[float(VAR_ZH1),float(VAR_ZH2),1],[float(VAR_ZH2),float(VAR_ZH3),2],[float(VAR_ZH3),float(VAR_ZH4),3],[float(VAR_ZH4),float(VAR_ZH5),4],[float(VAR_ZH5),float(VAR_ZH6),5]]),'NODATA')
outReclass2.save(OUTPUTPATH+OUTPUTNAME+".tif")
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
        return u"中等"
    elif a == 4:
        return u"较低"
    else:
        return u'低'"""
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")

arcpy.Delete_management("ff.tif")
if arcpy.Exists("tihuan.tif"):
    arcpy.Delete_management("tihuan.tif")
if arcpy.Exists("tihuan1.tif"):
    arcpy.Delete_management("tihuan1.tif")
if arcpy.Exists("tihuan2.tif"):
    arcpy.Delete_management("tihuan2.tif")
if arcpy.Exists("tihuan3.tif"):
    arcpy.Delete_management("tihuan3.tif")
if arcpy.Exists("tihuan4.tif"):
    arcpy.Delete_management("tihuan4.tif")
####################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#",  "C:/yz_spj/clr/Month4_nong_tu_zai_5J.clr")                           
################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
