# @Author  : ChaoQiezi
# @Time    : 2025/9/12 上午10:30
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: unify_datasets

"""
This script is used to 将前面预处理好的各个NDVI产品数据集进行统一

统一包括：

时间统一:
    时间范围: 2003-01-01 ~ 2020-6-30
    时间分辨率: 每月(聚合为每月一景)
空间统一:
    空间覆盖范围: -180 ~ 180, -60 ~ 90
    空间分辨率: 1/12°
输出为nc文件(基于xr输出):
    shape=(产品数=6, 时间步=月数量, 行数, 列数)

此外:
    nc文件中还包括坡度、坡向和DEM等辅助数据
"""
