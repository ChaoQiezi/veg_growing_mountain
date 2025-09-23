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
from osgeo import gdal
import traceback
import rioxarray
import rasterio as rio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor  # 线程和进程池(并发和并行处理)

from Config import ndvi_names
from utils import parse_paths_monthly, aggregate_to_temporal, mul_resample

# 准备
in_dir = r'I:\DataWorkspace\NDVI'
out_path = os.path.join(in_dir, 'NDVIs.nc')
start_date = date(2003, 1, 1)
end_date = date(2020, 6, 30)
out_bound = [-180, -60, 180, 90]
out_res = 0.08

# # 聚合为月尺度产品-CLMS_NDVI_V3(10天分辨率)
# clms_name = ndvi_names['clms']
# clms_in_dir = os.path.join(in_dir, clms_name, '10day')
# clms_out_dir = os.path.join(in_dir, clms_name, 'monthly')
# aggregate_to_temporal(clms_name, clms_in_dir, clms_out_dir, start_date, end_date, 'monthly', 'max')

# # 聚合为月尺度产品-GIMMS_NDVI_3G+(半月分辨率)
# gimms_name = ndvi_names['gimms']
# gimms_in_dir = os.path.join(in_dir, gimms_name, 'half_montly')
# gimms_out_dir = os.path.join(in_dir, gimms_name, 'monthly')
# aggregate_to_temporal(gimms_name, gimms_in_dir, gimms_out_dir, start_date, end_date, 'monthly', 'max')

# # 聚合为月尺度产品-NOAA_AVHRR_NDVI_V5(每天分辨率)
# noaa_name = ndvi_names['noaa']
# noaa_in_dir = os.path.join(in_dir, noaa_name, 'daily')
# noaa_out_dir = os.path.join(in_dir, noaa_name, 'monthly')
# aggregate_to_temporal(noaa_name, noaa_in_dir, noaa_out_dir, start_date, end_date, 'monthly', 'max')

# # 聚合为月尺度产品-PKU_GIMMS_NDVI_V1.2(半月分辨率)
# pku_gimms_name = ndvi_names['pku_gimms']
# pku_gimms_in_dir = os.path.join(in_dir, pku_gimms_name, 'half_monthly')
# pku_gimms_out_dir = os.path.join(in_dir, pku_gimms_name, 'monthly')
# aggregate_to_temporal(pku_gimms_name, pku_gimms_in_dir, pku_gimms_out_dir, start_date, end_date, 'monthly', 'max')

# # 并行处理
# with ThreadPoolExecutor(max_workers=6) as executor:
#     # 聚合为月尺度产品-CLMS_NDVI_V3(10天分辨率)
#     clms_name = ndvi_names['clms']
#     clms_in_dir = os.path.join(in_dir, clms_name, '10day')
#     clms_out_dir = os.path.join(in_dir, clms_name, 'monthly')
#     executor.submit(aggregate_to_monthly, clms_name, clms_in_dir, clms_out_dir, start_date, end_date, 'monthly', 'max')
#     # 聚合为月尺度产品-GIMMS_NDVI_3G+(半月分辨率)
#     gimms_name = ndvi_names['gimms']
#     gimms_in_dir = os.path.join(in_dir, gimms_name, 'half_montly')
#     gimms_out_dir = os.path.join(in_dir, gimms_name, 'monthly')
#     executor.submit(aggregate_to_monthly, gimms_name, gimms_in_dir, gimms_out_dir, start_date, end_date, 'monthly', 'max')
#     # 聚合为月尺度产品-NOAA_AVHRR_NDVI_V5(每天分辨率)
#     noaa_name = ndvi_names['noaa']
#     noaa_in_dir = os.path.join(in_dir, noaa_name, 'daily')
#     noaa_out_dir = os.path.join(in_dir, noaa_in_dir, 'monthly')
#     executor.submit(aggregate_to_monthly, noaa_name, noaa_in_dir, noaa_out_dir, start_date, end_date, 'monthly', 'max')
#     # 聚合为月尺度产品-PKU_GIMMS_NDVI_V1.2(半月分辨率)
#     pku_gimms_name = ndvi_names['pku_gimms']
#     pku_gimms_in_dir = os.path.join(in_dir, noaa_name, 'daily')
#     pku_gimms_out_dir = os.path.join(in_dir, pku_gimms_name, 'monthly')
#     executor.submit(aggregate_to_monthly, pku_gimms_name, pku_gimms_in_dir, pku_gimms_out_dir, start_date, end_date, 'monthly', 'max')
#     # MOD和MYD本就是每月分辨率, 因此无需进行聚合


# 对所有产品数据集进行对齐、重采样和裁剪
# # 重采样+对齐-CLMS_NDVI_V3(10天分辨率)
# clms_name = ndvi_names['clms']
# clms_in_dir = os.path.join(in_dir, clms_name, 'monthly')
# clms_out_dir = os.path.join(in_dir, clms_name, 'monthly_preprocessed')
# mul_resample(clms_name, clms_in_dir, clms_out_dir, out_res, out_bound, True)


def wrap_mul_resample(args):
    try:
        return mul_resample(*args)
    except Exception as e:
        return f'ERROR: {e}\n{traceback.format_exc()}'


# 并行处理
if __name__ == '__main__':
    with ProcessPoolExecutor(6) as executor:
        args_list = []  # 存储每个进程函数的顺序参数列表的容器
        for cur_ndvi_name in ndvi_names.values():
            cur_in_dir = os.path.join(in_dir, cur_ndvi_name, 'monthly')
            cur_out_dir = os.path.join(in_dir, cur_ndvi_name, 'monthly_preprocessed')
            args_list.append((cur_ndvi_name, cur_in_dir, cur_out_dir, out_res, out_bound, True))

        results = executor.map(wrap_mul_resample, args_list)

    for result in results:
        if isinstance(result, str) and result.startswith("ERROR:"):
            print("一个子进程失败了，错误信息如下:")
            print(result)
    print('重采样+对齐处理完成.')

