# @Author  : ChaoQiezi
# @Time    : 2025/9/10 上午9:00
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: pku_gimms_process

"""
This script is used to 预处理PKU_GIMMS_NDVI_V1.2数据集

包括: 比例缩放, 无效值处理

比例因子等属性来自: https://land.copernicus.eu/en/products/vegetation/normalised-difference-vegetation-index-v3-0-1km 具体见: Data layers 一节

scale_factor: 0.001
offset: 0
valid_range: 0 ~ 1000
两个波段: 第一个波段是NDVI, 第二个波段是QC控制层
"""


import os
from datetime import date, datetime, timedelta
from osgeo import gdal
import numpy as np
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from tqdm import tqdm
from glob import glob
import rasterio as rio
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TkAgg')

from my_utils import write_tiff

# 准备
in_dir = r'I:\DataHub\NDVI\PKU_GIMMS_NDVI_V1.2'
out_dir = r'I:\DataWorkspace\NDVI'
var_name = 'ndvi'  # nc文件NDVI数据集的变量名称
start_date = date(2003, 1, 1)  # 检索-起始日期
end_date = date(2020, 12, 31)  # 检索-终止日期
out_res = 1 / 12  # 输出分辨率(度/°), 约8km
geo_transform = [-180, out_res, 0, 90, 0, -out_res]  # 仿射系数矩阵
geo_transform = [-180, out_res, 0, 90, 0, -out_res]  # 仿射系数矩阵
delta = relativedelta(end_date, start_date)
month_count = delta.years * 12 + delta.months + 1
dataset_name = os.path.basename(in_dir)
out_dir = os.path.join(out_dir, dataset_name)
os.makedirs(out_dir, exist_ok=True)

# 迭代每半月的数据集
pbar = tqdm(range(month_count), desc='{}-预处理'.format(var_name), ncols=100, colour='blue')
for cur_month_count in pbar:
    # 获取当前日期所在月的信息
    cur_year_date = start_date + relativedelta(months=cur_month_count)

    for cur_ix in range(2):  # 前半月和后半月
        # 当前日期的基本信息
        cur_date = cur_year_date + relativedelta(days=(cur_ix * 15))
        cur_wildcard = 'PKU_GIMMS_NDVI_V1.2_{}{:02}{:02}.tif'.format(cur_date.year, cur_date.month, cur_ix + 1)
        cur_wildcard = os.path.join(in_dir, '**', cur_wildcard)
        cur_retrival_paths = glob(cur_wildcard, recursive=True)
        # 输出信息
        cur_out_filename = '{}_{}_{:02}{:02}.tif'.format(dataset_name, cur_date.year, cur_date.month, cur_date.day)
        cur_out_path = os.path.join(out_dir, cur_out_filename)
        # 更新进度条
        pbar.set_postfix_str('处理: {}'.format(cur_out_filename))
        # 检查文件数量是否正常(具体见/Src/Download/download_log.md)
        if len(cur_retrival_paths) != 1:
            pbar.write('\n{}-{:02}-{:02}: 文件数量异常'.format(cur_date.year, cur_date.month, cur_date.day))
            continue
        cur_retrival_path = cur_retrival_paths[0]

        # 处理当前循环tiff文件
        # 读取
        with rio.open(cur_retrival_path, 'r') as src:
            cur_band = src.read(1)  # 获取NDVI波段, index从1开始而非0
            cur_qc = src.read(2)  # 获取QC波段
            cur_meta = src.meta  # 获取元数据
        # 比例缩放和无效值处理
        cur_mask = (cur_band < 0) | (cur_band > 1000)  # 有效值范围的掩膜
        cur_mask = cur_mask | (cur_qc == 65535)  # 无效值的掩膜
        cur_band = (cur_band * 0.001).astype(np.float32)  # double --> float
        cur_band = np.ma.array(cur_band, mask=cur_mask, fill_value=np.nan)
        # 元数据修改
        cur_meta['dtype'] = 'float32'  # 数据类型设置为浮点型
        cur_meta['nodata'] = np.nan  # 无效值设置为nan
        cur_meta['count'] = 1  # 波段数量为1

        # 输出
        try:
            with rio.open(cur_out_path, 'w', **cur_meta) as dst:
                dst.write(cur_band, indexes=1)  # 本身支持MaskArray数组(如果传入二维数组(三维无需指定index), 那么需要指定index(从1开始)即输入到哪个波段)
        except Exception as e:  # 无论发生什么意外, 首先检索是否已经生成了结果文件, 将其删除(因为其可能是损坏的)
            if os.path.exists(cur_out_path):
                os.remove(cur_out_path)
            pbar.write('\n{}-{:02}-{:02}: 发生异常终止当前日期的处理并退出程序(error: {})'.format(cur_date.year, cur_date.month, cur_date.day, e))
            exit(1)  # 退出程序

print('{}-处理完成.'.format(dataset_name))
