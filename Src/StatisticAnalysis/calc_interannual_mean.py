# @Author  : ChaoQiezi
# @Time    : 2025/9/21 下午9:47
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: calc_interannual_mean

"""
This script is used to 计算所有NDVI产品的年际均值
"""
import os
from datetime import date
from glob import glob
import rasterio as rio

from Config import ndvi_names
from utils import aggregate_to_temporal
from my_utils import img_agg

# 准备
in_dir = r'I:\DataWorkspace\NDVI'
start_date = date(2003, 1, 1)
end_date = date(2019, 12, 31)  # 舍弃了2020年因为所有ndvi产品的时间交集范围是到2020年6月, 2020年不满一年

# 计算年均最大值(max)
for cur_ndvi_name in ndvi_names.values():
    # if cur_ndvi_name != 'GIMMS_NDVI_3G+':
    #     continue

    # 输入输出准备
    cur_in_dir = os.path.join(in_dir, cur_ndvi_name, 'monthly_preprocessed')
    cur_out_dir = os.path.join(in_dir, cur_ndvi_name, 'yearly')
    os.makedirs(cur_out_dir, exist_ok=True)

    # 聚合
    aggregate_to_temporal(cur_ndvi_name, cur_in_dir, cur_out_dir, start_date, end_date, 'yearly', 'max')

# 计算年际均值(mean)
for cur_ndvi_name in ndvi_names.values():
    # if cur_ndvi_name != 'GIMMS_NDVI_3G+':
    #     continue

    # 输入输出准备
    cur_in_dir = os.path.join(in_dir, cur_ndvi_name, 'yearly')
    cur_out_dir = os.path.join(in_dir, cur_ndvi_name, 'interannual')
    cur_out_path = os.path.join(cur_out_dir, '{}_interannual_mean.tif'.format(cur_ndvi_name))
    os.makedirs(cur_out_dir, exist_ok=True)

    # 检索文件,获取路径
    product_wildcard = '{}_*.tif'.format(cur_ndvi_name)  # 检索的通配符
    product_wildcard = os.path.join(cur_in_dir, product_wildcard)
    product_retrival_paths = glob(product_wildcard)

    # 聚合-年际尺度
    agg_arr, arr_meta = img_agg(product_retrival_paths, 'mean')
    with rio.open(cur_out_path, 'w', **arr_meta) as dst:
        dst.write(agg_arr, 1)

print('年际均值计算完成.')


