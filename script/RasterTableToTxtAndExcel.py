# -*- coding: utf-8 -*-

import arcpy
import xlwt
import os

list1 = [u"栅格单元值", u"等级", u"面积"]
def write2txt(inraster, txtpath, txtname):
    # 1、inraster必须是带路径的形式，如 "F:/1/raster.tif"
    # 2、字段识别'Value', 'dengji', 'mj'
    #写入txt
    with open(os.path.join(txtpath,txtname + ".txt"), "w") as f:
        f.writelines("栅格单元值,等级,面积\n")
    with arcpy.da.SearchCursor(inraster,['Value', 'dengji', 'mj']) as cur:
        with open(os.path.join(txtpath,txtname + ".txt"), "a") as f1:
            for row in cur:
                pValue = row[0]
                pDengji = row[1]
                pDengji2 = pDengji.encode("utf-8")
                pMj = row[2]
                f1.writelines(str(pValue) + "," + pDengji2 + "," + str(pMj) + "\n")



#写入excel
def write2excel(inraster, excelpath, excelname):
    excel1 = xlwt.Workbook()
    excel1_sheet1 = excel1.add_sheet("Statistics", cell_overwrite_ok=True)
    pi = 1
    pj = 0
    for i in range(3):
        excel1_sheet1.write(0,i, list1[i])
    with arcpy.da.SearchCursor(inraster,['Value', 'dengji', 'mj']) as cur:
        for row in cur:
            pValue = row[0]
            pDengji = row[1]
            pMj = row[2]
            list2 = [str(pValue), pDengji, pMj]
            for n in range(3):
                excel1_sheet1.write(pi, pj, list2[n])
                pj += 1
            pj = 0
            pi += 1

    excel1.save(os.path.join(excelpath, excelname + ".xls"))



#write2txt("F:/1/test.tif", "F:/1", "testtext")
#write2excel("F:/1/test.tif", "F:/1", "testexcel")