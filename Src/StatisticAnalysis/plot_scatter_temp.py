# @Author  : ChaoQiezi
# @Time    : 2025/9/23 下午5:45
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: plot_scatter

"""
This script is used to 绘制高程-NDVI散点图
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
import rasterio as rio
from rasterio.plot import show
from glob import glob
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
from scipy import stats

from Config import ndvi_names
from utils import scatter_plot
import my_utils


# 准备
ndvi_dir = r'I:\DataWorkspace\NDVI\interannual_mean'
aspect_path = r'E:\Datasets\Objects\veg_growing_mountain\辅助数据\aspect_0.08deg.tif'
dem_path = r'E:\Datasets\Objects\veg_growing_mountain\辅助数据\elevation_0.08deg.tif'
mountain_region_path = r'E:\Datasets\Objects\veg_growing_mountain\辅助数据\mountain_region_0.08deg.tif'
out_dir = r'E:\Datasets\Objects\veg_growing_mountain\Results\Figs\Scatter_Elevation_NDVI'
out_stat_path = r'E:\Datasets\Objects\veg_growing_mountain\Results\Tables\statistic_dem_ndvi.xlsx'  # 关于各个山区、坡向的DEM和NDVI统计数据的输出路径
os.makedirs(out_dir, exist_ok=True)
img_res = 0.08
img_rows = 1875
img_cols = 4500
img_lon_min = -180
img_lon_max = 180
img_lat_min = -60
img_lat_max = 90
run_force = False  # 强制重新运行所有文件
# 绘图准备
# sns.set_theme(style='whitegrid', font='Calibri')
plt.rcParams['font.family'] = 'Times New Roman, SimSun'
# plt.rcParams['font.sans-serif'] = ['Times New Roman', 'SimHei']
plt.rcParams['mathtext.fontset'] = 'stix' # 设置数学公式字体为stix
plt.rcParams['axes.unicode_minus'] = False
# 统计准备
# stat_df = pd.DataFrame(columns=['mountain_id', 'aspect', 'pixel_count', 'ndvi_min', 'ndvi_max', 'ndvi_mean',
#                                 'ndvi_median', 'dem_min', 'dem_max'])
stat_df = []  # 存储多行统计值

# 读取地理因子数据
with rio.open(aspect_path) as src:
    aspect = src.read(masked=True).squeeze()  # masked=True表示不读取最原始的栅格矩阵, 基于栅格属性信息读取掩膜后的矩阵
with rio.open(dem_path) as src:
    dem = src.read(masked=True).squeeze()
with rio.open(mountain_region_path) as src:
    mountain_region = src.read(masked=True).squeeze()
    mountain_region.mask = mountain_region.mask | (mountain_region == 0)  # 0表示所有山区之外的陆地区域
# 读取NDVI产品
NDVIs = {}
for cur_ndvi_short_name, cur_ndvi_full_name in ndvi_names.items():
    # 检索当前NDVI产品
    cur_wildcard = '{}_*.tif'.format(cur_ndvi_full_name)
    cur_wildcard = os.path.join(ndvi_dir, cur_wildcard)
    cur_retrival_path = glob(cur_wildcard)
    if len(cur_retrival_path) != 1:
        print('当前NDVI产品检索异常: {}'.format(cur_ndvi_full_name))
        continue
    cur_retrival_path = cur_retrival_path[0]

    # 读取NDVI栅格数据集
    with rio.open(cur_retrival_path, 'r') as src:
        NDVIs[cur_ndvi_short_name] = src.read(masked=True).squeeze()


# 整合地理因子和NDVI数据集
combined_ds = np.ma.stack([mountain_region, aspect, dem, *NDVIs.values()], axis=0)  # 堆叠的新维度在axis=0, 即(新维度, rows, cols)
da = xr.DataArray(
    data=combined_ds,
    dims=['ds_name', 'lat', 'lon'],  # 维度定义
    coords={  # 各个维度的坐标定义
        'ds_name': ['mountain_region', 'aspect', 'dem', *NDVIs.keys()],
        'lat': np.arange(img_lat_max, img_lat_min, -img_res) - img_res / 2,  # 注意栅格矩阵第一行是最上面的第一行, 因此纬度坐标是从上面北极往南极方向的递减
        'lon': np.arange(img_lon_min, img_lon_max, img_res) + img_res / 2,
    }
)
fill_mask = da.isnull().sel(ds_name=['mountain_region', 'aspect', 'dem']).any(dim='ds_name')  # True表示该像元存在[山区ID, 坡向, 海拔]其中一个或多个是无效值
da = da.where(~fill_mask)  # 掩膜
da = da.stack(pixel=['lat', 'lon'])  # 压缩lat和lon两个维度变成一个维度pixel
da = da.dropna(dim='pixel', how='all')  # 对于pixel维度, 只有全部是无效值, 那么当前pixel行则被drop剔除掉
da = da.transpose('pixel', 'ds_name')  # 互换行列维度 --> (pxiel, ds_name)
df = pd.DataFrame(da, columns=da.coords['ds_name'], index=da['pixel'])


# 绘制散点图
mountain_IDs = np.unique(da.sel(ds_name='mountain_region'))  # 获取所有的山区ID
aspect_NUMs = np.unique(da.sel(ds_name='aspect'))  # 获取所有的坡向方位(正常为8个, [1, 8])
for cur_mountain_id in mountain_IDs:
    for cur_aspect in aspect_NUMs:
        # 绘制当前山区当前坡向区域: DEM与NDVI的散点图(6个NDVI产品, 6景散点图)
        for cur_ndvi_short_name, cur_ndvi_full_name in ndvi_names.items():
            # 输出准备
            cur_out_dir = os.path.join(out_dir, 'mountain_{:03.0f}'.format(cur_mountain_id), 'aspect_{:.0f}'.format(cur_aspect))
            os.makedirs(cur_out_dir, exist_ok=True)
            cur_out_filename = 'mountain{:03.0f}_aspect{:.0f}_{}.png'.format(cur_mountain_id, cur_aspect, cur_ndvi_full_name)
            cur_out_path = os.path.join(cur_out_dir, cur_out_filename)
            if os.path.exists(cur_out_path) and (not run_force):
                continue

            # 筛选当前山区当前坡向区域的数据
            cur_df = df[(df.mountain_region == cur_mountain_id) & (df.aspect == cur_aspect)].copy()
            cur_df = cur_df[~np.isnan(cur_df[cur_ndvi_short_name])]
            cur_df['gt_zero'] = cur_df[cur_ndvi_short_name] > 0
            pixel_count = len(cur_df)
            # 当前循环项-统计分析
            # 计算常规统计值
            cur_ndvi_min = cur_df[cur_ndvi_short_name].min()
            cur_ndvi_max = cur_df[cur_ndvi_short_name].max()
            cur_ndvi_mean = cur_df[cur_ndvi_short_name].mean()
            cur_ndvi_median = cur_df[cur_ndvi_short_name].median()
            cur_dem_min = cur_df['dem'].min()
            cur_dem_max = cur_df['dem'].max()
            # 计算线性拟合的斜率、截距和p值
            slope, intercept, r, p, _ = stats.linregress(cur_df['dem'], cur_df[cur_ndvi_short_name])
            slope_direction = '上升' if slope > 0 else '下降'
            fig_text = f"""
                        $y = {slope:.6f}x + {intercept:.3f}, r={r:.3f}, p = {p:.3f}$
                        ps：海拔每上升100m, NDVI{slope_direction}{abs(slope * 100):.4f}\n
                        像元数量: {pixel_count:.0f}\n
                        NDVI值范围: {cur_ndvi_min:.3f} ~ {cur_ndvi_max:.3f}, NDVI均值: {cur_ndvi_mean:.3f}, NDVI中值: {cur_ndvi_median:.3f}\n
                        DEM范围: {cur_dem_min:.2f} ~ {cur_dem_max:.2f}"""
            # 保存统计值
            cur_row = {
                'mountain_id': cur_mountain_id,
                'aspect': cur_aspect,
                'ndvi_name': cur_ndvi_full_name,
                'pixel_count': pixel_count,
                'ndvi_min': cur_ndvi_min,
                'ndvi_max': cur_ndvi_max,
                'ndvi_mean': cur_ndvi_mean,
                'ndvi_median': cur_ndvi_median,
                'dem_min': cur_dem_min,
                'dem_max': cur_dem_max,
                'slope': slope,
                'r': r,
                'p': p,
            }
            stat_df.append(cur_row)

            # 绘制当前迭代项的散点图
            if pixel_count == 0:
                print('当前迭代项全为无效值: mountain id: {:03.0f}, aspect: {:.0f}, ndvi_name: {}'.format(cur_mountain_id, cur_aspect, cur_ndvi_full_name))
                continue
            cur_title = 'Mountain: {:.0f}, Aspect: {:.0f}, NDVI: {}'.format(cur_mountain_id, cur_aspect,
                                                                            cur_ndvi_full_name)
            cur_xlabel = 'Elevation (m)'
            cur_ylabel = f'{cur_ndvi_full_name}'
            scatter_plot(cur_df, 'dem', cur_ndvi_short_name, 'gt_zero', cur_out_path,
                         title=cur_title, xlabel=cur_xlabel, ylabel=cur_ylabel, text=fig_text)

    # 绘制当前山区所有区域(不分aspect): DEM与NDVI的散点图
    for cur_ndvi_short_name, cur_ndvi_full_name in ndvi_names.items():
        # 输出准备
        cur_out_dir = os.path.join(out_dir, 'mountain_{:03.0f}'.format(cur_mountain_id))
        os.makedirs(cur_out_dir, exist_ok=True)
        cur_out_filename = 'mountain{:03.0f}_{}.png'.format(cur_mountain_id, cur_ndvi_full_name)
        cur_out_path = os.path.join(cur_out_dir, cur_out_filename)
        if os.path.exists(cur_out_path) and (not run_force):
            continue

        # 筛选当前山区当前坡向区域的数据
        cur_df = df[df.mountain_region == cur_mountain_id].copy()
        cur_df = cur_df[~np.isnan(cur_df[cur_ndvi_short_name])]
        cur_df['gt_zero'] = cur_df[cur_ndvi_short_name] > 0
        pixel_count = len(cur_df)
        # 当前循环项-统计分析
        # 计算常规统计值
        cur_ndvi_min = cur_df[cur_ndvi_short_name].min()
        cur_ndvi_max = cur_df[cur_ndvi_short_name].max()
        cur_ndvi_mean = cur_df[cur_ndvi_short_name].mean()
        cur_ndvi_median = cur_df[cur_ndvi_short_name].median()
        cur_dem_min = cur_df['dem'].min()
        cur_dem_max = cur_df['dem'].max()
        # 计算线性拟合的斜率、截距和p值
        slope, intercept, r, p, _ = stats.linregress(cur_df['dem'], cur_df[cur_ndvi_short_name])
        slope_direction = '上升' if slope > 0 else '下降'
        fig_text = f"""
                    $y = {slope:.6f}x + {intercept:.3f}, r={r:.3f}, p = {p:.3f}$
                    ps：海拔每上升100m, NDVI{slope_direction}{abs(slope * 100):.4f}\n
                    像元数量: {pixel_count:.0f}\n
                    NDVI值范围: {cur_ndvi_min:.3f} ~ {cur_ndvi_max:.3f}, NDVI均值: {cur_ndvi_mean:.3f}, NDVI中值: {cur_ndvi_median:.3f}\n
                    DEM范围: {cur_dem_min:.2f} ~ {cur_dem_max:.2f}"""
        # 保存统计值
        cur_row = {
            'mountain_id': cur_mountain_id,
            'aspect': '1-8',
            'ndvi_name': cur_ndvi_full_name,
            'pixel_count': pixel_count,
            'ndvi_min': cur_ndvi_min,
            'ndvi_max': cur_ndvi_max,
            'ndvi_mean': cur_ndvi_mean,
            'ndvi_median': cur_ndvi_median,
            'dem_min': cur_dem_min,
            'dem_max': cur_dem_max,
            'slope': slope,
            'r': r,
            'p': p,
        }
        stat_df.append(cur_row)

        # 绘制当前迭代项的散点图
        if pixel_count == 0:
            print('当前迭代项全为无效值: mountain id: {:03.0f}, ndvi_name: {}'.format(cur_mountain_id, cur_ndvi_full_name))
            continue
        cur_title = 'Mountain: {:.0f}, Aspect: 1~8, NDVI: {}'.format(cur_mountain_id, cur_ndvi_full_name)
        cur_xlabel = 'Elevation (m)'
        cur_ylabel = f'{cur_ndvi_full_name}'
        scatter_plot(cur_df, 'dem', cur_ndvi_short_name, 'gt_zero', cur_out_path,
                     title=cur_title, xlabel=cur_xlabel, ylabel=cur_ylabel, text=fig_text)


# 统计结果输出
stat_df = pd.DataFrame(stat_df)
stat_df.to_excel(out_stat_path, index=False)


