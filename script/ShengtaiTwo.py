# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 10:13:49 2019
@author: 赵晓旭
水土保持
"""
from __future__ import division
import arcpy
import math
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
#####################################
PATH = sys.argv[1]#工作空间
IN_DEM = sys.argv[2]#地形起伏——高程  #输入数据
IN_TR = sys.argv[3]    #土壤
IN_F=sys.argv[4]	     #新加 第一步输出结果矢量文件
IN_NDVI=sys.argv[5]	#新加 第一步输出结果栅格文件
IN_CLIP = sys.argv[6]   #裁剪
IN_JY = sys.argv[7]     #降水txt文件
VAR_GEO = sys.argv[8] #0/1
VAR_FBL = sys.argv[9] #不要大于5000
#降雨量各变量的列数
VAR_njm = sys.argv[10]#暖季开始的月份
VAR_njr = sys.argv[11]#暖季开始的日
VAR_ljm = sys.argv[12]#冷季开始的月份
VAR_ljr = sys.argv[13]#冷季开始的日
VAR_jyqs = sys.argv[14] #降雨侵蚀范围
VAR_ST5 = sys.argv[15]   #水土保持
VAR_ST1 = sys.argv[16]
IN_XZQQ = sys.argv[17]
OUTPUTPATH = sys.argv[18]
OUTPUTNAME = sys.argv[19]  #输出
#####################################
#PATH='E:\\spj\\data\\st_stbc\\'#工作空间
##IN_XZZB = "0"  #0
##IN_NIR='NIR20.tif'#植被覆盖度近红外波段 输入数据
##IN_RED='RED20.tif'#植被覆盖度可见光红波段  #输入数据
##IN_NDVI = ""
#IN_DEM='dem_wgs84.tif'#地形起伏——高程  #输入数据
#IN_F='shpjg.shp'
#IN_NDVI='tifjg.tif'
#IN_CLIP="clipper.shp"   #裁剪
#IN_TR="TRLX_wgs84.shp"    #土壤TRLX_wgs84.shp
##IN_ZB="STXT_wgs84.shp"    #生态系统
#IN_JY=PATH+"jiangyu.txt"     #降水txt文件E:\\spj\\data\\st_stbc\\jiangyu.txt
#VAR_GEO="1" #0/1
#VAR_FBL="200" #不要大于5000
#  #降雨量各变量的列数
#VAR_njm="3"#暖季开始的月份
#VAR_njr="6"#暖季开始的日
#VAR_ljm="10"#冷季开始的月份
#VAR_ljr="4"#冷季开始的日
#VAR_jyqs="900" #降雨侵蚀范围
#VAR_ST1="50"   #水土保持
#VAR_ST5="15"
#IN_XZQQ = "XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="st_shuituliushi"  #输出
#####################################
env.workspace=PATH[:-1]
pdd='dxqf.tif' #地形起伏  输入数据
outputjy = "jiangyu.shp"
in_jy_csv=PATH+ "jiangyu.csv"
#######################################
#重采样像元大小设定
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
###########################
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
########################################
#地形起伏度
#地形起伏度的函数
def calc_gridRA(gridLength,DEM,outputFolder=None):
    nbr=NbrRectangle(gridLength,gridLength,'CELL') #邻域分析的窗口大小
    rasterMax=BlockStatistics(DEM,nbr,'MAXIMUM')
    rasterMin=BlockStatistics(DEM,nbr,'MINIMUM')
    RA=rasterMax-rasterMin
    RA.save(pdd)
    return RA.mean
RAMean=calc_gridRA(VAR_R,IN_DEM)
arcpy.Clip_management(pdd,"","dxqffinal.tif",IN_CLIP,"", "ClippingGeometry")
#############################################
#植被覆盖因子
cursor = arcpy.da.SearchCursor(IN_F, ["STXT","GRIDCODE"])
zbfg=[]
handi=[]
for row in cursor:
    if row[0]==u"水田" or row[0]==u"湿地":
        zbfg.append(0)
    elif row[0]==u"城镇":
        zbfg.append(0.01)
    elif row[0]==u"城镇":
        zbfg.append(0.7)
    elif row[0]==u"旱地":
        zbfg.append(0)
    elif row[0]==u"森林":
         if row[1]==1 :
             zbfg.append(0.1)
         elif  row[1]==2:
             zbfg.append(0.08)
         elif  row[1]==3:
             zbfg.append(0.06)
         elif  row[1]==4:
             zbfg.append(0.02) 
         elif  row[1]==5:
             zbfg.append(0.004)
         elif  row[1]==6:
             zbfg.append(0.001)    

    elif row[0]==u"灌丛":
         if row[1]==1 :
             zbfg.append(0.4)
         elif  row[1]==2:
             zbfg.append(0.22)
         elif  row[1]==3:
             zbfg.append(0.14)
         elif  row[1]==4:
             zbfg.append(0.085) 
         elif  row[1]==5:
             zbfg.append(0.04)
         elif  row[1]==6:
             zbfg.append(0.011)    
    elif row[0]==u"草地":
         if row[1]==1 :
             zbfg.append(0.45)
         elif  row[1]==2:
             zbfg.append(0.24)
         elif  row[1]==3:
             zbfg.append(0.15)
         elif  row[1]==4:
             zbfg.append(0.09) 
         elif  row[1]==5:
             zbfg.append(0.043)
         elif  row[1]==6:
             zbfg.append(0.011)    
    elif row[0]==u"乔木园地":
         if row[1]==1 :
             zbfg.append(0.42)
         elif  row[1]==2:
             zbfg.append(0.23)
         elif  row[1]==3:
             zbfg.append(0.14)
         elif  row[1]==4:
             zbfg.append(0.089) 
         elif  row[1]==5:
             zbfg.append(0.042)
         elif  row[1]==6:
             zbfg.append(0.011)    
    elif row[0]==u"灌木园地":
         if row[1]==1 :
             zbfg.append(0.4)
         elif  row[1]==2:
             zbfg.append(0.22)
         elif  row[1]==3:
             zbfg.append(0.14)
         elif  row[1]==4:
             zbfg.append(0.087) 
         elif  row[1]==5:
             zbfg.append(0.042)
         elif  row[1]==6:
             zbfg.append(0.011)
    else:
            zbfg.append(999)
cursor1 = arcpy.da.SearchCursor(IN_F, "STXT")            
for row in cursor1:
    if row[0]==unicode("旱地", "utf-8"):
        handi.append(1)
    else:
        handi.append(0)
del cursor,row,cursor1
s = arcpy.UpdateCursor(IN_F)
try:
    arcpy.DeleteField_management(IN_F, 'ndvi')
    arcpy.AddField_management(IN_F, 'ndvi','FLOAT')   
except:  
    arcpy.AddField_management(IN_F, 'ndvi','FLOAT') 
try:
    arcpy.DeleteField_management(IN_F, 'handi')
    arcpy.AddField_management(IN_F, 'handi', "FLOAT")   
except:  
    arcpy.AddField_management(IN_F, 'handi', "FLOAT")
i = 0
for my_row in s:
    my_row.setValue('ndvi', zbfg[i])
    my_row.setValue('handi', handi[i])
    s.updateRow(my_row)
    i += 1
del s,my_row
arcpy.FeatureToRaster_conversion(IN_F, "handi", "hd.tif",CC)
out=Log10(IN_NDVI)
out.save("ndvilog.tif")
out=(0.221-0.595*arcpy.Raster("ndvilog.tif"))*arcpy.Raster("hd.tif")
out.save('handi.tif')
arcpy.FeatureToRaster_conversion(IN_F, "ndvi", "qita.tif",CC)
out=arcpy.Raster("qita.tif")+arcpy.Raster("handi.tif")
out.save("zhenghendvi.tif")
arcpy.Clip_management("zhenghendvi.tif","","ndvifinal.tif",IN_CLIP,"", "ClippingGeometry")
exp=Con(IsNull("ndvifinal.tif"),0,"ndvifinal.tif")
exp.save("ndvif2.tif")
##############################################
####土壤可侵蚀因子
if IN_TR=="99999":
   create_raster(1,IN_CLIP,VAR_FBL,"trfinal.tif")
else:
    trk=[]
    cursor = arcpy.da.SearchCursor(IN_TR, ["粗砂","细砂","粉砂","粘粒","有机质"])    
    for row in cursor:
        mc=row[3]
        msilt=row[2]
        ms=row[0]+row[1]
        org=row[4]
        k1=0.2+0.3*math.exp(-0.0256*ms*(1-msilt/100))
        k2=pow(msilt/(mc+msilt),0.3)
        k3=1-0.25*org/(org+math.exp(3.72-2.95*org))
        k4=1-0.7*(1-ms/100)/((1-ms/100)+math.exp(-5.51+22.9*(1-ms/100)))
        ke=k1*k2*k3*k4
        k=(-0.01383+0.51575*ke)*0.1317
        trk.append(k)
    #print trk
    cursor2 = arcpy.UpdateCursor(IN_TR)
    try:
        arcpy.DeleteField_management(IN_TR, 'qinshi')
        arcpy.AddField_management(IN_TR, 'qinshi', "DOUBLE")    
    except:  
        arcpy.AddField_management(IN_TR, 'qinshi', "DOUBLE")     
    i = 0
    for my_row in cursor2:
        my_row.setValue('qinshi', trk[i])
        cursor2.updateRow(my_row)
        i += 1
    del cursor2
    del my_row
    del cursor
    del row   
    arcpy.FeatureToRaster_conversion(IN_TR,'qinshi','trqsf.tif',CC)    
    arcpy.Clip_management('trqsf.tif',"","trfinal.tif",IN_CLIP,"", "ClippingGeometry")   
#
#################################################
####降雨侵蚀力因子
if IN_JY=="99999":
    create_raster(1,IN_CLIP,VAR_FBL,"clipjy.tif")
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
           j=dataList[7]
           lat = dataList[2]
           lon = dataList[1]
           ivals = [y,m,d,j, float(lon), float(lat),(float(lon), float(lat))]
           iCur.insertRow(ivals)
       count += 1
    print('Finish Projection:',outputjy)
    del iCur
    cursor2 = arcpy.da.SearchCursor(outputjy, ["YEAR","MONTH","DAY","JY","lon","lat"])
    list1=[]
    for row in cursor2:
        if row[3]>int(VAR_jyqs):
           if int(VAR_njm)<row[1]<int(VAR_ljm):
               p=0.3937
           elif row[1]==int(VAR_njm) and row[2]>=int(VAR_njr):
               p=0.3937
           elif row[1]==int(VAR_ljm) and row[2]<int(VAR_ljr):
               p=0.3937
           else:
               p=0.3101
           list1.append(p*(pow(row[3]/10,1.7265)))
        else:
             list1.append(0) 
    #print list1
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
    del cursor2
    del row  
    list3=[]
    cursor2 = arcpy.da.SearchCursor(outputjy, ["YEAR","MONTH","DAY","rjy","lon","lat"])
    g=[]
    for row in cursor2:
        list3.append(row[0])
        n=len(list(set(list3)))
        for s in range(13):
                
                if  row[1]==s and row[2]>15:
                    g.append('%d3'%(s))
                elif row[1]==s and row[2]<=15:
                    g.append('%d'%(s))
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
    del cursor2
    del row   
    arcpy.Dissolve_management(outputjy, "jy2.shp", ["lon","lat","YEAR","SX"],[['rjy','SUM']])
    arcpy.Dissolve_management("jy2.shp", "jy3.shp", ["lon","lat","SX"],[['SUM_rjy','SUM']])
    cursor2 = arcpy.da.SearchCursor("jy3.shp", ["SUM_SUM_rj"])
    kk=[]
    for row in cursor2:
        kk.append(row[0] /n)
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
    del cursor2
    del row  
    arcpy.Dissolve_management("jy3.shp", "jy4.shp", ["lon","lat"],[['pjz','SUM']])
    chazhi("jy4.shp", "SUM_pjz", "jykrigph.tif",CC)
    arcpy.Clip_management("jykrigph.tif","","clipjy.tif",IN_CLIP,"", "ClippingGeometry")

#########################################
##整合
out=arcpy.Raster("clipjy.tif")*arcpy.Raster("trfinal.tif")*arcpy.Raster("dxqffinal.tif")*(1-arcpy.Raster("ndvif2.tif"))
out.save("stbc.tif")
outInt = Int("stbc.tif")
outInt.save("qqq.tif")
outReclass = arcpy.sa.Reclassify("qqq.tif", "Value", arcpy.sa.RemapRange([[-100000000,float(VAR_ST5),5],[float(VAR_ST5),float(VAR_ST1),3],[float(VAR_ST1),10000000000,1]]))
outReclass.save(OUTPUTPATH+OUTPUTNAME+".tif")
#######################################
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
arcpy.Delete_management('red2.tif')
arcpy.Delete_management(pdd)
#arcpy.Delete_management("ndvi.tif")
arcpy.Delete_management("ndvire.tif")
arcpy.Delete_management("ndvig.shp")
arcpy.Delete_management("jiangyu.shp")
arcpy.Delete_management('dxqf.tif')
arcpy.Delete_management("dxqffinal.tif")
arcpy.Delete_management("dxqffinal2.tif")
#arcpy.Delete_management("feng.shp")
arcpy.Delete_management("hd.tif")
arcpy.Delete_management("ndvilog.tif")
arcpy.Delete_management("ndvi.tif")
arcpy.Delete_management('handi.tif')
arcpy.Delete_management("qita.tif")
arcpy.Delete_management("zhenghendvi.tif")
arcpy.Delete_management("ndvifinal.tif")
arcpy.Delete_management("ndvif2.tif")
arcpy.Delete_management('trqsf.tif')
arcpy.Delete_management("trfinal.tif")
arcpy.Delete_management(outputjy)
arcpy.Delete_management("jy2.shp")
arcpy.Delete_management("jy3.shp")
arcpy.Delete_management("jy4.shp")
arcpy.Delete_management("jykrigph.tif")
arcpy.Delete_management("resamplejy.tif")
arcpy.Delete_management("clipjy.tif")
arcpy.Delete_management("stbc.tif")
arcpy.Delete_management("qqq.tif")
if os.path.exists(in_jy_csv) ==True:
    os.remove(in_jy_csv)
###############################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
       StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_fuwu_3J.clr")
#arcpy.ApplySymbologyFromLayer_management(OUTPUTPATH+OUTPUTNAME+".tif", "C:/yz_spj/clr/Month4_fuwu_3J.lyr")                               
#arcpy.ApplySymbologyFromLayer_management(fin, "F:\\1clr\\Month4_mingan_3J.lyr")
############################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
