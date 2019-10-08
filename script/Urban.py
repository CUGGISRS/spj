# -*- coding: utf-8 -*-
import arcpy
from arcpy import env
from arcpy.sa import *
import sys
import RasterTableToTxtAndExcel
import StaticticsByXZQ
arcpy.env.overwriteOutput=True
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
##################################
#HARDCODE
#PATH=sys.argv[1]
#IN_DEM=sys.argv[2]
#IN_CLIP=sys.argv[3]
#VAR_GEO=sys.argv[4]
#VAR_FBL=sys.argv[5]
#IN_SlpoeLow = sys.argv[6]
#IN_SlpoeMid = sys.argv[7]
#IN_SlopeHigh = sys.argv[8]
#IN_SlopeHighest = sys.argv[9]
#IN_DEMLevDown = sys.argv[10]
#IN_DEMLevLowest = sys.argv[11]
#IN_NeiLevDown1 = sys.argv[12]
#IN_NeiLevDown2 = sys.argv[13]
#IN_XZQQ=sys.argv[14]
#OUTPUTPATH = sys.argv[15]
#OUTPUTNAME=sys.argv[16]
##################################
PATH="E:\\spj\\data\\town_func_l\\"
IN_DEM='dem_wgs84.tif'
IN_CLIP="clipper.shp"
VAR_GEO="1" #0/1
VAR_FBL="150" #分辨率
IN_SlpoeLow = "3"  #坡度分级---高可利用性坡度上限
IN_SlpoeMid = "8"  #坡度分级---较高可利用性坡度上限
IN_SlopeHigh = "15"  #坡度分级---中等可利用性坡度上限
IN_SlopeHighest = "25"  #坡度分级---较低可利用性坡度上限
IN_DEMLevDown = "5000"  #DEM大于3500米小于5000米区域，降低一个等级
IN_DEMLevLowest = "3500"  #DEM大于5000米区域，取最低值
IN_NeiLevDown1 = "100"  #地形起伏度位于 100米 到 200米间 评价结果降低1级
IN_NeiLevDown2 = "200"  #地形起伏度大于 200米 评价结果降低2级
IN_XZQQ="E:\\spj\\data\\town_func_l\\XZQ_WGS84.shp"
OUTPUTPATH = "D:\\map\\"
OUTPUTNAME="town_tudi"
##################################
env.workspace = PATH[:-1]
pd = 'dbqf.tif'
slope="outslope.tif"
base="base.tif"
gc="gc.tif"
ppd="ppd.tif"
add="add.tif"
SlopeLow = int(IN_SlpoeLow)
SlopeMid = int(IN_SlpoeMid)
SlopeHigh = int(IN_SlopeHigh)
SlopeHighest = int(IN_SlopeHighest)

DEMLevLowest = int(IN_DEMLevLowest)
DEMLevDown = int(IN_DEMLevDown)

NeiLevDown2 = int(IN_NeiLevDown2)
NeiLevDown1 = int(IN_NeiLevDown1)
###################################
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
#####################################
def calc_gridRA(gridLength,DEM,outputFolder=None):
	nbr=NbrRectangle(gridLength,gridLength,'CELL') #邻域分析的窗口大小
	rasterMax=BlockStatistics(DEM,nbr,'MAXIMUM')
	rasterMin=BlockStatistics(DEM,nbr,'MINIMUM')
	RA=rasterMax-rasterMin
	RA.save(pd)
	return RA.mean
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
## ######################################## 
outSlope = arcpy.sa.Slope(IN_DEM, "DEGREE")
outSlope.save(slope)
#计算坡度，生成slope
#########################################
outReclass = arcpy.sa.Reclassify(slope, "Value", arcpy.sa.RemapRange([[-100000,SlopeLow,1],[SlopeLow,SlopeMid,2],[SlopeMid,SlopeHigh,3],
									 [SlopeHigh,SlopeHighest,4],[SlopeHighest,13000,5]]),"NODATA")
outReclass.save(base)
outReclass1 = arcpy.sa.Reclassify(IN_DEM, "Value", arcpy.sa.RemapRange([[0,DEMLevLowest,0],[DEMLevLowest,DEMLevDown,1],[DEMLevDown,10000,4]]))
outReclass1.save(gc)
RAMean=calc_gridRA(int(VAR_R),IN_DEM)
outReclass2 = arcpy.sa.Reclassify(pd, "Value", arcpy.sa.RemapRange([[-100000,NeiLevDown1,0],[NeiLevDown1,NeiLevDown2,1],[NeiLevDown2,3000,2]]))
outReclass2.save(ppd)
out = arcpy.sa.Raster(base) + arcpy.sa.Raster(gc)+arcpy.sa.Raster(ppd)
out.save(add)
outReclass3 = arcpy.sa.Reclassify(add, "Value", arcpy.sa.RemapRange([[-10000,1,1],[5,10000,5]]),"DATA")
outReclass3.save("relope.tif")
arcpy.Clip_management("relope.tif","",OUTPUTPATH+OUTPUTNAME+'.tif',IN_CLIP,"", "ClippingGeometry")
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
	elif a == 5:
		return u"低"
	else:
		return u" "
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
								codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")

############################################
arcpy.Delete_management(pd)
arcpy.Delete_management(slope)
arcpy.Delete_management(base)
arcpy.Delete_management(ppd)
arcpy.Delete_management(add)
arcpy.Delete_management(gc)
arcpy.Delete_management("relope.tif")
#######################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
       StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_tu_huan_5J.clr")
arcpy.CheckInExtension("Spatial")
arcpy.CheckInExtension("3D")
