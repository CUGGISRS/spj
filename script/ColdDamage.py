# -*- coding: utf-8 -*-
from __future__ import division
import arcpy
import sys
import numpy as np
from arcpy import env
from arcpy.sa import *
import pandas as pd
import os
import RasterTableToTxtAndExcel
import StaticticsByXZQ
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
######################################
PATH=sys.argv[1]#PATH="D:\\test\\data\\agri_func_zaihai\\diwen\\"
IN_DW=sys.argv[2]#DW="diwen.txt" #低温txt文件
IN_CLIP=sys.argv[3]#IN_CLIP="clipper.shp"#裁剪 输入数据
VAR_GEO=sys.argv[4]#VAR_GEO="1" #0/1   1地理坐标系  0投影坐标系
VAR_FBL=sys.argv[5]#VAR_FBL="150" #分辨率 不大于5000
IN_M=sys.argv[6]#IN_M="4"  #农作物发育开始月份
IN_M1=sys.argv[7]#IN_M1="9"  #农作物发育开始日期
IN_D=sys.argv[8]#IN_D="12"  #农作物发育结束月份
IN_D1=sys.argv[9]#IN_D1="16"  #农作物发育结束日期
IN_W=sys.argv[10]#IN_W="15" #农作物发育时段的环境温度
IN_TT=sys.argv[11]#IN_TT="20" #农作物发育时段气温低于其生长发育所需温度天数，当天数大于这个值时，判定为冷害年
##低温发生频率分级20
VAR_DW1=sys.argv[12]#VAR_DW1="0.2"  #小于等于 0.2 为低
VAR_DW2=sys.argv[13]#VAR_DW2="0.4" #0.2~0.4 为较低
VAR_DW3=sys.argv[14]#VAR_DW3="0.6" #0.4~0.6 为中等
VAR_DW4=sys.argv[15]#VAR_DW4="0.8" #0.6~0.8 为较高     大于0.8为高
IN_XZQQ=sys.argv[16]
OUTPUTPATH =  sys.argv[17]
OUTPUTNAME=sys.argv[18]#OUTPUTNAME="diwenzaihai" #输出
######################################
#PATH="E:\\spj\\data\\agri_func_zaihai\\diwen\\"
#IN_DW=PATH+"diwen.txt" #低温txt文件
#IN_CLIP="clipper.shp"#裁剪 输入数据
#VAR_GEO="1" #0/1   1地理坐标系  0投影坐标系
#VAR_FBL="150" #分辨率 不大于5000
#IN_M="4"  #农作物发育开始月份
#IN_M1="9"  #农作物发育开始日期
#IN_D="12"  #农作物发育结束月份
#IN_D1="16"  #农作物发育结束日期
#IN_W="15" #农作物发育时段的环境温度
#IN_TT="20" #农作物发育时段气温低于其生长发育所需温度天数，当天数大于这个值时，判定为冷害年
# #低温发生频率分级
#VAR_DW1="0.2"  #小于等于 0.2 为低
#VAR_DW2="0.4" #0.2~0.4 为较低
#VAR_DW3="0.6" #0.4~0.6 为中等
#VAR_DW4="0.8" #0.6~0.8 为较高     大于0.8为高
#IN_XZQQ="E:\\spj\\data\\agri_func_zaihai\\diwen\\XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="ny_diwen" #输出
#####################################
env.workspace=PATH[:-1]
#IN_DW=PATH+DW
MIDW="diwen.shp"
in_dw_csv=PATH+"diwen.csv"
####################################
#重采样像元大小设定
FBLL=int(VAR_FBL)
if int(VAR_GEO)==1:#地理坐标系
    VAR_FBL=0.0000101*int(VAR_FBL)
else:#投影坐标系
    VAR_FBL=int(VAR_FBL)
CC="%f"%(VAR_FBL)
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
if IN_DW.endswith(".txt") or IN_DW.endswith(".csv"):
    pass
if IN_DW.endswith(".xls") or IN_DW.endswith(".xlsx"):
    if __name__ == '__main__':
                xlsx_to_csv_pd(IN_DW,in_dw_csv)
                IN_DW = in_dw_csv
try:
    arcpy.Delete_management(MIDW)
    createFC = arcpy.CreateFeatureclass_management(env.workspace, MIDW, "POINT", "", "", "")  
except:  
    createFC = arcpy.CreateFeatureclass_management(env.workspace, MIDW, "POINT", "", "", "")
arcpy.AddField_management(env.workspace + "/" + MIDW, "YEAR", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIDW, "MONTH", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIDW, "DAY", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIDW, "DW", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIDW,  "lon", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MIDW,  "lat", "FLOAT" )
iflds = ["YEAR","MONTH","DAY","DW", "lon","lat", "SHAPE@XY"]
iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIDW, iflds)
count = 1
for ln in open(IN_DW, 'r').readlines():
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
print('Finish Projection:',MIDW)
del iCur
arcpy.Dissolve_management(MIDW, "dw1.shp", ["lon","lat",'YEAR'],[['DAY','COUNT']])
cursor = arcpy.da.SearchCursor("dw1.shp", ["YEAR","lon","lat","COUNT_DAY"])
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
    cursor = arcpy.da.SearchCursor(MIDW, ["YEAR","MONTH","DAY","lon","lat","DW"])
    for row in cursor:
        if row[0]==year[i] and row[3]==lon[i] and row[4]==lat[i] :
            if row[1]==int(IN_M) and row[2]>=int(IN_D):
                  lists[i].append(row[5]/10.)
            elif int(IN_M1)>row[1]>int(IN_M):
                  lists[i].append(row[5]/10.)
            elif row[1]==int(IN_M1) and row[2]<=int(IN_D1):
                  lists[i].append(row[5]/10.)
del row,cursor
#print lists[0]
ll=[]
for i in range(len(year)):
     count=[]
     for e in lists[i]:
         if e<int(IN_W):
            count.append(1)
         else:
            count.append(0)
     if sum_list(count) >=int(IN_TT)  :
        ll.append(1)
     else:
        ll.append(0)
try:
    arcpy.DeleteField_management("dw1.shp", 'dw')
    arcpy.AddField_management("dw1.shp", 'dw', "FLOAT")    
except:                       
    arcpy.AddField_management("dw1.shp", 'dw', "FLOAT")
cursor1 = arcpy.UpdateCursor("dw1.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('dw', ll[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row 
arcpy.Dissolve_management("dw1.shp", "dw2.shp", ["lon","lat"],[['YEAR','COUNT'],['dw','SUM']])
cursor = arcpy.da.SearchCursor("dw2.shp", ["COUNT_YEAR","SUM_dw"])
po=[]
for row in cursor:          
    po.append(row[1]/row[0])
del cursor,row
try:
    arcpy.DeleteField_management("dw2.shp", 'bfb')
    arcpy.AddField_management("dw2.shp", 'bfb', "FLOAT")    
except:                       
    arcpy.AddField_management("dw2.shp", 'bfb', "FLOAT")
cursor1 = arcpy.UpdateCursor("dw2.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('bfb', po[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
chazhi("dw2.shp", "bfb", "dwkrig.tif",CC)
arcpy.Clip_management("dwkrig.tif","","dwclip.tif",IN_CLIP,"", "ClippingGeometry")
outReclass2 = arcpy.sa.Reclassify("dwclip.tif", "Value", arcpy.sa.RemapRange([[-100000,float(VAR_DW1),5],[float(VAR_DW1),float(VAR_DW2),4],[float(VAR_DW2),float(VAR_DW3),3],[float(VAR_DW3),float(VAR_DW4),2],[float(VAR_DW4),10000,1]]),'NODATA')
outReclass2.save(OUTPUTPATH+OUTPUTNAME+".tif")
#########################################
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
arcpy.Delete_management(MIDW)
arcpy.Delete_management("dw1.shp")
arcpy.Delete_management("dw2.shp")
arcpy.Delete_management("dwkrig.tif")
arcpy.Delete_management("dwclip.tif")
if os.path.exists(in_dw_csv) == True:
    os.remove(in_dw_csv)
##################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
       StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_nong_tu_zai_5J.clr")
#######################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")