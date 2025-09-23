# @Author  : ChaoQiezi
# @Time    : 2025/9/3 下午10:23
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: mod13a3_process

"""
This script is used to 预处理MOD13A3数据集-第二种方法

包括: HDF4转tiff、镶嵌、裁剪

统一时间范围为: 2000 - 2020
    地理范围为: 全球
"""

import os
from datetime import date
from glob import glob
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from osgeo import gdal

# from utils import img_mosaic, img_warp, write_png

from my_utils.geo import img_glt, img_warp, img_mosaic, write_tiff

# 准备
in_dir = r'I:\DataHub\NDVI\MOD13A3'
out_dir = r'I:\DataWorkspace\NDVI'
var_name = '1 km monthly NDVI'
start_date = date(2004, 6, 1)
end_date = date(2020, 12, 31)
out_res = 1 / 120
delta = relativedelta(end_date, start_date)
month_count = delta.years * 12 + delta.months + 1
dataset_name = os.path.basename(in_dir)
out_dir = os.path.join(out_dir, dataset_name)
os.makedirs(out_dir, exist_ok=True)

# 迭代每月hdf文件处理
pbar = tqdm(range(month_count), desc='MOD13A3-预处理', ncols=100, colour='blue')
for cur_month_count in pbar:
    # 当前循环的日期项
    cur_date = start_date + relativedelta(months=cur_month_count)
    cur_yday = cur_date.timetuple().tm_yday  # 一年中的第几天

    # 更新进度条信息
    pbar.set_description(f'处理: {cur_date.strftime("%Y-%m-%d")}')

    # 检索当前日期的所有hdf文件
    cur_wildcard = 'MOD13A3.A{}{:03}.*.hdf'.format(cur_date.year, cur_yday)
    cur_paths = glob(os.path.join(in_dir, '**', cur_wildcard), recursive=True)

    # 检测是否存在hdf文件
    if len(cur_paths) == 0:
        pbar.write('\n{}-{:02}-{:02}({} days): 不存在文件'.format(cur_date.year, cur_date.month, cur_date.day,
                                                                 cur_yday))
        continue

    # 镶嵌
    mosaic_img, geo_transform, sinu_proj4, [xx, yy] = img_mosaic(cur_paths, var_name, True, unit_conversion=True, scale_factor_op='divide')

    # # 方法-1
    # # 裁剪掉一部分, 去除边界干扰
    # mosaic_clip_img = mosaic_img[1:-1, 1:-1]
    # geo_transform[0] = geo_transform[0] + geo_transform[1] * 1
    # geo_transform[3] = geo_transform[3] + geo_transform[5] * 1
    # # 输出
    # cur_out_path = os.path.join(out_dir, 'MOD13A3_{}_{:02}{:02}_1km_clip_4.tif'.format(cur_date.year, cur_date.month, cur_date.day))
    # # out_bound = [-180, -60, 180, 90]
    # # out_bound = None
    # img_warp(mosaic_clip_img, cur_out_path, geo_transform, sinu_proj4, dst_epsg=4326, out_res=out_res)

    # 方法-2
    # 分为-180-0, 0-180两个tiff文件
    rows, cols = mosaic_img.shape
    rows_left, cols_left = rows // 2, cols // 2
    geo_transform_left, geo_transform_right = geo_transform.copy(), geo_transform.copy()
    geo_transform_right[0] = geo_transform[0] + geo_transform[1] * cols_left
    # geo_transform_right[3] = geo_transform[3] + geo_transform[-1] * rows_left
    mosaic_img_left = mosaic_img[:, :cols_left]
    mosaic_img_right = mosaic_img[:, cols_left:]
    cur_left_path = '/vsimem/left.tif'
    cur_right_path = '/vsimem/right.tif'
    cur_left_ds = write_tiff(cur_left_path, mosaic_img_left, geo_transform_left, proj4_str=sinu_proj4, in_mem=True)
    cur_right_ds = write_tiff(cur_left_path, mosaic_img_right, geo_transform_right, proj4_str=sinu_proj4, in_mem=True)
    # 重投影
    cur_out_path = os.path.join(out_dir, 'MOD13A3_{}_{:02}{:02}_1km_clip_4.tif'.format(cur_date.year, cur_date.month, cur_date.day))
    out_bound = [-180, -60, 180, 90]
    warp_options = gdal.WarpOptions(
        # srcNodata=np.nan,
        # dstNodata=np.nan,
        outputBounds=out_bound,
        format='GTiff',
        dstSRS='EPSG:4326',
        xRes=out_res,
        yRes=out_res,
        resampleAlg=gdal.GRA_Bilinear,
        warpOptions=['WRAP_DATELINE=YES'],
        # multithread=True  # 多线程处理
    )

    print('开始warp')
    gdal.Warp(cur_out_path, [cur_left_ds, cur_right_ds], options=warp_options)

    break
