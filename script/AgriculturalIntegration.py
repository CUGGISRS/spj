
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 15:04:20 2019

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
#####################################
#HARDCODE
PATH=sys.argv[1]#PATH="D:\\test\\data\\agri_jc\\"
IN_TD=sys.argv[2]#IN_TD="agri_l_final.tif" #农业土地资源评价
IN_WA=sys.argv[3]#IN_WA="shuiziyuan.tif"   #水资源评价
IN_QH=sys.argv[4]#IN_QH="nongyeqihou.tif"   #气候评价
IN_HJ=sys.argv[5]#IN_HJ="huanjingpingjia.tif" #环境评价
IN_ST=sys.argv[6]#IN_ST="yanzihua.tif"   #生态评价（盐渍化评价）
IN_ZH=sys.argv[7]#IN_ZH="zaihai.tif"     #灾害评价
IN_CLIP=sys.argv[8]#IN_CLIP="clipper.shp"  #裁剪
VAR_GEO=sys.argv[9]#VAR_GEO="1" #0/1   1为地理坐标系。0为投影坐标系
VAR_FBL=sys.argv[10]#VAR_FBL="50" #分辨率 不大于5000
##根据地块集中连片度进行修正，确定城镇建设条件等级
VAR_D=sys.argv[11]#VAR_D="0.2" #0.2~0.4 降一级   小于0.2为5
VAR_C=sys.argv[12]#VAR_C="0.4"  #0.4~0.6 不变
VAR_M=sys.argv[13]#VAR_M="0.6" #0.6~0.8 升一级
VAR_U=sys.argv[14]#VAR_U="0.8"#大于0.8 为 1
IN_XZQQ=sys.argv[15]
OUTPUTPATH=sys.argv[16]
OUTPUTNAME=sys.argv[17]#OUTPUTNAME="agri_jicheng"#输出
#####################################
#HARDCODE
#PATH="E:\\spj\\data\\agri_jc\\"
#IN_TD="" #农业土地资源评价 #agri_l_final.tif
#IN_WA=""   #水资源评价
#IN_QH="nongyeqihou.tif"   #气候评价
#IN_HJ="huanjingpingjia.tif" #环境评价
#IN_ST="yanzihua.tif"   #生态评价（盐渍化评价）
#IN_ZH="zaihai.tif"     #灾害评价
#IN_CLIP="clipper.shp"  #裁剪
#VAR_GEO="1" #0/1   1为地理坐标系。0为投影坐标系
#VAR_FBL="50" #分辨率 不大于5000
# #根据地块集中连片度进行修正，确定城镇建设条件等级
#VAR_D="0.2" #0.2~0.4 降一级   小于0.2为5
#VAR_M="0.6" #0.6~0.8 升一级
#VAR_C="0.4"  #0.4~0.6 不变
#VAR_U="0.8"#大于0.8 为 1
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH="D:\\map\\"
#OUTPUTNAME="ny_jicheng"#输出
#############################################
env.workspace=PATH[:-1]
#######################################
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
##################################
if IN_TD == "99999":
    IN_TD=create_raster(5,IN_CLIP,VAR_FBL,"tihuan.tif")
if IN_WA == "99999":
     IN_WA=create_raster(5,IN_CLIP,VAR_FBL,"tihuan1.tif")
if IN_QH == "99999":
    IN_QH=create_raster(5,IN_CLIP,VAR_FBL,"tihuan2.tif")
if IN_ST == "99999":
    IN_ST =create_raster(5,IN_CLIP,VAR_FBL,"tihuan3.tif")
if IN_ZH == "99999":
    IN_ZH =create_raster(5,IN_CLIP,VAR_FBL,"tihuan4.tif")
if IN_HJ == "99999":
    IN_HJ =create_raster(5,IN_CLIP,VAR_FBL,"tihuan5.tif")
###################################
arcpy.RasterToPolygon_conversion (Int(IN_TD), "tdshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_WA), "washp.shp")
arcpy.Intersect_analysis (["tdshp.shp", "washp.shp"], "tdwashp.shp")

cursor = arcpy.da.SearchCursor("tdwashp.shp", ["GRIDCODE","GRIDCODE_1"])

#cursor = arcpy.da.SearchCursor("tdwashp.shp", ["gridcode","gridcode_1"])
new=[]
for row in cursor:
       if row[0]==1:
            if 1<=row[1]<=3:
                new.append(1)
            elif row[1]==4:
                new.append(2)
            elif row[1]==5:
                new.append(5)
       elif row[0]==2:
            if 1<=row[1]<=2:
                new.append(1)
            elif row[1]==3:
                new.append(2)
            elif row[1]==4:
                new.append(3)
            elif  row[1]==5:
                new.append(5)
       elif row[0]==3:
            if 1<=row[1]<=2:
                new.append(2)
            elif row[1]==3:
                new.append(3)
            elif row[1]==4:
                new.append(4)
            elif row[1]==5:
                new.append(5)
       elif row[0]==4:
            if row[1]==1:
                new.append(3)
            elif 2<=row[1]<=3:
                new.append(4)
            elif 4<=row[1]<=5:
                new.append(5)
       elif row[0]==5:
                new.append(5)

del row,cursor
try:
    arcpy.DeleteField_management("tdwashp.shp", 'base')
    arcpy.AddField_management("tdwashp.shp", 'base', "SHORT")     
except:    
      
    arcpy.AddField_management("tdwashp.shp", 'base', "SHORT")
cursor1 = arcpy.UpdateCursor("tdwashp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('base', new[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row 
arcpy.RasterToPolygon_conversion (Int(IN_QH), "qxshp.shp") 
arcpy.Intersect_analysis (["tdwashp.shp","qxshp.shp"], "qhtdshui.shp")
cursor = arcpy.da.SearchCursor("qhtdshui.shp", ["base","GRIDCODE_2"])
new1=[]
for row in cursor:
       if row[0]==1:
            if 1<=row[1]<=3:
                new1.append(1)
            elif row[1]==4:
                new1.append(2)
            elif row[1]==5:
                new1.append(5)
       elif row[0]==2:
            if row[1]==1:
                new1.append(1)
            elif 2<=row[1]<=3:
                new1.append(2)
            elif row[1]==4:
                new1.append(3)
            elif  row[1]==5:
                new1.append(5)
       elif row[0]==3:
            if 1<=row[1]<=2:
                new1.append(2)
            elif row[1]==3:
                new1.append(3)
            elif row[1]==4:
                new1.append(4)
            elif row[1]==5:
                new1.append(5)
       elif row[0]==4:
            if row[1]==1:
                new1.append(3)
            elif 2<=row[1]<=3:
                new1.append(4)
            elif 4<=row[1]<=5:
                new1.append(5)
       elif row[0]==5:
                new1.append(5)
del row,cursor
try:
    arcpy.DeleteField_management("qhtdshui.shp", 'base1')
    arcpy.AddField_management("qhtdshui.shp", 'base1', "SHORT")     
except:    
    arcpy.AddField_management("qhtdshui.shp", 'base1', "SHORT")
cursor1 = arcpy.UpdateCursor("qhtdshui.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('base1', new1[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row 
#############################################
arcpy.RasterToPolygon_conversion (Int(IN_HJ), "hjshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_ST), "stshp.shp")
arcpy.RasterToPolygon_conversion (Int(IN_ZH), "zhshp.shp")
arcpy.Intersect_analysis (["qhtdshui.shp","hjshp.shp", "stshp.shp","zhshp.shp"],"xzshp.shp" )   
cursor = arcpy.da.SearchCursor("xzshp.shp", ["base1","GRIDCODE_3"])
new2=[]
for row in cursor:
    if row[1]==5:
        new2.append(5)
    elif row[1]==3:
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
#print len(new2)
try:
    arcpy.DeleteField_management("xzshp.shp", 'xz1')
    arcpy.AddField_management("xzshp.shp", 'xz1', "SHORT")     
except:    
    arcpy.AddField_management("xzshp.shp", 'xz1', "SHORT")
cursor1 = arcpy.UpdateCursor("xzshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xz1', new2[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
##########################################
cursor = arcpy.da.SearchCursor("xzshp.shp", ["base1","GRIDCODE_4"])
new3=[]
for row in cursor:
    if row[1]==1:
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
#print len(new3)
try:
    arcpy.DeleteField_management("xzshp.shp", 'xz2')
    arcpy.AddField_management("xzshp.shp", 'xz2', "SHORT")     
except:                
    arcpy.AddField_management("xzshp.shp", 'xz2', "SHORT")
cursor1 = arcpy.UpdateCursor("xzshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xz2', new3[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
##############################################
cursor = arcpy.da.SearchCursor("xzshp.shp", ["base1","GRIDCODE_5"])
new4=[]
for row in cursor:
    if row[1]==1 and row[0]==1:
        new4.append(2)
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
#print len(new4)
try:
    arcpy.DeleteField_management("xzshp.shp", 'xz3')
    arcpy.AddField_management("xzshp.shp", 'xz3', "SHORT")    
except:                       
    arcpy.AddField_management("xzshp.shp", 'xz3', "SHORT")
cursor1 = arcpy.UpdateCursor("xzshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xz3', new4[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
#################################
ar=[] 
cursor = arcpy.da.SearchCursor("xzshp.shp", (["OID@", "SHAPE@AREA"])) 
for row in cursor: 
    ar.append(row[1]*pow(10,8))
del cursor,row
#print ar
try:
    arcpy.DeleteField_management("xzshp.shp", 'area')
    arcpy.AddField_management("xzshp.shp", 'area', "DOUBLE")    
except:                       
    arcpy.AddField_management("xzshp.shp", 'area', "DOUBLE")
cursor1 = arcpy.UpdateCursor("xzshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('area', ar[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
arcpy.MinimumBoundingGeometry_management("xzshp.shp", "zhfshp.shp", "CIRCLE","NONE")

ar2=[] 
cursor = arcpy.da.SearchCursor( "zhfshp.shp", (["OID@", "SHAPE@AREA"])) 
for row in cursor: 
    ar2.append(row[1]*pow(10,8))
del cursor,row
#print ar2
try:
    arcpy.DeleteField_management("zhfshp.shp", 'area2')
    arcpy.AddField_management( "zhfshp.shp", 'area2', "DOUBLE")    
except:                       
    arcpy.AddField_management( "zhfshp.shp", 'area2', "DOUBLE")
cursor1 = arcpy.UpdateCursor( "zhfshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('area2', ar2[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
#########################################################
cursor = arcpy.da.SearchCursor("zhfshp.shp", (["area", "area2"])) 
bll=[]
for row in cursor:
    bll.append(row[0]/row[1])
del cursor,row

try:
    arcpy.DeleteField_management("zhfshp.shp", 'bll')
    arcpy.AddField_management("zhfshp.shp", 'bll', "DOUBLE")    
except:                       
    arcpy.AddField_management("zhfshp.shp", 'bll', "DOUBLE")
cursor1 = arcpy.UpdateCursor("zhfshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('bll', bll[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
#########################################################
cursor = arcpy.da.SearchCursor("zhfshp.shp", ["xz3","bll"])
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
#print new6
try:
    arcpy.DeleteField_management("zhfshp.shp", 'xzjg')
    arcpy.AddField_management("zhfshp.shp", 'xzjg', "SHORT")    
except:                       
    arcpy.AddField_management("zhfshp.shp", 'xzjg', "SHORT")
cursor1 = arcpy.UpdateCursor("zhfshp.shp")
i = 0
for my_row in cursor1:
    my_row.setValue('xzjg', new6[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row
arcpy.FeatureToRaster_conversion("zhfshp.shp", "xzjg", "jg.tif",CC)
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
        return u"一般适宜"
    elif a == 5:
        return u"不适宜"
  """
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management("tdshp.shp")
arcpy.Delete_management("washp.shp")
arcpy.Delete_management("tdwashp.shp")
arcpy.Delete_management("qxshp.shp")
arcpy.Delete_management("qhtdshui.shp")
arcpy.Delete_management("xzshp.shp" )
arcpy.Delete_management("hjshp.shp")
arcpy.Delete_management("stshp.shp")
arcpy.Delete_management("zhshp.shp")
arcpy.Delete_management("zhfshp.shp")
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
##################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month7_shiyixing_3J.clr")
########################################
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")