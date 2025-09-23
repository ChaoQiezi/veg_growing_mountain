# @Author  : ChaoQiezi
# @Time    : 2025/9/8 下午3:32
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: myd13a3_process

"""
This script is used to 预处理MYD13A3数据集

包括: HDF4转tiff、镶嵌、裁剪、重投影

统一时间范围为: 2003 - 2020
    地理范围为: 全球(-180°W ~ 180°E, -60°S ~ 90°N)
"""

import os
from datetime import date
from glob import glob
from shutil import rmtree

import numpy as np
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from osgeo import gdal

from my_utils.geo import img_warp, read_geo_info, read_sinu_info, write_tiff, read_h4_var

# 准备
in_dir = r'I:\DataHub\NDVI\MYD13A3'
out_dir = r'I:\DataWorkspace\NDVI'
temp_dir = os.path.join(out_dir, 'MyTemp')
os.makedirs(temp_dir, exist_ok=True)
var_name = '1 km monthly NDVI'
start_date = date(2003, 1, 1)
end_date = date(2020, 12, 31)
out_res = 1 / 120
delta = relativedelta(end_date, start_date)
month_count = delta.years * 12 + delta.months + 1
dataset_name = os.path.basename(in_dir)
out_dir = os.path.join(out_dir, dataset_name)
os.makedirs(out_dir, exist_ok=True)

# 迭代每月hdf文件处理
pbar = tqdm(range(month_count), desc='MYD13A3-预处理', ncols=120, colour='blue')
for cur_month_count in pbar:
    # 当前循环的日期项
    cur_date = start_date + relativedelta(months=cur_month_count)
    cur_yday = cur_date.timetuple().tm_yday  # 一年中的第几天

    # 更新进度条信息
    pbar.set_description(f'处理: {cur_date.strftime("%Y-%m-%d")}')

    # 若结果已存在跳过该处理
    cur_out_path = os.path.join(out_dir,
                                'MYD13A3_{}_{:02}{:02}.tif'.format(cur_date.year, cur_date.month, cur_date.day))
    if os.path.exists(cur_out_path):  # 如果已经存在该重投影好的tiff文件, 那么跳过
        continue

    # 检索当前日期的所有hdf文件
    cur_wildcard = 'MYD13A3.A{}{:03}.*.hdf'.format(cur_date.year, cur_yday)
    cur_paths = glob(os.path.join(in_dir, '**', cur_wildcard), recursive=True)

    # 检测是否存在hdf文件
    if len(cur_paths) == 0:
        pbar.write('\n{}-{:02}-{:02}({} days): 不存在文件'.format(cur_date.year, cur_date.month, cur_date.day,
                                                                 cur_yday))
        continue

    # 批量输出为临时的原始(意为原坐标系, 原栅格矩阵, 只是显示形式发生变化)geotiff文件(方便gdal镶嵌)
    temp_paths = []  # 临时存储原始tiff文件路径
    temp_ds_list = []  # 临时存储输出在内存中的tiff文件的句柄/对象
    fill_value = None
    for ix, cur_path in enumerate(cur_paths):
        # 获取变量的栅格矩阵及其辅助信息(地理参数等)
        cur_var = read_h4_var(cur_path, var_name, scale_op='divide').astype(np.float32)
        geo_dict = read_geo_info(cur_path)  # 覆盖范围、分辨率、行列数
        sinu_proj4 = read_sinu_info(cur_path)  # 正弦投影的proj4 字符串
        geo_transform = [geo_dict['x_min'], geo_dict['x_res'], 0, geo_dict['y_max'], 0, -geo_dict['y_res']]

        # 输出路径
        cur_out_filename = os.path.basename(cur_path).replace('.hdf', '.tif')
        cur_temp_out_path = f'/vsimem/{cur_out_filename}'  # gdal中在内存虚拟文件系统中的tiff文件路径
        # cur_temp_out_path = os.path.join(temp_dir, cur_out_filename)
        temp_paths.append(cur_temp_out_path)

        # 输出tiff文件
        temp_ds = write_tiff(cur_temp_out_path, cur_var, geo_transform, proj4_str=sinu_proj4, in_mem=True, nodata_value=cur_var.fill_value)
        temp_ds_list.append(temp_ds)
        pbar.set_postfix_str('处理: {}'.format(cur_out_filename))
        # pbar.write('\n处理: {}'.format(cur_out_filename))

        if (ix + 1) == len(cur_paths):
            fill_value = cur_var.fill_value

    # write_png(mosaic_img, os.path.join(out_dir, 'mosaic.png'))
    # pbar.write('输出png文件完成.')
    try:
        # 重投影和镶嵌
        pbar.set_postfix_str('重投影中...')
        warp_options = gdal.WarpOptions(
            srcNodata=fill_value,
            dstNodata=fill_value,
            outputBounds=[-180, -60, 180, 90],
            format='GTiff',
            dstSRS='EPSG:4326',
            xRes=out_res,
            yRes=out_res,
            resampleAlg=gdal.GRA_Bilinear,
            warpOptions=['WRAP_DATELINE=YES'],
            # multithread=True  # 多线程处理
        )
        gdal.Warp(cur_out_path, temp_ds_list, options=warp_options)
    except (Exception, KeyboardInterrupt) as e:  # 无论发生什么意外, 首先检索是否已经生成了结果文件, 将其删除(因为其可能是损坏的)
        if os.path.exists(cur_out_path):
            os.remove(cur_out_path)
        pbar.write('\n{}-{:02}-{:02}: 发生异常终止当前日期的处理并退出程序(errr: {})'.format(cur_date.year, cur_date.month,
                                                                                   cur_date.day, e))
        exit(1)  # 退出程序
    finally:
        # 删除临时文件和释放资源
        pbar.set_postfix_str('删除临时文件...')
        temp_ds_list.clear()  # 清除列表所有元素-内存数据集对象
        for cur_path in temp_paths:
            gdal.Unlink(cur_path)  # 释放临时存储在内存中的tiff文件
        temp_paths.clear()  # 清除所有路径

    # break

rmtree(temp_dir, ignore_errors=True)  # 删除临时文件夹及其内所有文件, ignore_errors=True是为了避免同时运行多个类似程序导致重复删除目录报错
pbar.set_postfix_str('处理完成.')
print('{}-处理完成.'.format(dataset_name))
