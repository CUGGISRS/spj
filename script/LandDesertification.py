# -*- coding: utf-8 -*-
from __future__ import division
import arcpy
import sys
from arcpy import env
from arcpy.sa import *
import pandas as pd
import os
import StaticticsByXZQ
import RasterTableToTxtAndExcel
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
#####################################
PATH= sys.argv[1]#PATH="D:\\test\\data\\st_tdsh\\"
IN_TR= sys.argv[2]#IN_TR="TRLX2.shp"#土壤文件 获取土壤质地 输入数据
IN_XZZB=sys.argv[3]
IN_NIR= sys.argv[4]#IN_NIR='NIR20.tif'#植被覆盖度近红外波段
IN_RED= sys.argv[5]#IN_RED='RED20.tif'#植被覆盖度可见光红波段
IN_NDVI=sys.argv[6]
IN_FS= sys.argv[7]#FS="ave_fengsu.txt"  #风速txt文件
IN_QW= sys.argv[8]#QW="pingjun_qiwen.txt"  #平均气温txt文件
IN_JY= sys.argv[9]#JY="jiangyu.txt"      #降雨txt文件
IN_CLIP= sys.argv[10]#IN_CLIP="clipper.shp"#裁剪 输入数据
VAR_GEO= sys.argv[11]#VAR_GEO="1" #0/1
VAR_FBL= sys.argv[12]#VAR_FBL="200" #分辨率
VAR_FS= sys.argv[13]#VAR_FS="6"#大于这个值时被判定为起沙风
VAR_GZ_FL5= sys.argv[14]#VAR_GZ_FL5="1.5"   #干燥度指数分级
VAR_GZ_FL1= sys.argv[15]#VAR_GZ_FL1="16"
VAR_FS_FL5= sys.argv[16]#VAR_FS_FL5="10"   #起沙风天数分级
VAR_FS_FL1= sys.argv[17]#VAR_FS_FL1="30"
VAR_ZB_FL5= sys.argv[18]#VAR_ZB_FL5="0.2"   #植被覆盖度分级
VAR_ZB_FL1= sys.argv[19]#VAR_ZB_FL1="0.6"
VAR_MG_FL5= sys.argv[20]#VAR_MG_FL5="2.33"   #最后的敏感性分级
VAR_MG_FL1= sys.argv[21]#VAR_MG_FL1="3.66"
IN_XZQQ=sys.argv[22]
OUTPUTPATH = sys.argv[23]
OUTPUTNAME= sys.argv[24]#OUTPUTNAME="tudishahu"  #输出文件
#####################################
#PATH="E:\\spj\\data\\st_tdsh\\"
#IN_TR="99999"#土壤文件 获取土壤质地 输入数据TRLX2.shp
#IN_XZZB="0"
#IN_NIR='NIR20.tif'#植被覆盖度近红外波段
#IN_RED='RED20.tif'#植被覆盖度可见光红波段
#IN_NDVI=""
#IN_FS=PATH+"ave_fengsu.xls"  #风速txt文件PATH+"ave_fengsu.xls"
#IN_QW=PATH+"pingjun_qiwen.xls"  #平均气温txt文件PATH+"pingjun_qiwen.txt"
#IN_JY=PATH+"jiangyu.xls"      #降雨txt文件PATH+"jiangyu.txt"
#IN_CLIP="clipper.shp"#裁剪 输入数据
#VAR_GEO="1" #0/1
#VAR_FBL="200" #分辨率
#VAR_FS="6"#大于这个值时被判定为起沙风
#VAR_GZ_FL5="1.5"   #干燥度指数分级
#VAR_GZ_FL1="16"
#VAR_FS_FL5="10"   #起沙风天数分级
#VAR_FS_FL1="30"
#VAR_ZB_FL5="0.2"   #植被覆盖度分级
#VAR_ZB_FL1="0.6"
#VAR_MG_FL5="2.33"   #最后的敏感性分级
#VAR_MG_FL1="3.66"
#IN_XZQQ="XZQ_WGS84.shp"
#OUTPUTPATH = "D:\\map\\"
#OUTPUTNAME= "st_tudishahua"  #输出文件
#####################################
env.workspace=PATH[:-1]
MIFS="fengsu.shp"
MIJY='jiangyu.shp'
MIQW="qiwen.shp"
in_fs_csv = PATH+"ave_fengsu.csv"
in_qw_csv = PATH+"pingjun_qiwen.csv"
in_jy_csv = PATH+"jiangyu.csv"
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
###########################
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
######################################

##植被覆盖度
if int(IN_XZZB)==0:
    try:
    	arcpy.Delete_management( 'nir.tif')
    	arcpy.Float_3d(IN_NIR,'nir.tif')  
    except:  
    	arcpy.Float_3d(IN_NIR,'nir.tif')
    try:
    	arcpy.Delete_management('red.tif')
    	arcpy.Float_3d(IN_RED,'red.tif')  
    except:  
    	arcpy.Float_3d(IN_RED,'red.tif')
    NIR=arcpy.Raster('nir.tif')
    RED=arcpy.Raster('red.tif')
    ndvi=(NIR-RED)/(NIR+RED)
    ndvi.save("ndvi.tif")
    outReclass = arcpy.sa.Reclassify("ndvi.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_ZB_FL5),5],[float(VAR_ZB_FL5),float(VAR_ZB_FL1),3],[float(VAR_ZB_FL1),1,1]]),'NODATA')    
    outReclass.save("ndvire.tif")
else:
    outReclass = arcpy.sa.Reclassify(IN_NDVI, "Value", arcpy.sa.RemapRange([[0,float(VAR_ZB_FL5),5],[float(VAR_ZB_FL5),float(VAR_ZB_FL1),3],[float(VAR_ZB_FL1),1,1]]),'NODATA')    
    outReclass.save("ndvire.tif")
arcpy.Clip_management("ndvire.tif","","ndvifinal.tif",IN_CLIP,"", "ClippingGeometry") 
exp=Con(IsNull("ndvifinal.tif"),0,"ndvifinal.tif")
exp.save("ndvif2.tif")
######################################
###干壤质地
if IN_TR=="99999":
     create_raster(5,IN_CLIP,VAR_FBL,"trcjfinal.tif")
else:
    trzd=[]
    cursor = arcpy.da.SearchCursor(IN_TR, ["TRZD"])
    for row in cursor:
    	 if row[0]==unicode("基岩", "utf-8") or row[0]==unicode("粘质", "utf-8"):
    		 trzd.append(1)
    	 elif row[0]==unicode("砾质", "utf-8") or row[0]==unicode("壤质", "utf-8"):
    		 trzd.append(3)
    	 elif row[0]==unicode("沙质", "utf-8"):
    		 trzd.append(5)
    	 else:
    		 trzd.append(0)
    del cursor,row
    #print trzd
    try:
    	arcpy.DeleteField_management(IN_TR, 'trfj')
    	arcpy.AddField_management(IN_TR, 'trfj', "SHORT") 
    except:  
    	arcpy.AddField_management(IN_TR, 'trfj', "SHORT")
    cursor1 = arcpy.UpdateCursor(IN_TR)
    i = 0
    for my_row in cursor1:
    	my_row.setValue('trfj', trzd[i])
    	cursor1.updateRow(my_row)
    	i += 1
    del cursor1,my_row  
    arcpy.FeatureToRaster_conversion(IN_TR,'trfj','trcj.tif',VAR_FBL) 
    arcpy.Clip_management('trcj.tif',"","trcjfinal.tif",IN_CLIP,"", "ClippingGeometry") 
#####################################
#干燥度指数因子
if IN_FS=="99999":
    create_raster(5,IN_CLIP,VAR_FBL,"fsfinal.tif")
else:
    if IN_FS.endswith(".txt") or IN_FS.endswith(".csv"):
        pass
    if IN_FS.endswith(".xls") or IN_FS.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_FS,in_fs_csv)
                    IN_FS = in_fs_csv
    try:
    	arcpy.Delete_management(MIFS)
    	createFC = arcpy.CreateFeatureclass_management(env.workspace, MIFS ,"POINT", "", "", "")  
    except:       
    	createFC = arcpy.CreateFeatureclass_management(env.workspace, MIFS ,"POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MIFS, "fengsu", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIFS, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIFS,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIFS,  "lat", "FLOAT" )
    iflds = ["YEAR","fengsu", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIFS, iflds)
    count = 1
    for ln in open(IN_FS, 'r').readlines():
    		   lnstrip = ln.strip()
    		   if count > 1:
    			   dataList = ln.split(",")
    			   y=dataList[4]
    			   f=dataList[7]
    			   lat = dataList[2]
    			   lon = dataList[1]
    			   ivals = [y,f, float(lon), float(lat),(float(lon), float(lat))]
    			   iCur.insertRow(ivals)
    		   count += 1
    print('Finish Projection:',MIFS)
    del iCur
    cursor = arcpy.da.SearchCursor(MIFS, ["fengsu"])
    fs=[]
    for row in cursor:
    	if row[0]/10>int(VAR_FS):
    		fs.append(1)
    	else:
    		fs.append(0)
    try:
    	arcpy.DeleteField_management(MIFS, 'fs')
    	arcpy.AddField_management(MIFS, 'fs', "FLOAT") 
    except:  
    	arcpy.AddField_management(MIFS, 'fs', "FLOAT")
    cursor1 = arcpy.UpdateCursor(MIFS)
    i = 0
    for my_row in cursor1:
    	my_row.setValue('fs', fs[i])
    	cursor1.updateRow(my_row)
    	i += 1
    del my_row,cursor1
    arcpy.Dissolve_management(MIFS, "disfengsu.shp", ["lon","lat"],[['fs','SUM']])
    chazhi("disfengsu.shp", "SUM_fs", "fskrigph.tif",CC)
    W= arcpy.sa.Reclassify("fskrigph.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_FS_FL5),1],[float(VAR_FS_FL5),float(VAR_FS_FL5),3],[float(VAR_FS_FL5),10000,5]]),'NODATA')  
    W.save("fengsu.tif")
    arcpy.Clip_management("fengsu.tif","","fsfinal.tif",IN_CLIP,"", "ClippingGeometry")



if IN_QW=="99999" or IN_JY=="99999":
    create_raster(5,IN_CLIP,VAR_FBL,"ganzaofinal.tif")
else:
    if IN_QW.endswith(".txt") or IN_QW.endswith(".csv"):
        pass
    if IN_QW.endswith(".xls") or IN_QW.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_QW,in_qw_csv)
                    IN_QW = in_qw_csv
    try:
    	arcpy.Delete_management(MIQW )
    	createFC = arcpy.CreateFeatureclass_management(env.workspace,MIQW  ,"POINT", "", "", "")  
    except:       
    	createFC = arcpy.CreateFeatureclass_management(env.workspace, MIQW ,"POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MIQW, "qiwen", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIQW, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIQW,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIQW,  "lat", "FLOAT" )
    iflds = ["YEAR","qiwen", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIQW, iflds)
    count = 1
    for ln in open(IN_QW, 'r').readlines():
    		   lnstrip = ln.strip()
    		   if count > 1:
    			   dataList = ln.split(",")
    			   y=dataList[4]
    			   f=dataList[7]
    			   lat = dataList[2]
    			   lon = dataList[1]
    			   ivals = [y,f, float(lon), float(lat),(float(lon), float(lat))]
    			   iCur.insertRow(ivals)
    		   count += 1
    print('Finish Projection:',MIQW)
    del iCur
    if IN_JY.endswith(".txt") or IN_JY.endswith(".csv"):
        pass
    if IN_JY.endswith(".xls") or IN_JY.endswith(".xlsx"):
        if __name__ == '__main__':
                    xlsx_to_csv_pd(IN_JY,in_jy_csv)
                    IN_JY = in_jy_csv
    try:
    	arcpy.Delete_management( MIJY )
    	createFC = arcpy.CreateFeatureclass_management(env.workspace, MIJY  ,"POINT", "", "", "")  
    except:       
    	createFC = arcpy.CreateFeatureclass_management(env.workspace,  MIJY ,"POINT", "", "", "")
    arcpy.AddField_management(env.workspace + "/" + MIJY, "jiangshui", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIJY, "YEAR", "SHORT" )
    arcpy.AddField_management(env.workspace + "/" + MIJY,  "lon", "FLOAT" )
    arcpy.AddField_management(env.workspace + "/" + MIJY,  "lat", "FLOAT" )
    iflds = ["YEAR","jiangshui", "lon","lat", "SHAPE@XY"]
    iCur = arcpy.da.InsertCursor(env.workspace + "/" + MIJY, iflds)
    count = 1
    for ln in open(IN_JY, 'r').readlines():
    		   lnstrip = ln.strip()
    		   if count > 1:
    			   dataList = ln.split(",")
    			   y=dataList[4]
    			   f=dataList[7]
    			   lat = dataList[2]
    			   lon = dataList[1]
    			   ivals = [y,f, float(lon), float(lat),(float(lon), float(lat))]
    			   iCur.insertRow(ivals)
    		   count += 1
    print('Finish Projection:',MIJY)
    del iCur
    
    
    cursor = arcpy.da.SearchCursor(MIQW, ["qiwen"])
    qw=[]
    for row in cursor:
    	if row[0]/10>=10:
    		qw.append(row[0]/10)
    	else:
    		qw.append(0)
    cursor = arcpy.da.SearchCursor(MIJY, ["jiangshui"])
    js=[]
    for row in cursor:
    	if row[0]/10>=10:
    		js.append(row[0]/10)
    	else:
    		js.append(0)
    #print len(qw),len(js)
    del cursor,row
    try:
    	arcpy.DeleteField_management(MIQW, 'qw')
    	arcpy.AddField_management(MIQW, 'qw', "FLOAT") 
    except:  
    	arcpy.AddField_management(MIQW, 'qw', "FLOAT")
    try:
    	arcpy.DeleteField_management(MIJY, 'js')
    	arcpy.AddField_management(MIJY, 'js', "FLOAT") 
    except:  
    	arcpy.AddField_management(MIJY, 'js', "FLOAT")
    
    cursor1 = arcpy.UpdateCursor(MIQW)
    i = 0
    for my_row in cursor1:
    	my_row.setValue('qw', qw[i])
    	cursor1.updateRow(my_row)
    	i += 1
    del my_row,cursor1
    cursor1 = arcpy.UpdateCursor(MIJY)
    i = 0
    for my_row in cursor1:
    	my_row.setValue('js', js[i])
    	cursor1.updateRow(my_row)
    	i += 1
    del my_row,cursor1
    
    arcpy.Dissolve_management(MIQW, "disqiwen.shp", ["lon","lat"],[['qw','SUM']])
    arcpy.Dissolve_management(MIJY, "disjiangyu.shp", ["lon","lat"],[['js','SUM']])
    
    arcpy.Intersect_analysis (["disqiwen.shp","disjiangyu.shp"],"ganzao.shp" )
    cursor = arcpy.da.SearchCursor( "ganzao.shp", ["SUM_qw","SUM_js"])
    gz=[]
    for row in cursor:
    	gz.append(row[0]/row[1]*0.16)
    #print gz
    del row,cursor
    try:
    	arcpy.DeleteField_management("ganzao.shp", 'gz')
    	arcpy.AddField_management("ganzao.shp", 'gz', "FLOAT")
    except:  
    	arcpy.AddField_management("ganzao.shp", 'gz', "FLOAT")
    cursor1 = arcpy.UpdateCursor("ganzao.shp")
    i = 0
    for my_row in cursor1:
    	my_row.setValue('gz', gz[i])
    	cursor1.updateRow(my_row)
    	i += 1
    del my_row,cursor1
    chazhi("ganzao.shp", "gz", "gzkrigph.tif",CC)
    
    I= arcpy.sa.Reclassify("gzkrigph.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_GZ_FL5),1],[float(VAR_GZ_FL5),float(VAR_GZ_FL1),3],[float(VAR_GZ_FL1),10000,5]]),'NODATA')  
    I.save("ganzao1.tif")

    arcpy.Clip_management("ganzao1.tif","","ganzaofinal.tif",IN_CLIP,"", "ClippingGeometry")

##################################################################
lll=arcpy.Raster("ganzaofinal.tif")*arcpy.Raster("fsfinal.tif")*arcpy.Raster("trcjfinal.tif")*arcpy.Raster("ndvif2.tif")
lll.save("u.tif")
D=pow(arcpy.Raster("u.tif"),1.0/4)
D.save("jg.tif")
outReclass = arcpy.sa.Reclassify("jg.tif", "Value", arcpy.sa.RemapRange([[0,float(VAR_MG_FL5),1],[float(VAR_MG_FL5),float(VAR_MG_FL1),3],[float(VAR_MG_FL1),5,5]]))    
outReclass.save(OUTPUTPATH+OUTPUTNAME+".tif")
##########################################
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
arcpy.Delete_management('nir2.tif')
arcpy.Delete_management('red2.tif')
arcpy.Delete_management("ndvi.tif")
arcpy.Delete_management("ndvifinal.tif")
arcpy.Delete_management("ndvire.tif")
arcpy.Delete_management("ndvif2.tif")
arcpy.Delete_management('trcj.tif')
arcpy.Delete_management("trcjfinal.tif")
arcpy.Delete_management(MIFS)
arcpy.Delete_management(MIJY)
arcpy.Delete_management(MIQW)
arcpy.Delete_management("ganzao.shp")
arcpy.Delete_management("disqiwen.shp")
arcpy.Delete_management("disjiangyu.shp")
arcpy.Delete_management("disfengsu.shp")
arcpy.Delete_management("gzkrigph.tif")
arcpy.Delete_management("fskrigph.tif")
arcpy.Delete_management("ganzao1.tif")
arcpy.Delete_management("fengsu.tif")
arcpy.Delete_management("ganzaofinal.tif")
arcpy.Delete_management("fsfinal.tif")
arcpy.Delete_management("u.tif")
arcpy.Delete_management("jg.tif")
if os.path.exists(in_fs_csv) == True:
    os.remove(in_fs_csv)
if os.path.exists(in_qw_csv) == True:
    os.remove(in_qw_csv)
if os.path.exists(in_jy_csv) ==True:
    os.remove(in_jy_csv)
###################################################################
RasterTableToTxtAndExcel.write2excel(OUTPUTPATH+OUTPUTNAME+".tif", OUTPUTPATH, OUTPUTNAME)
if IN_XZQQ!="99999":
      StaticticsByXZQ.StatisticBYXZQ(OUTPUTPATH+OUTPUTNAME+".tif", IN_XZQQ, OUTPUTPATH, OUTPUTNAME+"_XZQ")
arcpy.AddColormap_management(OUTPUTPATH+OUTPUTNAME+".tif", "#", "C:/yz_spj/clr/Month4_mingan_3J.clr")
#arcpy.ApplySymbologyFromLayer_management(fin, "F:\\1clr\\Month4_mingan_3J.lyr")
############################
arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("Spatial")
