# @Author  : ChaoQiezi
# @Time    : 2025/3/28 上午10:44
# @Email   : chaoqiezi.one@qq.com
# @FileName: Config

"""
This script is used to 存储配置文件
"""

import os
from pathlib import Path

# 设置项目根文件夹为当前工作目录
root_dir = Path(__file__).resolve().parent
os.chdir(root_dir)
# 资源文件夹
Resources_dir = os.path.join(root_dir, 'Resources')
# IDM路径
idm_path = r"D:\Softwares\IDM\Internet Download Manager\IDMan.exe"

# 各个NDVI产品数据集名称
ndvi_names = {
    'clms': 'CLMS_NDVI_V3',
    'gimms': 'GIMMS_NDVI_3G+',
    'mod': 'MOD13A3',
    'myd': 'MYD13A3',
    'noaa': 'NOAA_AVHRR_NDVI_V5',
    'pku_gimms': 'PKU_GIMMS_NDVI_V1.2'
}

# api和key
my_url = "https://cds.climate.copernicus.eu/api"  # api链接
my_key = "c70a112c-b210-492d-a7a0-29a7c5356820"  # API密钥(Mine)
# my_key = "12eda166-47ae-4de6-a4df-1df6c0eb3b2e"  # API密钥(师兄)
# 下载参数
moniter_interval = 1
concurrent_downloads = 18
# 初始化下载请求
request = {
    "variable": [],
    "year": '',
    "month": '',
    "day": [],
    "time": [  # 每小时
        "00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00"
    ],
    "data_format": "netcdf",  # 输出格式为NetCDF4格式(.nc文件), 可选('grib', 'netcdf')
    "download_format": "unarchived"  # 不压缩下载, 可选('unarchived', 'zip')
}
# 进度条样式
bar_format = "{desc}: {percentage:.0f}%|{bar}| [{n_fmt}/{total_fmt}] [已用时间:{elapsed}, 剩余时间:{remaining}, {postfix}]"
