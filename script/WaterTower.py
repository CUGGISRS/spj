# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 14:17:34 2019

@author: yuanz
"""

from __future__ import division
import arcpy
import sys
import xlwt
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True
########################
PATH=sys.argv[1]#PATH="D:\\test\\data\\cz_town_w\\"
VAR_XSL=sys.argv[2]#VAR_XSL="21683"  #人均需水量
VAR_ZB=sys.argv[3]#VAR_ZB="0.339"   #生活和工业用水合理占比
VAR_KZ=sys.argv[4]#VAR_KZ="179100000000"    #评价区域用水总量控制指标
VAR_JSYD=sys.argv[5]#VAR_JSYD="80"  #人均城镇建设用地
OUTPUTPATH=sys.argv[6]
OUTPUTNAME=sys.argv[7]#VAR_TXT='test'
########################
#PATH="E:\\spj\\data\\cz_town_w\\"
#VAR_XSL="21683"  #人均需水量
#VAR_ZB="0.339"   #生活和工业用水合理占比
#VAR_KZ="179100000000"    #评价区域用水总量控制指标
#VAR_JSYD="80"  #人均城镇建设用地
#OUTPUTPATH="D:\\map\\"
#OUTPUTNAME='test'
######################
env.workspace=PATH[:-1]
#######################
area=float(VAR_ZB)*float(VAR_KZ)/float(VAR_XSL)*float(VAR_JSYD)
f = xlwt.Workbook()
sheet1 = f.add_sheet("Statistics", cell_overwrite_ok=True)
sheet1.write(0,0, u'水资源约束条件下城镇建设用地规模')
sheet1.write(1,0, area)
f.save(OUTPUTPATH+OUTPUTNAME + ".xls")
####################
arcpy.CheckInExtension("Spatial")
arcpy.CheckInExtension("3D")
