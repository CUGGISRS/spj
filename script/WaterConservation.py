# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 16:23:18 2019

@author: 赵晓旭
水源涵养重要性
"""
from __future__ import division
import arcpy
import sys
from arcpy import env
import pandas as pd
import os
import csv
import StaticticsByXZQ
import RasterTableToTxtAndExcel
from arcpy.sa import *
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
#####################################
#HARDCODE
PATH=sys.argv[1]#PATH="D:\\test\\data\\st_wat\\"
IN_STXT=sys.argv[2]#IN_STXT='生态系统_wgs84.shp' #生态系统，根据生态系统判断地表径流系数均值
IN_JYL=sys.argv[3]#IN_JYL='JiangYuLiang_wgs84.tif'#降雨量
IN_ZFL=sys.argv[4]#IN_ZFL='ZhengFaLiang_wgs84.tif'#蒸发量
IN_CLIP=sys.argv[5]#IN_CLIP="clipper.shp"   #裁剪
VAR_GEO=sys.argv[6]#VAR_GEO="1" #0/1 1：地理坐标系，0投影坐标系
VAR_FBL=sys.argv[7]#VAR_FBL="100" #分辨率，不要大于5000
VAR_SY5=sys.argv[8]#VAR_SY5="0.05"  #水源涵养重分类
VAR_SY1=sys.argv[9]#VAR_SY1="0.3"   #水源涵养重分类
IN_XZQQ = sys.argv[10]
OUTPUTPATH = sys.argv[11] 
OUTPUTNAME=sys.argv[12]#OUTPUTNAME="shuiyuanhanyang"  #输出
#####################################
#HARDCODE
#PATH="E:\\spj\\data\\st_wat\\"
#IN_STXT='生态系统_wgs84.shp' #生态系统，根据生态系统判断地表径流系数均值
#IN_JYL=""#降雨量PATH+"jiangyu.txt"
#IN_ZFL=PATH+"zhengfaliang.xls"#蒸发量PATH+"zhengfaliang.txt"
#IN_CLIP="clipper.shp"   #裁剪JY
#VAR_GEO="1" #0/1 1：地理坐标系，0投影坐标系
#VAR_FBL="200" #分辨率，不要大于5000
#VAR_SY5="0.05"  #水源涵养重分类
#VAR_SY1="0.3"   #水源涵养重分类
#IN_XZQQ=""
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="st_shuiyuanhanyang"  #输出
#######################################
env.workspace=PATH[:-1]
JYL="jiangyu.shp"
ZFL="zhengfaliang.shp"
in_jyl_csv = PATH+'jiangyu.csv'
in_zf_csv = PATH+'zhengfaliang.csv'
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
###############################
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
####################################
if IN_JYL=="99999":
    create_raster(0,IN_CLIP,VAR_FBL,"jykrigph.tif")
else:
    if IN_JYL.endswith(".txt") or IN_JYL.endswith(".csv"):
        pass
    if IN_JYL.endswith(".xls") or IN_JYL.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_JYL,in_jyl_csv)
                    IN_JYL = in_jyl_csv
    try:
        arcpy.Delete_management(JYL)
        createFC = arcpy.CreateFeatureclass_management(env.workspace, JYL, "POINT", "", "", "")   
    except:  
        createFC = arcpy.CreateFeatureclass_management(env.workspace, JYL, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + JYL, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + JYL, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + JYL, "DAY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + JYL, "JY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + JYL,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + JYL,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","DAY","JY", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + JYL, iflds)
    count = 1
    for ln in open(IN_JYL, 'r').readlines():
       lnstrip = ln.strip()
       if count > 1:
           dataList = ln.split(",")
           y=dataList[4]
           m=dataList[5]
           d=dataList[6]
           j=float(dataList[7])/10
           lat = dataList[2]
           lon = dataList[1]
           ivals = [y,m,d,j, float(lon), float(lat),(float(lon), float(lat))]
           iCur.insertRow(ivals)
       count += 1
    print('Finish Projection:',JYL)
    del iCur
    arcpy.Dissolve_management(JYL,"jyll.shp", ["lon","lat","YEAR"],[['JY','SUM']])
    arcpy.Dissolve_management("jyll.shp","jyll1.shp", ["lon","lat"],[['SUM_JY','MEAN']])
    chazhi("jyll1.shp","MEAN_SUM_J","jykrigph.tif",CC)
    
    
if IN_ZFL=="99999":
    create_raster(0,IN_CLIP,VAR_FBL,"zfkrigph.tif")
else:    
    
    if IN_ZFL.endswith(".txt") or IN_ZFL.endswith(".csv"):
        pass
    if IN_ZFL.endswith(".xls") or IN_ZFL.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_ZFL,in_zf_csv)
                    IN_ZFL = in_zf_csv
    try:
        arcpy.Delete_management(ZFL)
        createFC = arcpy.CreateFeatureclass_management(env.workspace, ZFL, "POINT", "", "", "")   
    except:  
        createFC = arcpy.CreateFeatureclass_management(env.workspace, ZFL, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + ZFL, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + ZFL, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + ZFL, "DAY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + ZFL, "ZF", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + ZFL,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + ZFL,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","DAY","ZF", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + ZFL, iflds)
    count = 1
    for ln in open(IN_ZFL, 'r').readlines():
       lnstrip = ln.strip()
       if count > 1:
           dataList = ln.split(",")
           y=dataList[4]
           m=dataList[5]
           d=dataList[6]
           j=float(dataList[7])/10
           lat = dataList[2]
           lon = dataList[1]
           ivals = [y,m,d,j, float(lon), float(lat),(float(lon), float(lat))]
           iCur.insertRow(ivals)
       count += 1
    print('Finish Projection:',ZFL)
    del iCur
    #####################################
    
    arcpy.Dissolve_management(ZFL,"zfll.shp", ["lon","lat","YEAR"],[['ZF','SUM']])
    arcpy.Dissolve_management("zfll.shp","zfll1.shp", ["lon","lat"],[['SUM_ZF','MEAN']])
    
    chazhi("zfll1.shp", "MEAN_SUM_Z", "zfkrigph.tif",CC)
#####################################
#地表径流量=平均降水量*平均地表径流系数
#根据生态类型获取径流系数

lj=[]
cursor = arcpy.da.SearchCursor(IN_STXT, ["STXT"]) 
for row in cursor:
    if row[0] ==unicode("常绿阔叶林", "utf-8"):
        lj.append(0.0267)
    elif row[0] ==unicode("常绿针叶林", "utf-8"):
        lj.append(0.0302)
    elif row[0] ==unicode("针阔混交林", "utf-8"):
        lj.append(0.0229)
    elif row[0] ==unicode("落叶阔叶林", "utf-8"):
        lj.append(0.0133)
    elif row[0] ==unicode("落叶针叶林", "utf-8"):
        lj.append(0.0088)
    elif row[0] ==unicode("稀疏林", "utf-8")or row[0] ==unicode("稀疏灌丛", "utf-8"):
        lj.append(0.1920)
    elif row[0] ==unicode("常绿阔叶灌丛", "utf-8"):
        lj.append(0.0426)
    elif row[0] ==unicode("落叶阔叶灌丛", "utf-8")or row[0] ==unicode("针叶灌丛", "utf-8"):
        lj.append(0.0417)
    elif row[0] ==unicode("草甸", "utf-8"):
        lj.append(0.0820)
    elif row[0] ==unicode("草原", "utf-8"):
        lj.append(0.0478)
    elif row[0] ==unicode("草丛", "utf-8"):
        lj.append(0.0937)
    elif row[0] ==unicode("稀疏草地", "utf-8"):
        lj.append(0.1827)
    elif row[0] ==unicode("不确定", "utf-8"):
        lj.append(1)
    else:
        lj.append(0)
del cursor
del row
#################################################
##添加jlxs列到shp文件里，内容是径流系数
try:
    arcpy.DeleteField_management(IN_STXT, 'jlxs')
    arcpy.AddField_management(IN_STXT, 'jlxs', "FLOAT")  
except:  
    arcpy.AddField_management(IN_STXT, 'jlxs', "FLOAT")
cursor1 = arcpy.UpdateCursor(IN_STXT)
i = 0
for my_row in cursor1:
    my_row.setValue('jlxs', lj[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1
del my_row
arcpy.FeatureToRaster_conversion(IN_STXT, "jlxs", "JLXS.tif", VAR_FBL)
###############################################
out = arcpy.sa.Raster("jykrigph.tif") * arcpy.sa.Raster("JLXS.tif")
out.save("JLYZ.tif")         #地表径流量=降水量*平均地表径流系数
out1 = Abs(arcpy.sa.Raster("jykrigph.tif") - arcpy.sa.Raster("JLYZ.tif")- arcpy.sa.Raster("zfkrigph.tif"))
out1.save("base.tif")         #p-r-et
arcpy.RasterToPoint_conversion("base.tif", "point.shp", "VALUE")
#将栅格数据转化成点要素
arcpy.gp.Int_sa("base.tif","intbase.tif")#将栅格数据转换成整型
arcpy.RasterToPolygon_conversion("intbase.tif", "polygon.shp", "NO_SIMPLIFY",
                                  "VALUE")
#将栅格数据集转换成面要素
arcpy.SpatialJoin_analysis("polygon.shp","point.shp" ,"whole.shp")
#点要素和面要素进行空间连接
arcpy.Intersect_analysis(["whole.shp",IN_STXT],'st.shp')
#相交
cursor2 = arcpy.da.SearchCursor("st.shp", ["SHAPE@AREA"])#面积
ar=[]
for row in cursor2:
    ar.append(row[0])

cursor3 = arcpy.da.SearchCursor("st.shp", ["GRID_CODE"])#前面计算的值
yt=[]
for row in cursor3: 
    yt.append(row[0]*pow(10,-3))#平方米转换成平方千米10**-6 在乘10**3
#
prod = [a*b for a, b in zip(yt,ar)]
#让两个列表相乘
try:
    arcpy.DeleteField_management("st.shp", 'SHY')
    arcpy.AddField_management("st.shp", 'SHY', "FLOAT") 
except:  
    arcpy.AddField_management("st.shp", 'SHY', "FLOAT")
cursor4 = arcpy.UpdateCursor("st.shp")
i = 0
for my_row in cursor4:
    my_row.setValue('SHY', prod[i])
    cursor4.updateRow(my_row)
    i += 1
del cursor4
del my_row
arcpy.Dissolve_management("st.shp","final.shp", 'STXT',[['SHY','SUM']])
#根据生态类型进行融合，并将SHY列根据生态类型的分类进行融合
arcpy.FeatureToRaster_conversion("final.shp", "SUM_SHY", "syhy.tif")
#最后根据SHY列转换成栅格，得到最终结果
arcpy.Clip_management("syhy.tif","","clipsyhy.tif",IN_CLIP,"", "ClippingGeometry")
outReclass = arcpy.sa.Reclassify("clipsyhy.tif", "Value", arcpy.sa.RemapRange([[-10,float(VAR_SY5),1],[float(VAR_SY5),float(VAR_SY1),3],[float(VAR_SY1),10,5]]),'NODATA')
outReclass.save(OUTPUTPATH+OUTPUTNAME+".tif")
################################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"极重要"
    if a == 3:
        return u"高度重要"
    else:
        return u'一般重要'"""
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL  , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management("JLXS.tif")
arcpy.Delete_management("JLYZ.tif")
arcpy.Delete_management("base.tif") 
arcpy.Delete_management("point.shp")
arcpy.Delete_management("intbase.tif")
arcpy.Delete_management("polygon.shp")
arcpy.Delete_management("whole.shp")
arcpy.Delete_management('st.shp')
arcpy.Delete_management("final.shp")
arcpy.Delete_management("syhy.tif")
arcpy.Delete_management("clipsyhy.tif")
if arcpy.Exists("jyll.shp"):
    arcpy.Delete_management("jyll.shp")
if arcpy.Exists("jykrigph.tif"):
    arcpy.Delete_management("jykrigph.tif") 
if arcpy.Exists("jyll1.shp"):
    arcpy.Delete_management("jyll1.shp") 
if arcpy.Exists("zfll.shp"):
    arcpy.Delete_management("zfll.shp")
if arcpy.Exists("zfll1.shp"):
    arcpy.Delete_management("zfll1.shp")
if arcpy.Exists("zfkrigph.tif"):
    arcpy.Delete_management("zfkrigph.tif")
if os.path.exists(in_jyl_csv) == True:
    os.remove(in_jyl_csv)
if os.path.exists(in_zf_csv) == True:
    os.remove(in_zf_csv)
##################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
     StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_fuwu_3J.clr")
#arcpy.ApplySymbologyFromLayer_management(fin, "F:\\1clr\\Month4_mingan_3J.lyr")
####################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")










