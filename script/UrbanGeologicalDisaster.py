# -*- coding: utf-8 -*-

from __future__ import division
import arcpy
from arcpy import env
from arcpy.sa import *
import sys
import RasterTableToTxtAndExcel
import StaticticsByXZQ
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
#####################################
PATH=sys.argv[1]
IN_DC=sys.argv[2]  #活动断层危险性
IN_FZ=sys.argv[3]  #地震动峰值加速度
IN_CJL=sys.argv[4] #累计沉降量
IN_CJSL=sys.argv[5] #沉降速率
IN_YFX=sys.argv[6] #崩塌滑坡泥石流易发性
IN_TX_YFX=sys.argv[7]  #地面塌陷易发性
IN_CLIP=sys.argv[8]   #裁剪
VAR_GEO=sys.argv[9] #0/1 0为投影坐标系 1为地理坐标系
VAR_FBL=sys.argv[10] #不要大于5000
   #累计沉降量的重分类
VAR_Cj1=sys.argv[11]  #小于100为不易发
VAR_Cj2=sys.argv[12] #100~200为低易发
VAR_Cj3=sys.argv[13]  #200~800为中易发
VAR_Cj4=sys.argv[14]  #800~1600为高易发   大于 1600为极高易发
   #沉降速率的重分类
VAR_SL1=sys.argv[15]  #小于5为不易发
VAR_SL2=sys.argv[16]#5~10为低易发
VAR_SL3=sys.argv[17]  #10~30为中易发
VAR_SL4=sys.argv[18] #30~50为高易发   大于 50为极高易发
IN_XZQQ=sys.argv[19] 
OUTPUTPATH= sys.argv[20]  
OUTPUTNAME=sys.argv[21]  #输出
#####################################
#PATH='E:\\spj\\data\\town_zaihai_dz\\'
#IN_DC='duanceng3.tif'  #活动断层危险性duanceng3.tif
#IN_FZ="dongfengzhi3.tif"  #地震动峰值加速度dongfengzhi.tif
#IN_CJL="leijicehnjianliang.tif" #累计沉降量leijicehnjianliang.tif
#IN_CJSL="chenjiangsulu.tif" #沉降速率
#IN_YFX="nishiliu3.tif" #崩塌滑坡泥石流易发性
#IN_TX_YFX="dimiantaxian3.tif"  #地面塌陷易发性
#IN_CLIP="clipper.shp"   #裁剪
#VAR_GEO="1" #0/1 0为投影坐标系 1为地理坐标系
#VAR_FBL="20" #不要大于5000
# #累计沉降量的重分类
#VAR_Cj1="100"  #小于100为不易发
#VAR_Cj2="200" #100~200为低易发
#VAR_Cj3="800"  #200~800为中易发
#VAR_Cj4="1600"  #800~1600为高易发   大于 1600为极高易发
# #沉降速率的重分类
#VAR_SL1="5"  #小于5为不易发
#VAR_SL2="10"#5~10为低易发
#VAR_SL3="30"  #10~30为中易发
#VAR_SL4="50" #30~50为高易发   大于 50为极高易发
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="town_dizhi"  #输出
##################################
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
#################################
env.workspace=PATH[:-1]
######################################
if IN_DC=="99999":
    create_raster(5,IN_CLIP,VAR_FBL,"weixianxing.tif")
else:
    if IN_FZ=="99999":
       create_raster(0,IN_CLIP,VAR_FBL,"fengzhi.tif")
    else:
       outReclass = arcpy.sa.Reclassify(IN_FZ, "Value", arcpy.sa.RemapValue([[1,-2],[2,-1],[3,0],[4,0]]),'NODATA')    
       outReclass.save("fengzhi.tif")
    oo=arcpy.Raster(IN_DC)+arcpy.Raster("fengzhi.tif")
    oo.save("jj.tif")
    arcpy.Clip_management("jj.tif","","clipdz.tif",IN_CLIP,"", "ClippingGeometry")
    outReclass = arcpy.sa.Reclassify("clipdz.tif", "Value", arcpy.sa.RemapRange([[-10,1,1],[5,10000,5]]),'DATA')    
    outReclass.save("weixianxing.tif")
arcpy.RasterToPolygon_conversion ("weixianxing.tif", "wxx.shp")
###################################
if IN_YFX=="99999":
   IN_YFX=create_raster(5,IN_CLIP,VAR_FBL,"tihuan.tif")
arcpy.RasterToPolygon_conversion (IN_YFX, "yfx.shp")
if IN_TX_YFX=="99999":
   IN_TX_YFX=create_raster(5,IN_CLIP,VAR_FBL,"tihuan1.tif")
arcpy.RasterToPolygon_conversion (IN_TX_YFX, "txyfx.shp")
#####################################
if IN_CJL=="99999":
   create_raster(5,IN_CLIP,VAR_FBL,"cjl.tif")
else:
    outReclass = arcpy.sa.Reclassify(IN_CJL, "Value", arcpy.sa.RemapValue([[-100000,float(VAR_Cj1),5],[float(VAR_Cj1),float(VAR_Cj2),4],[float(VAR_Cj2),float(VAR_Cj3),3],[float(VAR_Cj3),float(VAR_Cj4),2],[float(VAR_Cj4),10000000,1]]),'NODATA')    
    outReclass.save("cjl.tif")
arcpy.RasterToPolygon_conversion ("cjl.tif", "cjl.shp")

if IN_CJSL=="99999":
   create_raster(5,IN_CLIP,VAR_FBL,"cjsl.tif")
else:
    outReclass = arcpy.sa.Reclassify(IN_CJSL, "Value", arcpy.sa.RemapValue([[-100000,float(VAR_SL1),5],[float(VAR_SL1),float(VAR_SL2),4],[float(VAR_SL2),float(VAR_SL3),3],[float(VAR_SL3),float(VAR_SL4),2],[float(VAR_SL4),10000000,1]]),'NODATA')    
    outReclass.save("cjsl.tif")
arcpy.RasterToPolygon_conversion ("cjsl.tif", "cjsl.shp")

arcpy.Intersect_analysis (["cjl.shp", "cjsl.shp","wxx.shp","yfx.shp","txyfx.shp"], "cjyfx.shp")
cursor = arcpy.da.SearchCursor("cjyfx.shp", ["gridcode","gridcode_1","gridcode_2","gridcode_3","gridcode_4"])
new=[]
for row in cursor:
    new.append(min([row[0],row[1],row[2],row[3],row[4]]))
arcpy.AddField_management("cjyfx.shp", 'jc', "SHORT")
cursor1 = arcpy.UpdateCursor("cjyfx.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('jc', new[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
arcpy.FeatureToRaster_conversion("cjyfx.shp", "jc", "jc.tif",CC)
arcpy.Clip_management("jc.tif","",OUTPUTPATH+OUTPUTNAME+'.tif',IN_CLIP,"", "ClippingGeometry")
############################################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"极高"
    elif a == 2:
        return u"高"   
    elif a == 3:
        return u"较高"
    elif a == 4:
        return u"中"
    elif a == 5:
        return u"低"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management("fengzhi.tif")
arcpy.Delete_management("jj.tif")
arcpy.Delete_management("clipdz.tif")
arcpy.Delete_management("weixianxing.tif")
arcpy.Delete_management("wxx.shp")
arcpy.Delete_management("yfx.shp")
arcpy.Delete_management( "txyfx.shp")
arcpy.Delete_management("cjl.tif")
arcpy.Delete_management("cjsl.tif")
arcpy.Delete_management("cjl.shp")
arcpy.Delete_management( "cjsl.shp")
arcpy.Delete_management("cjyfx.shp")
arcpy.Delete_management("cjsl.tif")
arcpy.Delete_management("cjl.shp")
arcpy.Delete_management( "cjsl.shp")
arcpy.Delete_management( "jc.tif")
if arcpy.Exists("tihuan.tif"):
    arcpy.Delete_management("tihuan.tif")
if arcpy.Exists("tihuan1.tif"):
    arcpy.Delete_management("tihuan1.tif")
#########################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
     StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month4_tu_huan_5J.clr")
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")