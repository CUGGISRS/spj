# -*- coding: utf-8 -*-
from __future__ import division
import arcpy
import sys
import pandas as pd
import os
from arcpy import env
from arcpy.sa import *
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
######################################
PATH=sys.argv[1]      #PATH="D:\\test\\data\\agri_func_zaihai\\dafeng\\"
IN_DF=sys.argv[2]                 #DF="dafeng.txt" #大风txt文件
IN_CLIP=sys.argv[3] #IN_CLIP="clipper.shp"#裁剪 输入数据
VAR_GEO=sys.argv[4]#VAR_GEO="1" #0/1 1为地理坐标系 0为投影坐标系
VAR_FBL=sys.argv[5]#VAR_FBL="150" #分辨率 不大于5000
##大风发生频率分级
VAR_DF1=sys.argv[6]#VAR_DF1="0.2"  #小于等于 0.2 为低
VAR_DF2=sys.argv[7]#VAR_DF2="0.4" #0.2~0.4 为较低
VAR_DF3=sys.argv[8]#VAR_DF3="0.6" #0.4~0.6 为中等
VAR_DF4=sys.argv[9]#VAR_DF4="0.8" #0.6~0.8 为较高     大于0.8为高
VAR_DF=sys.argv[10]#VAR_DF="17" #顺时风速达到或超过17为大风日
VAR_KF=sys.argv[11]#VAR_KF="24.5" #顺时风速达到或超过24.5为狂风日
VAR_T=sys.argv[12]#VAR_T="30"  #一年中出现30大风日或狂风日为风灾年
IN_XZQQ=sys.argv[13]
OUTPUTPATH = sys.argv[14]
OUTPUTNAME=sys.argv[15]#OUTPUTNAME="dafengzaihai"  #输出
######################################
#PATH="E:\\spj\\data\\agri_func_zaihai\\dafeng\\"
#IN_DF=PATH+"dafeng.txt" #大风txt文件
#IN_CLIP="clipper.shp"#裁剪 输入数据
#VAR_GEO="1" #0/1 1为地理坐标系 0为投影坐标系
#VAR_FBL="150" #分辨率 不大于5000
# #大风发生频率分级
#VAR_DF1="0.2"  #小于等于 0.2 为低
#VAR_DF2="0.4" #0.2~0.4 为较低
#VAR_DF3="0.6" #0.4~0.6 为中等
#VAR_DF4="0.8" #0.6~0.8 为较高     大于0.8为高
#VAR_DF="17"
#VAR_KF="24.5"
#VAR_T="30"
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="ny_dafeng"  #输出
####################################
env.workspace=PATH[:-1]
#IN_DF=PATH+DF
MIDF="dafeng.shp"
in_df_csv=PATH+"dafeng.csv"
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
if IN_DF.endswith(".txt") or IN_DF.endswith(".csv"):
    pass
if IN_DF.endswith(".xls") or IN_DF.endswith(".xlsx"):
    if __name__ == '__main__':
                xlsx_to_csv_pd(IN_DF,in_df_csv)
                IN_DF = in_df_csv
try:
    arcpy.Delete_management(MIDF)
    createFC = arcpy.CreateFeatureclass_management(env.workspace, MIDF, "POINT", "", "", "")  
except:  
    createFC = arcpy.CreateFeatureclass_management(env.workspace, MIDF, "POINT", "", "", "")
arcpy.AddField_management(env.workspace + "/" + MIDF, "YEAR", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIDF, "MONTH", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIDF, "DAY", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIDF, "DF", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + MIDF,  "lon", "FLOAT" )
arcpy.AddField_management(env.workspace + "/" + MIDF,  "lat", "FLOAT" )
iflds = ["YEAR","MONTH","DAY","DF", "lon","lat", "SHAPE@XY"]
iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIDF, iflds)
count = 1
for ln in open(IN_DF, 'r').readlines():
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
print('Finish Projection:',MIDF)
del iCur
arcpy.Dissolve_management(MIDF, "df1.shp", ["lon","lat",'YEAR'],[['DAY','COUNT']])
cursor = arcpy.da.SearchCursor("df1.shp", ["YEAR","lon","lat","COUNT_DAY"])
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
    cursor = arcpy.da.SearchCursor(MIDF, ["YEAR","lon","lat","DF"])
    for row in cursor:
        if row[0]==year[i] and row[1]==lon[i] and row[2]==lat[i] :
            lists[i].append(row[3]/10.)
del row,cursor
ll=[]
for i in range(len(year)):
    count=[]
    count1=[]
    for e in lists[i]:
        if e>int(VAR_DF):
            count.append(1)
        else:
            count.append(0)
    for e in lists[i]:
        if e>float(VAR_KF):
            count1.append(1)
        else:
            count1.append(0)
    if sum_list(count) >=int(VAR_T) or sum_list(count1) >=1 :
        ll.append(1)
    else:
        ll.append(0)  
try:
    arcpy.DeleteField_management("df1.shp", 'df')
    arcpy.AddField_management("df1.shp", 'df', "FLOAT")    
except:                       
    arcpy.AddField_management("df1.shp", 'df', "FLOAT")
cursor1 = arcpy.UpdateCursor("df1.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('df', ll[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row 
arcpy.Dissolve_management("df1.shp", "df2.shp", ["lon","lat"],[['YEAR','COUNT'],['df','SUM']])
cursor = arcpy.da.SearchCursor("df2.shp", ["COUNT_YEAR","SUM_df"])
po=[]
for row in cursor:          
    po.append(row[1]/row[0])
del cursor,row
try:
    arcpy.DeleteField_management("df2.shp", 'bfb')
    arcpy.AddField_management("df2.shp", 'bfb', "FLOAT")   
except:                       
    arcpy.AddField_management("df2.shp", 'bfb', "FLOAT")
cursor1 = arcpy.UpdateCursor("df2.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('bfb', po[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
chazhi("df2.shp", "bfb", "dfkrig.tif",CC)
arcpy.Clip_management("dfkrig.tif","","dfclip.tif",IN_CLIP,"", "ClippingGeometry")
outReclass2 = arcpy.sa.Reclassify("dfclip.tif", "Value", arcpy.sa.RemapRange([[-10000,float(VAR_DF1),5],[float(VAR_DF1),float(VAR_DF2),4],[float(VAR_DF2),float(VAR_DF3),3],[float(VAR_DF3),float(VAR_DF4),2],[float(VAR_DF4),10000,1]]),'NODATA')
outReclass2.save(OUTPUTPATH+OUTPUTNAME+".tif")
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
arcpy.Delete_management(MIDF)
arcpy.Delete_management("df1.shp")
arcpy.Delete_management("df2.shp")
arcpy.Delete_management("dfkrig.tif")
arcpy.Delete_management("dfclip.tif")
if os.path.exists(in_df_csv):
    os.remove(in_df_csv)
#############################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_nong_tu_zai_5J.clr")
##############################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
