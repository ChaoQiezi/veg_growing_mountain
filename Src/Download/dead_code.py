import datetime as dt
from datetime import date
from terracatalogueclient import Catalogue
from terracatalogueclient.config import CatalogueConfig, CatalogueEnvironment

# 准备
config = CatalogueConfig.from_environment(CatalogueEnvironment.CGLS)  # 创建默认配置
catalogue = Catalogue(config)  # 实例化目录
out_dir = ''
out_url_txt = r'F:\PyProJect\veg_growing_mountain\Src\Download\urls\clms_ndvi_v3.txt'
start_date = date(2000, 1, 1)
end_date = date(2020, 12, 31)
collection_id = "clms_global_ndvi_1km_v3_10daily_geotiff"  # 通过下方的c.id获取

# # 打印所有的数据集合的标题和id(id用于下方的collection参数)
# for c in list(catalogue.get_collections()):
#     print("{} | {}".format(c.properties.get("title"), c.id))

# 数据集下载, e.g. the Normalized Difference Vegetation Index: global 10-daily (raster 1km)
products = list(catalogue.get_products(
   # "clms_global_ndvi_1km_v3_10daily_netcdf",  # this value can be found in the metadata of the collection
   collection_id,  # this value can be found in the metadata of the collection
    start=start_date,
    end=end_date,
))


# Download the selected products to a specific local folder
# catalogue.download_products(products, r"F:\PyProJect\veg_growing_mountain\Src\Download\NDVI_V3_2010_DOWNLOADS")

"""
上述官方下载速度太慢了, 我们直接获取下载链接, 使用IDM下载
"""
urls = []
for product in products:
    for cur_data in product.data:
        urls.append(cur_data.href)
with open(out_url_txt, 'w') as f:
    f.writelines(urls)