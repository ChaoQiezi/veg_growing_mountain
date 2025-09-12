# @Author  : ChaoQiezi
# @Time    : 2025/9/8 下午9:19
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: gimms_3g_process

"""
This script is used to 预处理NOAA CDR AVHRR NDVI V5数据集

包括: nc转tiff

统一时间范围为: 2003 - 2020
    地理范围为: 全球(-180°W ~ 180°E, -90°S ~ 90°N)
"""

import os
from datetime import date, datetime, timedelta
from osgeo import gdal
import numpy as np
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from tqdm import tqdm
from glob import glob
import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TkAgg')

from my_utils import write_tiff

# 准备
in_dir = r'I:\DataHub\NDVI\GIMMS_NDVI_3G+'
out_dir = r'I:\DataWorkspace\NDVI'
var_name = 'ndvi'  # nc文件NDVI数据集的变量名称
start_date = date(2003, 1, 1)  # 检索-起始日期
end_date = date(2020, 12, 31)  # 检索-终止日期
out_res = 1 / 12  # 输出分辨率(度/°), 约8km
geo_transform = [-180, out_res, 0, 90, 0, -out_res]  # 仿射系数矩阵
geo_transform = [-180, out_res, 0, 90, 0, -out_res]  # 仿射系数矩阵
delta = relativedelta(end_date, start_date)
year_count = delta.years + 1
dataset_name = os.path.basename(in_dir)
out_dir = os.path.join(out_dir, dataset_name)
os.makedirs(out_dir, exist_ok=True)

# 迭代每半月的数据集
pbar = tqdm(range(year_count), desc='{}-预处理'.format(var_name), ncols=100, colour='blue')
for cur_year_count in pbar:
    # 获取当前日期所在月的信息
    cur_year_date = start_date + relativedelta(years=cur_year_count)

    # 迭代半年的数据集
    for cur_ix in range(2):  # 前半年和后半年
        # 当前日期的基本信息
        cur_half_year_date = cur_year_date + relativedelta(months=(cur_ix * 6))
        cur_wildcard = 'ndvi3g_geo_v1_*_{}_{:02}*.nc4'.format(cur_half_year_date.year, cur_half_year_date.month)
        cur_wildcard = os.path.join(in_dir, cur_wildcard)
        cur_retrival_paths = glob(cur_wildcard)

        # 检查文件数量是否正常(具体见/Src/Download/download_log.md)
        if len(cur_retrival_paths) != 1:
            pbar.write('\n{}-{:02}-{:02}: 文件数量异常'.format(cur_half_year_date.year, cur_half_year_date.month, cur_half_year_date.day))
            continue

        # 处理nc4文件 -- 将其中12个时间步(步长: 半月)的数据集分别输出为geotiff文件
        cur_retrival_path = cur_retrival_paths[0]
        with nc.Dataset(cur_retrival_path, 'r') as f:
            # 关闭自动掩膜和缩放(该产品的属性非标准规范, 需手动进行)
            f.set_auto_maskandscale(False)

            # 读取valid_range, _FillValue, scale属性对数组进行预处理
            cur_var = f[var_name]
            valid_range = cur_var.valid_range  # 有效值范围
            fill_value = cur_var._FillValue  # 填充值
            scale_factor = float(cur_var.getncattr('scale').split('x')[1])  # 比例因子
            """
            不使用scale是因为cur_var.scale本身就是cur_var的一个内置控制属性(bool), 不能再用来获取scale属性
            """
            cur_var_arr = cur_var[:]  # 获取ndvi的栅格矩阵, shape=(时间步=12, 行数, 列数)
            # 无效值掩膜-1 (-FillValue)
            cur_var_mask = cur_var_arr == fill_value
            # 比例缩放
            cur_var_arr = cur_var_arr / scale_factor
            # 无效值掩膜-2 (valid_range, 比例缩放之后的有效值范围)
            cur_var_mask = cur_var_mask | (cur_var_arr < valid_range[0]) | (cur_var_arr > valid_range[1])
            # 输出为MaskArray数组
            cur_var_arr = np.ma.masked_where(cur_var_mask, cur_var_arr).astype(np.float32)

            # 读取时间变量和换算
            cur_times = f['time'][:]
            cur_times = [datetime(year=1982, month=1, day=1) + timedelta(days=int(cur_time)) for cur_time in cur_times]
        # 迭代每一个时间步, raster --> geotiff文件
        time_step, rows, cols = cur_var_arr.shape
        for cur_time_ix in range(time_step):
            cur_var_band = cur_var_arr[cur_time_ix, :, :]
            cur_date = cur_times[cur_time_ix]

            # 输出的信息
            cur_out_filename = '{}_{}_{:02}{:02}.tif'.format(dataset_name, cur_date.year, cur_date.month, cur_date.day)
            cur_out_path = os.path.join(out_dir, cur_out_filename)
            pbar.set_postfix_str('处理: {}'.format(cur_out_filename))
            if os.path.exists(cur_out_path):  # 存在就跳过
                continue

            # 输出
            write_tiff(cur_out_path, cur_var_band, geo_transform, epsg=4326)

print('{}-处理完成.'.format(dataset_name))
