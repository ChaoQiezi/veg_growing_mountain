# @Author  : ChaoQiezi
# @Time    : 2025/9/8 下午3:57
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: noaa_process

"""
This script is used to 预处理NOAA CDR AVHRR NDVI V5数据集

包括: nc转tiff

统一时间范围为: 2003 - 2020
    地理范围为: 全球(-180°W ~ 180°E, -90°S ~ 90°N)
"""

import os
from datetime import date
from osgeo import gdal
import numpy as np
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from tqdm import tqdm
from glob import glob
import netCDF4 as nc
import rasterio as rio
from rasterio.transform import Affine

from my_utils import write_tiff

# 准备
in_dir = r'I:\DataHub\NDVI\NOAA_AVHRR_NDVI_V5'
out_dir = r'I:\DataWorkspace\NDVI'
var_name = 'NDVI'  # nc文件NDVI数据集的变量名称
start_date = date(2003, 1, 1)  # 检索-起始日期
end_date = date(2020, 12, 31)  # 检索-终止日期
out_res = 0.05  # 输出分辨率
geo_transform = [-180, out_res, 0, 90, 0, -out_res]  # 仿射系数矩阵
delta = relativedelta(end_date, start_date)
month_count = delta.years * 12 + delta.months + 1
dataset_name = os.path.basename(in_dir)
out_dir = os.path.join(out_dir, dataset_name)
os.makedirs(out_dir, exist_ok=True)

# 迭代每天的数据集
pbar = tqdm(range(month_count), desc='{}-预处理'.format(dataset_name), ncols=150, colour='blue')
for cur_month_count in pbar:
    # 获取当前日期所在月的信息
    cur_month_date = start_date + relativedelta(months=cur_month_count)
    cur_month_days = monthrange(cur_month_date.year, cur_month_date.month)[1]

    # 迭代当前循环月的每天数据集
    for cur_month_day_ix in range(cur_month_days):
        # 当前日期的基本信息
        cur_date = cur_month_date + relativedelta(days=cur_month_day_ix)
        cur_wildcard = '*_{}{:02}{:02}_c*.nc'.format(cur_date.year, cur_date.month, cur_date.day)
        cur_wildcard = os.path.join(in_dir, cur_wildcard)
        # 输出的信息
        cur_out_filename = '{}_{}_{:02}{:02}.tif'.format(dataset_name, cur_date.year, cur_date.month, cur_date.day)
        cur_out_path = os.path.join(out_dir, cur_out_filename)
        # if os.path.exists(cur_out_path):  # 存在则跳过
        #     continue
        # 更新进度条
        pbar.set_postfix_str('处理: {}'.format(cur_out_filename))
        # 检索
        cur_retrival_paths = glob(cur_wildcard)
        if len(cur_retrival_paths) != 1:  # 检查文件数量是否正常(具体见/Src/Download/download_log.md)
            pbar.write('\n{}-{:02}-{:02}: 文件数量异常'.format(cur_date.year, cur_date.month, cur_date.day))
        cur_retrival_path = cur_retrival_paths[0]

        # nc -> geotiff文件
        # 读取NDVI变量
        with nc.Dataset(cur_retrival_path, 'r') as f:
            cur_var = f[var_name][:].astype(np.float32)  # 返回MaskArray数组
            """
            此处返回的掩膜数组是经过比例缩放和无效值处理的.(nc内部读取相关属性实现)
            """
        # 输出
        try:
            pbar.set_postfix_str('输出Geotiff文件中...')
            write_tiff(cur_out_path, cur_var, geo_transform, epsg=4326)
            # band_count, rows, cols = cur_var.shape
            # with rio.open(cur_out_path, 'w', 'GTiff', cols, rows, band_count, dtype=cur_var.dtype,
            #               nodata=np.nan, transform=Affine.from_gdal(*geo_transform), crs='EPSG:4326') as dst:
            #     dst.write(cur_var)
        except Exception as e:  # 无论发生什么意外, 首先检索是否已经生成了结果文件, 将其删除(因为其可能是损坏的)
            if os.path.exists(cur_out_path):
                os.remove(cur_out_path)
            pbar.write('\n{}-{:02}-{:02}: 发生异常终止当前日期的处理并退出程序(error: {})'.format(cur_date.year,
                                                                                                  cur_date.month,
                                                                                                  cur_date.day, e))
            exit(1)  # 退出程序

print('{}-处理完成.'.format(dataset_name))
