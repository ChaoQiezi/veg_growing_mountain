# @Author  : ChaoQiezi
# @Time    : 2025/8/26 21:51
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: mod13a3_download

"""
This script is used to 批量下载MOD13A3产品数据集
"""

# """
# 下载2000年-2003年
# """
# import os
# from utils import DownloadManager
#
# # 准备
# url_path = r'E:\Porjects\PyProjects\Common\Src\veg_growing_mountain\download\urls\mod13a3_00_03.txt'
# out_dir = r'F:\NDVI\MOD13A3'
# out_folder_name = os.path.basename(url_path).split('.')[0]
# out_dir = os.path.join(out_dir, out_folder_name)
# os.makedirs(out_dir, exist_ok=True)
# status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# # 下载
# downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
# downloader.download()


# """
# 下载2004年-2006年
# """
# import os
# from utils import DownloadManager
#
# # 准备
# url_path = r'E:\Porjects\PyProjects\Common\Src\veg_growing_mountain\download\urls\mod13a3_04_06.txt'
# out_dir = r'F:\NDVI\MOD13A3'
# out_folder_name = os.path.basename(url_path).split('.')[0]
# out_dir = os.path.join(out_dir, out_folder_name)
# os.makedirs(out_dir, exist_ok=True)
# status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# # 下载
# downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
# downloader.download()


# """
# 下载2007年-2010年
# """
# import os
# from utils import DownloadManager
#
# # 准备
# url_path = r'E:\Porjects\PyProjects\Common\Src\veg_growing_mountain\download\urls\mod13a3_07_10.txt'
# out_dir = r'F:\NDVI\MOD13A3'
# out_folder_name = os.path.basename(url_path).split('.')[0]
# out_dir = os.path.join(out_dir, out_folder_name)
# os.makedirs(out_dir, exist_ok=True)
# status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# # 下载
# downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
# downloader.download()


"""
下载2011年-2018年
"""
import os
from utils import DownloadManager

# 准备
url_path = r'F:\PyProJect\veg_growing_mountain\Src\Download\urls\mod13a3_11_18.txt'
out_dir = r'I:\DataHub\NDVI\MOD13A3'
out_folder_name = os.path.basename(url_path).split('.')[0]
out_dir = os.path.join(out_dir, out_folder_name)
os.makedirs(out_dir, exist_ok=True)
status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# 下载
downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
downloader.download()


# """
# 下载2019年-2023年
# """
# import os
# from utils import DownloadManager
#
# # 准备
# url_path = r'E:\Porjects\PyProjects\Common\Src\veg_growing_mountain\download\urls\mod13a3_19_23.txt'
# out_dir = r'F:\NDVI\MOD13A3'
# out_folder_name = os.path.basename(url_path).split('.')[0]
# out_dir = os.path.join(out_dir, out_folder_name)
# os.makedirs(out_dir, exist_ok=True)
# status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# # 下载
# downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
# downloader.download()
