# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 16:18:04 2019

@author: 赵晓旭

农业功能指向的水资源评价
"""
from __future__ import division
import sys
import os
import pandas as pd
import arcpy
from arcpy import env
from arcpy.sa import *
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput=True
#####################################
PATH=sys.argv[1]         #PATH="D:\\test\\data\\agri_func_w\\"
VAR_A= sys.argv[2]        #VAR_A="0" #1降水量/2干旱指数/0用水总量控制指标模数
IN_JY=sys.argv[3]                    #IN_JY="JiangYuLiang.tif" #降雨量
IN_ZF=sys.argv[4]           #IN_ZF="ZhengFaLiang.tif" #蒸发量
IN_YS=sys.argv[5]                   #IN_YS="YongShuiMoShu.tif" #用水模数
IN_CLIP= sys.argv[6]                    #IN_CLIP="clipper.shp"  #裁剪
VAR_GEO=sys.argv[7]  #VAR_GEO="1" #0/1 1地理坐标系，0投影坐标系
VAR_FBL= sys.argv[8] #VAR_FBL="20" #分辨率，不大于5000
#降水量重分类
VAR_JY5=sys.argv[9]  #VAR_JY5="200"  #小于200为差
VAR_JY4=sys.argv[10]    #VAR_JY4="400" #200~400 较差
VAR_JY3=sys.argv[11]        #VAR_JY3="800" #400~800 一般
VAR_JY2=sys.argv[12]     #VAR_JY2="1200" #800~1200 较好 大于等于1200 好
#干旱重分类 
VAR_GH1=sys.argv[13]       #VAR_GH1="0.5"  #小于等于0.5 好
VAR_GH2=sys.argv[14]      #VAR_GH2="1.0" #0.5~1.0 较好
VAR_GH3=sys.argv[15]       #VAR_GH3="3.0" #1.0~3.0 一般
VAR_GH4=sys.argv[16]        #VAR_GH4="7.0"  #3.0~7.0 较差 大于7.0 差
#用水总量控制指标模数重分类 
VAR_YS4=sys.argv[17]#VAR_YS4="30000" #3~8万 较差   小于3万 差
VAR_YS3=sys.argv[18]#VAR_YS3="80000"  #8~13万 一般
VAR_YS2=sys.argv[19]#VAR_YS2="130000" #13~25万 较好
VAR_YS1=sys.argv[20]#VAR_YS1="250000" #大于等于 250000 为好
IN_XZQQ=sys.argv[21]
OUTPUTPATH = sys.argv[22]
OUTPUTNAME=sys.argv[23] #OUTPUTNAME="shuiziyuan" #输出

#######################################
#HARDCODE
#PATH="E:\\spj\\data\\agri_func_w\\"
#VAR_A="2" #1降水量/2干旱指数/0用水总量控制指标模数
#IN_JY=PATH+"jiangyu.xls" #降雨量
#IN_ZF=PATH+"zhengfaliang.xls" #蒸发量
#IN_YS="YongShuiMoShu.tif" #用水模数
#IN_CLIP="clipper.shp"
#VAR_GEO="1" #0/1
#VAR_FBL="150" #不要大于5000
# #降水量重分类
#VAR_JY5="200"  #小于200为差
#VAR_JY4="400" #200~400 较差
#VAR_JY3="800" #400~800 一般
#VAR_JY2="1200" #800~1200 较好 大于等于1200 好
#  #干旱重分类 
#VAR_GH1="0.5"  #小于等于0.5 好
#VAR_GH2="1.0" #0.5~1.0 较好
#VAR_GH3="3.0" #1.0~3.0 一般
#VAR_GH4="7.0"  #3.0~7.0 较差 大于7.0 差
# #用水总量控制指标模数重分类 
#VAR_YS4="30000" #3~8万 较差   小于3万 差
#VAR_YS3="80000"  #8~13万 一般
#VAR_YS2="130000" #13~25万 较好
#VAR_YS1="250000" #大于等于 250000 为好 
#IN_XZQQ="XZQ_WGS84.shp" 
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME="ny_shui" #输出
####################################
env.workspace = PATH[:-1]
outputjy="jiangyu.shp"
outputzf="zhengfa.shp"
ganhan="ganhan.tif"
in_jy_csv=PATH+"jiangyu.csv"
in_zf_csv=PATH+"zhengfa.csv"
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
########################################

if int(VAR_A) ==1 :
    if IN_JY.endswith('.txt') or IN_JY.endswith('.csv') :
        pass
    if IN_JY.endswith('.xlsx') or IN_JY.endswith('.xls'):
        if __name__ == '__main__':
                xlsx_to_csv_pd(IN_JY,in_jy_csv)
                IN_JY=in_jy_csv
    try:
       arcpy.Delete_management(outputjy)
       createFC = arcpy.CreateFeatureclass_management(env.workspace, outputjy, "POINT", "", "", "")  
    except:
       createFC = arcpy.CreateFeatureclass_management(env.workspace, outputjy, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + outputjy, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy, "DAY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy, "JY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","DAY","JY", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + outputjy, iflds)
    count = 1
    for ln in open(IN_JY, 'r').readlines():
       lnstrip = ln.strip()
       if count > 1:
           dataList = ln.split(",")
           y=dataList[4]
           m=dataList[5]
           d=dataList[6]
           j=dataList[7]
           lat = dataList[2]
           lon = dataList[1]
           ivals = [y,m,d,j, float(lon), float(lat),(float(lon), float(lat))]
           iCur.insertRow(ivals)
       count += 1
    print('Finish Projection:',outputjy)
    del iCur
#######################################
    arcpy.Dissolve_management(outputjy, "jy.shp", ["lon","lat","YEAR"],[['JY','SUM']])
    arcpy.Dissolve_management("jy.shp", "jy1.shp", ["lon","lat"],[['SUM_JY','SUM'],['YEAR','COUNT']])
    cursor2 = arcpy.da.SearchCursor("jy1.shp", ["SUM_SUM_JY","COUNT_YEAR"])
    kk=[]
    for row in cursor2:
        kk.append(row[0]/10/row[1]) 
    del row,cursor2
    try:
       arcpy.DeleteField_management("jy1.shp", 'bl')
       arcpy.AddField_management("jy1.shp", 'bl', "FLOAT")
    except:
       arcpy.AddField_management("jy1.shp", 'bl', "FLOAT")
    cursor1 = arcpy.UpdateCursor("jy1.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('bl', kk[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row
    chazhi("jy1.shp", "bl", "jykrigph.tif",CC)
    outReclass = arcpy.sa.Reclassify("jykrigph.tif", "Value", arcpy.sa.RemapRange([[-10000,float(VAR_JY5),5],[float(VAR_JY5),float(VAR_JY4),4],[float(VAR_JY4),float(VAR_JY3),3],
                                     [float(VAR_JY3),float(VAR_JY2),2],[float(VAR_JY2),300000,1]]))
    outReclass.save("jg.tif")
    arcpy.Delete_management(outputjy)
    arcpy.Delete_management("jy.shp")
    arcpy.Delete_management("jy1.shp")
    arcpy.Delete_management("jykrigph.tif")
elif int(VAR_A) ==2 :
    if IN_JY.endswith('.txt') or IN_JY.endswith('.csv'):
        pass
    if IN_JY.endswith('.xlsx') or IN_JY.endswith('.xls'):
        if __name__ == '__main__':
                xlsx_to_csv_pd(IN_JY,in_jy_csv)
                IN_JY=in_jy_csv
    try:
       arcpy.Delete_management(outputjy)
       createFC = arcpy.CreateFeatureclass_management(env.workspace, outputjy, "POINT", "", "", "")  
    except:
       createFC = arcpy.CreateFeatureclass_management(env.workspace, outputjy, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + outputjy, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy, "DAY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy, "JY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + outputjy,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","DAY","JY", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + outputjy, iflds)
    count = 1
    for ln in open(IN_JY, 'r').readlines():
       lnstrip = ln.strip()
       if count > 1:
           dataList = ln.split(",")
           y=dataList[4]
           m=dataList[5]
           d=dataList[6]
           j=dataList[7]
           lat = dataList[2]
           lon = dataList[1]
           ivals = [y,m,d,j, float(lon), float(lat),(float(lon), float(lat))]
           iCur.insertRow(ivals)
       count += 1
    print('Finish Projection:',outputjy)
    del iCur  
    if IN_ZF.endswith('.txt') or IN_ZF.endswith('.csv') :
        pass
    if IN_ZF.endswith('.xlsx') or IN_ZF.endswith('.xls') :
        if __name__ == '__main__':
                xlsx_to_csv_pd(IN_ZF,in_zf_csv)
                IN_ZF = in_zf_csv
    try:
       arcpy.Delete_management(outputzf)
       createFC = arcpy.CreateFeatureclass_management(env.workspace, outputzf, "POINT", "", "", "")  
    except:  
       createFC = arcpy.CreateFeatureclass_management(env.workspace, outputzf, "POINT", "", "", "")
    createFC = arcpy.CreateFeatureclass_management(env.workspace, outputzf, "POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + outputzf, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputzf, "MONTH", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputzf, "DAY", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputzf, "ZF", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + outputzf,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + outputzf,  "lat", "FLOAT" )
    iflds = ["YEAR","MONTH","DAY","ZF", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + outputzf, iflds)
    count = 1
    for ln in open(IN_ZF, 'r').readlines():
       lnstrip = ln.strip()
       if count > 1:
           dataList = ln.split(",")
           y=dataList[4]
           m=dataList[5]
           d=dataList[6]
           j=dataList[7]
           lat = dataList[2]
           lon = dataList[1]
           ivals = [y,m,d,j, float(lon), float(lat),(float(lon), float(lat))]
           iCur.insertRow(ivals)
       count += 1
    print('Finish Projection:',outputzf)
    del iCur
    
        
    arcpy.Dissolve_management(outputjy, "jy.shp", ["lon","lat","YEAR"],[['JY','SUM']])
    arcpy.Dissolve_management("jy.shp", "jy1.shp", ["lon","lat"],[['SUM_JY','SUM'],['YEAR','COUNT']])
    cursor2 = arcpy.da.SearchCursor("jy1.shp", ["SUM_SUM_JY","COUNT_YEAR"])
    kk=[]
    for row in cursor2:
        kk.append(row[0]/10/row[1]) 
    del row,cursor2
    try:
       arcpy.DeleteField_management("jy1.shp", 'bl')
       arcpy.AddField_management("jy1.shp", 'bl', "FLOAT")
    except:
       arcpy.AddField_management("jy1.shp", 'bl', "FLOAT")
    cursor1 = arcpy.UpdateCursor("jy1.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('bl', kk[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row
    chazhi("jy1.shp", "bl", "jykrigph.tif",CC)
    arcpy.Dissolve_management(outputzf, "zf.shp", ["lon","lat","YEAR"],[['ZF','SUM']])
    arcpy.Dissolve_management("zf.shp", "zf1.shp", ["lon","lat"],[['SUM_ZF','SUM'],['YEAR','COUNT']])
    cursor2 = arcpy.da.SearchCursor("zf1.shp", ["SUM_SUM_ZF","COUNT_YEAR"])
    kj=[]
    for row in cursor2:
        kj.append(row[0]/10/row[1]) 
    del row,cursor2
    try:
       arcpy.DeleteField_management("zf1.shp", 'bl')
       arcpy.AddField_management("zf1.shp", 'bl', "FLOAT")
    except:
        arcpy.AddField_management("zf1.shp", 'bl', "FLOAT")
    cursor1 = arcpy.UpdateCursor("zf1.shp")
    i = 0
    for my_row in cursor1:
        my_row.setValue('bl', kj[i])
        cursor1.updateRow(my_row)
        i += 1
    del cursor1,my_row
    chazhi("jy1.shp", "bl", "jykrigph.tif",CC)
    chazhi("zf1.shp", "bl", "zfkrigph.tif",CC)
    out = arcpy.sa.Raster( "zfkrigph.tif") / arcpy.sa.Raster("jykrigph.tif")
    out.save(ganhan)
    outReclass = arcpy.sa.Reclassify(ganhan, "Value", arcpy.sa.RemapRange([[-1000,float(VAR_GH1),1],[float(VAR_GH1),float(VAR_GH2),2],[float(VAR_GH2),float(VAR_GH3),3],
                                     [float(VAR_GH3),float(VAR_GH4),4],[float(VAR_GH4),150000,5]]))
    outReclass.save("jg.tif") 
    arcpy.Delete_management(outputjy)
    arcpy.Delete_management(outputzf)
    arcpy.Delete_management("jy.shp")
    arcpy.Delete_management("jy1.shp")
    arcpy.Delete_management("jykrigph.tif")
    arcpy.Delete_management( "zf.shp")
    arcpy.Delete_management("zf1.shp")
    arcpy.Delete_management("zfkrigph.tif")
    arcpy.Delete_management(ganhan)
elif int(VAR_A) ==0 :
     outReclass = arcpy.sa.Reclassify(IN_YS, "Value", arcpy.sa.RemapRange([[-300000,float(VAR_YS4),5],[float(VAR_YS4),float(VAR_YS3),4],[float(VAR_YS3),float(VAR_YS2),3],
                                     [float(VAR_YS2),float(VAR_YS1),2],[float(VAR_YS1),30000000,1]]))
     outReclass.save("jg.tif") 
arcpy.Clip_management("jg.tif","",OUTPUTPATH+OUTPUTNAME+'.tif',IN_CLIP,"", "ClippingGeometry")


###############################
arcpy.BuildRasterAttributeTable_management(OUTPUTPATH+OUTPUTNAME+".tif", "Overwrite")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", "STRING", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj", "DOUBLE", "", "", "")
arcpy.AddField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl", "DOUBLE", "", "", "")
expression = "getClass(!VALUE!)"
codeblock = """def getClass(a):
    if a == 1:
        return u"好"
    elif a == 2:
        return u"较好"
    elif a == 3:
        return u"一般"
    elif a == 4:
        return u"较差"
    else:
        return u'差'"""
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl",FBLL , "PYTHON_9.3")
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "dengji", expression, "PYTHON_9.3", 
                                codeblock)
arcpy.CalculateField_management(OUTPUTPATH+OUTPUTNAME+".tif", "mj","(!fbl!)*(!COUNT!)" , "PYTHON_9.3")
arcpy.DeleteField_management(OUTPUTPATH+OUTPUTNAME+".tif", "fbl")
arcpy.Delete_management("jg.tif")
if os.path.exists(in_zf_csv)==True:
    os.remove(in_zf_csv)
if os.path.exists(in_jy_csv)==True:
    os.remove(in_jy_csv)
##############################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
    StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_nong_cheng_shui_5J.clr")
###########################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")


    