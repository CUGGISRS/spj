# -*- coding: utf-8 -*-
import arcpy
import sys
from arcpy import env
from arcpy.sa import *
import RasterTableToTxtAndExcel
import StaticticsByXZQ
arcpy.env.overwriteOutput=True
arcpy.CheckOutExtension('Spatial')
arcpy.CheckOutExtension("3D")
##################################
PATH=sys.argv[1]#PATH='D:\\test\\data\\cz_town_l\\'
IN_TOWN_L=sys.argv[2]#IN_TOWN_L="town_l_final.tif"
VAR_GEO=sys.argv[3]#VAR_GEO="1" #0/1
VAR_FBL=sys.argv[4]#VAR_FBL="200000" #分辨率
IN_XZQQ=sys.argv[5]
OUTPUTPATH=sys.argv[6]
OUTPUTNAME=sys.argv[7]#OUTPUTNAME="text"
##################################
#PATH='E:\\spj\\data\\cz_town_l\\'
#IN_TOWN_L="town_l_final.tif"
#VAR_GEO="1" #0/1
#VAR_FBL="200" #分辨率
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH="D:\\map\\"
#OUTPUTNAME="cz_t_t"
#################################
env.workspace=PATH[:-1]
#######################################
#重采样像元大小设定
FBLL=int(VAR_FBL)
if int(VAR_GEO)==1:#地理坐标系
    VAR_FBL=0.0000101*int(VAR_FBL)
else:#投影坐标系
    VAR_FBL=int(VAR_FBL)
CC="%f"%(VAR_FBL)
################################
outReclass = arcpy.sa.Reclassify(Int(IN_TOWN_L), "Value", arcpy.sa.RemapRange([[1,4,1]]),'NODATA')
outReclass.save(OUTPUTPATH+OUTPUTNAME+".tif")
#cursor = arcpy.da.SearchCursor(OUTPUTPATH+OUTPUTNAME+".tif", ["Count"])
###########################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"土地资源约束下城镇建设的最大规模"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")

arcpy.Delete_management('jg.tif')
##################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
      StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_jianshe_1J.clr")
arcpy.CheckInExtension("Spatial")
arcpy.CheckInExtension("3D")
