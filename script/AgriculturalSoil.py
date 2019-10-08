# -*- coding: utf-8 -*-
import arcpy
import sys
from arcpy import env
from arcpy.sa import *
import numpy as np
import RasterTableToTxtAndExcel
import StaticticsByXZQ
arcpy.env.overwriteOutput=True
arcpy.CheckOutExtension('Spatial')
arcpy.CheckOutExtension("3D")
###################################
PATH=sys.argv[1]#PATH='D:\\test\\data\\cz_agri_l\\'
IN_AGRI_L=sys.argv[2]#IN_AGRI_L='agri_l_final.tif'
IN_ENVI=sys.argv[3]#IN_ENVI="huanjingpingjia.tif"
IN_DEM=sys.argv[4]#IN_DEM='dem_wgs84.tif'
IN_CLIP=sys.argv[5]#IN_CLIP='clip_wgs84.shp'
VAR_GEO=sys.argv[6]#VAR_GEO="1" #0/1
VAR_FBL=sys.argv[7]#VAR_FBL="200" #分辨率
IN_XZQQ=sys.argv[8]
OUTPUTPATH=sys.argv[9]
OUTPUTNAME=sys.argv[10]#OUTPUTNAME="final"
##################################
#PATH='E:\\spj\\data\\cz_agri_l\\'
#IN_AGRI_L='agri_l_final.tif'
#IN_ENVI=""#huanjingpingjia.tif
#IN_DEM='dem_wgs84.tif'
#IN_CLIP='clip_wgs84.shp'
#VAR_GEO="1" #0/1
#VAR_FBL="200" #分辨率
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH="D:\\map\\"
#OUTPUTNAME="cz_n_t"
###############################
env.workspace =PATH[:-1]
#############################
#重采样像元大小设定
FBLL=int(VAR_FBL)
if int(VAR_GEO)==1:#地理坐标系
    VAR_FBL=0.0000101*int(VAR_FBL)
else:#投影坐标系
    VAR_FBL=int(VAR_FBL)
CC="%f"%(VAR_FBL)
#################################
if IN_ENVI=="99999":
    outReclass = arcpy.sa.Reclassify(Int(IN_AGRI_L), "Value", arcpy.sa.RemapRange([[1,4,1]]),'NODATA')
    outReclass.save("tdzyfinal.tif")
    outReclass1 = arcpy.sa.Reclassify(IN_DEM, "Value", arcpy.sa.RemapRange([[0,5000,1]]),'NODATA')
    outReclass1.save("demfinal.tif")
    arcpy.Clip_management("demfinal.tif","","demclip.tif",IN_CLIP,"", "ClippingGeometry")
    gg=arcpy.Raster("tdzyfinal.tif")*arcpy.Raster("demclip.tif")
    gg.save(OUTPUTPATH+OUTPUTNAME+'.tif')
else:
    outReclass = arcpy.sa.Reclassify(Int(IN_AGRI_L), "Value", arcpy.sa.RemapRange([[1,4,1]]),'NODATA')
    outReclass.save("tdzyfinal.tif")
    ##################################
    outReclass = arcpy.sa.Reclassify(Int(IN_ENVI), "Value", arcpy.sa.RemapRange([[1,3,1]]),'NODATA')
    outReclass.save("trhjfinal.tif")
    ######################################
    outReclass1 = arcpy.sa.Reclassify(IN_DEM, "Value", arcpy.sa.RemapRange([[0,5000,1]]),'NODATA')
    outReclass1.save("demfinal.tif")
    arcpy.Clip_management("demfinal.tif","","demclip.tif",IN_CLIP,"", "ClippingGeometry") 
    #####################################
    #整合
    gg=arcpy.Raster("tdzyfinal.tif")*arcpy.Raster("trhjfinal.tif")*arcpy.Raster("demclip.tif")
    gg.save(OUTPUTPATH+OUTPUTNAME+'.tif')
cursor = arcpy.da.SearchCursor(OUTPUTPATH+OUTPUTNAME+'.tif', ["Count"])
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"土地资源约束下农业生产的最大规模"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")


arcpy.Delete_management("tdzyfinal.tif")
arcpy.Delete_management("trhjfinal.tif")
arcpy.Delete_management("demfinal.tif")
arcpy.Delete_management("demclip.tif")
##################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_nongye_1J.clr")
##############
arcpy.CheckInExtension("Spatial")
arcpy.CheckInExtension("3D")



