# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 10:29:25 2019

@author: 赵晓旭
农业生产适宜性评价——气候评价
"""
from __future__ import division
import arcpy
import pandas as pd
import os
import sys
from arcpy import env
from arcpy.sa import *
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
##############################################
##HARDCODE
#PATH=sys.argv[1]       #PATH = 'D:\\test\\data\\agri_climate\\'
#IN_QW=sys.argv[2]      #qiwen="ave_qiwen.txt"  #气温的txt文件
#IN_DEM=sys.argv[3]         #IN_DEM="dem_wgs84.tif"#高程
#IN_CLIP=sys.argv[4]          #IN_CLIP="clipper.shp"   #裁剪
#VAR_GEO=sys.argv[5]         #VAR_GEO="1" #0/1     #1：地理坐标系，0：投影坐标系
#VAR_FBL=sys.argv[6]        #VAR_FBL="150" #分辨率 不大于5000
#VAR_XZ=sys.argv[7]        #VAR_XZ="1"#等于1根据高程修正。其他值不根据高程修正
##积温的重分类
#VAR_JW4=sys.argv[8]    #VAR_JW4='1500'    #   1500~4000 为较差    小于1500 为差
#VAR_JW3=sys.argv[9]    #VAR_JW3='4000'    # 4000~5800 为一般
#VAR_JW2=sys.argv[10]    #VAR_JW2='5800'    #  5800~7600 为较好
#VAR_JW1=sys.argv[11]    #VAR_JW1='7600'   # 大于等于7600 为好
#IN_XZQQ=sys.argv[12]
#OUTPUTPATH = sys.argv[13]
#OUTPUTNAME=sys.argv[14]   #OUTPUTNAME="qihoupingjia"  #输出文件
##############################################
#HARDCODE
PATH = 'E:\\spj\\data\\agri_climate\\'
IN_QW=PATH+"ave_qiwen.xls"  #气温的txt文件
IN_DEM="99999"  #高程dem_wgs84.tif
IN_CLIP="clipper.shp"   #裁剪
VAR_GEO="1" #0/1     #1：地理坐标系，0：投影坐标系
VAR_FBL="150" #分辨率 不大于5000
VAR_XZ="0"#等于1根据高程修正。其他值不根据高程修正
VAR_JW4='1500'    #积温的重分类   1500~4000 为较差    小于1500 为差
VAR_JW3='4000'    #积温的重分类  5800~7600 为较好
VAR_JW2='5800'    #积温的重分类  4000~5800 为一般
VAR_JW1='7600'   #积温的重分类 大于等于7600 为好
IN_XZQQ="E:\\spj\\data\\agri_climate\\XZQ_WGS84.shp"
OUTPUTPATH = "D:\\map\\"
OUTPUTNAME="ny_qihou"  #输出文件
##################################
env.workspace = PATH[:-1]#工作环境
outputqw = "jiwen.shp"
in_qw_csv = PATH+"suibian.csv"
#################################
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
#################################################
#txt转shp文件
if IN_QW.endswith(".txt") or IN_QW.endswith(".csv"):
    pass
if IN_QW.endswith(".xls") or IN_QW.endswith(".xlsx"):
    if __name__ == '__main__':
                xlsx_to_csv_pd(IN_QW,in_qw_csv)
                IN_QW = in_qw_csv
try:
    arcpy.Delete_management(outputqw)
    createFC = arcpy.CreateFeatureclass_management(env.workspace, outputqw, "POINT", "", "", "")
except:           
    createFC = arcpy.CreateFeatureclass_management(env.workspace, outputqw, "POINT", "", "", "")
arcpy.AddField_management(env.workspace + "/" + outputqw, "QIWen", "FLOAT")
arcpy.AddField_management(env.workspace + "/" + outputqw, "YEAR", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + outputqw, "MONTH", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + outputqw, "DAY", "SHORT" )
arcpy.AddField_management(env.workspace + "/" + outputqw,  "lon", "FLOAT")
arcpy.AddField_management(env.workspace + "/" + outputqw,  "lat", "FLOAT")
iflds = ["YEAR","MONTH","DAY","QIWEN", "lon","lat", "SHAPE@XY"]
iCur = arcpy.da.InsertCursor(env.workspace + "/" + outputqw, iflds)
count = 1
for ln in open(IN_QW, 'r').readlines():
           lnstrip = ln.strip()
           if count > 1:
               dataList = ln.split(",")
               lat = dataList[2]
               lon = dataList[1]
               y = dataList[4]
               m = dataList[5]
               d = dataList[6]
               qw = dataList[7]
               ivals = [y,m,d,qw, float(lon), float(lat),(float(lon), float(lat))]
               iCur.insertRow(ivals)
           count += 1
print('Finish Projection:',outputqw)
del iCur
###############################################
cursor = arcpy.da.SearchCursor(outputqw, ["QIWen"])
qt=[]
for row in cursor:
    if row[0]>=0:
        qt.append(row[0])
    else:
        qt.append(0)
del cursor,row
try:
    arcpy.DeleteField_management(outputqw, 'qt')
    arcpy.AddField_management(outputqw, 'qt', "FLOAT")     
except:
    arcpy.AddField_management(outputqw, 'qt', "FLOAT")
cursor1 = arcpy.UpdateCursor(outputqw)
i = 0
for my_row in cursor1:
    my_row.setValue('qt', qt[i])
    cursor1.updateRow(my_row)
    i += 1
del my_row,cursor1
#print qt
arcpy.Dissolve_management(outputqw, "nianjiwen.shp", ["YEAR","lon","lat"],[['qt','SUM']])
arcpy.Dissolve_management("nianjiwen.shp", "nianjw.shp", ["lon","lat"],[['SUM_qt','SUM'],['YEAR','COUNT']])
cursor = arcpy.da.SearchCursor("nianjw.shp", ["SUM_SUM_qt","COUNT_YEAR"])
jw=[]
for row in cursor:
    jw.append(row[0]/row[1]/10)
try:
    arcpy.DeleteField_management("nianjw.shp", 'jw')
    arcpy.AddField_management("nianjw.shp", 'jw', "FLOAT")     
except:
    arcpy.AddField_management("nianjw.shp", 'jw', "FLOAT")
cursor1 = arcpy.UpdateCursor("nianjw.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('jw', jw[i])
    cursor1.updateRow(my_row)
    i += 1
del my_row,cursor1    
#克里金法（空间插值）
chazhi("nianjw.shp", "jw", "krigout.tif",CC)
arcpy.Clip_management("krigout.tif","","clip.tif",IN_CLIP,"", "ClippingGeometry")
if int(VAR_XZ)==1 :
     t=arcpy.Raster("clip.tif")-arcpy.Raster(IN_DEM)/100*0.6
     t.save("re.tif")
     outReclass = arcpy.sa.Reclassify("re.tif", "Value", arcpy.sa.RemapRange([[-1000000,float(VAR_JW4),5],[float(VAR_JW4),float(VAR_JW3),4],[float(VAR_JW3),float(VAR_JW2),3],[float(VAR_JW2),float(VAR_JW1),2],[float(VAR_JW1),1000000,1]]))
     outReclass.save(OUTPUTPATH +OUTPUTNAME+".tif")
     arcpy.Delete_management("re.tif")
else:
     outReclass = arcpy.sa.Reclassify("clip.tif", "Value", arcpy.sa.RemapRange([[-1000000,float(VAR_JW4),5],[float(VAR_JW4),float(VAR_JW3),4],[float(VAR_JW3),float(VAR_JW2),3],[float(VAR_JW2),float(VAR_JW1),2],[float(VAR_JW1),1000000,1]]))
     outReclass.save(OUTPUTPATH +OUTPUTNAME+".tif")
####################################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH +OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH +OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH +OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH +OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
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
    else:
        return u'差'"""
arcpy.CalculateField_management(OUTPUTPATH +OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH +OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH +OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH +OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management(outputqw)
arcpy.Delete_management( "nianjiwen.shp")
arcpy.Delete_management("nianjw.shp")
arcpy.Delete_management("krigout.tif")
arcpy.Delete_management("clip.tif")
if os.path.exists(in_qw_csv)==True:
    os.remove(in_qw_csv)
####################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH +OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_nong_tu_zai_5J.clr")
###########################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")

