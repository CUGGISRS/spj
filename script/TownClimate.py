# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 18:56:46 2019

@author: 赵晓旭
城镇建设适宜性评价方法——气候评价
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
PATH = sys.argv[1]
IN_XDSD = sys.argv[2]  #相对湿度的txt文件
IN_HSD = sys.argv[3]       #月均温度——华氏度     
IN_DEM = sys.argv[4]    #输入高程
IN_CLIP = sys.argv[5]      #输入研究区范围的矢量数据
VAR_XZ=sys.argv[6] #等于1修正。其他值不根据高程修正，修正按钮
VAR_wendu=sys.argv[7]  #1:华氏度  0：摄氏度
VAR_GEO=sys.argv[8] #0/1
VAR_FBL=sys.argv[9] #分辨率
VAR_SSD1=sys.argv[10]  #舒适度重分类
VAR_SSD2=sys.argv[11]  #舒适度重分类
VAR_SSD3=sys.argv[12]  #舒适度重分类
VAR_SSD4=sys.argv[13]  #舒适度重分类
VAR_SSD5=sys.argv[14]  #舒适度重分类
VAR_SSD6=sys.argv[15]  #舒适度重分类
VAR_SSD7=sys.argv[16]  #舒适度重分类
VAR_SSD8=sys.argv[17]  #舒适度重分类
VAR_SSD9=sys.argv[18]  #舒适度重分类
VAR_SSD10=sys.argv[19]  #舒适度重分类
VAR_SSD11=sys.argv[20]  #舒适度重分类
VAR_SSD12=sys.argv[21]  #舒适度重分类
IN_XZQQ=sys.argv[22]
OUTPUTPATH = sys.argv[23]
OUTPUTNAME = sys.argv[24]   #输出的结果
################################
#PATH = 'E:\\spj\\data\\town_climate\\'
#IN_XDSD=PATH+"xiangduishidu.xls"  #相对湿度的txt文件 PATH+"xiangduishidu.xls"
#IN_HSD=PATH+"pingjun_qiwen.xls"       #月均温度——华氏度
#IN_DEM="dem_min_wgs84.tif"    #高程
#IN_CLIP="clipper.shp"      #裁剪
#VAR_XZ="0"#等于1修正。其他值不根据高程修正
#VAR_wendu="0"  #1:华氏度  0：摄氏度
#VAR_GEO="1" #0/1
#VAR_FBL="200" #分辨率
#VAR_SSD1="32"  #舒适度重分类
#VAR_SSD2="40"  #舒适度重分类
#VAR_SSD3="45"  #舒适度重分类
#VAR_SSD4="50"  #舒适度重分类
#VAR_SSD5="56"  #舒适度重分类
#VAR_SSD6="60"  #舒适度重分类
#VAR_SSD7="65"  #舒适度重分类
#VAR_SSD8="70"  #舒适度重分类
#VAR_SSD9="75"  #舒适度重分类
#VAR_SSD10="80"  #舒适度重分类
#VAR_SSD11="85"  #舒适度重分类
#VAR_SSD12="90"  #舒适度重分类
#IN_XZQQ='XZQ_WGS84.shp'
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME = "town_qihou"   #输出的结果
##################################
env.workspace=PATH[:-1]#工作环境
MIPUTXDSD = "xdsd.shp"
MIPUTXSD = "hsd.shp"
in_sd_csv = PATH+"xiangduishidu.csv"
in_wd_csv = PATH+"pingjun_qiwen.csv"
#派生数据
#IN_XDSD=PATH+XDSD
#IN_HSD=PATH+HSD
SSD1 = int(VAR_SSD1)
SSD2 = int(VAR_SSD2)
SSD3 = int(VAR_SSD3)
SSD4 = int(VAR_SSD4)
SSD5 = int(VAR_SSD5)
SSD6 = int(VAR_SSD6)
SSD7 = int(VAR_SSD7)
SSD8 = int(VAR_SSD8)
SSD9 = int(VAR_SSD9)
SSD10 = int(VAR_SSD10)
SSD11 = int(VAR_SSD11)
SSD12 = int(VAR_SSD12)
#####################################
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
def get_mode(arr):
    mode = [];
    arr_appear = dict((a, arr.count(a)) for a in arr);  # 统计各个元素出现的次数
    if max(arr_appear.values()) == 1:  # 如果最大的出现为1
        return;  # 则没有众数
    else:
        for k, v in arr_appear.items():  # 否则，出现次数最大的数字，就是众数
            if v == max(arr_appear.values()):
                mode.append(k);
    return mode
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
################################
#txt转shp文件
if IN_XDSD=="99999":
     for i in range(1,13):
         outputclip="clipshidu%d.tif"%(i)
         create_raster(0,IN_CLIP,VAR_FBL,outputclip)
else:
    if IN_XDSD.endswith(".txt") or IN_XDSD.endswith(".csv"):
        pass
    if IN_XDSD.endswith(".xls") or IN_XDSD.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_XDSD,in_sd_csv)
                    IN_XDSD = in_sd_csv
    createFC = arcpy.CreateFeatureclass_management(env.workspace, MIPUTXDSD, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MIPUTXDSD, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIPUTXDSD, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIPUTXDSD, "sd", "FLOAT")
    arcpy.AddField_management(env.workspace + "/" + MIPUTXDSD,  "lon", "FLOAT")
    arcpy.AddField_management(env.workspace + "/" + MIPUTXDSD,  "lat", "FLOAT")
    iflds = ["YEAR","MONTH","sd", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIPUTXDSD, iflds)
    count = 1
    for ln in open(IN_XDSD, 'r').readlines():
               lnstrip = ln.strip()
               if count > 1:
                   dataList = ln.split(",")
                   y = dataList[4]
                   m = dataList[5]
                   lat = dataList[2]
                   lon = dataList[1]
                   xdsd = dataList[7]
                   ivals = [y,m,xdsd, float(lon), float(lat),(float(lon), float(lat))]
                   iCur.insertRow(ivals)
               count += 1
    print('Finish Projection:',MIPUTXDSD)
    del iCur
    arcpy.Dissolve_management(MIPUTXDSD, "shidu.shp", ["lon","lat","YEAR","MONTH"],[['sd','MEAN']])
    arcpy.Dissolve_management( "shidu.shp", "shidujh.shp", ["lon","lat","MONTH"],[['MEAN_sd','SUM'],["YEAR","COUNT"]])
    cursor = arcpy.da.SearchCursor("shidujh.shp", ["SUM_MEAN_s","COUNT_YEAR"])
    ysd=[]
    for row in cursor:
        ysd.append(row[0]/row[1]/10.)
    del cursor,row
    arcpy.AddField_management("shidujh.shp", 'ysd', "FLOAT")
    cursor1 = arcpy.UpdateCursor("shidujh.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('ysd', ysd[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row    
    for i in range(1,13):
        outputname2="shidu%d.shp"%(i)
        outputkrigph="krigshidu%d.tif"%(i)
        outputclip="clipshidu%d.tif"%(i)
        print outputname2
        exp='"MONTH"=%d'%(i)
        arcpy.Select_analysis("shidujh.shp", outputname2, exp)
        chazhi(outputname2, "ysd", outputkrigph,CC)
        arcpy.Clip_management( outputkrigph,"",outputclip,IN_CLIP,"", "ClippingGeometry")
        arcpy.Delete_management(outputname2)
        arcpy.Delete_management(outputkrigph)



if IN_HSD.endswith(".txt") or IN_HSD.endswith(".csv") :
    pass
if IN_HSD.endswith(".xls") or IN_HSD.endswith(".xlsx"):
    if __name__ == '__main__':
                xlsx_to_csv_pd(IN_HSD,in_wd_csv)
                IN_HSD = in_wd_csv
createFC = arcpy.CreateFeatureclass_management(env.workspace, MIPUTXSD, "POINT", "", "", "")
arcpy.AddField_management(env.workspace + "/" + MIPUTXSD, "YEAR", "SHORT" )
arcpy.AddField_management(env.workspace + "/" +MIPUTXSD, "MONTH", "SHORT" )
arcpy.AddField_management(env.workspace + "/" +MIPUTXSD, "wd", "FLOAT")
arcpy.AddField_management(env.workspace + "/" + MIPUTXSD,  "lon", "FLOAT")
arcpy.AddField_management(env.workspace + "/" + MIPUTXSD,  "lat", "FLOAT")
iflds = ["YEAR","MONTH","wd", "lon","lat", "SHAPE@XY"]
iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIPUTXSD, iflds)
count = 1
for ln in open(IN_HSD, 'r').readlines():
           lnstrip = ln.strip()
           if count > 1:
               dataList = ln.split(",")
               y = dataList[4]
               m = dataList[5]
               lat = dataList[2]
               lon = dataList[1]
               hsd = dataList[7]
               ivals = [y,m,hsd, float(lon), float(lat),(float(lon), float(lat))]
               iCur.insertRow(ivals)
           count += 1
print('Finish Projection:',MIPUTXSD)
del iCur
arcpy.Dissolve_management(MIPUTXSD, "wendu.shp", ["lon","lat","YEAR","MONTH"],[['wd','MEAN']])
arcpy.Dissolve_management( "wendu.shp", "wendujh.shp", ["lon","lat","MONTH"],[['MEAN_wd','SUM'],["YEAR","COUNT"]])
cursor = arcpy.da.SearchCursor("wendujh.shp", ["SUM_MEAN_w","COUNT_YEAR"])
ywd=[]
for row in cursor:
    if int(VAR_wendu)==0:
        ywd.append(((row[0]/10. * 1.8) + 32)/row[1])
    elif int(VAR_wendu)==1:
        ywd.append(row[0]/row[1]/10.)
del cursor,row
#print ywd
arcpy.AddField_management("wendujh.shp", 'ywd', "FLOAT")
cursor1 = arcpy.UpdateCursor("wendujh.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('ywd', ywd[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row 
####################################

##########################
for i in range(1,13):
    outputclip="clipshidu%d.tif"%(i)
    outputname1="wendu%d.shp"%(i)
    outputkrigph1="krigwendu%d.tif"%(i)
    outputclip1="clipwendu%d.tif"%(i)
    outputxz="gaocheng%d.tif"%(i)
    outputjg="jieguo%d.tif"%(i)
    outputjjj="jieggg%d.tif"%(i)
    outputfinal="zongshu%d.shp"%(i)
    print outputname1
    exp='"MONTH"=%d'%(i)
    arcpy.Select_analysis("wendujh.shp", outputname1, exp)
    chazhi(outputname1, "ywd", outputkrigph1,CC)
    arcpy.Clip_management(outputkrigph1,"",outputclip1,IN_CLIP,"", "ClippingGeometry")
    arcpy.Delete_management(outputname1)
    arcpy.Delete_management(outputkrigph1)   
    if int(VAR_XZ)==1:
          hsd=arcpy.Raster(outputclip1)-arcpy.Raster(IN_DEM)/100*(0.6*1.8+32)#根据高程修正
          hsd.save(outputxz)
          out=arcpy.Raster(outputxz)-0.55*(1-arcpy.Raster(outputclip))*(arcpy.Raster(outputxz)-58)
          out.save(outputjg)
          arcpy.Delete_management(outputxz)
    else :
          out=arcpy.Raster(outputclip1)-0.55*(1-arcpy.Raster(outputclip))*(arcpy.Raster(outputclip1)-58)
          out.save(outputjg)
    outReclass = arcpy.sa.Reclassify(Int(outputjg), "Value", arcpy.sa.RemapRange([[-100,SSD1,1],[SSD1,SSD2,2],[SSD2,SSD3,3],[SSD3,SSD4,4],[SSD4,SSD5,5] ,[SSD5,SSD6,6],[SSD6,SSD7,7],[SSD7,SSD8,6],[SSD8,SSD9,5],[SSD9,SSD10,4],[SSD10,SSD11,3],[SSD11,SSD12,2],[SSD12,1000000,1]]))
    outReclass.save(outputjjj)
    arcpy.RasterToPolygon_conversion (outputjjj, outputfinal)
    arcpy.Delete_management(outputclip)
    arcpy.Delete_management(outputclip1)
    arcpy.Delete_management(outputjg)
    arcpy.Delete_management(outputjjj)   
arcpy.Intersect_analysis (["zongshu1.shp","zongshu2.shp","zongshu3.shp","zongshu4.shp","zongshu5.shp","zongshu6.shp","zongshu7.shp","zongshu8.shp",
                           "zongshu9.shp","zongshu10.shp","zongshu11.shp","zongshu12.shp"],"mafan.shp" )
cursor = arcpy.da.SearchCursor("mafan.shp", ["GRIDCODE","GRIDCODE_1","GRIDCODE_2","GRIDCODE_3","GRIDCODE_4","GRIDCODE_5","GRIDCODE_6","GRIDCODE_7","GRIDCODE_8","GRIDCODE_9","GRIDCOD_10","GRIDCOD_11"])
new=[]
for row in cursor:
    new.append(get_mode([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]])[0])
print new
arcpy.AddField_management("mafan.shp" , 'jg', "FLOAT")
cursor1 = arcpy.UpdateCursor("mafan.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('jg', new[i])
    cursor1.updateRow(my_row)
    i += 1
del my_row,cursor1 
arcpy.FeatureToRaster_conversion("mafan.shp", "jg", OUTPUTPATH+OUTPUTNAME+".tif",CC)
########################################## 
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"很不舒适"
    elif a == 2:
        return u"较不舒适"   
    elif a == 3:
        return u"一般不舒适"
    elif a == 4:
        return u"中等舒适"
    elif a == 5:
        return u"一般舒适"
    elif a == 6:
        return u"较舒适"
    elif a == 7:
        return u"很舒适"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
###################################################################################
arcpy.Delete_management(MIPUTXDSD)
arcpy.Delete_management(MIPUTXSD)
arcpy.Delete_management("krigsd.tif")
arcpy.Delete_management("krighsd.tif")
arcpy.Delete_management("clipsd.tif")
arcpy.Delete_management("cliphsd.tif")
arcpy.Delete_management("swzs.tif")
arcpy.Delete_management( "shidu.shp")
arcpy.Delete_management( "shidujh.shp")
arcpy.Delete_management("wendu.shp")
arcpy.Delete_management("mafan.shp")
arcpy.Delete_management("zongshu1.shp")
arcpy.Delete_management("zongshu2.shp")
arcpy.Delete_management("zongshu3.shp")
arcpy.Delete_management("zongshu4.shp")
arcpy.Delete_management("zongshu5.shp")
arcpy.Delete_management("zongshu6.shp")
arcpy.Delete_management("zongshu7.shp")
arcpy.Delete_management("zongshu8.shp")
arcpy.Delete_management("zongshu9.shp")
arcpy.Delete_management("zongshu10.shp")
arcpy.Delete_management("zongshu11.shp")
arcpy.Delete_management("zongshu12.shp")
if os.path.exists(in_sd_csv):
    os.remove(in_sd_csv)
if os.path.exists(in_wd_csv):
    os.remove(in_wd_csv)
##########################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
       StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
#arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_shiyixing_7J.clr")
arcpy.CheckInExtension('Spatial')
arcpy.CheckInExtension('3D')
