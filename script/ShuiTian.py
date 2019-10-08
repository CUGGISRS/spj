# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 17:24:23 2019

@author: 赵晓旭
农业生产适宜性评价——环境评价
"""
from __future__ import division
import arcpy
from arcpy import env
from arcpy.sa import *
import sys
import pandas as pd
import os
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
##############################################
#HARDCODE
PATH = sys.argv[1]      #PATH = 'D:\\test\\data\\agri_envi\\'
IN_TR=sys.argv[2]     #TR="TuRangWuRan.txt"  #土壤污染状况
IN_ST=sys.argv[3]   #IN_ST="ShiFouShuiTian.shp"
IN_CLIP=sys.argv[4]     #IN_CLIP="clipper.shp"  #裁剪
VAR_GEO= sys.argv[5]    #VAR_GEO="1" #0/1  1地理坐标系，0投影坐标系
VAR_FBL=sys.argv[6]     #VAR_FBL="150" #分辨率，不要大于5000
#镉-PH重分类的的参数
VAR_P_min=sys.argv[7]   #VAR_GN_P_min="5.5"  #ph<=5.5 
VAR_P_mid=sys.argv[8]        #VAR_GN_P_mid="6.5"  #5.5<ph<=6.5
VAR_P_max=sys.argv[9]                     #VAR_GN_P_max="7.5"  #6.5<ph<=7.5   ph>7.5
VAR_GN_SX1=sys.argv[10]#VAR_GN_SX1="0.3"   #ph<=5.5时的风险筛选值
VAR_GN_SX2=sys.argv[11]#VAR_GN_SX2="0.4"
VAR_GN_SX3=sys.argv[12]#VAR_GN_SX3="0.6"
VAR_GN_SX4=sys.argv[13]#VAR_GN_SX4="0.8"
VAR_GN_GZ1=sys.argv[14]#VAR_GN_GZ1="1.5"
VAR_GN_GZ2=sys.argv[15]#VAR_GN_GZ2="2.0"
VAR_GN_GZ3=sys.argv[16]#VAR_GN_GZ3="3.0"
VAR_GN_GZ4=sys.argv[17]#VAR_GN_GZ4="4.0"
#汞-PH重分类的的参数
VAR_GON_SX1=sys.argv[18]#VAR_GON_SX1="0.5"
VAR_GON_SX2=sys.argv[19]#VAR_GON_SX2="0.5"
VAR_GON_SX3=sys.argv[20]#VAR_GON_SX3="0.6"
VAR_GON_SX4=sys.argv[21]#VAR_GON_SX4="1.0"
VAR_GON_GZ1=sys.argv[22]#VAR_GON_GZ1="2.0"
VAR_GON_GZ2=sys.argv[23]#VAR_GON_GZ2="2.5"
VAR_GON_GZ3=sys.argv[24]#VAR_GON_GZ3="4.0"
VAR_GON_GZ4=sys.argv[25]#VAR_GON_GZ4="6.0"
#砷-PH重分类的参数
VAR_SN_SX1=sys.argv[26]#VAR_SN_SX1="30"
VAR_SN_SX2=sys.argv[27]#VAR_SN_SX2="30"
VAR_SN_SX3=sys.argv[28]#VAR_SN_SX3="25"
VAR_SN_SX4=sys.argv[29]#VAR_SN_SX4="20"
VAR_SN_GZ1=sys.argv[30]#VAR_SN_GZ1="200"
VAR_SN_GZ2=sys.argv[31]#VAR_SN_GZ2="150"
VAR_SN_GZ3=sys.argv[32]#VAR_SN_GZ3="120"
VAR_SN_GZ4=sys.argv[33]#VAR_SN_GZ4="100"
#铅-PH重分类的参数
VAR_QN_SX1=sys.argv[34]#VAR_QN_SX1="80"
VAR_QN_SX2=sys.argv[35]#VAR_QN_SX2="100"
VAR_QN_SX3=sys.argv[36]#VAR_QN_SX3="140"
VAR_QN_SX4=sys.argv[37]#VAR_QN_SX4="240"
VAR_QN_GZ1=sys.argv[38]#VAR_QN_GZ1="400"
VAR_QN_GZ2=sys.argv[39]#VAR_QN_GZ2="500"
VAR_QN_GZ3=sys.argv[40]#VAR_QN_GZ3="700"
VAR_QN_GZ4=sys.argv[41]#VAR_QN_GZ4="1000"
#铬-PH重分类的参数
VAR_GEN_SX1=sys.argv[42]#VAR_GEN_SX1="250"
VAR_GEN_SX2=sys.argv[43]#VAR_GEN_SX2="250"
VAR_GEN_SX3=sys.argv[44]#VAR_GEN_SX3="300"
VAR_GEN_SX4=sys.argv[45]#VAR_GEN_SX4="350"
VAR_GEN_GZ1=sys.argv[46]#VAR_GEN_GZ1="800"
VAR_GEN_GZ2=sys.argv[47]#VAR_GEN_GZ2="850"
VAR_GEN_GZ3=sys.argv[48]#VAR_GEN_GZ3="1000"
VAR_GEN_GZ4=sys.argv[49]#VAR_GEN_GZ4="1300"
IN_XZQQ=sys.argv[50]
OUTPUTPATH= sys.argv[51]
OUTPUTNAME=sys.argv[52] #OUTPUTNAME="huanjingpingjia" #输出
##############################################
#HARDCODE
#PATH = 'E:\\spj\\data\\agri_envi_st\\'
#IN_TR=PATH+"TuRangWuRan.xls"  #土壤污染状况
#IN_ST="ShiFouShuiTian.shp"
#IN_CLIP="clipper.shp"  #裁剪
#VAR_GEO="1" #0/1  1地理坐标系，0投影坐标系
#VAR_FBL="150" #分辨率，不要大于5000
##镉-PH重分类的的参数
#VAR_P_min="5.5"  #ph<=5.5 
#VAR_P_mid="6.5"  #5.5<ph<=6.5
#VAR_P_max="7.5"  #6.5<ph<=7.5   ph>7.5
#VAR_GN_SX1="0.3"   #ph<=5.5时的风险筛选值
#VAR_GN_SX2="0.4"
#VAR_GN_SX3="0.6"
#VAR_GN_SX4="0.8"
#VAR_GN_GZ1="1.5"
#VAR_GN_GZ2="2.0"
#VAR_GN_GZ3="3.0"
#VAR_GN_GZ4="4.0"
##汞-PH重分类的的参数
#VAR_GON_SX1="0.5"
#VAR_GON_SX2="0.5"
#VAR_GON_SX3="0.6"
#VAR_GON_SX4="1.0"
#VAR_GON_GZ1="2.0"
#VAR_GON_GZ2="2.5"
#VAR_GON_GZ3="4.0"
#VAR_GON_GZ4="6.0"
##砷-PH重分类的参数
#VAR_SN_SX1="30"
#VAR_SN_SX2="30"
#VAR_SN_SX3="25"
#VAR_SN_SX4="20"
#VAR_SN_GZ1="200"
#VAR_SN_GZ2="150"
#VAR_SN_GZ3="120"
#VAR_SN_GZ4="100"
##铅-PH重分类的参数
#VAR_QN_SX1="80"
#VAR_QN_SX2="100"
#VAR_QN_SX3="140"
#VAR_QN_SX4="240"
#VAR_QN_GZ1="400"
#VAR_QN_GZ2="500"
#VAR_QN_GZ3="700"
#VAR_QN_GZ4="1000"
##铬-PH重分类的参数
#VAR_GEN_SX1="250"
#VAR_GEN_SX2="250"
#VAR_GEN_SX3="300"
#VAR_GEN_SX4="350"
#VAR_GEN_GZ1="800"
#VAR_GEN_GZ2="850"
#VAR_GEN_GZ3="1000"
#VAR_GEN_GZ4="1300"
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="ny_shuitianhuanjing" #输出
#################################################
env.workspace=PATH[:-1]#工作环境
MI_TR="turang.shp"
in_trwr_csv =PATH+"TuRangWuRan.csv"
VAR_PH_min=float(VAR_P_min)
VAR_PH_mid=float(VAR_P_mid)
VAR_PH_max=float(VAR_P_max)
#重采样像元大小设定
########################################
FBLL=int(VAR_FBL)
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
#print CC
###################################
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
###############################################
cursor = arcpy.da.SearchCursor(IN_ST, ["SFST"])
nt=[]
for row in cursor:
    if row[0]==unicode("水田", "utf-8"):
        nt.append(1)
    else:
        nt.append(0)
del cursor
del row
cursor2 = arcpy.UpdateCursor(IN_ST)
try:
    arcpy.DeleteField_management(IN_ST, 'nt')
    arcpy.AddField_management(IN_ST, 'nt', "SHORT")   #创建aaa列，用来放置1，2，3，4，5    
except:
    arcpy.AddField_management(IN_ST, 'nt', "SHORT")  
i = 0
for my_row in cursor2:
    my_row.setValue('nt', nt[i])
    cursor2.updateRow(my_row)
    i += 1
del cursor2
del my_row
arcpy.FeatureToRaster_conversion(IN_ST,'nt','nongtian.tif',CC)
arcpy.Clip_management('nongtian.tif',"","ntfinal.tif",IN_CLIP,"", "ClippingGeometry")
###################################
#txt转shp文件
if IN_TR.endswith(".txt") or IN_TR.endswith(".csv"):
    pass
if IN_TR.endswith(".xls") or IN_TR.endswith(".xlsx"):
    if __name__ == '__main__':
                xlsx_to_csv_pd(IN_TR,in_trwr_csv)
                IN_TR = in_trwr_csv
try:
    arcpy.Delete_management(MI_TR)
    createFC = arcpy.CreateFeatureclass_management(env.workspace, MI_TR, "POINT", "", "", "")
except:
    createFC = arcpy.CreateFeatureclass_management(env.workspace, MI_TR, "POINT", "", "", "")
arcpy.AddField_management(env.workspace + "/" + MI_TR, "PH", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MI_TR, "镉", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MI_TR, "汞", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MI_TR, "砷", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MI_TR, "铅", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MI_TR, "铬", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MI_TR,  "lon", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MI_TR,  "lat", "FLOAT" )
iflds = ["PH","镉","汞","砷","铅","铬", "lon","lat", "SHAPE@XY"]
iCur = arcpy.da.InsertCursor(env.workspace + "/" + MI_TR, iflds)
count = 1
for ln in open(IN_TR, 'r').readlines():
           lnstrip = ln.strip()
           if count > 1:
               dataList = ln.split(",")
               ph=dataList[1]
               g=dataList[2]
               go=dataList[3]
               s=dataList[4]
               qh=dataList[5]
               ge=dataList[6]
               lat = dataList[8]
               lon = dataList[7]
               ivals = [float(ph),float(g),float(go),float(s),float(qh),float(ge), float(lon), float(lat),(float(lon), float(lat))]
#               print ivals
               iCur.insertRow(ivals)
           count += 1
print('Finish Projection:',MI_TR)
del iCur
###############################################
#克里金法（空间插值）
chazhi(MI_TR, "PH", "krigph.tif",CC)
chazhi(MI_TR, "镉", "krigg.tif",CC)
chazhi(MI_TR, "汞", "kriggo.tif",CC)
chazhi(MI_TR, "砷", "krigs.tif",CC)
chazhi(MI_TR, "铅", "krigq.tif",CC)
chazhi(MI_TR, "铬", "krigge.tif",CC)
#arcpy.Copy_management("krigph.tif","krigph1.tif" )
#################################################
#镉
var=arcpy.RasterToNumPyArray("krigph.tif")
var1=arcpy.RasterToNumPyArray("krigph.tif")
var2=arcpy.RasterToNumPyArray("krigg.tif")
rowNum,colNum = var.shape #波段、行数、列数
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = var[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            var[i][j] = float(VAR_GN_SX1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            var[i][j] = float(VAR_GN_SX2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            var[i][j] = float(VAR_GN_SX3)
        elif VAR_PH_max<value:
            var[i][j] = float(VAR_GN_SX4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = var1[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            var1[i][j] = float(VAR_GN_GZ1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            var1[i][j] = float(VAR_GN_GZ2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            var1[i][j] = float(VAR_GN_GZ3)
        elif VAR_PH_max<value:
            var1[i][j] =float(VAR_GN_GZ4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = var2[i][j]
        if var[i][j]<var2[i][j]<=var1[i][j]: 
             var2[i][j]= 3
        elif var[i][j]>=var2[i][j]:
            var2[i][j] = 1
        elif var2[i][j]>var1[i][j]:
            var2[i][j] = 5  
r = arcpy.Raster("krigph.tif")
lowerLeft = arcpy.Point(r.extent.XMin,r.extent.YMin)
cellWidth = r.meanCellWidth #栅格像元宽度
cellHeight =r.meanCellHeight #栅格像元高度
newRaster = arcpy.NumPyArrayToRaster(var2,lowerLeft,cellWidth,cellHeight)
newRaster.save("ge.tif")
ax=Int("ge.tif")
ax.save("gefinal.tif")
#####################################################
#汞
var3=arcpy.RasterToNumPyArray("krigph.tif")
var4=arcpy.RasterToNumPyArray("krigph.tif")
var5=arcpy.RasterToNumPyArray("kriggo.tif")
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = var3[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            var3[i][j] = float(VAR_GON_SX1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            var3[i][j] = float(VAR_GON_SX2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            var3[i][j] = float(VAR_GON_SX3)
        elif VAR_PH_max<value:
            var3[i][j] = float(VAR_GON_SX4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = var4[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            var4[i][j] = float(VAR_GON_GZ1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            var4[i][j] = float(VAR_GON_GZ2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            var4[i][j] = float(VAR_GON_GZ3)
        elif VAR_PH_max<value:
            var4[i][j] = float(VAR_GON_GZ4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = var5[i][j]
        if var3[i][j]<var5[i][j]<=var4[i][j]: 
             var5[i][j]= 3
        elif var3[i][j]>=var5[i][j]:
            var5[i][j] = 1
        elif var5[i][j]>var4[i][j]:
            var5[i][j] = 5   
newRaster = arcpy.NumPyArrayToRaster(var5,lowerLeft,cellWidth,cellHeight)
newRaster.save("go.tif")
ax=Int("go.tif")
ax.save("gofinal.tif")
#########################################
#砷
vara=arcpy.RasterToNumPyArray("krigph.tif")
vara1=arcpy.RasterToNumPyArray("krigph.tif")
vara2=arcpy.RasterToNumPyArray("krigs.tif")
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = vara[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            vara[i][j] = float(VAR_SN_SX1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            vara[i][j] = float(VAR_SN_SX2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            vara[i][j] = float(VAR_SN_SX3)
        elif VAR_PH_max<value:
            vara[i][j] = float(VAR_SN_SX4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = vara1[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            vara1[i][j] = float(VAR_SN_GZ1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            vara1[i][j] = float(VAR_SN_GZ2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            vara1[i][j] = float(VAR_SN_GZ3)
        elif VAR_PH_max<value:
            vara1[i][j] =float(VAR_SN_GZ4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = vara2[i][j]
        if vara[i][j]<vara2[i][j]<=vara1[i][j]: 
             vara2[i][j]= 3
        elif var[i][j]>=vara2[i][j]:
            vara2[i][j] = 1
        elif vara2[i][j]>vara1[i][j]:
            vara2[i][j] = 5   
newRaster = arcpy.NumPyArrayToRaster(vara2,lowerLeft,cellWidth,cellHeight)
newRaster.save("shen.tif")
ax=Int("shen.tif")
ax.save("shenfinal.tif")
########################################
#铅
varq=arcpy.RasterToNumPyArray("krigph.tif")
varq1=arcpy.RasterToNumPyArray("krigph.tif")
varq2=arcpy.RasterToNumPyArray("krigq.tif")
rowNum,colNum = var.shape #波段、行数、列数
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = varq[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            varq[i][j] = float(VAR_QN_SX1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            varq[i][j] = float(VAR_QN_SX2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            varq[i][j] =float(VAR_QN_SX3)
        elif VAR_PH_max<value:
            varq[i][j] = float(VAR_QN_SX4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = varq1[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            varq1[i][j] = float(VAR_QN_GZ1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            varq1[i][j] = float(VAR_QN_GZ2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            varq1[i][j] = float(VAR_QN_GZ3)
        elif VAR_PH_max<value:
            varq1[i][j] =float(VAR_QN_GZ4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = varq2[i][j]
        if varq[i][j]<varq2[i][j]<=varq1[i][j]: 
             varq2[i][j]= 3
        elif varq[i][j]>=varq2[i][j]:
            var2[i][j] = 1
        elif varq2[i][j]>varq1[i][j]:
            varq2[i][j] = 5   
newRaster = arcpy.NumPyArrayToRaster(varq2,lowerLeft,cellWidth,cellHeight)
newRaster.save("qian.tif")
ax=Int("qian.tif")
ax.save("qianfinal.tif")
###################################
#铬
vart=arcpy.RasterToNumPyArray("krigph.tif")
vart1=arcpy.RasterToNumPyArray("krigph.tif")
vart2=arcpy.RasterToNumPyArray("krigge.tif")
rowNum,colNum = var.shape #波段、行数、列数
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = vart[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            vart[i][j] = float(VAR_GEN_SX1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            vart[i][j] = float(VAR_GEN_SX2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            vart[i][j] = float(VAR_GEN_SX3)
        elif VAR_PH_max<value:
            vart[i][j] = float(VAR_GEN_SX4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = vart1[i][j]
        if value<=VAR_PH_min: #最大值的像元分成最后一类
            vart1[i][j] = float(VAR_GEN_GZ1)
        elif VAR_PH_min<value<=VAR_PH_mid:
            vart1[i][j] = float(VAR_GEN_GZ2)
        elif VAR_PH_mid<value<=VAR_PH_max:
            vart1[i][j] = float(VAR_GEN_GZ3)
        elif VAR_PH_max<value:
            vart1[i][j] =float(VAR_GEN_GZ4)
for i in range(0,rowNum):
    for j in range(0,colNum):
        value = vart2[i][j]
        if vart[i][j]<vart2[i][j]<=vart1[i][j]: 
             vart2[i][j]= 3
        elif vart[i][j]>=vart2[i][j]:
            vart2[i][j] = 1
        elif vart2[i][j]>vart1[i][j]:
            vart2[i][j] = 5  
newRaster = arcpy.NumPyArrayToRaster(vart2,lowerLeft,cellWidth,cellHeight)
newRaster.save("gee.tif")
ax=Int("gee.tif")
ax.save("geefinal.tif")
#######################################
arcpy.RasterToPolygon_conversion ("gefinal.tif", "geshp.shp")
arcpy.RasterToPolygon_conversion ("gofinal.tif", "goshp.shp")
arcpy.RasterToPolygon_conversion ("shenfinal.tif", "shenshp.shp")
arcpy.RasterToPolygon_conversion ("qianfinal.tif", "qianshp.shp")
arcpy.RasterToPolygon_conversion ("geefinal.tif", "geeshp.shp")
arcpy.Intersect_analysis (["geshp.shp", "goshp.shp","shenshp.shp","qianshp.shp","geeshp.shp"],"zhshp.shp" )    
cursor = arcpy.da.SearchCursor("zhshp.shp", ["GRIDCODE","GRIDCODE_1","GRIDCODE_2","GRIDCODE_3","GRIDCODE_4"])
new=[]
for row in cursor:
    new.append(max(row[0],row[1],row[2],row[3],row[4]))
    
    
try:
    arcpy.DeleteField_management("zhshp.shp", 'jg')
    arcpy.AddField_management("zhshp.shp", 'jg', "SHORT")   #创建aaa列，用来放置1，2，3，4，5    
except:    
    arcpy.AddField_management("zhshp.shp", 'jg', "SHORT")    
cursor1 = arcpy.UpdateCursor("zhshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('jg', new[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
arcpy.FeatureToRaster_conversion("zhshp.shp", "jg", "jg.tif",CC)
arcpy.Clip_management("jg.tif","",'tuu.tif',IN_CLIP,"", "ClippingGeometry")
e=arcpy.Raster('tuu.tif')*arcpy.Raster("ntfinal.tif")
e.save(OUTPUTPATH+OUTPUTNAME+".tif")
################################
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
    else:
        return u"非水田区域"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3", )
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
#########################
arcpy.Delete_management(MI_TR)
arcpy.Delete_management("ntfinal.tif")
arcpy.Delete_management("nongtian.tif")
arcpy.Delete_management('tuu.tif')
arcpy.Delete_management("krigph.tif")
arcpy.Delete_management("krigg.tif")
arcpy.Delete_management("kriggo.tif")
arcpy.Delete_management("krigs.tif")
arcpy.Delete_management("krigq.tif")
arcpy.Delete_management("krigge.tif")
arcpy.Delete_management("go.tif")
arcpy.Delete_management("ge.tif")
arcpy.Delete_management("shen.tif")
arcpy.Delete_management("qian.tif")
arcpy.Delete_management("gee.tif")
arcpy.Delete_management("gofinal.tif")
arcpy.Delete_management("gefinal.tif")
arcpy.Delete_management("shenfinal.tif")
arcpy.Delete_management("qianfinal.tif")
arcpy.Delete_management("geefinal.tif")
arcpy.Delete_management("goshp.tif")
arcpy.Delete_management("geshp.tif")
arcpy.Delete_management("shenshp.tif")
arcpy.Delete_management("qianshp.tif")
arcpy.Delete_management("geeshp.tif")
arcpy.Delete_management("zhshp.shp")
arcpy.Delete_management("qianshp.tif")
arcpy.Delete_management("geeshp.tif")
arcpy.Delete_management( "jg.tif")
if os.path.exists(in_trwr_csv) == True:
    os.remove(in_trwr_csv)
################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
     StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_nong_huan_3J.clr")
###########################################
##############################################
arcpy.CheckInExtension('Spatial')
arcpy.CheckInExtension('3D')
