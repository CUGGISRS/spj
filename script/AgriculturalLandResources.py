# -*- coding: utf-8 -*-
import arcpy
import sys
from arcpy import env
from arcpy.sa import *
import RasterTableToTxtAndExcel
import StaticticsByXZQ
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput=True
##################################
PATH = sys.argv[1] #PATH='D:\\test\\data\\agri_func_l\\'
IN_DEM = sys.argv[2] #IN_DEM='dem_wgs84.tif' #高程
IN_FS = sys.argv[3]  #IN_FS ='FenShaHanLiang_wgs84.tif'  #粉砂含量
IN_CLIP= sys.argv[4] #IN_CLIP="clipper.shp"  #裁剪
VAR_GEO=sys.argv[5]  #VAR_GEO="1" #0/1 1地理坐标系，0投影坐标系
VAR_FBL= sys.argv[6] #VAR_FBL="20" #分辨率，不大于5000
VAR_PD1=sys.argv[7]  #VAR_PD1="2" #坡度重分类 小于2，划分为高
VAR_PD2=sys.argv[8]  #VAR_PD2="6" #坡度重分类 2~6 较高
VAR_PD3=sys.argv[9]  #VAR_PD3="15" #坡度重分类 6~15 中等
VAR_PD4=sys.argv[10] #VAR_PD4="25" #坡度重分类 15~25 较低 大于25 低
VAR_FS2=sys.argv[11] #VAR_FS2="0.6"  #粉砂重分类  0.6~0.8 将坡度分级降1级作为土地资源等级
VAR_FS1=sys.argv[12] #VAR_FS1="0.8" #粉砂重分类  大于0.8的区域，土地资源直接取最低
IN_XZQQ= sys.argv[13] 
OUTPUTPATH = sys.argv[14]  #输出路径
OUTPUTNAME = sys.argv[15]  #OUTPUTNAME="agri_l_final" #输出
#################################
#PATH='E:\\spj\\data\\agri_func_l\\'
#IN_DEM='dem_wgs84.tif' #高程
#IN_FS =''  #粉砂含量
#IN_CLIP="clipper.shp"  #裁剪
#VAR_GEO="1" #0/1 1地理坐标系，0投影坐标系
#VAR_FBL="20" #分辨率，不大于5000
#VAR_PD1="2" #坡度重分类 小于2，划分为高
#VAR_PD2="6" #坡度重分类 2~6 较高
#VAR_PD3="15" #坡度重分类 6~15 中等
#VAR_PD4="25" #坡度重分类 15~25 较低 大于25 低
#VAR_FS2="0.6"  #粉砂重分类  0.6~0.8 将坡度分级降1级作为土地资源等级
#VAR_FS1="0.8" #粉砂重分类  大于0.8的区域，土地资源直接取最低
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME = "ny_tudi" #输出
##################################
env.workspace =PATH[:-1]
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
#################################
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
################################
slope = "outslope.tif"
base = "base.tif"
ppd = "ppd.tif"
add = "add.tif"
clipbase = "clipbase.tif"
clipppd = "clipppd.tif"
####################################
outSlope = arcpy.sa.Slope(IN_DEM, "DEGREE")
outSlope.save(slope)
#计算坡度，生成slope
#########################################
outReclass = arcpy.sa.Reclassify(slope, "Value", arcpy.sa.RemapRange([[-10000,float(VAR_PD1),1],[float(VAR_PD1),float(VAR_PD2),2],[float(VAR_PD2),float(VAR_PD3),3],
                                     [float(VAR_PD3),float(VAR_PD4),4],[float(VAR_PD4),10000,5]]))
outReclass.save(base)
arcpy.Clip_management(base,"",clipbase,IN_CLIP,"", "ClippingGeometry")
if IN_FS == "99999":
    create_raster(0,IN_CLIP,VAR_FBL,ppd)
else:
    outReclass2 = arcpy.sa.Reclassify(IN_FS, "Value", arcpy.sa.RemapRange([[-10000,float(VAR_FS2),0],[float(VAR_FS2),float(VAR_FS1),1],[float(VAR_FS1),10000,4]]))
    outReclass2.save(ppd)
arcpy.Clip_management(ppd,"",clipppd,IN_CLIP,"", "ClippingGeometry") 
out = arcpy.sa.Raster(clipbase) +arcpy.sa.Raster(clipppd)
out.save(add)
outReclass3 = arcpy.sa.Reclassify(add, "Value", arcpy.sa.RemapRange([[-1000,1,1],[5,1000,5]]),"DATA")
outReclass3.save(OUTPUTPATH+OUTPUTNAME+'.tif')
######################################
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
arcpy.Delete_management(slope)
arcpy.Delete_management(base)
arcpy.Delete_management(ppd)
arcpy.Delete_management(clipbase)
arcpy.Delete_management(clipppd)
arcpy.Delete_management(add)
###########################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_nong_tu_zai_5J.clr")
#######################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")