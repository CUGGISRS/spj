# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 13:25:50 2019

@author: 赵晓旭
生态敏感性评价——石漠化
"""
from __future__ import division
import arcpy
import sys
from arcpy import env
from arcpy.sa import *
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
#####################################
#HARDCODE
#PATH=sys.argv[1]#PATH='D:\\test\\data\\st_shimohua\\'
#IN_TSY=sys.argv[2]#IN_TSY='landuse.shp' #碳酸岩出露面积百分比
#IN_XZZB =  sys.argv[3]
#IN_NIR=sys.argv[4]#IN_NIR='NIR20m.tif'#近红外波段
#IN_RED=sys.argv[5]#IN_RED='RED20m.tif'#可见光红波段
#IN_NDVI = sys.argv[6]
#IN_DEM=sys.argv[7]#IN_DEM='DEM.tif' #高程
#IN_CLIP=sys.argv[8]#IN_CLIP="生物多样性用地数据.shp"#裁剪 输入数据
#VAR_GEO=sys.argv[9]#VAR_GEO="0" #0/1 1为地理坐标系，0为投影坐标系
#VAR_FBL=sys.argv[10]#VAR_FBL="17" #分辨率
#VAR_CSY1=sys.argv[11]#VAR_CSY1="0.3" #碳酸岩出露面积百分比的重分类
#VAR_CSY5=sys.argv[12]#VAR_CSY5="0.7" #碳酸岩出露面积百分比的重分类
#VAR_SLOPE1=sys.argv[13]#VAR_SLOPE1="8"  #地形坡度的重分类
#VAR_SLOPE5=sys.argv[14]#VAR_SLOPE5="25"  #地形坡度的重分类
#VAR_NDVI5=sys.argv[15]#VAR_NDVI5="0.2"   #植被覆盖度的重分类
#VAR_NDVI1=sys.argv[16]#VAR_NDVI1="0.6"   #植被覆盖度的重分类
#VAR_SHIMOHUA1=sys.argv[17]#VAR_SHIMOHUA1="2.33"  #石漠化最终的重分类的标准
#VAR_SHIMOHUA5=sys.argv[18]#VAR_SHIMOHUA5="3.66"  #石漠化最终的重分类的标准
#IN_XZQQ = sys.argv[19]
#OUTPUTPATH = sys.argv[20]
#OUTPUTNAME=sys.argv[21]#OUTPUTNAME="shimohua"   #输出栅格的名称
#####################################
#HARDCODE
PATH='E:\\spj\\data\\st_shimohua\\'
IN_TSY='landuse.shp' #碳酸岩出露面积百分比
IN_XZZB = "0"
IN_NIR='NIR20m.tif'#近红外波段
IN_RED='RED20m.tif'#可见光红波段
IN_NDVi = ""
IN_DEM='DEM.tif' #高程
IN_CLIP="生物多样性用地数据.shp"#裁剪 输入数据
VAR_GEO="0" #0/1 1为地理坐标系，0为投影坐标系
VAR_FBL="17" #分辨率
VAR_CSY1="0.3" #碳酸岩出露面积百分比的重分类
VAR_CSY5="0.7" #碳酸岩出露面积百分比的重分类
VAR_SLOPE1="8"  #地形坡度的重分类
VAR_SLOPE5="25"  #地形坡度的重分类
VAR_NDVI1="0.6"   #植被覆盖度的重分类
VAR_NDVI5="0.2"   #植被覆盖度的重分类
VAR_SHIMOHUA1="2.33"  #石漠化最终的重分类的标准
VAR_SHIMOHUA5="3.66"  #石漠化最终的重分类的标准
IN_XZQQ = "E:\\spj\\data\\st_shimohua\\XZQ_WGS84.shp"
OUTPUTPATH = "D:\\map\\"
OUTPUTNAME="shimohua"   #输出栅格的名称
#####################################
env.workspace=PATH[:-1]
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
#####################################
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
    exp=Con(IsNull("ndvi.tif"),0,"ndvi.tif")
    exp.save("ndvi1.tif")
else:
    exp=Con(IsNull(IN_NDVI),0,IN_NDVI)
    exp.save("ndvi1.tif")
#DEM=arcpy.Raster(IN_DEM)
##############################
#创建渔网
if IN_TSY=="99999":
    create_raster(5,IN_CLIP,VAR_FBL,"csy2.tif")
else:
    arcpy.CopyFeatures_management(IN_TSY, "landusecopy.shp")#复制
    desc=arcpy.Describe(IN_TSY)
    extent=desc.extent
    xmin=float(extent.XMin) #x的最小坐标
    xmax=float(extent.XMax)
    ymin=float(extent.YMin)
    ymax=float(extent.YMax)
    o ='%f %f'% (xmin,ymin)#格式化
    y= '%f %f'% (xmin,ymin+1)
    w=NIR.meanCellWidth#长
    h=NIR.meanCellHeight#宽
    r=arcpy.GetRasterProperties_management (NIR, 'ROWCOUNT')#行
    c=arcpy.GetRasterProperties_management (NIR, 'COLUMNCOUNT')#列
    #print o,y
    arcpy.CreateFishnet_management("fishnet.shp",o,y,w,h,r,c,'#','NO_LABELS','#','POLYGON')
    ###########################################
    arcpy.Dissolve_management ("landusecopy.shp", "solve.shp") #融合                             
    arcpy.Intersect_analysis(["solve.shp","fishnet.shp"],'xiangjiao.shp')#相交                             
    cursor = arcpy.da.SearchCursor("xiangjiao.shp", ["SHAPE@AREA"])#面积
    ar=[]
    for row in cursor:
        ar.append(row[0])
    try:
        arcpy.DeleteField_management("xiangjiao.shp", 'area')
        arcpy.AddField_management("xiangjiao.shp", 'area', "FLOAT") 
    except:             
        arcpy.AddField_management("xiangjiao.shp", 'area', "FLOAT")
    del cursor,row
    cursor1 = arcpy.UpdateCursor("xiangjiao.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('area', ar[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1
    del my_row
    #arcpy.Select_analysis("xiangjiao.shp", "sele.shp",'"DLMC" =\'碳酸岩\'' )
    arcpy.Intersect_analysis(["xiangjiao.shp",IN_TSY],'xiangjiao2.shp')#相交
    ###################################################
    #碳酸岩出露面积百分比
    cursor = arcpy.da.SearchCursor("xiangjiao2.shp", ["DLMC","area_1","area"])
    t=[]
    for row in cursor:
              if row[0]== unicode("碳酸岩", "utf-8"):
                  t.append(row[1]/row[2])
              else:
                  t.append(0)
    #print t
    try:
        arcpy.DeleteField_management("xiangjiao2.shp", 'cs')
        arcpy.AddField_management("xiangjiao2.shp", 'cs', "FLOAT")  
    except:             
        arcpy.AddField_management("xiangjiao2.shp", 'cs', "FLOAT")
    cursor2 = arcpy.UpdateCursor("xiangjiao2.shp")   
    i = 0
    for my_row in cursor2:
        my_row.setValue('cs', t[i])
        cursor2.updateRow(my_row)
        i += 1
    del cursor
    del cursor2
    del row
    del my_row
    arcpy.FeatureToRaster_conversion("xiangjiao2.shp", "cs", "csy.tif", VAR_FBL)
    outReclass = arcpy.sa.Reclassify("csy.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_CSY1),1],[float(VAR_CSY1),float(VAR_CSY5),3],[float(VAR_CSY5),10,5]]))
    outReclass.save("csy2.tif")
#################################################################
#地形坡度
outSlope = arcpy.sa.Slope(IN_DEM, "DEGREE")
outSlope.save("outslope.tif")
arcpy.Clip_management("outslope.tif","","clipslope.tif",IN_CLIP,"", "ClippingGeometry")
###################################################################
#植被覆盖度

################################################################
#重分类

outReclass = arcpy.sa.Reclassify("clipslope.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_SLOPE1),1],[float(VAR_SLOPE1),float(VAR_SLOPE5),3],[float(VAR_SLOPE5),100,5]]))
outReclass.save("slope2.tif")
outReclass = arcpy.sa.Reclassify("ndvi1.tif", "Value", arcpy.sa.RemapRange([[-10,float(VAR_NDVI5),5],[float(VAR_NDVI5),float(VAR_NDVI1),3],[float(VAR_NDVI1),1,1]]),'NODATA')    
outReclass.save("ndvi2.tif")

re=pow(arcpy.Raster("csy2.tif")*arcpy.Raster("slope2.tif")*arcpy.Raster("ndvi2.tif"),1.0/3)
re.save('duibi.tif')
outReclass = arcpy.sa.Reclassify("duibi.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_SHIMOHUA1),1],[float(VAR_SHIMOHUA1),float(VAR_SHIMOHUA5),3],[float(VAR_SHIMOHUA5),5,5]]))    
outReclass.save(OUTPUTPATH+OUTPUTNAME+".tif")
#################################
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
arcpy.Delete_management("landusecopy.shp")
arcpy.Delete_management("fishnet.shp")
arcpy.Delete_management("solve.shp")
arcpy.Delete_management('xiangjiao.shp')
arcpy.Delete_management("xiangjiao2.shp")
arcpy.Delete_management("csy.tif")
arcpy.Delete_management("outslope.tif")
arcpy.Delete_management("clipslope.tif")
arcpy.Delete_management("ndvi.tif")
arcpy.Delete_management("ndvi1.tif")
arcpy.Delete_management("csy2.tif")
arcpy.Delete_management("slope2.tif")
arcpy.Delete_management("ndvi2.tif")
arcpy.Delete_management('duibi.tif')
##################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
       StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_mingan_3J.clr")
#res=arcpy.Raster(OUTPUTPATH+OUTPUTNAME+".tif")
#arcpy.ApplySymbologyFromLayer_management(res, "C:/yz_spj/clr/Month4_mingan_3J.lyr") 
#fin=arcpy.MakeRasterLayer_management(OUTPUTPATH+OUTPUTNAME+".tif",'rasterLayer')  
#arcpy.ApplySymbologyFromLayer_management(fin, "F:\\1clr\\Month4_mingan_3J.lyr")
###########################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
