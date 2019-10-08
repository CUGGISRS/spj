# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 14:11:05 2019

@author: yuanz
"""
from __future__ import division
import arcpy
import sys
from arcpy import env
from arcpy.sa import *
import xlwt
import os
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
########################
PATH=sys.argv[1]#PATH="D:\\test\\data\\cz_agri_w\\"
VAR_ZB=sys.argv[2]#VAR_ZB="1"  #农业用水合理占比
VAR_GGDE=sys.argv[3]#VAR_GGDE="1"  #综合灌溉定额 
VAR_YSZL=sys.argv[4]#VAR_YSZL="1"   #用水总量控制指标
VAR_JYMJ=sys.argv[5]#VAR_JYMJ="1" #单纯以天然降水为水源的农业面积
VAR_GGBHL=sys.argv[6]#VAR_GGBHL="1" #不合理农业灌溉水量
OUTPUTPATH=sys.argv[7]
OUTPUTNAME=sys.argv[8]#VAR_TXT='test'
########################
#PATH="E:\\spj\\data\\cz_agri_w\\"
#VAR_ZB="1"  #农业用水合理占比
#VAR_GGDE="1"  #综合灌溉定额 
#VAR_YSZL="1"   #用水总量控制指标
#VAR_JYMJ="1" #单纯以天然降水为水源的农业面积
#VAR_GGBHL="1" #不合理农业灌溉水量
#OUTPUTPATH="D:\\map\\"
#OUTPUTNAME='test'
########################
env.workspace=PATH[:-1]
#######################
gg=float(VAR_ZB)*float(VAR_YSZL)/float(VAR_GGDE)+float(VAR_JYMJ)
bhl=float(VAR_GGBHL)/float(VAR_GGDE)
f = xlwt.Workbook()
sheet1 = f.add_sheet("Statistics", cell_overwrite_ok=True)
sheet1.write(0,0, u'可承载耕地面积')
sheet1.write(0,1, u'现状不合理灌溉耕地面积')
sheet1.write(1,0, gg)
sheet1.write(1,1, bhl)
f.save(OUTPUTPATH+OUTPUTNAME + ".xls")
#######################
arcpy.CheckInExtension("Spatial")
arcpy.CheckInExtension("3D")
