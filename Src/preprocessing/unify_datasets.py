# @Author  : ChaoQiezi
# @Time    : 2025/9/12 上午10:30
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: unify_datasets


"""
This script is used to 将前面预处理好的各个NDVI产品数据集进行统一

统一包括：

时间统一:
    时间范围: 2003-01-01 ~ 2020-6-30
    时间分辨率: 每月(聚合为每月一景)
空间统一:
    空间覆盖范围: -180 ~ 180, -60 ~ 90
    空间分辨率: 1/12°
输出为nc文件(基于xr输出):
    shape=(产品数=6, 时间步=月数量, 行数, 列数)

此外:
    nc文件中还包括坡度、坡向和DEM等辅助数据
"""

import os
from glob import glob
from datetime import date
from my_utils import img_mosaic, img_agg
import rioxarray
import rasterio as rio

from Config import ndvi_names
from utils import parse_paths_monthly

# 准备
in_dir = r'I:\DataWorkspace\NDVI'
out_path = os.path.join(in_dir, 'NDVIs.nc')
start_date = date(2003, 1, 1)
end_date = date(2020, 6, 30)

# 聚合为月尺度产品-CLMS_NDVI_V3(10天分辨率)
clms_name = ndvi_names['clms']
clms_in_dir = os.path.join(in_dir, clms_name, '10day')
clms_out_dir = os.path.join(in_dir, clms_name, 'monthly')
os.makedirs(clms_out_dir, exist_ok=True)
clms_wildcard = '{}_*.tif'.format(clms_name)  # 检索的通配符
clms_wildcard = os.path.join(clms_in_dir, clms_wildcard)
clms_paths = glob(clms_wildcard)
monthly_paths = parse_paths_monthly(clms_paths, clms_name, start_date, end_date)  # 解析路径
for cur_date_ym, cur_paths in monthly_paths.items():
    cur_out_filename = '{}_{}.tif'.format(clms_name, cur_date_ym)
    cur_out_path = os.path.join(clms_out_dir, cur_out_filename)
    agg_arr, arr_meta = img_agg(cur_paths, agg_mode='mean')
    with rio.open(cur_out_path, 'w', **arr_meta) as dst:
        dst.write(agg_arr, 1)


# 循环各个产品数据集-输出为nc文件
# for cur_ndvi_name in ndvi_names:
#     # 检索当前NDVI产品的tiff文件(预处理结果)
#     cur_in_dir = os.path.join(in_dir, cur_ndvi_name)
#     cur_wildcard = '{}_*.tif'.format(cur_ndvi_name)
#     cur_wildcard = os.path.join(cur_in_dir, cur_wildcard)
#     cur_retrival_paths = glob(cur_wildcard)
#     if len(cur_retrival_paths) == 0:





























