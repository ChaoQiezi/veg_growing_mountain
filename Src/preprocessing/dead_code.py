# @Author  : ChaoQiezi
# @Time    : 2025/9/13 上午10:07
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: dead_code

"""
This script is used to 
"""

import os
import netCDF4 as nc
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TkAgg')

# 准备
in_path = r"I:\DataHub\NDVI\GIMMS_NDVI_3G+\ndvi3g_geo_v1_1_2000_0106.nc4"

# 读取原始的栅格矩阵
# with nc.Dataset(in_path, 'r') as f:
#     f.variables['ndvi'][:]
cur_var = xr.open_dataset(in_path, engine='netcdf4', mask_and_scale=True)
ndvi = cur_var['ndvi']
plt.imshow(ndvi[0, :, :])
plt.show()
