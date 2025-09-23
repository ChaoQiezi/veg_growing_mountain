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

args_list = [[1, 11, 111], [2, 22, 222]]
for args in zip(args_list):
    print(args)
