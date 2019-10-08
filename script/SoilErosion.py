# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 17:36:29 2019

@author: 赵晓旭
水土流失

"""
from __future__ import division
import arcpy
import sys
from arcpy import env
from arcpy.sa import *
import pandas as pd
import os
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
#####################################
PATH= sys.argv[1]#PATH='D:\\test\\data\\st_stls\\'
IN_TR= sys.argv[2]#IN_TR="TRLX_wgs84.shp"  #土壤可蚀性
IN_XZZB = sys.argv[3]
IN_NIR= sys.argv[4]#IN_NIR='NIR20.tif'#植被覆盖度近红外波段
IN_RED= sys.argv[5]#IN_RED='RED20.tif'#植被覆盖度可见光红波段
IN_NDVI = sys.argv[6]

IN_DEM= sys.argv[7]#IN_DEM='dem_min_wgs84.tif'#地形起伏——高程
IN_JY= sys.argv[8]#JY="jiangyu.txt"   #降雨txt文件
IN_CLIP= sys.argv[9]#IN_CLIP="clipper.shp"#裁剪 输入数据
VAR_GEO= sys.argv[10]#VAR_GEO="1" #0/1
VAR_FBL= sys.argv[11]#VAR_FBL="200" #分辨率
##
njm= sys.argv[12]#njm="3"#暖季开始的月份
njr= sys.argv[13]#njr="6"#暖季开始的日
ljm= sys.argv[14]#ljm="10"#冷季开始的月份
ljr= sys.argv[15]#ljr="4"#冷季开始的日
jyqs= sys.argv[16]#jyqs="900" #降雨侵蚀范围
##土壤变量
##粘土
nl= sys.argv[17]#nl="45"   #粘粒下限（包含此值）
nl1= sys.argv[18]#nl1="65"  #粘粒上限（不包含此值）
nfs= sys.argv[19]#nfs="0"   #粉砂下限（包含此值）
nfs1= sys.argv[20]#nfs1="55"  #粉砂上限（不包含此值）
nsl= sys.argv[21]#nsl="0"   #砂粒下限（包含此值）
nsl1= sys.argv[22]#nsl1="55"  #砂粒上限（不包含此值）
#壤土
rl= sys.argv[23]#rl="0"  #粘粒下限（包含此值）
rl1= sys.argv[24]#rl1="15" #粘粒上限（不包含此值）
rfs= sys.argv[25]#rfs="30"    #粉砂下限（包含此值）
rfs1= sys.argv[26]#rfs1="45" #粉砂上限（不包含此值）
rsl= sys.argv[27]#rsl="40" #砂粒下限（包含此值
rsl1= sys.argv[28]#rsl1="55" #砂粒上限（不包含此值）
#砂壤土
sl= sys.argv[29]#sl="0"  #粘粒下限（包含此值）
sl1= sys.argv[30]#sl1="15" #粘粒上限（不包含此值）
sfl= sys.argv[31]#sfl="0"   #粉砂下限（包含此值）
sfl1= sys.argv[32]#sfl1="45" #粉砂上限（不包含此值）
ssl= sys.argv[33]#ssl="55" #砂粒下限（包含此值
ssl1= sys.argv[34]#ssl1="85" #砂粒上限（不包含此值）
#粉粘土
fl= sys.argv[35]#fl="25"  #粘粒下限（包含此值）
fl1= sys.argv[36]#fl1="45" #粘粒上限（不包含此值）
ffl= sys.argv[37]#ffl="45"  #粉砂下限（包含此值）
ffl1= sys.argv[38]#ffl1="75" #粉砂上限（不包含此值）
fsl= sys.argv[39]#fsl="0" #砂粒下限（包含此值
fsl1= sys.argv[40]#fsl1="30" #砂粒上限（不包含此值）
#砂粉土
rzl= sys.argv[41]#rzl="25"   #粘粒下限（包含此值）
rzl1= sys.argv[42]#rzl1="45"  #粘粒上限（不包含此值）
rzf= sys.argv[43]#rzf="0"    #粉砂下限（包含此值）
rzf1= sys.argv[44]#rzf1="45" #粉砂上限（不包含此值）
rzs= sys.argv[45]#rzs="10" #砂粒下限（包含此值
rzs1= sys.argv[46]#rzs1="55" #砂粒上限（不包含此值）
#壤粘土
sfzl= sys.argv[47]#sfzl="0"  #粘粒下限（包含此值）
sfzl1= sys.argv[48]#sfzl1="15"#粘粒上限（不包含此值）
sffs= sys.argv[49]#sffs="0"    #粉砂下限（包含此值）
sffs1= sys.argv[50]#sffs1="15" #粉砂上限（不包含此值）
sfsl= sys.argv[51]#sfsl="85" #砂粒下限（包含此值
sfsl1= sys.argv[52]#sfsl1="100" #砂粒上限（不包含此值）
#粉土
ftl= sys.argv[53]#ftl="25" #粘粒下限（包含此值）
ftl1= sys.argv[54]#ftl1="45" #粘粒上限（不包含此值）
ftfs= sys.argv[55]#ftfs="20"    #粉砂下限（包含此值）
ftfs1= sys.argv[56]#ftfs1="45" #粉砂上限（不包含此值）
ftsl= sys.argv[57]#ftsl="0" #砂粒下限（包含此值
ftsl1= sys.argv[58]#ftsl1="30" #砂粒上限（不包含此值）
##
VAR_JYQSL1= sys.argv[59]#VAR_JYQSL1="100"  #降雨侵蚀力的重分类
VAR_JYQSL5= sys.argv[60]#VAR_JYQSL5="600"  #降雨侵蚀力的重分类
VAR_DXQF1= sys.argv[61]#VAR_DXQF1="50"   #地形起伏的重分类
VAR_DXQF5= sys.argv[62]#VAR_DXQF5="300"  #地形起伏的重分类
VAR_NDVI5= sys.argv[63]#VAR_NDVI5="0.2"  #植被覆盖度的重分类
VAR_NDVI1= sys.argv[64]#VAR_NDVI1="0.6"  #植被覆盖度的重分类

VAR_ZZ1= sys.argv[65]#VAR_ZZ1="2.33"    #水土流失的最终重分类
VAR_ZZ5= sys.argv[66]#VAR_ZZ5="3.66"    #水土流失的最终重分
IN_XZQQ= sys.argv[67]
OUTPUTPATH = sys.argv[68]
OUTPUTNAME= sys.argv[69]#OUTPUTNAME="shuituliushi"  #输出
#####################################
#PATH='E:\\spj\\data\\st_stls\\'
#IN_TR=""  #土壤可蚀性TRLX_wgs84.shp
#IN_XZZB="0"  #0遥感数据1成品
#IN_NIR='NIR20.tif'#植被覆盖度近红外波段
#IN_RED='RED20.tif'#植被覆盖度可见光红波段
#IN_NDVI=""
#IN_DEM='dem_min_wgs84.tif'#地形起伏——高程
#IN_JY=PATH+"jiangyu.xls"   #降雨txt文件PATH+"jiangyu.txt"
#IN_CLIP="clipper.shp"#裁剪 输入数据
#VAR_GEO="1" #0/1
#VAR_FBL="200" #分辨率
####
#njm="3"#暖季开始的月份
#njr="6"#暖季开始的日
#ljm="10"#冷季开始的月份
#ljr="4"#冷季开始的日
#jyqs="900" #降雨侵蚀范围
####土壤变量
####粘土
#nl="45"   #粘粒下限（包含此值）
#nl1="65"  #粘粒上限（不包含此值）
#nfs="0"   #粉砂下限（包含此值）
#nfs1="55"  #粉砂上限（不包含此值）
#nsl="0"   #砂粒下限（包含此值）
#nsl1="55"  #砂粒上限（不包含此值）
# #壤土
#rl="0"  #粘粒下限（包含此值）
#rl1="15" #粘粒上限（不包含此值）
#rfs="30"    #粉砂下限（包含此值）
#rfs1="45" #粉砂上限（不包含此值）
#rsl="40" #砂粒下限（包含此值
#rsl1="55" #砂粒上限（不包含此值）
# #砂壤土
#sl="0"  #粘粒下限（包含此值）
#sl1="15" #粘粒上限（不包含此值）
#sfl="0"   #粉砂下限（包含此值）
#sfl1="45" #粉砂上限（不包含此值）
#ssl="55" #砂粒下限（包含此值
#ssl1="85" #砂粒上限（不包含此值）
##粉粘土
#fl="25"  #粘粒下限（包含此值）
#fl1="45" #粘粒上限（不包含此值）
#ffl="45"  #粉砂下限（包含此值）
#ffl1="75" #粉砂上限（不包含此值）
#fsl="0" #砂粒下限（包含此值
#fsl1="30" #砂粒上限（不包含此值）
##砂粉土
#rzl="25"   #粘粒下限（包含此值）
#rzl1="45"  #粘粒上限（不包含此值）
#rzf="0"    #粉砂下限（包含此值）
#rzf1="45" #粉砂上限（不包含此值）
#rzs="10" #砂粒下限（包含此值
#rzs1="55" #砂粒上限（不包含此值）
##壤粘土
#sfzl="0"  #粘粒下限（包含此值）
#sfzl1="15"#粘粒上限（不包含此值）
#sffs="0"    #粉砂下限（包含此值）
#sffs1="15" #粉砂上限（不包含此值）
#sfsl="85" #砂粒下限（包含此值
#sfsl1="100" #砂粒上限（不包含此值）
##粉土
#ftl="25" #粘粒下限（包含此值）
#ftl1="45" #粘粒上限（不包含此值）
#ftfs="20"    #粉砂下限（包含此值）
#ftfs1="45" #粉砂上限（不包含此值）
#ftsl="0" #砂粒下限（包含此值
#ftsl1="30" #砂粒上限（不包含此值）
####
#VAR_JYQSL1="100"  #降雨侵蚀力的重分类
#VAR_JYQSL5="600"  #降雨侵蚀力的重分类
#VAR_DXQF1="50"   #地形起伏的重分类
#VAR_DXQF5="300"  #地形起伏的重分类
#VAR_NDVI5="0.2"  #植被覆盖度的重分类
#VAR_NDVI1="0.6"  #植被覆盖度的重分类
#
#VAR_ZZ1="2.33"    #水土流失的最终重分类
#VAR_ZZ5="3.66"    #水土流失的最终重分类
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="st_shuituliushi"  #输出
#######################################
env.workspace=PATH[:-1]
pdd='dxqf.tif' #地形起伏
outputjy = "jiangyu.shp" 
in_jy_csv = PATH+"jiangyu.csv"
#######################################
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
###############################
#地形起伏度的函数
def xlsx_to_csv_pd(xlsxpath,csvpath):
    data_xls = pd.read_excel(xlsxpath, index_col=0)
    data_xls.to_csv(csvpath, encoding='utf-8')
def calc_gridRA(gridLength,DEM,outputFolder=None):
    nbr=NbrRectangle(gridLength,gridLength,'CELL') #邻域分析的窗口大小
    rasterMax=BlockStatistics(DEM,nbr,'MAXIMUM')
    rasterMin=BlockStatistics(DEM,nbr,'MINIMUM')
    RA=rasterMax-rasterMin
    RA.save(pdd)
    return RA.mean
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
###########################
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
###植被覆盖度
if int(IN_XZZB)==0:
    try:
        arcpy.Delete_management( 'nir.tif')
        arcpy.Float_3d(IN_NIR,'nir.tif')  
    except:  
        arcpy.Float_3d(IN_NIR,'nir.tif')
    try:
        arcpy.Delete_management('red.tif')
        arcpy.Float_3d(IN_RED,'red.tif')  
    except:  
        arcpy.Float_3d(IN_RED,'red.tif')
    NIR=arcpy.Raster('nir.tif')
    RED=arcpy.Raster('red.tif')
    ndvi=(NIR-RED)/(NIR+RED)
    ndvi.save("ndvi.tif")

    outReclass = arcpy.sa.Reclassify("ndvi.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_NDVI5),5],[float(VAR_NDVI5),float(VAR_NDVI1),3],[float(VAR_NDVI1),1,1]]),'NODATA')    
    outReclass.save("ndvi2.tif")
else:
    outReclass = arcpy.sa.Reclassify(IN_NDVI, "Value", arcpy.sa.RemapRange([[0,float(VAR_NDVI5),5],[float(VAR_NDVI5),float(VAR_NDVI1),3],[float(VAR_NDVI1),1,1]]),'NODATA')    
    outReclass.save("ndvi2.tif")
arcpy.Clip_management("ndvi2.tif","","ndvifinal.tif",IN_CLIP,"", "ClippingGeometry")
exp=Con(IsNull("ndvifinal.tif"),1,"ndvifinal.tif")
exp.save("ndvif.tif")
#######################################
##地形起伏度
RAMean=calc_gridRA(VAR_R,IN_DEM)
outReclass2 = arcpy.sa.Reclassify(pdd, "Value", arcpy.sa.RemapRange([[0,float(VAR_DXQF1),1],[float(VAR_DXQF1),float(VAR_DXQF5),3],[float(VAR_DXQF5),3000,5]]))
outReclass2.save("dxqf2.tif")
arcpy.Clip_management("dxqf2.tif","","dxqffinal.tif",IN_CLIP,"", "ClippingGeometry")
#########################################
#土壤
if IN_TR=="99999":
     create_raster(1,IN_CLIP,VAR_FBL,"trfinal.tif")
else:
    trksx=[]#土壤可蚀性
    cursor = arcpy.da.SearchCursor(IN_TR, ["石砾","粗砂","细砂","粉砂","粘粒"])
    for row in cursor:
    #    print row[0],row[1]+row[2],row[3],row[4]
        if row[0]>0:
            trksx.append(1)#"石砾"
        elif row[0]==0 and int(nl)<=row[1]+row[2]<int(nl1) and int(nfs)<=row[3]<int(nfs1) and int(nsl)<=row[4]<int(nsl1):
            trksx.append(1)#"粘土"
        elif row[0]==0 and int(rl)<=row[1]+row[2]<int(rl1) and int(rfs)<=row[3]<int(rfs1) and int(rsl)<=row[4]<int(rsl1):
            trksx.append(3)#"壤土"
        elif row[0]==0 and int(sl)<=row[1]+row[2]<int(sl1) and int(sfl)<=row[3]<int(sfl1) and int(ssl)<=row[4]<int(ssl1):
            trksx.append(3)#"砂壤土"
        elif row[0]==0 and int(fl)<=row[1]+row[2]<int(fl1) and int(ffl)<=row[3]<int(ffl1) and int(fsl)<=row[4]<int(fsl1):
            trksx.append(3)#"粉粘土"
        elif row[0]==0 and int(rzl)<=row[1]+row[2]<int(rzl1) and int(rzf)<=row[3]<int(rzf1) and int(rzs)<=row[4]<int(rzs1):
            trksx.append(5)#"砂粉土"
        elif row[0]==0 and int(sfzl)<=row[1]+row[2]<int(sfzl1) and int(sffs)<=row[3]<int(sffs1) and int(sfsl)<=row[4]<int(sfsl1):
            trksx.append(3)#"壤粘土"
        elif row[0]==0 and int(ftl)<=row[1]+row[2]<int(ftl1) and int(ftfs)<=row[3]<int(ftfs1) and int(ftsl)<=row[4]<int(ftsl1):
            trksx.append(5)#"粉土"
        else:
            trksx.append(0) 
    del cursor
    del row
    cursor2 = arcpy.UpdateCursor(IN_TR)
    try:
        arcpy.DeleteField_management(IN_TR, 'trk')
        arcpy.AddField_management(IN_TR, 'trk', "SHORT")
    except:  
        arcpy.AddField_management(IN_TR, 'trk', "SHORT")    
    i = 0
    for my_row in cursor2:
        my_row.setValue('trk', trksx[i])
        cursor2.updateRow(my_row)
        i += 1
    del cursor2
    del my_row
    arcpy.FeatureToRaster_conversion(IN_TR,'trk','trq.tif',CC)
    arcpy.Clip_management('trq.tif',"","trfinal.tif",IN_CLIP,"", "ClippingGeometry")#arcpy.Resample_management('trq.tif', "trfinal.tif", "20")
######################################
#降雨侵蚀力
if IN_JY=="99999":
    create_raster(1,IN_CLIP,VAR_FBL,"jiangyufinal.tif")
else:
    if IN_JY.endswith(".txt") or IN_JY.endswith(".csv"):
        pass
    if IN_JY.endswith(".xls") or IN_JY.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_JY,in_jy_csv)
                    IN_JY = in_jy_csv
    try:
        arcpy.Delete_management(outputjy)
        createFC = arcpy.CreateFeatureclass_management(env.workspace, outputjy, "POINT", "", "", "") 
    except:       
        createFC = arcpy.CreateFeatureclass_management(env.workspace, outputjy, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + outputjy, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy, "DAY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy, "JY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","DAY","JY", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + outputjy, iflds)
    count = 1
    for ln in open(IN_JY, 'r').readlines():
               lnstrip = ln.strip()
               if count > 1:
                   dataList = ln.split(",")
                   y=dataList[4]
                   m=dataList[5]
                   d=dataList[6]
                   jy=dataList[7]
                   lat = dataList[2]
                   lon = dataList[1]
                   ivals = [y,m,d,jy, float(lon), float(lat),(float(lon), float(lat))]
                   iCur.insertRow(ivals)
               count += 1
    print('Finish Projection:',outputjy)
    del iCur
    cursor2 = arcpy.da.SearchCursor(outputjy, ["YEAR","MONTH","DAY","JY","lon","lat"])
    list1=[]
    for row in cursor2:
        if row[3]>int(jyqs):
           if int(njm)<row[1]<int(ljm):
               p=0.3937
           elif row[1]==int(njm) and row[2]>=int(njr):
               p=0.3937
           elif row[1]==int(ljm) and row[2]<int(ljr):
               p=0.3937
           else:
               p=0.3101
           list1.append(p*(pow(row[3]/10.,1.7265)))
        else:
             list1.append(0) 
    del cursor2
    del row
    try:
        arcpy.DeleteField_management(outputjy, 'rjy')
        arcpy.AddField_management(outputjy, 'rjy', "FLOAT") 
    except:       
        arcpy.AddField_management(outputjy, 'rjy', "FLOAT")
    cursor1 = arcpy.UpdateCursor(outputjy)
    i = 0
    for my_row in cursor1:
        my_row.setValue('rjy', list1[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1
    del my_row 
    list3=[]
    cursor2 = arcpy.da.SearchCursor(outputjy, ["YEAR","MONTH","DAY","rjy","lon","lat"])
    g=[]
    for row in cursor2:
        list3.append(row[0])
        for s in range(13):
                
                if  row[1]==s and row[2]>15:
                    g.append('%d3'%(s))
                elif row[1]==s and row[2]<=15:
                    g.append('%d'%(s))
    n=len(list(set(list3)))          
    del cursor2
    del row
    try:
        arcpy.DeleteField_management(outputjy, 'sx')
        arcpy.AddField_management(outputjy, 'sx', "SHORT") 
    except:       
        arcpy.AddField_management(outputjy, 'sx', "SHORT")
    cursor1 = arcpy.UpdateCursor(outputjy)
    i = 0
    for my_row in cursor1:
        my_row.setValue('sx', g[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1
    del my_row   
    arcpy.Dissolve_management(outputjy, "jy2.shp", ["lon","lat","YEAR","sx"],[['rjy','SUM']])
    arcpy.Dissolve_management("jy2.shp", "jy3.shp", ["lon","lat","sx"],[['SUM_rjy','SUM']])
    cursor2 = arcpy.da.SearchCursor("jy3.shp", ["SUM_SUM_rj"])
    kk=[]
    for row in cursor2:
        kk.append(row[0] /n)
    del cursor2
    del row
    try:
        arcpy.DeleteField_management("jy3.shp", 'pjz')
        arcpy.AddField_management("jy3.shp", 'pjz', "FLOAT") 
    except:             
        arcpy.AddField_management("jy3.shp", 'pjz', "FLOAT")
    cursor1 = arcpy.UpdateCursor("jy3.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('pjz', kk[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1
    del my_row
    arcpy.Dissolve_management("jy3.shp", "jy4.shp", ["lon","lat"],[['pjz','SUM']])
    
    chazhi("jy4.shp", "SUM_pjz", "jykrigph.tif",CC)
    arcpy.Clip_management("jykrigph.tif","","clipjy.tif",IN_CLIP,"", "ClippingGeometry")
    outReclass2 = arcpy.sa.Reclassify("clipjy.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_JYQSL1),1],[float(VAR_JYQSL1),float(VAR_JYQSL5),3],[float(VAR_JYQSL5),11000000000,5]]),'NODATA')
    outReclass2.save("jiangyufinal.tif")
#########################################
#整合 
re=pow(arcpy.Raster("ndvif.tif")*arcpy.Raster("dxqffinal.tif")*arcpy.Raster("trfinal.tif")*arcpy.Raster("jiangyufinal.tif"),1.0/4)
re.save('jg.tif')
outReclass = arcpy.sa.Reclassify('jg.tif', "Value", arcpy.sa.RemapRange([[0,float(VAR_ZZ1),1],[float(VAR_ZZ1),float(VAR_ZZ5),3],[float(VAR_ZZ5),5,5]]))    
outReclass.save(OUTPUTPATH+OUTPUTNAME+".tif")
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"极敏感"
    if a == 3:
        return u"高度敏感"
    else:
        return u'一般敏感'"""
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management('nir.tif')
arcpy.Delete_management('red.tif')
arcpy.Delete_management("ndvi.tif")
arcpy.Delete_management("ndvi2.tif")
arcpy.Delete_management(pdd)
arcpy.Delete_management("dxqf2.tif")
arcpy.Delete_management("ndvifinal.tif")
arcpy.Delete_management("dxqffinal.tif")
arcpy.Delete_management('trq.tif')
arcpy.Delete_management("jy2.shp")
arcpy.Delete_management( outputjy)
arcpy.Delete_management("jy3.shp")
arcpy.Delete_management("jy4.shp")
arcpy.Delete_management("jykrigph.tif")
arcpy.Delete_management("clipjy.tif")
arcpy.Delete_management("jiangyufinal.tif")
arcpy.Delete_management('ndvif.tif')
arcpy.Delete_management('jg.tif')
arcpy.Delete_management('trfinal.tif')
if os.path.exists(in_jy_csv) == True:
    os.remove(in_jy_csv)
#############################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
       StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_mingan_3J.clr")
#arcpy.ApplySymbologyFromLayer_management(fin, "F:\\1clr\\Month4_mingan_3J.lyr")
############################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
