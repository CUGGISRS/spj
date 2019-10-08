# -*- coding: utf-8 -*-
from __future__ import division
import arcpy
import sys
import pandas as pd
import os
import numpy as np
from arcpy import env
from arcpy.sa import *
import RasterTableToTxtAndExcel
import StaticticsByXZQ
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
######################################
PATH=sys.argv[1] #PATH="D:\\test\\data\\agri_func_zaihai\\gaowen\\"
IN_GW=sys.argv[2]#GW="gaowen.txt"  #高温txt文件
IN_CLIP=sys.argv[3]   #IN_CLIP="clipper.shp"#裁剪 输入数据
VAR_GEO=sys.argv[4]#VAR_GEO="1" #0/1  1地理坐标系 0投影坐标系
VAR_FBL=sys.argv[5]#VAR_FBL="150" #分辨率
##高温发生频率分级
VAR_GW1=sys.argv[6]#VAR_GW1="0.2"  #小于等于 0.2 为低
VAR_GW2=sys.argv[7]#VAR_GW2="0.4" #0.2~0.4 为较低
VAR_GW3=sys.argv[8]#VAR_GW3="0.6" #0.4~0.6 为中等
VAR_GW4=sys.argv[9]#VAR_GW4="0.8" #0.6~0.8 为较高     大于0.8为高
VAR_w3=sys.argv[10]#VAR_w3="38"  #判定为高温日的温度
VAR_T=sys.argv[11]#VAR_T="3"  #3天以上大于等于35度为一次高温过程
VAR_w=sys.argv[12]#VAR_w="35"
VAR_T1=sys.argv[13]#VAR_T1="2"  # 2天以上大于等于35度并有一天大于等于38度为一次高温过程
VAR_w1=sys.argv[14]#VAR_w1="35"
VAR_T2=sys.argv[15]#VAR_T2="1"
VAR_w2=sys.argv[16]#VAR_w2="38"
VAR_C=sys.argv[17]#VAR_C="3"   #一年中出现3次以上高温过程为一个高温年
VAR_T3=sys.argv[18]#VAR_T3="30"  #出现30天以上高温日为一个高温年
IN_XZQQ=sys.argv[19]
OUTPUTPATH = sys.argv[20]
OUTPUTNAME = sys.argv[21]#OUTPUTNAME="gaowenzaihai"
######################################
#PATH="E:\\spj\\data\\agri_func_zaihai\\gaowen\\"
#IN_GW=PATH+"gaowen.xls"  #高温txt文件
#IN_CLIP="clipper.shp"#裁剪 输入数据
#VAR_GEO="1" #0/1  1地理坐标系 0投影坐标系
#VAR_FBL="150" #分辨率
# #高温发生频率分级
#VAR_GW1="0.2"  #小于等于 0.2 为低
#VAR_GW2="0.4" #0.2~0.4 为较低
#VAR_GW3="0.6" #0.4~0.6 为中等
#VAR_GW4="0.8" #0.6~0.8 为较高     大于0.8为高
#VAR_w3="38"  #判定为高温日的温度
#VAR_T="3"  #3天以上大于等于35度为一次高温过程
#VAR_w="35"
#VAR_T1="2"  # 2天以上大于等于35度并有一天大于等于38度为一次高温过程
#VAR_w1="35"
#VAR_T2="1"
#VAR_w2="38"
#VAR_C="3"   #一年中出现3次以上高温过程为一个高温年
#VAR_T3="30"  #出现30天以上高温日为一个高温年
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="ny_gaowen"
#####################################
env.workspace=PATH[:-1]
MIGW="gaowen.shp"
in_gw_csv = PATH+"gaowen.csv"
####################################
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
def xlsx_to_csv_pd(xlsxpath,csvpath):
    data_xls = pd.read_excel(xlsxpath, index_col=0)
    data_xls.to_csv(csvpath, encoding='utf-8')
def sum_list(items):  
    sum_numbers = 0  
    for x in items:  
        sum_numbers += x  
    return sum_numbers 
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
######################################
if IN_GW.endswith(".txt") or IN_GW.endswith(".csv")  :
    pass
if IN_GW.endswith(".xls") or IN_GW.endswith(".xlsx"):
    if __name__ == '__main__':
                xlsx_to_csv_pd(IN_GW,in_gw_csv)
                IN_GW = in_gw_csv
try:
    arcpy.Delete_management(MIGW)
    createFC = arcpy.CreateFeatureclass_management(env.workspace, MIGW, "POINT", "", "", "")  
except:  
    createFC = arcpy.CreateFeatureclass_management(env.workspace, MIGW, "POINT", "", "", "")
arcpy.AddField_management(env.workspace + "/" + MIGW, "YEAR", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIGW, "MONTH", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIGW, "DAY", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIGW, "GW", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIGW,  "lon", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MIGW,  "lat", "FLOAT" )
iflds = ["YEAR","MONTH","DAY","GW", "lon","lat", "SHAPE@XY"]
iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIGW, iflds)
count = 1
for ln in open(IN_GW, 'r').readlines():
           lnstrip = ln.strip()
           if count > 1:
               dataList = ln.split(",")
               y=dataList[4]
               m=dataList[5]
               d=dataList[6]
               j=dataList[7]
               lat = dataList[2]
               lon = dataList[1]
               ivals = [y,m,d,j, float(lon), float(lat),(float(lon), float(lat))]
               iCur.insertRow(ivals)
           count += 1
print('Finish Projection:',MIGW)
del iCur
arcpy.Dissolve_management(MIGW, "gw1.shp", ["lon","lat",'YEAR'],[['DAY','COUNT']])
cursor = arcpy.da.SearchCursor("gw1.shp", ["YEAR","lon","lat","COUNT_DAY"])
year=[]
lon=[]
lat=[]
count_day=[]
for row in cursor:
    year.append(row[0])
    lon.append(row[1])
    lat.append(row[2])
    count_day.append(row[3])
del cursor,row
lists=[]
for i in range(len(year)):
    lists.append([])
for i in range(len(year)):
    cursor = arcpy.da.SearchCursor(MIGW, ["YEAR","lon","lat","GW"])
    for row in cursor:
        if row[0]==year[i] and row[1]==lon[i] and row[2]==lat[i] :
            lists[i].append(row[3]/10.)
del row,cursor
ll=[]
for i in range(len(year)):
    chunks =[lists[i][s:s + int(VAR_T)] for s in range(0, len(lists[i])-int(VAR_T))]
    chunks1 =[lists[i][s:s + int(VAR_T1)] for s in range(0, len(lists[i])-int(VAR_T1))]
    count=[]
    count1=[]
    count2=[]
    for s in chunks:
#        print s
        if s[0]>=int(VAR_w) and s[1]>=int(VAR_w) and s[2]>=int(VAR_w)   :
            count.append(1)
        else:
              count.append(0)
#    print count
    for t in chunks1:
#        print t
        if t[0]>=int(VAR_w1) and t[1]>=int(VAR_w2)   :
            count1.append(1)
        elif t[0]>=int(VAR_w2) and t[1]>=int(VAR_w1):
            count1.append(1)
        else:
              count1.append(0)
#    print count1
    for e in lists[i]:
        if e>int(VAR_w3):
            count2.append(1)
        else:
            count2.append(0)
    if sum_list(count) >int(VAR_C) or sum_list(count1) >int(VAR_C) or sum_list(count2)>int(VAR_T3):
        ll.append(1)
    else:
        ll.append(0)
try:
    arcpy.DeleteField_management("gw1.shp", 'gw')
    arcpy.AddField_management("gw1.shp", 'gw', "FLOAT")   
except:                       
    arcpy.AddField_management("gw1.shp", 'gw', "FLOAT")
cursor1 = arcpy.UpdateCursor("gw1.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('gw', ll[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row 
arcpy.Dissolve_management("gw1.shp", "gw2.shp", ["lon","lat"],[['YEAR','COUNT'],['gw','SUM']])
cursor = arcpy.da.SearchCursor("gw2.shp", ["COUNT_YEAR","SUM_gw"])
po=[]
for row in cursor:          
    po.append(row[1]/row[0])
del cursor,row
try:
    arcpy.DeleteField_management("gw2.shp", 'bfb')
    arcpy.AddField_management("gw2.shp", 'bfb', "FLOAT")  
except:                       
    arcpy.AddField_management("gw2.shp", 'bfb', "FLOAT")
cursor1 = arcpy.UpdateCursor("gw2.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('bfb', po[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
#p="Variable %d"%(len(po)) 
chazhi("gw2.shp", "bfb", "gwkrig.tif",CC)
arcpy.Clip_management("gwkrig.tif","","gwclip.tif",IN_CLIP,"", "ClippingGeometry")
outReclass2 = arcpy.sa.Reclassify("gwclip.tif", "Value", arcpy.sa.RemapRange([[-10000,float(VAR_GW1),5],[float(VAR_GW1),float(VAR_GW2),4],[float(VAR_GW2),float(VAR_GW3),3],[float(VAR_GW3),float(VAR_GW4),2],[float(VAR_GW4),10000,1]]),'NODATA')
outReclass2.save(OUTPUTPATH+OUTPUTNAME+".tif")
###########################################
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
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management(MIGW)
arcpy.Delete_management("gw1.shp")
arcpy.Delete_management("gw2.shp")
arcpy.Delete_management("gwkrig.tif")
arcpy.Delete_management("gwclip.tif")
if os.path.exists(in_gw_csv):
    os.remove(in_gw_csv)
##############################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
      StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_nong_tu_zai_5J.clr")
################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
