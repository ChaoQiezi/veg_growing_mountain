# @Author  : ChaoQiezi
# @Time    : 2025/8/30 上午9:17
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: emodis_ndvi_download

"""
This script is used to 批量下载eMODIS数据集
"""

"""
目前由于分辨率过高, 且该eMODIS产品

已经申请的eMODIS数据集: https://dds.cr.usgs.gov/queue/orders/1
usgs viewer：https://earthexplorer.usgs.gov/
M2M API: https://m2m.cr.usgs.gov/

username = 'HeZehuang'
# token = '_NMaCDVFjd@AcYTR8zYaMu2Z!GSeLyPv2Ki8STyq0uX@7TPXG9R9orPqhubAiyG5'
token = 'CD2cHXVOlDgMuVOjCQgEJqvORK_luBuM!@Ec_ogu_J37nTufh8csWgfiDnWTeBG7'
datasetName = "emodis_ndvi_v6"
serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
"""