# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 16:51:00 2019

@author: yuanz
"""
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
#HARDCODE
PATH=sys.argv[1]
IN_TD=sys.argv[2]   #土地资源可利用程度
IN_WA=sys.argv[3]     #水资源可利用程度
IN_DZ=sys.argv[4]    #地质灾害危险性
IN_FB=sys.argv[5]     #风暴潮灾危险性
IN_DAQI=sys.argv[6]     #大气环境容量
IN_SHUI=sys.argv[7]       #水环境容量
IN_QH=sys.argv[8]      #气候舒适度
IN_QUWEI=sys.argv[9]        #区位优势度
IN_CLIP=sys.argv[10]       #研究范围
VAR_GEO=sys.argv[11] #0/1
VAR_FBL=sys.argv[12] #不要大于5000
VAR_D1=sys.argv[13]
VAR_C1=sys.argv[14]
VAR_M1=sys.argv[15]
VAR_U1=sys.argv[16]  #根据地块集中连片度进行修正，确定城镇建设条件等级
IN_XZQQ=sys.argv[17]
OUTPUTPATH = sys.argv[18]
OUTPUTNAME=sys.argv[19]   #输出数据名称
#####################################
#HARDCODE
#PATH="E:\\spj\\data\\town_jc\\"
#IN_TD="town_tudi.tif"  #
#IN_WA="town_shui.tif"
#IN_DZ="town_dizhi.tif"
#IN_FB="town_fengbaochao.tif"
#IN_DAQI="town_daqi.tif"
#IN_SHUI=""
#IN_QH="town_qihou.tif"
#IN_QUWEI="town_quwei.tif"
#IN_CLIP="clipper.shp"
#VAR_GEO="1" #0/1
#VAR_FBL="20" #不要大于5000
#VAR_D1="0.2"
#VAR_C1="0.6"
#VAR_M1="1"
#VAR_U1="1"  #根据地块集中连片度进行修正，确定城镇建设条件等级
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="town_jicheng"
##################################
env.workspace=PATH[:-1]
VAR_U=float(VAR_U1)  #根据地块集中连片度进行修正，确定城镇建设条件等级
VAR_M=float(VAR_M1)
VAR_C=float(VAR_C1)
VAR_D=float(VAR_D1)
#######################################
#重采样像元大小设定
FBLL=int(VAR_FBL)
if int(VAR_GEO)==1:#地理坐标系0/1
    VAR_FBL=0.0000101*int(VAR_FBL)
else:#投影坐标系
    VAR_FBL=int(VAR_FBL)
CC="%f"%(VAR_FBL)
#print CC
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
##################################
if IN_TD=="99999":
    IN_TD = create_raster(5,IN_CLIP,VAR_FBL,"tihuan.tif")
if IN_WA=="99999":
    IN_WA = create_raster(5,IN_CLIP,VAR_FBL,"tihuan1.tif")
if IN_DZ=="99999":
    IN_DZ = create_raster(5,IN_CLIP,VAR_FBL,"tihuan2.tif")
if IN_FB=="99999":
    IN_FB = create_raster(5,IN_CLIP,VAR_FBL,"tihuan3.tif")
if IN_DAQI=="99999":
    IN_DAQI = create_raster(5,IN_CLIP,VAR_FBL,"tihuan4.tif")
if IN_SHUI=="99999":
    IN_SHUI = create_raster(5,IN_CLIP,VAR_FBL,"tihuan5.tif")
if IN_QH=="99999":
    IN_QH = create_raster(5,IN_CLIP,VAR_FBL,"tihuan6.tif")
if IN_QUWEI=="99999":
    IN_QUWEI = create_raster(5,IN_CLIP,VAR_FBL,"tihuan7.tif")
arcpy.RasterToPolygon_conversion (Int(IN_TD), "tdshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_WA), "washp.shp")
arcpy.Intersect_analysis (["tdshp.shp", "washp.shp"], "tdwashp.shp")
cursor = arcpy.da.SearchCursor("tdwashp.shp", ["GRIDCODE","GRIDCODE_1"])
new=[]
for row in cursor:
       if row[0]==1:
            if 1<=row[1]<=3:
                new.append(1)
            elif row[1]==4:
                new.append(2)
            elif row[1]==5:
                new.append(3)
       elif row[0]==2:
            if 1<=row[1]<=2:
                new.append(1)
            elif 3<=row[1]<=4:
                new.append(2)
            elif row[1]==5:
                new.append(3)
       elif row[0]==3:
            if 1<=row[1]<=2:
                new.append(2)
            elif 3<=row[1]<=4:
                new.append(3)
            elif row[1]==5:
                new.append(4)
       elif row[0]==4:
            if row[1]==1:
                new.append(3)
            elif 2<=row[1]<=3:
                new.append(4)
            elif 4<=row[1]<=5:
                new.append(5)
       elif row[0]==5:
                new.append(5)
#print new
arcpy.AddField_management("tdwashp.shp", 'base', "SHORT")
cursor1 = arcpy.UpdateCursor("tdwashp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('base', new[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row  
arcpy.RasterToPolygon_conversion (Int(IN_DZ), "dzshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_FB), "fbshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_DAQI), "dqshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_SHUI), "shuishp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_QH), "qhshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_QUWEI), "qwshp.shp")
arcpy.Intersect_analysis (["tdwashp.shp","fbshp.shp","dzshp.shp","dqshp.shp","shuishp.shp","qhshp.shp","qwshp.shp"],"shp3.shp" )
###############################
cursor = arcpy.da.SearchCursor("shp3.shp", ["base","GRIDCODE_2"])
new1=[]
for row in cursor:
    if row[1]==1:
        new1.append(5)
    elif row[1]==2:
        new1.append(row[0]+2)
    elif row[1]==3:
        new1.append(row[0]+1)
    else:
        new1.append(row[0])          
del cursor,row
for i in range(len(new1)):
    if new1[i]>=5:
        new1[i]=5
    elif new1[i]<=1:
        new1[i]=1
    else:
        new1[i]=new1[i]
arcpy.AddField_management("shp3.shp", 'xz1', "SHORT")
cursor1 = arcpy.UpdateCursor("shp3.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xz1', new1[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
##########################################
cursor = arcpy.da.SearchCursor("shp3.shp", ["xz1","GRIDCODE_3"])
new2=[]
for row in cursor:
    if row[1]==1:
        new2.append(row[0]+1)
    else:
        new2.append(row[0])
del cursor,row
for i in range(len(new2)):
    if new2[i]>=5:
        new2[i]=5
    elif new2[i]<=1:
        new2[i]=1
    else:
        new2[i]=new2[i]
arcpy.AddField_management("shp3.shp", 'xz2', "SHORT")
cursor1 = arcpy.UpdateCursor("shp3.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xz2', new2[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
#############################################
cursor = arcpy.da.SearchCursor("shp3.shp", ["xz2","GRIDCODE_4","GRIDCODE_5"])
new3=[]
for row in cursor:
    if row[1]==5 and row[2]==5:
        new3.append(row[0]+2)
    elif row[1]==5 or row[2]==5:
        new3.append(row[0]+1)
    else:
        new3.append(row[0])
del cursor,row
for i in range(len(new3)):
    if new3[i]>=5:
        new3[i]=5
    elif new3[i]<=1:
        new3[i]=1
    else:
        new3[i]=new3[i]
arcpy.AddField_management("shp3.shp", 'xz3', "SHORT")
cursor1 = arcpy.UpdateCursor("shp3.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xz3', new3[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
####################################################
cursor = arcpy.da.SearchCursor("shp3.shp", ["xz3","GRIDCODE_6"])
new4=[]
for row in cursor:
    if row[1]==1:
        new4.append(row[0]+1)
    else:
        new4.append(row[0])
del cursor,row
for i in range(len(new4)):
    if new4[i]>=5:
        new4[i]=5
    elif new4[i]<=1:
        new4[i]=1
    else:
        new4[i]=new4[i]
arcpy.AddField_management("shp3.shp", 'xz4', "SHORT")
cursor1 = arcpy.UpdateCursor("shp3.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xz4', new4[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
######################################################
cursor = arcpy.da.SearchCursor("shp3.shp", ["xz4","GRIDCODE_7"])
new5=[]
for row in cursor:
    if row[1]==5:
        new5.append(row[0]+2)
    elif row[1]==4:
        new5.append(row[0]+1)
    elif row[1]==1:
         if 2<=row[0]<=4:
             new5.append(row[0]-1)
         else:
             new5.append(row[0])
    else:
        new5.append(row[0])    
del cursor,row
for i in range(len(new5)):
    if new5[i]>=5:
        new5[i]=5
    elif new5[i]<=1:
        new5[i]=1
    else:
        new5[i]=new5[i]
arcpy.AddField_management("shp3.shp", 'xz5', "SHORT")
cursor1 = arcpy.UpdateCursor("shp3.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xz5', new5[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
##########################################################
ar=[] 
cursor = arcpy.da.SearchCursor("shp3.shp", (["OID@", "SHAPE@AREA"])) 
for row in cursor: 
    ar.append(row[1]*pow(10,8))
del cursor,row
#print ar
arcpy.AddField_management("shp3.shp", 'area', "DOUBLE")
cursor1 = arcpy.UpdateCursor("shp3.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('area', ar[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
arcpy.MinimumBoundingGeometry_management("shp3.shp", "shp4.shp", "CIRCLE","NONE")

ar2=[] 
cursor = arcpy.da.SearchCursor("shp4.shp", (["OID@", "SHAPE@AREA"])) 
for row in cursor: 
    ar2.append(row[1]*pow(10,8))
del cursor,row
#print ar2
arcpy.AddField_management("shp4.shp", 'area2', "DOUBLE")
cursor1 = arcpy.UpdateCursor("shp4.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('area2', ar2[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
#########################################################
cursor = arcpy.da.SearchCursor("shp4.shp", (["area", "area2"])) 
bll=[]
for row in cursor:
    bll.append(row[0]/row[1])
del cursor,row
arcpy.AddField_management("shp4.shp", 'bll', "DOUBLE")
cursor1 = arcpy.UpdateCursor("shp4.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('bll', bll[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
#########################################################
cursor = arcpy.da.SearchCursor("shp4.shp", ["xz5","bll"])
new6=[]
for row in cursor:
    if row[1]>=float(VAR_U):
        new6.append(1)
    elif float(VAR_M)<=row[1]<float(VAR_U):
        new6.append(row[0]-1)
    elif float(VAR_C)<=row[1]<float(VAR_M):
        new6.append(row[0])
    elif float(VAR_D)<=row[1]<float(VAR_C):
        new6.append(row[0]+1)
    else:
        new6.append(5)
for i in range(len(new6)):
    if new6[i]>=5:
        new6[i]=5
    elif new6[i]<=1:
        new6[i]=1
    else:
        new6[i]=new6[i]
for i in range(len(new6)):
    if new6[i]==2 or new6[i]==1:
        new6[i]=1
    elif new6[i]==4 or new6[i]==3:
        new6[i]=3
    else:
        new6[i]=5
arcpy.AddField_management("shp4.shp", 'xzjg', "SHORT")
cursor1 = arcpy.UpdateCursor("shp4.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xzjg', new6[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
arcpy.FeatureToRaster_conversion("shp4.shp", "xzjg", "jg.tif",CC)
arcpy.Clip_management("jg.tif","",OUTPUTPATH+OUTPUTNAME+'.tif',IN_CLIP,"", "ClippingGeometry")
#####################################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"适宜"
    elif a == 3:
        return u"一般"
    elif a == 5:
        return u"一般适宜"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
########################################
arcpy.Delete_management("tdshp.shp")
arcpy.Delete_management("washp.shp")
arcpy.Delete_management("tdwashp.shp")
arcpy.Delete_management("dzshp.shp")
arcpy.Delete_management("fbshp.shp")
arcpy.Delete_management("dqshp.shp")
arcpy.Delete_management("shuishp.shp")
arcpy.Delete_management("qhshp.shp")
arcpy.Delete_management("qwshp.shp")
arcpy.Delete_management("shp3.shp")
arcpy.Delete_management("shp4.shp")
arcpy.Delete_management("jg.tif")
if arcpy.Exists("tihuan.tif"):
   arcpy.Delete_management("tihuan.tif")
if arcpy.Exists("tihuan1.tif"):
   arcpy.Delete_management("tihuan1.tif")
if arcpy.Exists("tihuan2.tif"):
   arcpy.Delete_management("tihuan2.tif")
if arcpy.Exists("tihuan3.tif"):
   arcpy.Delete_management("tihuan3.tif")
if arcpy.Exists("tihuan4.tif"):
   arcpy.Delete_management("tihuan4.tif")
if arcpy.Exists("tihuan5.tif"):
   arcpy.Delete_management("tihuan5.tif")
if arcpy.Exists("tihuan6.tif"):
   arcpy.Delete_management("tihuan6.tif")
if arcpy.Exists("tihuan7.tif"):
   arcpy.Delete_management("tihuan7.tif")
##############################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
      StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:\\yz_spj\\clr\\Month7_cheng_ji_3J.clr")
########################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
