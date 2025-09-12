# @Author  : ChaoQiezi
# @Time    : 2025/9/3 下午4:06
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: glass_process

"""
This script is used to 对MOD17A3 GPP数据集进行预处理

包括: HDF4转tiff、镶嵌、裁剪、掩膜
"""

import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from glob import glob
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

import re
from math import ceil, floor
from osgeo import gdal, osr
import os
import numpy as np
from typing import Union
from pyhdf.SD import SD


def img_mosaic(mosaic_paths: list, mosaic_ds_name: str, return_all: bool = True, img_nodata: Union[int, float] = np.nan,
               img_type: Union[np.int32, np.float32, None] = np.float32, unit_conversion: bool = False,
               scale_factor_op: str = 'multiply', mosaic_mode: str = 'last'):
    """
    该函数用于对列表中的所有HDF4文件进行镶嵌
    :param mosaic_paths: 多个HDF4文件路径组成的字符串列表
    :param mosaic_ds_name: 待镶嵌的数据集名称
    :param return_all: 是否一同返回仿射变换、镶嵌数据集的坐标系等参数
    :param img_nodata: 影像中的无效值设置
    :param img_type: 待镶嵌影像的数据类型
    :param unit_conversion: 是否进行单位换算
    :param scale_factor_op: 比例因子的运算符, 默认是乘以(可选: multiply, divide), 该参数尽在unit_conversion为True时生效
    :param mosaic_mode: 镶嵌模式, 默认是Last(即如果有存在像元重叠, mosaic_paths中靠后影像的像元将覆盖其),
        可选: last, mean, max, min, 镶嵌策略默认是last模式,
    :return: 默认返回镶嵌好的数据集
    """

    # 获取镶嵌范围
    x_mins, x_maxs, y_mins, y_maxs = [], [], [], []
    for mosaic_path in mosaic_paths:
        hdf = SD(mosaic_path)  # 默认只读
        # 获取元数据
        metadata = hdf.attributes()['StructMetadata.0']
        # 获取角点信息
        ul_pt = [float(x) for x in re.search(r'UpperLeftPointMtrs=\((.*?)\)', metadata).group(1).split(',')]
        lr_pt = [float(x) for x in re.search(r'LowerRightMtrs=\((.*?)\)', metadata).group(1).split(',')]
        x_mins.append(ul_pt[0])
        x_maxs.append(lr_pt[0])
        y_mins.append(lr_pt[1])
        y_maxs.append(ul_pt[1])
    else:
        # 计算分辨率
        col = int(re.search(r'XDim=(.*?)\n', metadata).group(1))
        row = int(re.search(r'YDim=(.*?)\n', metadata).group(1))
        x_res = (lr_pt[0] - ul_pt[0]) / col
        y_res = (ul_pt[1] - lr_pt[1]) / row
        # 如果img_type没有指定, 那么数据类型默认为与输入相同
        if img_type is None:
            img_type = hdf.select(mosaic_ds_name)[:].dtype
        # 获取数据集的坐标系参数并转化为proj4字符串格式
        projection_param = [float(_param) for _param in re.findall(r'ProjParams=\((.*?)\)', metadata)[0].split(',')]
        """
        Sinusoidal Equal Area (INSYS = 16): TPARIN( 1 ) and TPARIN( 6:8 ) used.
            1. Radius of sphere of reference
            2. (unused)
            3. (unused)
            4. (unused)
            5. Longitude of central meridian
            6. Latitude of central meridian
            7. False easting in the same units as the semimajor axis
            8. False northing in the same units as the semimajor axis
            9. (unused)...
        """
        mosaic_img_proj4 = "+proj={} +R={:0.4f} +lon_0={:0.4f} +lat_0={:0.4f} +x_0={:0.4f} " \
                           "+y_0={:0.4f} +units=m +no_defs".format('sinu', projection_param[0], projection_param[4],
                                                                   projection_param[5], projection_param[6],
                                                                   projection_param[7])
        """
        proj4语法:
        +proj=, 坐标系(可填: latlong, sinu等)
        +R=, 参考椭球体的半径<如果椭球体的长半轴和短半轴不一样, 可以分别设置即: +a=, +b=>
        +lon_0=, 中央经线的经度
        +lat_0=, 中央纬线的维度
        +x_0=, 投影坐标系原点的东西偏移(东为正)
        +y_0=, 投影坐标系原点的南北偏移(北为正)
        +units=, 坐标系单位(可填: m, deg等)
        +no_defs, 禁止加载默认参数, 避免冲突
        """
        # 关闭文件, 释放资源
        hdf.end()
    x_min, x_max, y_min, y_max = min(x_mins), max(x_maxs), min(y_mins), max(y_maxs)

    # 镶嵌
    col = ceil((x_max - x_min) / x_res)
    row = ceil((y_max - y_min) / y_res)
    sum_array = np.zeros((row, col), dtype=np.float32)
    count_array = np.zeros((row, col), dtype=np.int16)
    for ix, mosaic_path in enumerate(mosaic_paths):
        hdf = SD(mosaic_path)
        target_ds = hdf.select(mosaic_ds_name)

        # 读取数据集和预处理
        target = np.ma.array(target_ds.get())
        valid_range = target_ds.attributes()['valid_range']
        target.mask = (target < valid_range[0]) | (target > valid_range[1])

        if unit_conversion:
            scale_factor = target_ds.attributes()['scale_factor']
            add_offset = target_ds.attributes()['add_offset']
            if scale_factor_op == 'multiply':
                target = target * scale_factor + add_offset
            elif scale_factor_op == 'divide':
                target = target / scale_factor + add_offset

        # 计算当前瓦片在总图中的位置
        start_row = floor((y_max - (y_maxs[ix] - y_res / 2)) / y_res)
        start_col = floor(((x_mins[ix] + x_res / 2) - x_min) / x_res)
        end_row = start_row + target.shape[0]
        end_col = start_col + target.shape[1]

        # 定义目标区域的切片
        roi_slice = (slice(start_row, end_row), slice(start_col, end_col))

        # 仅对有效值进行累加和计数
        sum_array[roi_slice] += np.ma.filled(target, 0)
        count_array[roi_slice] += ~target.mask

        # 释放资源
        target_ds.endaccess()
        hdf.end()

    mask_where = count_array == 0
    count_array[mask_where] = 1  # 避免被除数为0的错误
    mosaic_img = sum_array / count_array
    mosaic_img = np.ma.masked_where(mask_where, mosaic_img)

    if return_all:
        extrent_geo = [  # 地理覆盖范围(四个角点, 左上角点顺时针开始)
            [x_min, x_max, x_max, x_min],
            [y_max, y_max, y_min, y_min]
        ]
        return mosaic_img, [x_min, x_res, 0, y_max, 0, -y_res], mosaic_img_proj4, extrent_geo

    return mosaic_img


def img_warp(src_img: np.ndarray, out_path: str, transform: list, src_proj4: str, out_res: Union[float, None] = None,
             nodata_value: Union[int, float] = np.nan, resample: str = 'bilinear', dst_epsg=4326) -> None:
    """
    该函数用于对正弦投影下的栅格矩阵进行重投影(GLT校正), 得到WGS84坐标系下的栅格矩阵并输出为TIFF文件
    :param src_img: 待重投影的栅格矩阵
    :param out_path: 输出路径
    :param transform: 仿射变换参数([x_min, x_res, 0, y_max, 0, -y_res], 旋转参数为0是常规选项)
    :param out_res: 输出的分辨率(栅格方形)
    :param nodata_value: 设置为NoData的数值
    :param out_type: 输出的数据类型
    :param resample: 重采样方法(默认是最近邻, ['nearest', 'bilinear', 'cubic'])
    :param src_proj4: 表达源数据集(src_img)的坐标系参数(以proj4字符串形式)
    :return: None
    """

    # 输出数据类型
    if np.issubdtype(src_img.dtype, np.integer):
        out_type = gdal.GDT_Int32
    elif np.issubdtype(src_img.dtype, np.floating):
        out_type = gdal.GDT_Float32
    else:
        raise ValueError("当前待校正数组类型为不支持的数据类型")
    resamples = {'nearest': gdal.GRA_NearestNeighbour, 'bilinear': gdal.GRA_Bilinear, 'cubic': gdal.GRA_Cubic}
    # 原始数据集创建(正弦投影)
    driver = gdal.GetDriverByName('MEM')  # 在内存中临时创建
    src_ds = driver.Create("", src_img.shape[1], src_img.shape[0], 1, out_type)  # 注意: 先传列数再传行数, 1表示单波段
    srs = osr.SpatialReference()
    srs.ImportFromProj4(src_proj4)
    """
    对于src_proj4, 依据元数据StructMetadata.0知:
        Projection=GCTP_SNSOID; ProjParams=(6371007.181000,0,0,0,0,0,0,0,0,0,0,0,0)
    或数据集属性(MODIS_Grid_8Day_1km_LST/Data_Fields/Projection)知:
        :grid_mapping_name = "sinusoidal";
        :longitude_of_central_meridian = 0.0; // double
        :earth_radius = 6371007.181; // double
    """
    src_ds.SetProjection(srs.ExportToWkt())  # 设置投影信息
    src_ds.SetGeoTransform(transform)  # 设置仿射参数
    b1 = src_ds.GetRasterBand(1)
    b1.WriteArray(src_img)  # 写入数据
    b1.ComputeStatistics(False)  # 计算统计数据, 方便显示
    if nodata_value is not None:
        b1.SetNoDataValue(nodata_value)
    # 重投影信息(默认WGS84)
    dst_srs = osr.SpatialReference()
    dst_srs.ImportFromEPSG(dst_epsg)
    # 重投影
    options = gdal.WarpOptions(
        dstSRS=dst_srs,  # 输出的空间参考系
        xRes=out_res,  # 输出的X轴方向上的分辨率
        yRes=out_res,  # 输出的y轴方向上的分辨率
        dstNodata=nodata_value,  # 栅格矩阵中的无效值
        outputType=out_type,  # 输出的数据类型
        multithread=True,  # 多线程处理
        resampleAlg=resamples[resample]  # 重采样分辨率
    )
    dst_ds = gdal.Warp(out_path, src_ds, options=options)

    if dst_ds:  # 释放缓存和资源
        dst_ds.FlushCache()
        src_ds, dst_ds = None, None

# 准备
in_dir = r'E:\Datasets\Objects\glass_process'
out_dir = r"E:\MyTEMP\GLASS_dealt"
var_name = 'LAI'
out_res = 0.008333333333333333  # 约1km分辨率
os.makedirs(out_dir, exist_ok=True)

# 镶嵌
mosaic_paths = glob(os.path.join(in_dir, '*.hdf'))

# 镶嵌
mosaic_img, geo_transform, sinu_proj4, [xx, yy] = img_mosaic(mosaic_paths, var_name,
                                                             unit_conversion=True,
                                                             scale_factor_op='multiply', mosaic_mode='mean')
# # 重投影(sinu正弦投影转换为UTM-横轴墨卡托)
# reproj_path = os.path.join(out_dir, 'mosaic.tif')
# zone = cal_zone(xx, yy, sinu_proj4, 'EPSG: 4326')
# out_epsg = 32600 + zone
# img_warp(mosaic_img, reproj_path, geo_transform, sinu_proj4, dst_epsg=out_epsg)

# 重投影(sinu正弦投影转换为WGS84)
reproj_path = os.path.join(out_dir, 'mosaic.tif')
img_warp(mosaic_img, reproj_path, geo_transform, sinu_proj4, dst_epsg=4326, out_res=out_res)

