# @Author  : ChaoQiezi
# @Time    : 2025/8/27 下午8:57
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: check_integrity

"""
This script is used to 检查所下载的数据集的完整性
"""

# """
# 检查NOAA CDR AVHRR NDVI V5 产品完整性
#
# 时间分辨率: 每天
# 下载范围: 2000-01-01 ~ 2023-12-31
# 产品时间范围: 1981-06-24 ~ present
# """
# import os
# from datetime import datetime, timedelta
# from glob import glob
# from tqdm import tqdm
#
# # 准备
# in_dir = r'I:\DataHub\NDVI\NOAA_AVHRR_NDVI_V5'
# start_date = datetime(2000, 1, 1)
# end_date = datetime(2023, 12, 31)
# days = (end_date - start_date).days + 1  # +1: 包含起始和终止日期(即闭区间)
# # 检查完整性
# pbar = tqdm(range(days), desc='检查数据完整性', unit='file', colour='blue', ncols=100)
# for cur_month_count in pbar:
#     # 获取当前日期的相关信息
#     cur_date = start_date + timedelta(days=cur_month_count)
#     cur_filename_wildcard = '*_{}{:02}{:02}_c*.nc'.format(cur_date.year, cur_date.month, cur_date.day)
#     cur_file_path = os.path.join(in_dir, cur_filename_wildcard)
#     # 更新进度条信息
#     pbar.set_description(f'检索: {cur_date.strftime("%Y-%m-%d")}')
#
#     # 检索
#     retrieval_file_paths = glob(cur_file_path)
#     if len(retrieval_file_paths) == 0:
#         pbar.write('\n{}-{:02}-{:02}: 不存在文件'.format(cur_date.year, cur_date.month, cur_date.day))
#     elif len(retrieval_file_paths) == 1:
#         continue
#     elif len(retrieval_file_paths) >= 2:
#         pbar.write('\n{}-{:02}-{:02}: 存在多个文件'.format(cur_date.year, cur_date.month, cur_date.day))
#     else:
#         pbar.write('\n{}-{:02}-{:02}: 检索异常'.format(cur_date.year, cur_date.month, cur_date.day))
# print('检索完成.')


# """
# 检查 MOD13A3 产品完整性
#
# 时间分辨率: 每天
# 下载范围: 2000-02-01 ~ 2023-12-31
# 产品时间范围: 2000-02-01 ~ present
# """
# import os
# from datetime import datetime
# from glob import glob
# from tqdm import tqdm
# from dateutil.relativedelta import relativedelta
#
# # 准备
# in_dir = r'I:\DataHub\NDVI\MOD13A3'
# start_date = datetime(2000, 2, 1)
# end_date = datetime(2023, 12, 31)
# delta = relativedelta(end_date, start_date)
# months = delta.years * 12 + delta.months + 1  # 总月份数
# # 检查完整性
# pbar = tqdm(range(months), desc='检查数据完整性', unit='file', colour='blue', ncols=100)
# for cur_month_count in pbar:
#     # 获取当前日期的相关信息
#     cur_date = start_date + relativedelta(months=cur_month_count)
#     cur_day_of_year = cur_date.timetuple().tm_yday  # 当前年份的第几天
#     cur_filename_wildcard = 'MOD13A3.A{}{:03}.*.hdf'.format(cur_date.year, cur_day_of_year)
#     cur_file_path = os.path.join(in_dir, '**', cur_filename_wildcard)
#     # 更新进度条信息
#     pbar.set_description(f'检索: {cur_date.strftime("%Y-%m-%d")}')
#
#     # 检索
#     retrieval_file_paths = glob(cur_file_path, recursive=True)
#     retrieval_count = len(retrieval_file_paths)
#     if retrieval_count == 0:
#         pbar.write('\n{}-{:02}-{:02}({} days): 不存在文件'.format(cur_date.year, cur_date.month, cur_date.day,
#                                                                   cur_day_of_year))
#     elif retrieval_count < 270:
#         pbar.write('\n{}-{:02}-{:02}({} days): 文件数量不足({}个)'.format(cur_date.year, cur_date.month, cur_date.day,
#                                                                           cur_day_of_year, retrieval_count))
#     elif 270 <= retrieval_count <= 300:
#         continue
#     elif retrieval_count > 300:
#         pbar.write('\n{}-{:02}-{:02}({} days): 文件数量过多({}个)'.format(cur_date.year, cur_date.month, cur_date.day,
#                                                                           cur_day_of_year, retrieval_count))
#     else:
#         pbar.write('\n{}-{:02}-{:02}({} days): 检索异常({})'.format(cur_date.year, cur_date.month, cur_date.day,
#                                                                     cur_day_of_year, retrieval_count))
# print('检索完成.')


# """
# 检查 MYD13A3 产品完整性
#
# 时间分辨率: 每天
# 下载范围: 2002-07-01 ~ 2023-12-31
# 产品时间范围: 2002-07-01 ~ present
# """
# import os
# from datetime import datetime
# from glob import glob
# from tqdm import tqdm
# from dateutil.relativedelta import relativedelta
#
# # 准备
# in_dir = r'I:\DataHub\NDVI\MYD13A3'
# start_date = datetime(2002, 7, 1)
# end_date = datetime(2023, 12, 31)
# delta = relativedelta(end_date, start_date)
# months = delta.years * 12 + delta.months + 1  # 总月份数
# # 检查完整性
# pbar = tqdm(range(months), desc='检查数据完整性', unit='file', colour='blue', ncols=100)
# for cur_month_count in pbar:
#     # 获取当前日期的相关信息
#     cur_date = start_date + relativedelta(months=cur_month_count)
#     cur_day_of_year = cur_date.timetuple().tm_yday  # 当前年份的第几天
#     cur_filename_wildcard = 'MYD13A3.A{}{:03}.*.hdf'.format(cur_date.year, cur_day_of_year)
#     cur_file_path = os.path.join(in_dir, '**', cur_filename_wildcard)
#     # 更新进度条信息
#     pbar.set_description(f'检索: {cur_date.strftime("%Y-%m-%d")}')
#
#     # 检索
#     retrieval_file_paths = glob(cur_file_path, recursive=True)
#     retrieval_count = len(retrieval_file_paths)
#     if retrieval_count == 0:
#         pbar.write('\n{}-{:02}-{:02}({} days): 不存在文件'.format(cur_date.year, cur_date.month, cur_date.day, cur_day_of_year))
#     elif retrieval_count < 270:
#         pbar.write('\n{}-{:02}-{:02}({} days): 文件数量不足({}个)'.format(cur_date.year, cur_date.month, cur_date.day, cur_day_of_year, retrieval_count))
#     elif 270 <= retrieval_count <= 300:
#         continue
#     elif retrieval_count > 300:
#         pbar.write('\n{}-{:02}-{:02}({} days): 文件数量过多({}个)'.format(cur_date.year, cur_date.month, cur_date.day, cur_day_of_year, retrieval_count))
#     else:
#         pbar.write('\n{}-{:02}-{:02}({} days): 检索异常({})'.format(cur_date.year, cur_date.month, cur_date.day, cur_day_of_year, retrieval_count))
# print('检索完成.')


# """
# 检查 GIMMS NDVI 3G+ 产品完整性
#
# 时间分辨率: 半月
# 下载范围: 2000-01-01 ~ 2022-12-31
# 产品时间范围: 1982-01-01 ~ 2022-12-31
# """
# import os
# from datetime import datetime
# from glob import glob
# from tqdm import tqdm
# from dateutil.relativedelta import relativedelta
#
# # 准备
# in_dir = r'I:\DataHub\NDVI\GIMMS_NDVI_3G+'
# start_date = datetime(2000, 1, 1)
# end_date = datetime(2022, 12, 31)
# delta = relativedelta(end_date, start_date)
# files_count = (delta.years + 1) * 2  # 一年两个nc文件, 单个nc文件shape=(time_step=12, rows, cols)存储半年(6个月*2<半月一景>)的数据
# # 检查完整性
# pbar = tqdm(range(files_count), desc='检查数据完整性', unit='file', colour='blue', ncols=100)
# for cur_month_count in pbar:
#     # 获取当前日期的相关信息
#     cur_date = start_date + relativedelta(months=cur_month_count * 6)
#     if cur_date.month == 1:
#         cur_date = cur_date.replace(day=6)
#     elif cur_date.month == 7:
#         cur_date = cur_date.replace(day=12)
#     cur_filename_wildcard = 'ndvi3g_geo_v1_*_{}_{:02}{:02}.nc4'.format(cur_date.year, cur_date.month, cur_date.day)
#     cur_file_path = os.path.join(in_dir, cur_filename_wildcard)
#     # 更新进度条信息
#     pbar.set_description(f'检索: {cur_date.strftime("%Y-%m-%d")}')
#
#     # 检索
#     retrieval_file_paths = glob(cur_file_path, recursive=True)
#     retrieval_count = len(retrieval_file_paths)
#     if retrieval_count == 0:
#         pbar.write('\n{}-{:02}-{:02}: 不存在文件'.format(cur_date.year, cur_date.month, cur_date.day))
#     elif retrieval_count == 1:
#         continue
#     elif retrieval_count > 1:
#         pbar.write('\n{}-{:02}-{:02}: 文件数量过多({}个)'.format(cur_date.year, cur_date.month, cur_date.day, retrieval_count))
#     else:
#         pbar.write('\n{}-{:02}-{:02}: 检索异常({})'.format(cur_date.year, cur_date.month, cur_date.day, retrieval_count))
# print('检索完成.')


"""
检查 CLMS NDVI V3 产品完整性

时间分辨率: 10天
下载范围: 2000-01-01 ~ 2020-06-31
产品时间范围: 1999-01-01 ~ 2020-06-31
"""
import os
from datetime import datetime
from glob import glob
from tqdm import tqdm
from dateutil.relativedelta import relativedelta

# 准备
in_dir = r'I:\DataHub\NDVI\CLMS_NDVI_V3'
start_date = datetime(2000, 1, 1)
end_date = datetime(2020, 6, 30)
delta = relativedelta(end_date, start_date)
months = delta.years * 12 + delta.months + 1  # 月份
# 检查完整性
pbar = tqdm(range(months), desc='检查数据完整性', unit='month', colour='blue', ncols=100)
for cur_month_count in pbar:
    # 获取当前日期的相关信息
    cur_month_date = start_date + relativedelta(months=cur_month_count)

    for cur_ix in range(3):  # 一个月3个文件(时间分辨率10天)
        cur_date = cur_month_date + relativedelta(days=cur_ix * 10)

        cur_filename_wildcard = 'c_gls_NDVI-*_{}{:02}{:02}0000_GLOBE_*_V3.0.1.tiff'.format(cur_date.year, cur_date.month, cur_date.day)
        cur_file_path = os.path.join(in_dir, cur_filename_wildcard)
        # 更新进度条信息
        pbar.set_description(f'检索: {cur_date.strftime("%Y-%m-%d")}')

        # 检索
        retrieval_file_paths = glob(cur_file_path)
        retrieval_count = len(retrieval_file_paths)  # 一个日期包括5个文件(5个波段)
        if retrieval_count == 0:
            pbar.write('\n{}-{:02}-{:02}: 不存在文件'.format(cur_date.year, cur_date.month, cur_date.day))
        elif retrieval_count < 5:
            print('\n{}-{:02}-{:02}: 文件数量不足({}个)'.format(cur_date.year, cur_date.month, cur_date.day, retrieval_count))
        elif retrieval_count == 5:
            continue
        elif retrieval_count > 5:
            pbar.write('\n{}-{:02}-{:02}: 文件数量过多({}个)'.format(cur_date.year, cur_date.month, cur_date.day, retrieval_count))
        else:
            pbar.write('\n{}-{:02}-{:02}: 检索异常({})'.format(cur_date.year, cur_date.month, cur_date.day, retrieval_count))
print('检索完成.')


# """
# 检查 PKU GIMMS NDVI V1.2 产品完整性
#
# 时间分辨率: 半月
# 下载范围: 2000-01-01 ~ 2022-12-31
# 产品时间范围: 1982-01-01 ~ 2022-12-31
# """
# import os
# from datetime import datetime
# from glob import glob
# from tqdm import tqdm
# from dateutil.relativedelta import relativedelta
#
# # 准备
# in_dir = r'I:\DataHub\NDVI\PKU_GIMMS_NDVI_V1.2\AVHRR_MODIS'
# start_date = datetime(2000, 1, 1)
# end_date = datetime(2022, 12, 31)
# delta = relativedelta(end_date, start_date)
# months = delta.years * 12 + delta.months + 1
# # 检查完整性
# pbar = tqdm(range(months), desc='检查数据完整性', unit='file', colour='blue', ncols=100)
# for cur_month_count in pbar:
#     # 获取当前日期的相关信息
#     cur_date = start_date + relativedelta(months=cur_month_count)
#
#     cur_filename_wildcard = 'PKU_GIMMS_NDVI_V1.2_{}{:02}*.tif'.format(cur_date.year, cur_date.month)
#     cur_file_path = os.path.join(in_dir, cur_filename_wildcard)
#     # 更新进度条信息
#     pbar.set_description(f'检索: {cur_date.strftime("%Y-%m-%d")}')
#
#     # 检索
#     retrieval_file_paths = glob(cur_file_path, recursive=True)
#     retrieval_count = len(retrieval_file_paths)
#     if retrieval_count == 0:
#         pbar.write('\n{}-{:02}-{:02}: 不存在文件'.format(cur_date.year, cur_date.month, cur_date.day))
#     elif retrieval_count < 2:
#         pbar.write('\n{}-{:02}-{:02}: 文件数量不足({} 个)'.format(cur_date.year, cur_date.month, cur_date.day, retrieval_count))
#     elif retrieval_count == 2:
#         continue
#     elif retrieval_count > 2:
#         pbar.write('\n{}-{:02}-{:02}: 文件数量过多({}个)'.format(cur_date.year, cur_date.month, cur_date.day, retrieval_count))
#     else:
#         pbar.write('\n{}-{:02}-{:02}: 检索异常({})'.format(cur_date.year, cur_date.month, cur_date.day, retrieval_count))
# print('检索完成.')