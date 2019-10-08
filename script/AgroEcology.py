# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 14:56:20 2019

@author: 赵晓旭
盐渍化
"""
from __future__ import division
import arcpy
import sys
import os
import pandas as pd
from arcpy import env
from arcpy.sa import *
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput=True
#####################################
#PATH= sys.argv[1]#PATH="D:\\test\\data\\agri_yzh\\"
#IN_JY= sys.argv[2]#JY="jiangyu.txt"#降雨量的txt文件
#IN_ZF= sys.argv[3]#ZF='zfl.txt'#蒸发量的txt文件
#IN_KHD= sys.argv[4]#KHD="skhd.txt"#矿化度的txt文件
#
#IN_SMS= sys.argv[5]#SMS="sms.txt"#水埋深的txt文件
#IN_TR= sys.argv[6]#IN_TR="TRLX2.shp"#土壤文件  输入数据
#IN_CLIP= sys.argv[7]#IN_CLIP="clipper.shp"#裁剪
#
#VAR_GEO= sys.argv[8]#VAR_GEO="1" #0/1  1：地理坐标系，0投影坐标系
#VAR_FBL= sys.argv[9]#VAR_FBL="150" #分辨率，，不要大于5000
###蒸发量/降雨量 的重分类
#VAR_ZJ1= sys.argv[10]#VAR_ZJ1="3"  # 小于等于3为1
#VAR_ZJ5= sys.argv[11]#VAR_ZJ5="15"#3~15为3  ，  大于15为5
###矿化度的重分类
#VAR_KHD1= sys.argv[12]#VAR_KHD1="5"  # 小于等于 5为1
#VAR_KHD5= sys.argv[13]#VAR_KHD5="25" # 5~25 为 3 ，大于25 为5
###水埋深的重分类
#VAR_SMS5= sys.argv[14]#VAR_SMS5="1" # 1~5为3， 小于等于1为5
#VAR_SMS1= sys.argv[15]#VAR_SMS1="5" # 大于等于5 为1
###盐渍化最后的分级标准
#VAR_YZH1= sys.argv[16]#VAR_YZH1="1.0" #1.0~3.0 为低
#VAR_YZH2= sys.argv[17]#VAR_YZH2="3.0" #   3.1~5.0 为较低
#VAR_YZH3= sys.argv[18]#VAR_YZH4="5.0" # 5.1~6.0 为中等
#VAR_YZH4= sys.argv[19]#VAR_YZH6="6.0" #  6.1~7.0 为较高
#VAR_YZH5= sys.argv[20]#VAR_YZH8="7.0"#  大于7.0 为高
#IN_XZQQ=sys.argv[21]
#OUTPUTPATH = sys.argv[22]
#OUTPUTNAME= sys.argv[23]#OUTPUTNAME="yanzihua"  #输出
######################################
PATH="E:\\spj\\data\\agri_yzh\\"
IN_JY=PATH+"jiangyu.xls"#降雨量的txt文件PATH+"jiangyu.txt"
IN_KHD="99999"#矿化度的txt文件
IN_ZF=PATH+"zfl.txt"#蒸发量的txt文件
IN_SMS="99999"#水埋深的txt文件
IN_TR="TRLX2.shp"#土壤文件  输入数据
IN_CLIP="clipper.shp"#裁剪
VAR_GEO="1" #0/1  1：地理坐标系，0投影坐标系
VAR_FBL="150" #分辨率，，不要大于5000
#蒸发量/降雨量 的重分类
VAR_ZJ1="3"  # 小于等于3为1
VAR_ZJ5="15"#3~15为3  ，  大于15为5
#矿化度的重分类
VAR_KHD1="5"  # 小于等于 5为1
VAR_KHD5="25" # 5~25 为 3 ，大于25 为5
#水埋深的重分类
VAR_SMS1="5" # 大于等于5 为1
VAR_SMS5="1" # 1~5为3， 小于等于1为5
#盐渍化最后的分级标准
VAR_YZH1="1.0" #1.0~3.0 为低
VAR_YZH2="3.0" #    3.1~5.0 为较低
VAR_YZH3="5.0" # 5.1~6.0 为中等
VAR_YZH4="6.0" #  6.1~7.0 为较高
VAR_YZH5="7.0"#  大于7.0 为高
IN_XZQQ="E:\\spj\\data\\agri_yzh\\XZQ_WGS84.shp"
OUTPUTPATH = "D:\\map\\"
OUTPUTNAME="1111111"  #输出
####################################
env.workspace=PATH[:-1]
MIjy = "jiangyu.shp"
MIzf="zhengfa.shp"
MIkhd="kuanghd.shp"
MIsms="maishen.shp"
in_jy_csv=PATH+"jiangyu.csv"
in_zfl_csv=PATH+'zhengfaliang.csv'
in_sms_csv=PATH+"sms.csv"
in_khd_csv=PATH+"skhd.csv"
####################################
#重采样像元大小设定
FBLL=int(VAR_FBL)
if int(VAR_GEO)==1:#地理坐标系
    VAR_FBL=0.0000101*int(VAR_FBL)
else:#投影坐标系
    VAR_FBL=int(VAR_FBL)
    CC="%f"%(VAR_FBL)
####################################
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
##################################
#降雨shp文件
if IN_JY=="99999" or IN_ZF=="99999":
    create_raster(5,IN_CLIP,VAR_FBL,"z.tif")
else:
    if IN_JY.endswith('.txt') or IN_JY.endswith('.csv') :
        pass
    if IN_JY.endswith('.xls') or IN_JY.endswith('.xlsx'):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_JY,in_jy_csv)
                    IN_JY=in_jy_csv
    try:
        arcpy.Delete_management(MIjy)
        C = arcpy.CreateFeatureclass_management(env.workspace, MIjy, "POINT", "", "", "")   
    except:  
        C = arcpy.CreateFeatureclass_management(env.workspace, MIjy, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MIjy, "JY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIjy, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIjy,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIjy,  "lat", "FLOAT" )
    iflds = ["YEAR","JY", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIjy, iflds)
    count = 1
    for ln in open(IN_JY, 'r').readlines():
        lnstrip = ln.strip()
        if count > 1:
            dataList = ln.split(",")
            y=dataList[4]
            s=float(dataList[7])/10
            lat = dataList[2]
            lon = dataList[1]
            ivals = [y,s, float(lon), float(lat),(float(lon), float(lat))]
            iCur.insertRow(ivals)
        count += 1
    print('Finish Projection:',MIjy)
    del iCur
    #蒸发量shp文件
    if IN_ZF.endswith('.txt') or IN_ZF.endswith('.csv'):
        pass
    if IN_ZF.endswith('.xls') or IN_ZF.endswith('.xlsx'):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_ZF,in_zfl_csv)
                    IN_ZF=in_zfl_csv
    try:
        arcpy.Delete_management(MIzf)
        createFC = arcpy.CreateFeatureclass_management(env.workspace, MIzf, "POINT", "", "", "")   
    except:  
        createFC = arcpy.CreateFeatureclass_management(env.workspace, MIzf, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MIzf, "ZF", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIzf, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIzf,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIzf,  "lat", "FLOAT" )
    iflds = ["YEAR","ZF", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIzf, iflds)
    count = 1
    for ln in open(IN_ZF, 'r').readlines():
        lnstrip = ln.strip()
        if count > 1:
            dataList = ln.split(",")
            y=dataList[4]
            s=float(dataList[7])/10
            lat = dataList[2]
            lon = dataList[1]
            ivals = [y,s, float(lon), float(lat),(float(lon), float(lat))]
            iCur.insertRow(ivals)
        count += 1
    print('Finish Projection:',MIzf)
    del iCur  
    arcpy.Dissolve_management(MIjy, "jy2.shp", ["lon","lat"],[['JY','SUM']])
    year=[]
    cursor2 = arcpy.da.SearchCursor(MIjy, ["YEAR"])
    for row in cursor2:
        year.append(row[0])
        n=len(list(set(year))) 
    del cursor2,row    
    cursor2 = arcpy.da.SearchCursor("jy2.shp", ["SUM_JY"])
    jy=[]
    for row1 in cursor2:
        jy.append(row1[0]/n)
    del cursor2,row1
    try:
        arcpy.DeleteField_management("jy2.shp", 'pj')
        arcpy.AddField_management("jy2.shp", 'pj', "FLOAT")   #创建aaa列，用来放置1，2，3，4，5    
    except:  
        arcpy.AddField_management("jy2.shp", 'pj', "FLOAT")
    cursor1 = arcpy.UpdateCursor("jy2.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('pj', jy[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row
    chazhi("jy2.shp", "pj", "jykrigph.tif",CC)
##########################################################    
    arcpy.Dissolve_management(MIzf, "zf2.shp", ["lon","lat"],[['ZF','SUM']])
    year=[]
    cursor2 = arcpy.da.SearchCursor(MIzf, ["YEAR"])
    for row in cursor2:
        year.append(row[0])
        n=len(list(set(year))) 
    del cursor2,row    
    cursor2 = arcpy.da.SearchCursor("zf2.shp", ["SUM_ZF"])
    zf=[]
    for row1 in cursor2:
        zf.append(row1[0]/n)
    del cursor2,row1
    try:
        arcpy.DeleteField_management("zf2.shp", 'pj')
        arcpy.AddField_management("zf2.shp", 'pj', "FLOAT")   #创建aaa列，用来放置1，2，3，4，5    
    except:  
        arcpy.AddField_management("zf2.shp", 'pj', "FLOAT")
    cursor1 = arcpy.UpdateCursor("zf2.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('pj', zf[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row    
    chazhi("zf2.shp", "pj", "zfkrigph.tif",CC)
    arcpy.Clip_management("jykrigph.tif","","jyfinal.tif",IN_CLIP,"", "ClippingGeometry")
    arcpy.Clip_management("zfkrigph.tif","","zffinal.tif",IN_CLIP,"", "ClippingGeometry")
    zj=arcpy.Raster("zffinal.tif")/arcpy.Raster("jyfinal.tif")
    zj.save("zj.tif")
    Z = arcpy.sa.Reclassify("zj.tif", "Value", arcpy.sa.RemapRange([[-10000,float(VAR_ZJ1),1],[float(VAR_ZJ1),float(VAR_ZJ5),3],[float(VAR_ZJ5),10000,5]]),'NODATA')    
    Z.save("z.tif")
##############################################
#地下水埋深shp文件
if IN_SMS=="99999":
    create_raster(5,IN_CLIP,VAR_FBL,"m.tif")
else:
    if IN_SMS.endswith('.txt') or IN_SMS.endswith('.csv'):
        pass
    if IN_SMS.endswith('.xls') or IN_SMS.endswith('.xlsx'):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_SMS,in_sms_csv)
                    IN_SMS=in_sms_csv
    try:
        arcpy.Delete_management(MIsms)
        createFC = arcpy.CreateFeatureclass_management(env.workspace, MIsms, "POINT", "", "", "")  
    except:  
        createFC = arcpy.CreateFeatureclass_management(env.workspace, MIsms, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MIsms, "SMS", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIsms,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIsms,  "lat", "FLOAT" )
    iflds = ["SMS", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIsms, iflds)
    count = 1
    for ln in open(IN_SMS, 'r').readlines():
        lnstrip = ln.strip()
        if count > 1:
            dataList = ln.split(",")
            s=dataList[4]
            lat = dataList[2]
            lon = dataList[1]
            ivals = [s, float(lon), float(lat),(float(lon), float(lat))]
            iCur.insertRow(ivals)
        count += 1
    print('Finish Projection:',MIsms)
    del iCur
    chazhi(MIsms,"SMS","smskrigph.tif",CC)  
    arcpy.Clip_management("smskrigph.tif","","smsfinal.tif",IN_CLIP,"", "ClippingGeometry")
    M = arcpy.sa.Reclassify("smsfinal.tif", "Value", arcpy.sa.RemapRange([[-100000,float(VAR_SMS5),5],[float(VAR_SMS5),float(VAR_SMS1),3],[float(VAR_SMS1),10000,1]]),'NODATA')
    M.save("m.tif")
##############################################
#地下水矿化度
if IN_KHD=="99999":
    create_raster(5,IN_CLIP,VAR_FBL,"k.tif")
else:
    if IN_KHD.endswith('.txt') or IN_KHD.endswith('.csv'):
        pass
    if IN_KHD.endswith('.xls') or IN_KHD.endswith('.xlsx'):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_KHD,in_khd_csv)
                    IN_KHD=in_khd_csv
    try:
        arcpy.Delete_management(MIkhd)
        createFC = arcpy.CreateFeatureclass_management(env.workspace, MIkhd, "POINT", "", "", "")  
    except:  
        createFC = arcpy.CreateFeatureclass_management(env.workspace, MIkhd, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MIkhd, "KHD", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIkhd,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIkhd,  "lat", "FLOAT" )
    iflds = ["KHD", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIkhd, iflds)
    count = 1
    for ln in open(IN_KHD, 'r').readlines():
        lnstrip = ln.strip()
        if count > 1:
            dataList = ln.split(",")
            s=dataList[4]
            lat = dataList[2]
            lon = dataList[1]
            ivals = [s, float(lon), float(lat),(float(lon), float(lat))]
            iCur.insertRow(ivals)
        count += 1
    print('Finish Projection:',MIkhd)
    del iCur  
    rows = arcpy.da.SearchCursor(MIkhd,['FID'])
    for row in rows:
        y= row[0]
    del rows,row
    chazhi(MIkhd, "KHD", "khdkrigph.tif",CC)    
    arcpy.Clip_management("khdkrigph.tif","","khdfinal.tif",IN_CLIP,"", "ClippingGeometry")
    
    K = arcpy.sa.Reclassify("khdfinal.tif", "Value", arcpy.sa.RemapRange([[-10000,float(VAR_KHD1),1],[float(VAR_KHD1),float(VAR_KHD5),3],[float(VAR_KHD5),10000,5]]),'NODATA')
    K.save("k.tif")  
################################################
trzd=[]
cursor = arcpy.da.SearchCursor(IN_TR, ["TRZD"])
for row in cursor:
    if row[0]==u"砂土" or row[0]==u"粘土":
         trzd.append(1)
    elif row[0]==u"粘壤土" or row[0]==u"壤土":
         trzd.append(3)
    elif row[0]==u"砂壤土":
         trzd.append(5)
    else:
         trzd.append(0)
del cursor,row
#print trzd
try:
    arcpy.DeleteField_management(IN_TR, 'fj')
    arcpy.AddField_management(IN_TR, 'fj', "SHORT")   #创建aaa列，用来放置1，2，3，4，5    
except:  
    arcpy.AddField_management(IN_TR, 'fj', "SHORT")
cursor1 = arcpy.UpdateCursor(IN_TR)
i = 0
for my_row in cursor1:
    my_row.setValue('fj', trzd[i])
    cursor1.updateRow(my_row)
    i += 1
del cursor1,my_row  
arcpy.FeatureToRaster_conversion(IN_TR,'fj','trfj.tif',VAR_FBL) 
arcpy.Clip_management('trfj.tif',"","trfjfinal.tif",IN_CLIP,"", "ClippingGeometry") 
############################################################
L=arcpy.Raster("z.tif")*arcpy.Raster("k.tif")*arcpy.Raster("m.tif")*arcpy.Raster("trfjfinal.tif")
L.save("l.tif")
S= pow(arcpy.Raster("l.tif"),1.0/4)
S.save("jg.tif")
tt = arcpy.sa.Reclassify("jg.tif", "Value", arcpy.sa.RemapRange([[float(VAR_YZH1),float(VAR_YZH2),5],[float(VAR_YZH2),float(VAR_YZH3),4],[float(VAR_YZH3),float(VAR_YZH4),3],[float(VAR_YZH4),float(VAR_YZH5),2],[float(VAR_YZH5),10000,1]]),'NODATA')    
tt.save(OUTPUTPATH+OUTPUTNAME+".tif")
##############################
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
#####################################
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management( MIjy)
arcpy.Delete_management( MIzf)
arcpy.Delete_management( MIkhd)
arcpy.Delete_management( MIsms)
arcpy.Delete_management( 'trfj.tif')
arcpy.Delete_management( "trfjfinal.tif")
arcpy.Delete_management( "jy2.shp")
arcpy.Delete_management( "jykrigph.tif")
arcpy.Delete_management( "zf2.shp")
arcpy.Delete_management( "zfkrigph.tif")
arcpy.Delete_management( "khdkrigph.tif")
arcpy.Delete_management( "smskrigph.tif")
arcpy.Delete_management( "jyfinal.tif")
arcpy.Delete_management( "zffinal.tif")
arcpy.Delete_management( "khdfinal.tif")
arcpy.Delete_management( "smsfinal.tif")
arcpy.Delete_management( "zj.tif")
arcpy.Delete_management( "z.tif")
arcpy.Delete_management( "k.tif")
arcpy.Delete_management( "m.tif")
arcpy.Delete_management( "l.tif")
arcpy.Delete_management( "jg.tif")
if os.path.exists(in_zfl_csv)==True:
    os.remove(in_zfl_csv)
if os.path.exists(in_jy_csv)==True:
    os.remove(in_jy_csv)
if os.path.exists(in_khd_csv)==True:
    os.remove(in_khd_csv)
if os.path.exists(in_sms_csv)==True:
    os.remove(in_sms_csv)
###############################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_nong_tu_zai_5J.clr")
################################################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")

