# @Author  : ChaoQiezi
# @Time    : 2025/9/9 上午11:09
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: clms_process

"""
This script is used to 预处理CLMS_NDVI_V3数据集

包括: 比例缩放

比例因子等属性来自: https://land.copernicus.eu/en/products/vegetation/normalised-difference-vegetation-index-v3-0-1km 具体见: Data layers 一节

scale_factor: 1 / 250
offset: -0.08
DN值的范围是: 0 ~ 250
比例缩放后的范围是: -0.08 ~ 0.92, 0 * (1 / 250) - 0.08, 250 * (1 / 250) - 0.08)
"""

import os
from sys import exit
from datetime import date

import numpy as np
from dateutil.relativedelta import relativedelta
from glob import glob
from tqdm import tqdm
import rasterio as rio  # 用一用rasterio熟悉一下这种python风格的gdal

# 准备
in_dir = r'I:\DataHub\NDVI\CLMS_NDVI_V3'
out_dir = r'I:\DataWorkspace\NDVI'
start_date = date(2003, 1, 1)  # 检索-起始日期
end_date = date(2020, 12, 31)  # 检索-终止日期, CLMS产品的终止日期是2020-06-30
delta = relativedelta(end_date, start_date)
scale_factor = 1 / 250
offset = -0.08
month_count = delta.years * 12 + delta.months + 1
dataset_name = os.path.basename(in_dir)
out_dir = os.path.join(out_dir, dataset_name)
os.makedirs(out_dir, exist_ok=True)

# 循环每月(一月有三个tiff文件, 10天分辨率)
pbar = tqdm(range(month_count), desc='{}-预处理'.format(dataset_name), ncols=100, colour='blue')
for cur_month_count in pbar:
    # 获取当前月的信息
    cur_month_date = start_date + relativedelta(months=cur_month_count)

    # 循环三次(10天分辨率, 一个月三个tiff文件)
    for cur_ix in range(3):  # 一个月三个产品
        # 当前循环日期的信息
        cur_date = cur_month_date + relativedelta(days=(cur_ix * 10))  # 分辨率10天
        cur_wildcard = 'c_gls_NDVI-NDVI_{}{:02}{:02}*_V3.0.1.tiff'.format(cur_date.year, cur_date.month, cur_date.day)
        cur_wildcard = os.path.join(in_dir, cur_wildcard)
        # 输出信息
        cur_out_filename = '{}_{}_{:02}{:02}.tif'.format(dataset_name, cur_date.year, cur_date.month, cur_date.day)
        cur_out_path = os.path.join(out_dir, cur_out_filename)
        # 更新进度条信息
        pbar.set_postfix_str('处理: {}'.format(cur_out_filename))
        # 检查当前循环文件的结果文件是否存在
        if os.path.exists(cur_out_path):
            continue
        # 检索当前循环的文件
        cur_retrival_paths = glob(cur_wildcard)
        if len(cur_retrival_paths) != 1:
            pbar.write('\n{}-{:02}-{:02}: 文件数量异常'.format(cur_date.year, cur_date.month, cur_date.day))
            continue
        cur_retrival_path = cur_retrival_paths[0]

        # 处理tiff文件(比例缩放, 其他crs等地理参数完全不变)
        # 比例缩放
        with rio.open(cur_retrival_path, 'r') as src:
            cur_meta = src.meta  # 获取元数据
            """
            {'driver': 'GTiff',
             'dtype': 'uint8',
             'nodata': 255.0,
             'width': 40320,
             'height': 15680,
             'count': 1,
             'crs': CRS.from_wkt('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]'),
             'transform': Affine(0.00892857142858361, 0.0, -180.00446428571428,
                    0.0, -0.0089285714285694, 80.00446428571429)}
            """
            cur_band = src.read()  # 获取栅格矩阵
            cur_mask = (cur_band == cur_meta['nodata'])
            cur_band = cur_band * scale_factor + offset  # 比例缩放
            cur_band = cur_band.astype(np.float32)  # 将默认的float64转化为float32
            cur_band = np.ma.array(cur_band, mask=cur_mask, fill_value=np.nan)
            cur_meta['dtype'] = 'float32'
            cur_meta['nodata'] = np.nan
        # 输出tiff文件
        try:
            with rio.open(cur_out_path, 'w', **cur_meta) as dst:
                dst.write(cur_band)  # 本身支持MaskArray数组
        except Exception as e:  # 无论发生什么意外, 首先检索是否已经生成了结果文件, 将其删除(因为其可能是损坏的)
            if os.path.exists(cur_out_path):
                os.remove(cur_out_path)
            pbar.write('\n{}-{:02}-{:02}: 发生异常终止当前日期的处理并退出程序(error: {})'.format(cur_date.year, cur_date.month, cur_date.day, e))
            exit(1)  # 退出程序
