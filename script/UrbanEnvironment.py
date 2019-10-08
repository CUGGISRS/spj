# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 11:24:37 2019

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
######################################
#GUI传入数据
PATH = sys.argv[1]
IN_AVE_FS = sys.argv[2] #输入日平均风速txt文件
IN_MAX_FS = sys.argv[3] #输入日最大风速txt文件
IN_CLIP = sys.argv[4]#输入研究区范围的矢量数据
VAR_GEO = sys.argv[5] #0/1 地理坐标系---1，投影坐标系---0
VAR_FBL = sys.argv[6] #空间分辨率，单位米
VAR_FS = sys.argv[7] #日最大风速数据中的 日风速低于这个值时，为静风日
VAR_JFHighest = sys.argv[8] #由最大风速获得的静风日分级图---高上限,默认5%
VAR_JFHigh = sys.argv[9] #~~~---较高上限，默认10%
VAR_JFMid = sys.argv[10] #~~~---中等上限，默认20%
VAR_JFLow = sys.argv[11] #~~~---较低上限，低下限，默认30%
VAR_FSHighest = sys.argv[12] #由平均风速获得的平均风速分级图---高下限，默认5m/s
VAR_FSHigh = sys.argv[13] #~~~---较高下限，默认3m/s
VAR_FSMid = sys.argv[14] #~~~---中等下限，默认2m/s
VAR_FSLow = sys.argv[15] #~~~---较低下限，默认1m/s
IN_XZQQ=sys.argv[16]
OUTPUTPATH = sys.argv[17]
OUTPUTNAME=sys.argv[18] #输出数据的名称
######################################
# #person test
#PATH="E:\\spj\\data\\town_envi_dq\\"
#IN_AVE_FS=PATH+"ave_fengsu.xls"   #PATH+"ave_fengsu.xls
#IN_MAX_FS=PATH+"max_fengsu.xls"
#IN_CLIP="clipper.shp"#裁剪 输入数据
#VAR_GEO="1" #0/1
#VAR_FBL="150" #分辨率
#VAR_FS="3" #风速低于这个值时，为静风日
#VAR_JFHighest ="0.05" #由最大风速获得的静风日分级图---高上限,默认5%
#VAR_JFHigh ="0.1" #~~~---较高上限，默认10%
#VAR_JFMid = "0.2" #~~~---中等上限，默认20%
#VAR_JFLow = "0.3" #~~~---较低上限，低下限，默认30%
#VAR_FSHighest = "5" #由平均风速获得的平均风速分级图---高下限，默认5m/s
#VAR_FSHigh ="3"  #~~~---较高下限，默认3m/s
#VAR_FSMid ="2" #~~~---中等下限，默认2m/s
#VAR_FSLow ="1"  #~~~---较低下限，默认1m/s
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="town_daqi"
#####################################
env.workspace=PATH[:-1]
MI_AVE_FS="ave_fengsu.shp"
MI_MAX_FS="max_fengsu.shp"
in_ave_csv = PATH+"ave_fengsu.csv"
in_max_csv = PATH+"max_fengsu.csv"
FSHighest = float(VAR_FSHighest)
FSHigh = float(VAR_FSHigh)
FSMid = float(VAR_FSMid)
FSLow =float(VAR_FSLow)
JFHighest = float(VAR_JFHighest)
JFHigh = float(VAR_JFHigh)
JFMid =float(VAR_JFMid)
JFLow = float(VAR_JFLow)
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
######################################
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
########################################
if IN_AVE_FS=="99999":
          create_raster(1,IN_CLIP,VAR_FBL,"afsjg.tif") 
else:
    if IN_AVE_FS.endswith(".txt") or IN_AVE_FS.endswith(".csv"):
        pass
    if IN_AVE_FS.endswith(".xls") or IN_AVE_FS.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_AVE_FS,in_ave_csv)
                    IN_AVE_FS = in_ave_csv
    try:
        arcpy.Delete_management(MI_AVE_FS)
        createFC = arcpy.CreateFeatureclass_management(env.workspace,MI_AVE_FS, "POINT", "", "", "")
    except:
        createFC = arcpy.CreateFeatureclass_management(env.workspace,MI_AVE_FS, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MI_AVE_FS, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MI_AVE_FS, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MI_AVE_FS, "DAY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MI_AVE_FS, "AVE_FS", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MI_AVE_FS,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MI_AVE_FS,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","DAY","AVE_FS", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MI_AVE_FS, iflds)
    count = 1
    for ln in open(IN_AVE_FS, 'r').readlines():
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
    print('Finish Projection:',MI_AVE_FS)
    del iCur
    arcpy.Dissolve_management(MI_AVE_FS, "afs.shp", ["lon","lat","YEAR"],[['DAY','COUNT'],['AVE_FS','SUM']])
    cursor = arcpy.da.SearchCursor( "afs.shp", ["COUNT_DAY","SUM_AVE_FS"])
    afb=[]
    for row in cursor:
        afb.append(row[1]/row[0]/10)
    del row,cursor
    #print afb
    arcpy.AddField_management("afs.shp", 'bl', "FLOAT")
    cursor1 = arcpy.UpdateCursor("afs.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('bl', afb[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row 
    chazhi("afs.shp", "bl", "afskrig.tif",CC,y=[])
    arcpy.Clip_management("afskrig.tif","","afsclip.tif",IN_CLIP,"", "ClippingGeometry")
    outReclass2 = arcpy.sa.Reclassify("afsclip.tif", "Value", arcpy.sa.RemapRange([[-10000,FSLow,5],[FSLow,FSMid,4],[FSMid,FSHigh,3],[FSHigh,FSHighest,2],[FSHighest,100000,1]]),'NODATA')
    outReclass2.save("afsjg.tif")  



if IN_MAX_FS=="99999":
          create_raster(1,IN_CLIP,VAR_FBL,"mfsjg.tif") 
else:

    if IN_MAX_FS.endswith(".txt") or IN_MAX_FS.endswith(".csv"):
        pass
    if IN_MAX_FS.endswith(".xls") or IN_MAX_FS.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_MAX_FS,in_max_csv)
                    IN_MAX_FS = in_max_csv
    try:
        arcpy.Delete_management(MI_MAX_FS)
        createFC = arcpy.CreateFeatureclass_management(env.workspace,MI_MAX_FS, "POINT", "", "", "")
    except:
        createFC = arcpy.CreateFeatureclass_management(env.workspace,MI_MAX_FS, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MI_MAX_FS, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MI_MAX_FS, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MI_MAX_FS, "DAY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MI_MAX_FS, "MAX_FS", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MI_MAX_FS,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MI_MAX_FS,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","DAY","MAX_FS", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MI_MAX_FS, iflds)
    count = 1
    for ln in open(IN_MAX_FS, 'r').readlines():
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
    print('Finish Projection:',MI_MAX_FS)
    del iCur
    mfs=[]
    cursor = arcpy.da.SearchCursor(MI_MAX_FS, ["MAX_FS"])
    for row in cursor:
        if row[0]/10<int(VAR_FS):
            mfs.append(1)
        else:
            mfs.append(0)
    del row,cursor
    try:
        arcpy.DeleteField_management(MI_MAX_FS, 'jfr')
        arcpy.AddField_management(MI_MAX_FS, 'jfr', "FLOAT")
    except:
        arcpy.AddField_management(MI_MAX_FS, 'jfr', "FLOAT")
    cursor1 = arcpy.UpdateCursor(MI_MAX_FS)
    i = 0
    for my_row in cursor1:
        my_row.setValue('jfr', mfs[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row 
    arcpy.Dissolve_management(MI_MAX_FS, "mfs.shp", ["lon","lat","YEAR"],[['DAY','COUNT'],['jfr','SUM']])
    cursor = arcpy.da.SearchCursor("mfs.shp", ["COUNT_DAY","SUM_jfr"])
    jfbl=[]
    for row in cursor:
        jfbl.append(row[1]/row[0])
    del row,cursor
    arcpy.AddField_management("mfs.shp", 'bl', "FLOAT")
    cursor1 = arcpy.UpdateCursor("mfs.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('bl', jfbl[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row  
    chazhi("mfs.shp", "bl", "mfskrig.tif",CC,y=[])
    arcpy.Clip_management("mfskrig.tif","","mfsclip.tif",IN_CLIP,"", "ClippingGeometry")
    outReclass2 = arcpy.sa.Reclassify("mfsclip.tif", "Value", arcpy.sa.RemapRange([[-1000,JFHighest,1],[JFHighest,JFHigh,2],[JFHigh,JFMid,3],[JFMid,JFLow,4],[JFLow,1000,5]]),'NODATA')
    outReclass2.save("mfsjg.tif") 

#############################################################
arcpy.RasterToPolygon_conversion ("mfsjg.tif", "mfsshp.shp")
arcpy.RasterToPolygon_conversion ("afsjg.tif", "afsshp.shp")
arcpy.Intersect_analysis (["mfsshp.shp","afsshp.shp"],"zhshp.shp" )
cursor = arcpy.da.SearchCursor("zhshp.shp", ["GRIDCODE","GRIDCODE_1"])
new1=[]
for row in cursor:
    new1.append(max(row[0],row[1]))
#print new1
arcpy.AddField_management("zhshp.shp", 'xz', "SHORT")
cursor1 = arcpy.UpdateCursor("zhshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xz', new1[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
arcpy.FeatureToRaster_conversion("zhshp.shp", "xz", "jg.tif",CC)
arcpy.Clip_management("jg.tif","",OUTPUTPATH+OUTPUTNAME+'.tif',IN_CLIP,"", "ClippingGeometry")
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
        return u"一般"
    elif a == 4:
        return u"较低"
    elif a == 5:
        return u"低"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
############################################################
arcpy.Delete_management("mfskrig.tif")
arcpy.Delete_management("mfsclip.tif")
arcpy.Delete_management("mfsjg.tif")
arcpy.Delete_management("mfskrig.tif")
arcpy.Delete_management("mfsclip.tif")
arcpy.Delete_management("mfsjg.tif")
arcpy.Delete_management("mfskrig.tif")
arcpy.Delete_management("mfsclip.tif")
arcpy.Delete_management("afs.shp")
arcpy.Delete_management("afskrig.tif")
arcpy.Delete_management("afsjg.tif")
arcpy.Delete_management("mfsjg.tif")
arcpy.Delete_management("afsclip.tif")
arcpy.Delete_management("afsshp.shp")
arcpy.Delete_management("jg.tif")
arcpy.Delete_management("mfsshp.shp")
arcpy.Delete_management("mfs.shp")
arcpy.Delete_management("zhshp.shp")
arcpy.Delete_management(MI_AVE_FS)
arcpy.Delete_management(MI_MAX_FS)
if os.path.exists(in_ave_csv)==True:
    os.remove(in_ave_csv)
if os.path.exists(in_max_csv)==True:
    os.remove(in_max_csv)
########################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
     StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_tu_huan_5J.clr")
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")