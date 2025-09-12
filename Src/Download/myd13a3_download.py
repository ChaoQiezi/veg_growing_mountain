# @Author  : ChaoQiezi
# @Time    : 2025/8/26 21:51
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: mod13a3_download

"""
This script is used to 批量下载MYD13A3产品数据集
"""

# """
# 下载2002年-2008年
# """
# import os
# from utils import DownloadManager
#
# # 准备
# url_path = r'F:\PyProJect\veg_growing_mountain\Src\Download\urls\myd13a3_02_08.txt'
# out_dir = r'I:\DataHub\NDVI\MYD13A3'
# out_folder_name = os.path.basename(url_path).split('.')[0]
# out_dir = os.path.join(out_dir, out_folder_name)
# os.makedirs(out_dir, exist_ok=True)
# status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# # 下载
# downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
# downloader.download()


"""
下载2009年-2016年
"""
import os
from utils import DownloadManager

# 准备
# url_path = r'F:\PyProJect\veg_growing_mountain\Src\Download\urls\myd13a3_09_16.txt'
# out_dir = r'I:\DataHub\NDVI\MYD13A3'
url_path = r'F:\PyProJect\veg_growing_mountain\Src\Download\urls\myd13a3_09_16_supplement.txt'
out_dir = r'I:\DataHub\NDVI\MYD13A3\myd13a3_09_16'
out_folder_name = os.path.basename(url_path).split('.')[0]
status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# 下载
downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
downloader.download()


# """
# 下载2017年-2023年
# """
# import os
# from utils import DownloadManager
#
# # 准备
# url_path = r'E:\Porjects\PyProjects\Common\Src\veg_growing_mountain\download\urls\myd13a3_17_23.txt'
# out_dir = r'F:\NDVI\MYD13A3'
# out_folder_name = os.path.basename(url_path).split('.')[0]
# out_dir = os.path.join(out_dir, out_folder_name)
# os.makedirs(out_dir, exist_ok=True)
# status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# # 下载
# downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
# downloader.download()