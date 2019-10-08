
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 14:11:01 2019

@author: yuanz
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
##############################
PATH= sys.argv[1]#PATH="D:\\test\\data\\st_haianqinshi\\"
IN_HADM= sys.argv[2]#IN_HADM="海岸地貌类型_WGS84.shp"  #海岸地貌类型
IN_ZDZS= sys.argv[3]#IN_ZDZS="zengshui.tif"  #风暴潮最大增水
IN_BG= sys.argv[4]#IN_BG="bogao.tif"   #平均波高
IN_HASL= sys.argv[5]#IN_HASL="海岸侵蚀速率_WGS84.shp" #海岸侵蚀速率
IN_CLIP= sys.argv[6]#IN_CLIP="clipper.shp"#裁剪 输入数据
VAR_GEO= sys.argv[7]#VAR_GEO="1" #0/1  0为投影坐标系 1为地理坐标系
VAR_FBL= sys.argv[8]#VAR_FBL="200" #分辨率
VAR_a1= sys.argv[9]#VAR_a1="0.2"   #海岸地貌类型的权重
VAR_a2= sys.argv[10]#VAR_a2="0.4"    #风暴潮最大增水的权重
VAR_a3= sys.argv[11]#VAR_a3="0.4"     #平均波高的权重
##风暴潮最大增水的重分类
VAR_ZDZS1= sys.argv[12]#VAR_ZDZS1="1.5"
VAR_ZDZS5= sys.argv[13]#VAR_ZDZS5="3.0"   #风暴潮最大增水的重分类
##平均波高的重分类
VAR_BG1= sys.argv[14]#VAR_BG1="0.4"
VAR_BG5= sys.argv[15]#VAR_BG5="1.0"     #平均波高的重分类
##粉砂淤泥质海岸的重分类
VAR_FSYNZ1= sys.argv[16]#VAR_FSYNZ1="1.0"
VAR_FSYNZ5= sys.argv[17]#VAR_FSYNZ5="10"    #粉砂淤泥质海岸的重分类
##砂质海岸的重分类
VAR_SZHA1= sys.argv[18]#VAR_SZHA1="0.5"
VAR_SZHA5= sys.argv[19]#VAR_SZHA5="2.0"    #砂质海岸的重分类
# #海岸侵蚀的最终的重分类
VAR_ZZ1= sys.argv[20]#VAR_ZZ1="0.1"
VAR_ZZ2= sys.argv[21]#VAR_ZZ2="2"       #海岸侵蚀的最终的重分类
VAR_ZZ3= sys.argv[22]#VAR_ZZ3="3.5"     #海岸侵蚀的最终的重分类
VAR_ZZ4= sys.argv[23]#VAR_ZZ4="5.0"     #海岸侵蚀的最终的重分类
IN_XZQQ = sys.argv[24]
OUTPUTPATH = sys.argv[25]
OUTPUTNAME= sys.argv[26]#OUTPUTNAME="haianqinshi"
##############################
#PATH="E:\\spj\\data\\st_haianqinshi\\"
#IN_HADM=""  #海岸地貌类型海岸地貌类型_WGS84.shp
#IN_ZDZS=""  #风暴潮最大增水zengshui.tif
#IN_BG=""   #平均波高bogao.tif
#IN_HASL="" #海岸侵蚀速率海岸侵蚀速率_WGS84.shp
#IN_CLIP="clipper.shp"#裁剪 输入数据
#VAR_GEO="1" #0/1  0为投影坐标系 1为地理坐标系
#VAR_FBL="200" #分辨率
#VAR_a1="0.2"   #海岸地貌类型的权重
#VAR_a2="0.4"    #风暴潮最大增水的权重
#VAR_a3="0.4"     #平均波高的权重
# #风暴潮最大增水的重分类
#VAR_ZDZS1="1.5"
#VAR_ZDZS5="3.0"   #风暴潮最大增水的重分类
# #平均波高的重分类
#VAR_BG1="0.4"
#VAR_BG5="1.0"     #平均波高的重分类
# #粉砂淤泥质海岸的重分类
#VAR_FSYNZ1="1.0"
#VAR_FSYNZ5="10"    #粉砂淤泥质海岸的重分类
# #砂质海岸的重分类
#VAR_SZHA1="0.5"
#VAR_SZHA5="2.0"    #砂质海岸的重分类
#  #海岸侵蚀的最终的重分类
#VAR_ZZ1="0.1"
#VAR_ZZ2="2"       #海岸侵蚀的最终的重分类
#VAR_ZZ3="3.5"     #海岸侵蚀的最终的重分类
#VAR_ZZ4="5.0"     #海岸侵蚀的最终的重分类
#IN_XZQQ = "XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="st_haianqinshi"
###############################
env.workspace = PATH[:-1]
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
################################
if IN_HADM=="99999":
    create_raster(1,IN_CLIP,VAR_FBL,"haianclip.tif")
    VAR_a1 = "0"
else:
    HA=[]
    cursor = arcpy.da.SearchCursor(IN_HADM, ["HADM"])    
    for row in cursor:
        if row[0]==unicode("砂质海岸", "utf-8") or row[0]==unicode("淤泥质海岸", "utf-8") or row[0]==unicode("极敏感", "utf-8") :
            HA.append(5)
        elif row[0]==unicode("具有自然形态和生态功能岸线", "utf-8") or row[0]==unicode("敏感", "utf-8") :
            HA.append(3)
        elif row[0]==unicode("人工护岸", "utf-8") or row[0]==unicode("基岩护岸", "utf-8") or row[0]==unicode("一般敏感", "utf-8") :
            HA.append(1)
    del cursor,row
    #print len(HA)
    cursor1 = arcpy.UpdateCursor(IN_HADM)
    try:
        arcpy.DeleteField_management(IN_HADM, 'HADMfj')
        arcpy.AddField_management(IN_HADM, 'HADMfj', "SHORT")
    except:
        arcpy.AddField_management(IN_HADM, 'HADMfj', "SHORT")
    i = 0
    for my_row in cursor1:
        my_row.setValue('HADMfj', HA[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row
    arcpy.FeatureToRaster_conversion(IN_HADM,'HADMfj','haiandimao.tif',CC)
    arcpy.Clip_management('haiandimao.tif',"","haianclip.tif",IN_CLIP,"", "ClippingGeometry")  
##############################
if IN_ZDZS=="99999":
    create_raster(1,IN_CLIP,VAR_FBL,"zsclip.tif")
    VAR_a2 = "0"
else:
    outReclass2 = arcpy.sa.Reclassify(IN_ZDZS, "Value", arcpy.sa.RemapRange([[0,float(VAR_ZDZS1),1],[float(VAR_ZDZS1),float(VAR_ZDZS5),3],[float(VAR_ZDZS5),11000000000,5]]))
    outReclass2.save("zuidazengshui.tif")
    arcpy.Clip_management("zuidazengshui.tif","","zsclip.tif",IN_CLIP," ", "ClippingGeometry")
################################
if IN_BG=="99999":
    create_raster(1,IN_CLIP,VAR_FBL,"bogaoclip.tif")
    VAR_a3 = "0"
else:
    outReclass2 = arcpy.sa.Reclassify(IN_BG, "Value", arcpy.sa.RemapRange([[0,float(VAR_BG1),1],[float(VAR_BG1),float(VAR_BG5),3],[float(VAR_BG5),11000000000,5]]),'NODATA')
    outReclass2.save("bogaof.tif")
    arcpy.Clip_management("bogaof.tif","","bogaoclip.tif",IN_CLIP," ", "ClippingGeometry")  
#################################
if IN_HASL=="99999":
    create_raster(0,IN_CLIP,VAR_FBL,"suluclip.tif")
else:
    SL=[]
    cursor = arcpy.da.SearchCursor(IN_HASL, ["HAQS_Type","HAQSSL_M"])    
    for row in cursor: 
        if row[0]==unicode("粉砂淤泥质海岸", "utf-8"):
            if row[1]>=float(VAR_FSYNZ5):
                SL.append(5)
            elif float(VAR_FSYNZ1)<=row[1]<float(VAR_FSYNZ5):
                SL.append(3)
            else:
                SL.append(1)
        elif row[0]==unicode("砂质海岸", "utf-8"):
            if row[1]>=float(VAR_SZHA5):
                SL.append(5)
            elif float(VAR_SZHA5)<=row[1]<float(VAR_SZHA1):
                SL.append(3)
            else:
                SL.append(1)
    del cursor,row
    cursor1 = arcpy.UpdateCursor(IN_HASL)
    
    try:
        arcpy.DeleteField_management(IN_HASL, 'HASL')
        arcpy.AddField_management(IN_HASL, 'HASL', "SHORT")
    except:
        arcpy.AddField_management(IN_HASL, 'HASL', "SHORT")
    i = 0
    for my_row in cursor1:
        my_row.setValue('HASL', SL[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row
    arcpy.FeatureToRaster_conversion(IN_HASL,'HASL','haiansulu.tif',CC)
    arcpy.Clip_management('haiansulu.tif',"","suluclip.tif",IN_CLIP,"", "ClippingGeometry") 
###############################
N = float(VAR_a1)*arcpy.Raster("haianclip.tif")+float(VAR_a2)*arcpy.Raster("zsclip.tif") + float(VAR_a3)*arcpy.Raster("bogaoclip.tif")
N.save("nnn.tif") 
MGX=(arcpy.Raster("nnn.tif")+arcpy.Raster("suluclip.tif"))/2
MGX.save("jg.tif")
outReclass2 = arcpy.sa.Reclassify("jg.tif", "Value", arcpy.sa.RemapRange([[float(VAR_ZZ1),float(VAR_ZZ2),5],[float(VAR_ZZ2),float(VAR_ZZ3),3],[float(VAR_ZZ3),float(VAR_ZZ4),1]]),'NODATA')
outReclass2.save(OUTPUTPATH+OUTPUTNAME+".tif")
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
arcpy.Delete_management('haiandimao.tif')
arcpy.Delete_management("haianclip.tif")
arcpy.Delete_management("zuidazengshui.tif")
arcpy.Delete_management("zsclip.tif")
arcpy.Delete_management("bogaof.tif")
arcpy.Delete_management("bogaoclip.tif")
arcpy.Delete_management('haiansulu.tif')
arcpy.Delete_management("suluclip.tif")
arcpy.Delete_management("jg.tif")
arcpy.Delete_management('nnn.tif')
################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#","C:/yz_spj/clr/Month4_mingan_3J.clr")
#arcpy.ApplySymbologyFromLayer_management(OUTPUTPATH+OUTPUTNAME+".tif", "C:/yz_spj/clr/Month4_mingan_3J.lyr")                          
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
