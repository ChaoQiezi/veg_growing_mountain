from datetime import date
from terracatalogueclient import Catalogue
from terracatalogueclient.config import CatalogueConfig, CatalogueEnvironment

# 准备
config = CatalogueConfig.from_environment(CatalogueEnvironment.CGLS)  # 创建默认配置(默认配置无需API认证例如账户和密钥)
catalogue = Catalogue(config)  # 实例化CLMS数据集目录
out_dir = r'F:\PyProJect\veg_growing_mountain\Src\Download\NDVI_V3_2010_DOWNLOADS'  # 输出目录
start_date = date(2000, 1, 1)  # 检索的起始日期
end_date = date(2020, 12, 31)  # 检索的终止日期
collection_id = "clms_global_ndvi_1km_v3_10daily_geotiff"  # 通过下方的c.id获取

# 打印所有的数据集合的标题和id(id用于下方的collection参数), 用时较长
for c in list(catalogue.get_collections()):
    print("{} | {}".format(c.properties.get("title"), c.id))

# 数据集下载(Normalised Difference Vegetation Index 1999-2020 (raster 1 km), global, 10-daily – version 3)
products = list(catalogue.get_products(
    collection_id,  # 填入数据集id
    start=start_date,
    end=end_date,
    # 如需要限制覆盖范围指定bbox=(west, south, east, north)
))


# 下载检索到的数据集
catalogue.download_products(products, out_dir)

"""
上述官方下载速度太慢了, 我们直接获取下载链接, 使用IDM下载
"""
urls = []
url_path = r'F:\PyProJect\veg_growing_mountain\Src\Download\urls\clms_ndvi_v3.txt'
for product in products:
    for cur_data in product.data:
        urls.append(cur_data.href)
with open(url_path, 'w') as f:
    f.write('\n'.join(urls))

from utils import DownloadManager
import os

# 准备
out_dir = r'I:\DataHub\NDVI\CLMS_NDVI_V3'
out_folder_name = os.path.basename(url_path).split('.')[0]
out_dir = os.path.join(out_dir, out_folder_name)
os.makedirs(out_dir, exist_ok=True)
status_path = os.path.join(os.path.dirname(url_path), '{}.json'.format(out_folder_name))
# 下载
downloader = DownloadManager(out_dir, url_path, status_path, monitor_interval=1)
downloader.download()