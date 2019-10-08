# -*- coding: utf-8 -*-
from __future__ import division
import arcpy
import math
import numpy as np
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
##############################
PATH = sys.argv[1]
#栅格图
IN_XZZB = sys.argv[2]
IN_NIR = sys.argv[3]#植被覆盖度近红外波段 输入数据
IN_RED = sys.argv[4]#植被覆盖度可见光红波段  #输入数据
IN_NDVI = sys.argv[5]
IN_DEM = sys.argv[6]#地形起伏——高程  #输入数据
IN_XG = sys.argv[7]   #雪盖因子
#矢量数据
IN_TR = sys.argv[8] #土壤文件  输入数据
IN_ZB = sys.argv[9]   # 植被覆盖因子输入数据
IN_CLIP = sys.argv[10] #裁剪 输入数据

IN_FS = sys.argv[11]    #风速
IN_SHIDU = sys.argv[12]   #土壤湿度

VAR_GEO = sys.argv[13] #0/1
VAR_FBL = sys.argv[14] #分辨率

VAR_DXQFCS = sys.argv[15]   #地形起伏参数
VAR_PP = sys.argv[16]#空气密度
VAR_G = sys.argv[17] #重力加速度
VAR_Z = sys.argv[18] #最大风蚀出现距离
VAR_FF1 = sys.argv[19]  #防风固沙
VAR_FF5 = sys.argv[20]
IN_XZQQ = sys.argv[21]
OUTPUTPATH= sys.argv[22]
OUTPUTNAME = sys.argv[23] #输出
# ##############################
#PATH="E:\\spj\\data\\st_ffgs\\"
#IN_XZZB="0"
#IN_NIR='NIR20.tif'#植被覆盖度近红外波段 输入数据
#IN_RED='RED20.tif'#植被覆盖度可见光红波段  #输入数据
#IN_NDVI="99999"
#IN_DEM='dem_min_wgs84.tif'#地形起伏——高程  #输入数据
#IN_XG="99999"   #雪盖因子XUEGAI.tif
#IN_TR="99999"#土壤文件  输入数据TRLX_wgs84.shp
#IN_ZB="STXT_WGS84.shp"   # 植被覆盖因子输入数据
#IN_CLIP="clipper.shp"#裁剪 输入数据
#IN_FS="99999"    #风速E:\\spj\\data\\st_ffgs\\fengsu.txt
#IN_SHIDU="99999"  #土壤湿度E:\\spj\\data\\st_ffgs\\shidu.txt
#VAR_GEO="1" #0/1
#VAR_FBL="200" #分辨率
#VAR_DXQFCS='1'   #地形起伏参数
#VAR_PP="10"#空气密度
#VAR_G="10" #重力加速度
#VAR_Z="900" #最大风蚀出现距离
#VAR_FF1="5"  #防风固沙
#VAR_FF5="10"
#IN_XZQQ="99999"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="st_fangfenggusha" #输出
# # ##############################
env.workspace = PATH[:-1]
pdd='dxqf.tif' #地形起伏度  输出数据
outputfs="fengsu.shp"
shid2="shidu.shp"
in_fs_csv = PATH+"fengsu.csv"
in_sd_csv =PATH+ "shidu.csv"
#########################
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
##############################
#ndvi
if int(IN_XZZB)==0:
    try:
        arcpy.Delete_management( 'nir2.tif')
        arcpy.Float_3d(IN_NIR,'nir2.tif')  
    except:  
        arcpy.Float_3d(IN_NIR,'nir2.tif')
    try:
        arcpy.Delete_management('red2.tif')
        arcpy.Float_3d(IN_RED,'red2.tif')  
    except:  
        arcpy.Float_3d(IN_RED,'red2.tif')
    NIR=arcpy.Raster("nir2.tif")
    RED=arcpy.Raster("red2.tif")
    nd=(NIR-RED)/(NIR+RED)
    nd.save("ndvi.tif")
    arcpy.Clip_management('ndvi.tif',"","ndvifinal.tif",IN_CLIP,"", "ClippingGeometry")
else: 
    arcpy.Clip_management(IN_NDVI,"","ndvifinal.tif",IN_CLIP,"", "ClippingGeometry")
########################################
#地表糙度因子K/地形起伏
def calc_gridRA(gridLength,DEM,outputFolder=None):
    nbr=NbrRectangle(gridLength,gridLength,'CELL') #邻域分析的窗口大小
    rasterMax=BlockStatistics(DEM,nbr,'MAXIMUM')
    rasterMin=BlockStatistics(DEM,nbr,'MINIMUM')
    RA=rasterMax-rasterMin
    RA.save(pdd)
    return RA
RA=calc_gridRA(VAR_R,IN_DEM)
arcpy.Clip_management(pdd,"","dxqfclip.tif",IN_CLIP,"", "ClippingGeometry")  
y=pow(arcpy.Raster("dxqfclip.tif"),2)/int(VAR_DXQFCS)*0.2
y.save("cdyz.tif")
ui=1.86*arcpy.Raster("cdyz.tif")-2.41*pow(arcpy.Raster("cdyz.tif"),0.934)
ui.save("fff.tif")
kk=pow(2.71,arcpy.Raster("fff.tif"))
kk.save("cdyzff.tif")
##地表糙度因子的最总栅格图
###############################
##土壤可蚀因子EF / 土壤结皮因子SCF
if IN_TR=="99999":
    create_raster(1,IN_CLIP,VAR_FBL,"effinal.tif")
    create_raster(1,IN_CLIP,VAR_FBL,"scffinal.tif")
else:
    ef=[]
    scf=[]
    cursor = arcpy.da.SearchCursor(IN_TR, ["粗砂","粉砂","粘粒","有机质"])    
    for row in cursor:
        sa=row[0]
        si=row[1]
        cl=row[2]
        OM=row[3]
        EF=29.09+0.31*sa+0.17*si+0.33*(sa/cl)-2.59*OM
        SCF=1/(1+0.0066*math.pow(cl,2)+0.021*math.pow(OM,2))
        ef.append(EF)
        scf.append(SCF)
    #print ef,scf
    del cursor,row
    cursor1 = arcpy.UpdateCursor(IN_TR)
    try:
        arcpy.DeleteField_management(IN_TR, 'EF')
        arcpy.AddField_management(IN_TR, 'EF', "DOUBLE") 
    except:  
        arcpy.AddField_management(IN_TR, 'EF', "DOUBLE")
    try:
        arcpy.DeleteField_management(IN_TR, 'SCF')
        arcpy.AddField_management(IN_TR, 'SCF', "DOUBLE") 
    except:    
        arcpy.AddField_management(IN_TR, 'SCF', "DOUBLE")
    i = 0
    for my_row in cursor1:
        my_row.setValue('EF', ef[i])
        my_row.setValue('SCF', scf[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row
    arcpy.FeatureToRaster_conversion(IN_TR,'EF','ef.tif',VAR_FBL)
    arcpy.FeatureToRaster_conversion(IN_TR,'SCF','scf.tif',VAR_FBL)
    #arcpy.Resample_management('trq.tif', "trfinal.tif", "20")    
    arcpy.Clip_management('ef.tif',"","effinal.tif",IN_CLIP,"", "ClippingGeometry") 
    #土壤可侵因子的最终栅格图
    arcpy.Clip_management('scf.tif',"","scffinal.tif",IN_CLIP,"", "ClippingGeometry") 
    ##土壤结皮因子的最终栅格图
###############################
##植被覆盖因子C
a=[]
cursor = arcpy.da.SearchCursor(IN_ZB, ["STXT"])    
for row in cursor:
    if row[0]==unicode("林地", "utf-8") :
        a.append(0.1535)
    elif row[0]==unicode("草地", "utf-8"):
        a.append(0.1151)
    elif row[0]==unicode("灌丛", "utf-8"):
        a.append(0.0921)  
    elif row[0]==unicode("裸地", "utf-8"):
        a.append(0.0768)
    elif row[0]==unicode("沙地", "utf-8"):
        a.append(0.0658)
    elif row[0]==unicode("农田", "utf-8"):
        a.append(0.0438)
    else:
        a.append(0)
#print a
del cursor,row
cursor1 = arcpy.UpdateCursor(IN_ZB)
try:
    arcpy.DeleteField_management(IN_ZB, 'CNDVI')
    arcpy.AddField_management(IN_ZB, 'CNDVI', "DOUBLE") 
except:  
    arcpy.AddField_management(IN_ZB, 'CNDVI', "DOUBLE")
i = 0
for my_row in cursor1:
    my_row.setValue('CNDVI', a[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
arcpy.FeatureToRaster_conversion(IN_ZB,'CNDVI','c.tif',VAR_FBL)
arcpy.Clip_management('c.tif',"","cfinal.tif",IN_CLIP,"", "ClippingGeometry") 
t=arcpy.Raster("cfinal.tif")*arcpy.Raster("ndvifinal.tif")
C=pow(math.e,t)
C.save("Cndvi.tif")
##植被覆盖度的最终栅格图
#############################
##气候因子WF
if IN_FS=="99999":
    for i in range(1,13):
          create_raster(1,IN_CLIP,VAR_FBL,"clip%d.tif"%(i))
else:
    if IN_FS.endswith(".txt") or IN_FS.endswith(".csv"):
        pass
    if IN_FS.endswith(".xls") or IN_FS.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_FS,in_fs_csv)
                    IN_FS = in_fs_csv
    try:
        arcpy.Delete_management(outputfs)
        createFC = arcpy.CreateFeatureclass_management(env.workspace, outputfs ,"POINT", "", "", "")   
    except:       
        createFC = arcpy.CreateFeatureclass_management(env.workspace, outputfs ,"POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + outputfs, "fengsu", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + outputfs, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputfs, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputfs,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + outputfs,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","fengsu", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + outputfs, iflds)
    count = 1
    for ln in open(IN_FS, 'r').readlines():
           lnstrip = ln.strip()
           if count > 1:
               dataList = ln.split(",")
               y=dataList[4]
               m=dataList[5]
               f=dataList[7]
               lat = dataList[2]
               lon = dataList[1]
               ivals = [y,m,f, float(lon), float(lat),(float(lon), float(lat))]
               iCur.insertRow(ivals)
           count += 1
    print('Finish Projection:',outputfs)
    del iCur
    arcpy.Dissolve_management(outputfs, "qihou.shp", ["MONTH","lon","lat"],[['fengsu','SUM'],['YEAR','MAX'],['YEAR','MIN']])
    cursor = arcpy.da.SearchCursor("qihou.shp", ["SUM_fengsu","MAX_YEAR","MIN_YEAR"])
    fs=[]
    for row in cursor:
        n=row[1]-row[2]+1
        fs.append(row[0]/n)
    del row,cursor
    try:
        arcpy.DeleteField_management("qihou.shp", 'fs')
        arcpy.AddField_management("qihou.shp", 'fs', "FLOAT") 
    except:  
        arcpy.AddField_management("qihou.shp", 'fs', "FLOAT")
    cursor1 = arcpy.UpdateCursor("qihou.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('fs', fs[i])
        cursor1.updateRow(my_row)
        i += 1
    del my_row,cursor1
    for i in range(1,13):
        outputname2="fengli%d.shp"%(i)
        outputkrigph="krigph%d.tif"%(i)
        outputclip="clip%d.tif"%(i)
        print outputname2
        exp='"MONTH"=%d'%(i)
        arcpy.Select_analysis("qihou.shp", outputname2, exp)
        chazhi(outputname2, "fs", outputkrigph,CC)
        arcpy.Clip_management( outputkrigph,"",outputclip,IN_CLIP,"", "ClippingGeometry")
        arcpy.Delete_management(outputname2)
        arcpy.Delete_management(outputkrigph)
    
    
    
if  IN_SHIDU=="99999":
    for i in range(1,13):
          create_raster(1,IN_CLIP,VAR_FBL,"trclip%d.tif"%(i))
else:    
    if IN_SHIDU.endswith(".txt") or IN_SHIDU.endswith(".csv"):
        pass
    if IN_SHIDU.endswith(".xls") or IN_SHIDU.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_SHIDU,in_sd_csv)
                    IN_SHIDU = in_sd_csv 
    try:
        arcpy.Delete_management(shid2)
        eateFC = arcpy.CreateFeatureclass_management(env.workspace, shid2 ,"POINT", "", "", "")   
    except:    
        eateFC = arcpy.CreateFeatureclass_management(env.workspace, shid2 ,"POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + shid2, "shidu", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + shid2, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + shid2, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + shid2,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + shid2,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","shidu", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + shid2, iflds)
    count = 1
    for ln in open(IN_SHIDU, 'r').readlines():
               lnstrip = ln.strip()
               if count > 1:
                   dataList = ln.split(",")
                   y=dataList[4]
                   m=dataList[5]
                   f=dataList[6]
                   lat = dataList[2]
                   lon = dataList[1]
                   ivals = [y,m,f, float(lon), float(lat),(float(lon), float(lat))]
                   iCur.insertRow(ivals)
               count += 1
    print('Finish Projection:',shid2)
    del iCur
    ############################################     
    
        
    ###############################################
    arcpy.Dissolve_management(shid2, "trsd.shp", ["MONTH","lon","lat"],[['shidu','SUM'],['YEAR','MAX'],['YEAR','MIN']])
    #融合
    cursor = arcpy.da.SearchCursor("trsd.shp", ["SUM_shidu","MAX_YEAR","MIN_YEAR"])
    sd=[]
    for row in cursor:
        n=row[1]-row[2]+1
        sd.append(row[0]/n)
    del row,cursor
    try:
        arcpy.DeleteField_management("trsd.shp", 'trsd')
        arcpy.AddField_management("trsd.shp", 'trsd', "FLOAT")  
    except:  
        arcpy.AddField_management("trsd.shp", 'trsd', "FLOAT")
    cursor1 = arcpy.UpdateCursor("trsd.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('trsd', sd[i])
        cursor1.updateRow(my_row)
        i += 1
    del my_row,cursor1
    for i in range(1,13):
        outputname1="trshidu%d.shp"%(i)
        outputkrigph1="trkrigph%d.tif"%(i)
        outputclip1="trclip%d.tif"%(i)
        
        print outputname1
        exp='"MONTH"=%d'%(i)
        arcpy.Select_analysis("trsd.shp", outputname1, exp)
        cursor = arcpy.da.SearchCursor(outputname1, ["trsd"])
        sdt=[]
        for row in cursor:
             sdt.append(row[0])
        del row,cursor
        if len(set(sdt))==1:
            arcpy.Idw_3d(outputname1, "trsd", outputkrigph1,CC)
        else:
            chazhi(outputname1, "trsd", outputkrigph1,CC)
        arcpy.Clip_management(outputkrigph1,"",outputclip1,IN_CLIP,"", "ClippingGeometry")
        arcpy.Delete_management(outputname1)
        arcpy.Delete_management(outputkrigph1)
        
WFF=0   
for i in range(1,13): 
    outputclip="clip%d.tif"%(i)
    outputclip1="trclip%d.tif"%(i)
    outputwf="wffinal%d.tif"%(i)
    if IN_XG =="99999":
        WF=arcpy.Raster(outputclip)*arcpy.Raster(outputclip1)*int(VAR_PP)/int(VAR_G)
    else:
        WF=arcpy.Raster(outputclip)*arcpy.Raster(outputclip1)*arcpy.Raster(IN_XG)*int(VAR_PP)/int(VAR_G)
    WF.save(outputwf)
    WFF+=arcpy.Raster(outputwf)
    
    arcpy.Delete_management(outputclip)
    
    arcpy.Delete_management(outputclip1)
    #arcpy.Delete_management(outputwf)
WFF.save("wf.tif")
#############################
##整合
WFH=arcpy.Raster("wf.tif")#气候因子
EF=arcpy.Raster("effinal.tif")#土壤刻蚀因子
SCF=arcpy.Raster("scffinal.tif")#土壤结皮因
K=arcpy.Raster("cdyzff.tif")
C=arcpy.Raster("Cndvi.tif")
Qmaxz=109.8*(WFH*EF*SCF*K)
Sz=150.71*pow(WFH*EF*SCF*K,-0.3711)
o=-pow(int(VAR_Z)/Sz,2)
jz=pow(math.e,o)
Slz=(2-int(VAR_Z))/pow(Sz,2)*Qmaxz*jz
Slz.save("slz.tif")
#############################
Qmax=109.8*(WFH*EF*SCF*K*C)
S=150.71*pow(WFH*EF*SCF*K*C,-0.3711)
p=-pow(int(VAR_Z)/S,2)
j=pow(math.e,p)
Sl=(2-int(VAR_Z))/pow(S,2)*Qmax*j
Sl.save("sl.tif")
SR=arcpy.Raster("slz.tif")-arcpy.Raster("sl.tif")
SR.save("ffgs.tif")
outReclass = arcpy.sa.Reclassify("ffgs.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_FF1),1],[float(VAR_FF1),float(VAR_FF5),3],[float(VAR_FF5),10000,5]]),'NODATA')
outReclass.save(OUTPUTPATH+OUTPUTNAME+".tif")
################################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"极重要"
    if a == 3:
        return u"高度重要"
    else:
        return u'一般重要'"""
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management('nir2.tif')
arcpy.Delete_management(pdd)
arcpy.Delete_management('red2.tif')
arcpy.Delete_management("ndvi.tif")
arcpy.Delete_management("ndvifinal.tif")
arcpy.Delete_management('dxqf.tif')
arcpy.Delete_management("dxqfclip.tif")
arcpy.Delete_management("randomclip.tif")
arcpy.Delete_management("cdyz.tif")
arcpy.Delete_management("cdyzff.tif")
arcpy.Delete_management('ef.tif')
arcpy.Delete_management('scf.tif')
arcpy.Delete_management("effinal.tif")
arcpy.Delete_management("scffinal.tif")
arcpy.Delete_management('c.tif')
arcpy.Delete_management("cfinal.tif")
arcpy.Delete_management("Cndvi.tif")
arcpy.Delete_management(outputfs)
arcpy.Delete_management(shid2)
arcpy.Delete_management("qihou.shp",)
arcpy.Delete_management("trsd.shp")
arcpy.Delete_management("wf.tif")
arcpy.Delete_management('ffgs.tif')
arcpy.Delete_management("wffinal1.tif")
arcpy.Delete_management("wffinal2.tif")
arcpy.Delete_management("wffinal3.tif")
arcpy.Delete_management("wffinal4.tif")
arcpy.Delete_management("wffinal5.tif")
arcpy.Delete_management("wffinal6.tif")
arcpy.Delete_management("wffinal7.tif")
arcpy.Delete_management("wffinal8.tif")
arcpy.Delete_management("wffinal9.tif")
arcpy.Delete_management("wffinal10.tif")
arcpy.Delete_management("wffinal11.tif")
arcpy.Delete_management("wffinal12.tif")
if os.path.exists(in_fs_csv) ==True:
    os.remove(in_fs_csv)
if os.path.exists(in_sd_csv) == True:
    os.remove(in_sd_csv)
#######################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
       StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_fuwu_3J.clr")
#arcpy.ApplySymbologyFromLayer_management(OUTPUTPATH+OUTPUTNAME+".tif", "C:/yz_spj/clr/Month4_fuwu_3J.lyr")
#####################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
