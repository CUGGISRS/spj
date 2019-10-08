# -*- coding: utf-8 -*-

import arcpy
import os
import PieChart
"""
输入内容为：1、输入数据(矢量、栅格都可以)；2、行政区数据(shp);3、输出路径；4、输出名称；
5、字段名(当1为矢量数据时可选)---格式：
1）、一个字段："FieldName"
2）、多个字段：["FieldName1", "FieldName2", "FieldName3", .....]

输出数据格式为：shp、EXCEL
"""

arcpy.env.overwriteOutput = True
try:
    os.makedirs("C:/yz_spj/temp/excel2txt")
except:
    pass

def StatisticBYXZQ(inputData, inputXZQ, outpath, outname, shpFields = ""):
    arcpy.env.workspace = outpath
    print arcpy.env.workspace
    rastoshp = os.path.join(outpath, "ras2shp.shp")
    intershp = os.path.join(outpath, "inter.shp")
    dissoshp = os.path.join(outpath, outname + ".shp")

    if os.path.exists(rastoshp):
        try:
            arcpy.Delete_management(rastoshp)
        except:
            pass
    elif os.path.exists(intershp):
        try:
            arcpy.Delete_management(intershp)
        except:
            pass
    elif os.path.exists(dissoshp):
        try:
            arcpy.Delete_management(dissoshp)
        except:
            pass

    desc1 = arcpy.Describe(inputData)

    if desc1.dataType == "RasterDataset":
        pras2shp = arcpy.RasterToPolygon_conversion(inputData, rastoshp, "NO_SIMPLIFY", "VALUE")
        inter = arcpy.Intersect_analysis([pras2shp, inputXZQ], intershp)
        shpDisso = arcpy.Dissolve_management(inter, dissoshp, ["XZQNAME", "GRIDCODE"])
        result = arcpy.AddField_management(shpDisso, "mj_sta", "DOUBLE")
        spa = arcpy.Describe(inputXZQ).spatialReference
        arcpy.DefineProjection_management(dissoshp, spa)
        result1 = arcpy.CalculateField_management(result, "mj_sta", "!shape.area!", "PYTHON_9.3")
        excel = arcpy.TableToExcel_conversion(result1, os.path.join(outpath, outname) + ".xls")

    elif desc1.dataType == "ShapeFile" or "FeatureClass":
        if shpFields == "":
            disField = ["XZQNAME"]
        else:
            disField = ["XZQNAME"]
            for i in shpFields:
                disField.append(i)
            #     print disField
            # print disField
        inter = arcpy.Intersect_analysis([inputData, inputXZQ], intershp)
        shpDisso = arcpy.Dissolve_management(inter, dissoshp, disField)
        result = arcpy.AddField_management(shpDisso, "mj_sta", "DOUBLE")
        spa = arcpy.Describe(inputXZQ).spatialReference
        arcpy.DefineProjection_management(dissoshp, spa)
        result1 = arcpy.CalculateField_management(result, "mj_sta", "!shape.area!", "PYTHON_9.3")
        excel = arcpy.TableToExcel_conversion(result1, os.path.join(outpath, outname + "_WithOutChart" + ".xls"))
    try:
        arcpy.Delete_management(rastoshp)
        arcpy.Delete_management(intershp)
    except:
        pass
    PieChart.xls2xlsxWithPieChart(result1, outpath, outname)

# 测试区域

# IN_raster = arcpy.Raster("D:/1/raster1.tif")
# # IN_xzq = "D:/1/XZQ2.shp"
# outpaths = "D:/1/11"
# outname = "kaer888"
# IN_xzq = "D:/1/22/Copy_0.shp"
# # fields = ['Input_FID', 'aa', "qqq"]
# IN_raster = "D:/1/44/ggggggggg.tif"
# IN_xzq = "D:/1/44/XZQ_WGS84.shp"
# IN_raster = "D:/1/44/ggggggggg_UTM48N.tif"
# IN_xzq = "D:/1/44/XZQ_WGS84_UTM48N.shp"
#
# outpaths = "D:/1/22"
# outname ="kaer55"
#
#
# StatisticBYXZQ(IN_raster, IN_xzq, outpaths, outname)


