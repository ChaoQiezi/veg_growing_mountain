# @Author  : ChaoQiezi
# @Time    : 2025/8/28 15:59
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: gimms_download

"""
This script is used to 批量下载 GIMMS NDVI 3G+ 数据集
"""

"""
下载2000年-2023年
"""
import os
from utils import DownloadManager

# 准备
url_path = r'F:\PyProJect\veg_growing_mountain\Src\Download\urls\gimms_00_23.txt'
out_dir = r'I:\DataHub\NDVI\GIMMS_NDVI_3G+'
out_folder_name = os.path.basename(url_path).split('.')[0]
out_dir = os.path.join(out_dir, out_folder_name)
os.makedirs(out_dir, exist_ok=True)
status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# 下载
downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
downloader.download()
