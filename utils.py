# @Author  : ChaoQiezi
# @Time    : 2025/3/28 上午11:10
# @Email   : chaoqiezi.one@qq.com
# @FileName: utils

"""
This script is used to 
"""

from tqdm import tqdm
import re
from math import ceil, floor
from osgeo import gdal, osr
import rasterio as rio
import json
import calendar
import os
import time
from subprocess import call
from urllib.parse import urlparse
import numpy as np
from sys import exit
from typing import Union
from pyhdf.SD import SD
from PIL import Image
from matplotlib import pyplot as plt

import Config
from Config import idm_path

gdal.DontUseExceptions()

def generate_request(var_name, datetime, request=Config.request):
    """
    生成ERA5的请求
    :param var_name:
    :param datetime:
    :param request:
    :return:
    """

    # 下载请求
    request['year'] = '{}'.format(datetime.year)
    request['month'] = '{:02}'.format(datetime.month)
    days_of_month = calendar.monthrange(datetime.year, datetime.month)[1]  # 当前月份的天数
    request['day'] = ['{:02}'.format(_day) for _day in range(1, days_of_month + 1)]
    request['variable'] = [var_name]

    return request


class DownloadManager:
    """
    version=0.1

    - 使用下载器时如遇IDM下载错误-解决方法
    ps: 如刚开始运行程序后DIM出现下载错误请等待1-2min, 稍后IDM自动重试下载之后可能会恢复正常(期间IDM初次登录)
    1. 检查下载是否需要登录账户(例如NASA) --> IDM设置 --> 站点管理 --> 新建
    2. 添加账户确认无误之后还是出现下载错误, 确认登录是否需要魔法(NASA登录需要魔法但下载不需要)
        --> 最初下载时开启魔法一段时间后待下载正常后可关闭魔法(可能关闭魔法时仍会存在下载错误或部分文件, 无需担心IDM二次尝试下载一般会下载成功)
        --> 如存在部分文件仍是0kb/s, 尝试中断py程序并重复IDM中操作: 全部停止+继续
    3. 如果仍是存在下载错误, 重启后执行步骤1,2
    4. 如果还是不行, 可以事先在浏览器下载单个文件(挑选一个url在浏览器打开(此时如需VPN可将VPN打开), 务必登录<即浏览器要下载成功
        该链接文件即可, 确保cookies生成>)

    - 没有添加任何数据进IDM或只有少量数据后就陷入停滞-解决方法
    1. 可能是由于IDM没有事先启动, 通过命令行启动的IDM没有接收到python传输的添加数据导致的停滞
    """
    def __init__(self, out_dir, links_path=None, status_path=None, concurrent_downloads=Config.concurrent_downloads,
                 monitor_interval=Config.moniter_interval):
        """
        初始化类
        :param out_dir: 下载文件的输出目录
        :param links_path: 存储下载链接的txt文件(一行一个下载链接)
        :param status_path: 存储结构化下载链接的json文件(用于存储下载链接和状态的json文件)
        """

        # 存储下载状态的json文件
        if status_path is None:
            status_path = os.path.join(Config.Resources_dir, 'links_status.json')
        self.status_path = status_path
        # 下载文件的输出路径
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        self.out_dir = out_dir
        # 下载状态
        self.downloading_links = list()
        self.pending_links = list()
        self.completed_links = list()
        self.links = list()
        self.pbar = None  # 下载进度条, 执行self.download()时触发
        # 下载参数
        self.concurrent_downloads = concurrent_downloads  # 同时下载文件数量(并发量)
        self.monitor_interval = monitor_interval  # 监测下载事件的时间间隔, 单位:秒/s
        self.downloaded_count = len(self.completed_links)  # 已下载数
        self.remaining_downloads = len(self.links) - self.downloaded_count  # 未下载数
        self.link_count = len(self.links)

        # 初始化下载状态
        if links_path is not None:  # 将存储下载链接的txt文件存储为结构化json文件
            self._init_save(links_path)
        elif os.path.exists(self.status_path):
            with open(self.status_path, 'r') as f:
                links_status = json.load(f)
                self.downloading_links = links_status['downloading_links']
                self.pending_links = links_status['pending_links']
                self.completed_links = links_status['completed_links']
                self.links = links_status['links']
                self._update()
        else:
            self._update()

    def _init_save(self, links_path):
        """
        从存储下载链接的txt文件中初始化下载链接及其下载状态等参数
        :param links_path: 存储下载链接的txt文件
        :return: None
        """

        with open(links_path, 'r') as f:
            urls = []
            for line in f:
                if not line.startswith('http'):
                    continue
                urls.append({
                    'url': line.rstrip('\n'),
                    'filename': self._get_filename(line.rstrip('\n'))
                })

        self.links = urls.copy()
        self.pending_links = urls.copy()
        """
        # 必须使用copy(), 否则后续对self.pending_links中元素操作, 会影响self.links的元素, 因为二者本质上都是指向(id相同)同一个列表urls
        self.links = urls
        self.pending_links = urls
        """

        self._update()

    def _update(self, downloading_links=None, pending_links=None, completed_links=None, links=None):
        """更新下载链接的状态位置并保存"""

        if downloading_links is None:
            downloading_links = self.downloading_links
        if pending_links is None:
            pending_links = self.pending_links
        if completed_links is None:
            completed_links = self.completed_links
        if links is None:
            links = self.links

        self.downloaded_count = len(self.completed_links)
        self.remaining_downloads = len(self.links) - self.downloaded_count
        self.link_count = len(self.links)

        with open(self.status_path, 'w') as f:
            json.dump({
                'downloading_links': downloading_links,
                'pending_links': pending_links,
                'completed_links': completed_links,
                'links': links
            }, f, indent=4)  # indent=4表示缩进为4,让排版更美观

    def add_link(self, link: str, filename=None):
        """
        添加新链接
        :param link: 需要添加的一个链接
        :param filename: 该链接对应下载文件的输出文件名
        :return: None
        """

        # 结构化下载链接
        new_item = self._generate_item(link, filename)

        # 添加下载链接到links
        if new_item not in self.links:
            self.links.append(new_item)
            self.pending_links.append(new_item)

        self._update()

    def _get_filename(self, url):
        """获取下载链接url对应的默认文件名称"""

        return os.path.basename(urlparse(url).path)

    def _generate_item(self, link: str, filename=None):
        """基于下载链接生成item"""

        item = {
            'url': link,
        }
        if filename is not None:
            item['filename'] = filename
        else:
            item['filename'] = self._get_filename(link)

        return item

    def _init_download(self):
        """
        初始化下载链接的状态并启动下载
        :return:
        """

        # self.links复制一份到pending_links中
        self.pending_links = self.links.copy()

        self._pending2downloading()  # 将<等待下载队列>中的链接添加到<正在下载队列>去
        call([Config.idm_path, '/s'])  # 启动IDM中<主要下载队列>的所有待下载链接

    def download(self):
        """
        对此前加入的所有url进行下载
        :return:
        """

        try:
            self.pbar = tqdm(total=self.link_count, desc='下载', bar_format=Config.bar_format, colour='blue')
            self._init_download()
            self._monitor()
        except KeyboardInterrupt:
            print('您已中断下载程序; 下次下载将继续从({}/{})处下载...'.format(self.downloaded_count, self.link_count))
        except Exception as e:
            print('下载异常错误: {};\n下次下载将继续从({}/{})处下载...'.format(e, self.downloaded_count, self.link_count))
        finally:
            self._update()  # 无论是否发生异常, 最后都必须保存当前下载状态, 以备下次下载继续从断开处进行
            exit(1)  # 错误退出

    def download_single(self, url, filename=None, wait_time=None):
        """
        对输入的单个url进行下载, 最好不要与download()方法连用
        :param url: 所需下载的文件链接
        :param filename: 输出的文件名称
        :return:
        """

        if filename is None:
            filename = self._get_filename(url)

        # 判断当前url文件是否已经下载
        out_path = os.path.join(self.out_dir, filename)
        if os.path.exists(out_path):
            if wait_time is not None:
                return wait_time

        call([Config.idm_path, '/d', url, '/p', self.out_dir, '/f', filename, '/a', '/n'])
        call([Config.idm_path, '/s'])

        if wait_time is not None:
            return wait_time + 0
        """
        IDM命令行说明:
        cmd: idman /s
        /s: 开始(start)下载添加IDM中下载队列中的所有文件
        cmd: idman /d URL [/p 本地_路径] [/f 本地_文件_名] [/q] [/h] [/n] [/a]
        /d URL: 从下载链接url中下载文件
        /p 本地_路径: 下载好的文件保存在哪个本地路径(文件夹路径/目录)
        /f 本地_文件_名: 下载好的文件输出/保存的文件名称
        /q: IDM 将在成功下载之后退出。这个参数只为第一个副本工作
        /h: IDM 将在正常下载之后挂起您的连接(下载窗口最小化/隐藏到系统托盘)
        /n: IDM不要询问任何问题不要弹窗,安静地/后台地下载
        /a: 添加一个指定的文件, 用/d到下载队列, 但是不要开始下载.(即添加一个下载链接到IDM的下载队列中, 可通过/s启动队列的所有下载链接文件的下载)
        """

    def _monitor(self):
        while True:
            for item in self.downloading_links.copy():  # .copy()是为了防止在循环过程中一边迭代downloading_links一边删除其中元素
                self._check_update_download(item)
            self._update()  # 更新和保存下载状态
            self.pbar.refresh()  # 更新下载进度条状态
            call([idm_path, '/s'])  # 防止IDM意外停止下载

            # 直到等待下载链接和正在下载链接中均无下载链接说明下载完毕.
            if not self.pending_links and not self.downloading_links:
                self.pbar.close()  # 关闭下载进度条
                print('所有链接均下载完毕.')
                break

            time.sleep(self.monitor_interval)

    def _check_update_download(self, downloading_item):
        """
        检查当前项是否已经下载, 成功下载则更新该项的状态并返回True, 否则不操作并返回False
        :param downloading_item: <正在下载链接>中的当前项
        :return: Bool
        """

        out_path = os.path.join(self.out_dir, downloading_item['filename'])

        # 检查当前文件是否存在(是否下载)
        if os.path.exists(out_path):  # 存在(即已经下载过了)
            # 更新当前文件的下载状态
            self.completed_links.append(downloading_item)
            self.downloading_links.remove(downloading_item)
            self._update_pbar(downloading_item['filename'])  # 更新下载进度条
            # print('文件: {} - 下载完成({}/{})'.format(downloading_item['filename'], len(self.completed_links), len(self.links)))
            # 从<阻塞/等待下载链接>中取链接到<正在下载链接>中(如果pending_links中还有链接)
            if self.pending_links:
                self._pending2downloading()  # 取<阻塞/等待下载链接>中的链接添加到<正在下载链接>中

            return True
        return False

    def _download(self, item):
        self.download_single(item['url'], item['filename'])

    def _pending2downloading(self):
        """
        从阻塞的<等待下载链接>中取链接<正在下载链接>中,若所取链接已经下载则跳过
        :return:
        """

        for item in self.pending_links.copy():
            out_path = os.path.join(self.out_dir, item['filename'])
            # 判断当前下载链接是否已经被下载
            if os.path.exists(out_path):  # 若当前链接已经下载, 跳过下载并更新其状态
                self.pending_links.remove(item)
                self.completed_links.append(item)
                self._update_pbar(item['filename'])
                continue
            elif self.downloading_links.__len__() < self.concurrent_downloads:  # 若当前链接未被下载且当前下载数量小于并发量
                self.pending_links.remove(item)
                self.downloading_links.append(item)
                self._download(item)
            else:
                # 若elif中不能执行, 说明当前项未下载, 且当前同时下载的文件数量已达到最大, 因此不需要迭代下去了
                break


    def should_add_link(self, item=None, url=None, filename=None):
        """
        依据item/url/filename判断该链接此前已经被添加过, 如果添加过那么返回False, 如果没有被添加过则返回True
        :param item: 形如dict{'url': str, 'filename': str}的item
        :param url: 包含单个下载链接的字符串
        :param filename: 包含输出文件名称的字符串
        :return: Bool
        """

        if not self.links:
            return True, {}

        # 依据item判断
        if item is not None:
            for cur_item in self.links:
                if cur_item == item:
                    return False, item
            return True, {}

        # 依据链接判断
        if url is not None:
            for item in self.links:
                if item['url'] == url:
                    return False, item
            return True, {}

        # 依据输出文件名称判断
        if filename is not None:
            for item in self.links:
                if item['filename'] == filename:
                    return False, item
            return True, {}

    def _update_pbar(self, filename):
        """
        更新下载进度条
        :return:
        """

        self.pbar.n = len(self.completed_links)  # 更新已完成地数目
        self.pbar.set_postfix_str('当前下载文件: {}'.format(filename))
        # self.pbar.refresh()  # 立即刷新显示


def img_mosaic(mosaic_paths: list, mosaic_ds_name: str, return_all: bool = True, img_nodata: Union[int, float] = np.nan,
               img_type: Union[np.int32, np.float32, None] = np.float32, unit_conversion: bool = False,
               scale_factor_op: str = 'multiply', mosaic_mode: str = 'last'):
    """
    该函数用于对列表中的所有HDF4文件进行镶嵌
    :param mosaic_paths: 多个HDF4文件路径组成的字符串列表
    :param mosaic_ds_name: 待镶嵌的数据集名称
    :param return_all: 是否一同返回仿射变换、镶嵌数据集的坐标系等参数
    :param img_nodata: 影像中的无效值设置
    :param img_type: 待镶嵌影像的数据类型
    :param unit_conversion: 是否进行单位换算
    :param scale_factor_op: 比例因子的运算符, 默认是乘以(可选: multiply, divide), 该参数尽在unit_conversion为True时生效
    # :param mosaic_mode: 镶嵌模式, 默认是Last(即如果有存在像元重叠, mosaic_paths中靠后影像的像元将覆盖其),
    #     可选: last, mean, max, min, 镶嵌策略默认是last模式,
    :return: 默认返回镶嵌好的数据集
    """

    # 获取镶嵌范围
    x_mins, x_maxs, y_mins, y_maxs = [], [], [], []
    for mosaic_path in mosaic_paths:
        hdf = SD(mosaic_path)  # 默认只读
        # 获取元数据
        metadata = hdf.attributes()['StructMetadata.0']
        # 获取角点信息
        ul_pt = [float(x) for x in re.search(r'UpperLeftPointMtrs=\((.*?)\)', metadata).group(1).split(',')]
        lr_pt = [float(x) for x in re.search(r'LowerRightMtrs=\((.*?)\)', metadata).group(1).split(',')]
        x_mins.append(ul_pt[0])
        x_maxs.append(lr_pt[0])
        y_mins.append(lr_pt[1])
        y_maxs.append(ul_pt[1])
    else:
        # 计算分辨率
        col = int(re.search(r'XDim=(.*?)\n', metadata).group(1))
        row = int(re.search(r'YDim=(.*?)\n', metadata).group(1))
        x_res = (lr_pt[0] - ul_pt[0]) / col
        y_res = (ul_pt[1] - lr_pt[1]) / row
        # 如果img_type没有指定, 那么数据类型默认为与输入相同
        if img_type is None:
            img_type = hdf.select(mosaic_ds_name)[:].dtype
        # 获取数据集的坐标系参数并转化为proj4字符串格式
        projection_param = [float(_param) for _param in re.findall(r'ProjParams=\((.*?)\)', metadata)[0].split(',')]
        """
        Sinusoidal Equal Area (INSYS = 16): TPARIN( 1 ) and TPARIN( 6:8 ) used.
            1. Radius of sphere of reference
            2. (unused)
            3. (unused)
            4. (unused)
            5. Longitude of central meridian
            6. Latitude of central meridian
            7. False easting in the same units as the semimajor axis
            8. False northing in the same units as the semimajor axis
            9. (unused)...
        """
        mosaic_img_proj4 = "+proj={} +R={:0.4f} +lon_0={:0.4f} +lat_0={:0.4f} +x_0={:0.4f} " \
                           "+y_0={:0.4f} +units=m +no_defs".format('sinu', projection_param[0], projection_param[4],
                                                                   projection_param[5], projection_param[6],
                                                                   projection_param[7])
        """
        proj4语法:
        +proj=, 坐标系(可填: latlong, sinu等)
        +R=, 参考椭球体的半径<如果椭球体的长半轴和短半轴不一样, 可以分别设置即: +a=, +b=>
        +lon_0=, 中央经线的经度
        +lat_0=, 中央纬线的维度
        +x_0=, 投影坐标系原点的东西偏移(东为正)
        +y_0=, 投影坐标系原点的南北偏移(北为正)
        +units=, 坐标系单位(可填: m, deg等)
        +no_defs, 禁止加载默认参数, 避免冲突
        """
        # 关闭文件, 释放资源
        hdf.end()
    x_min, x_max, y_min, y_max = min(x_mins), max(x_maxs), min(y_mins), max(y_maxs)

    # 镶嵌
    col = ceil((x_max - x_min) / x_res)
    row = ceil((y_max - y_min) / y_res)
    sum_array = np.zeros((row, col), dtype=np.float32)
    count_array = np.zeros((row, col), dtype=np.int16)
    for ix, mosaic_path in enumerate(mosaic_paths):
        hdf = SD(mosaic_path)
        target_ds = hdf.select(mosaic_ds_name)

        # 读取数据集和预处理
        target = np.ma.array(target_ds.get())
        valid_range = target_ds.attributes()['valid_range']
        target.mask = (target < valid_range[0]) | (target > valid_range[1])

        if unit_conversion:
            scale_factor = target_ds.attributes()['scale_factor']
            add_offset = target_ds.attributes()['add_offset']
            if scale_factor_op == 'multiply':
                target = target * scale_factor + add_offset
            elif scale_factor_op == 'divide':
                target = target / scale_factor + add_offset

        # 计算当前瓦片在总图中的位置
        start_row = floor((y_max - (y_maxs[ix] - y_res / 2)) / y_res)
        start_col = floor(((x_mins[ix] + x_res / 2) - x_min) / x_res)
        end_row = start_row + target.shape[0]
        end_col = start_col + target.shape[1]

        # 定义目标区域的切片
        roi_slice = (slice(start_row, end_row), slice(start_col, end_col))

        # 仅对有效值进行累加和计数
        sum_array[roi_slice] += np.ma.filled(target, 0)
        count_array[roi_slice] += ~target.mask

        # 释放资源
        target_ds.endaccess()
        hdf.end()

    mask_where = count_array == 0
    count_array[mask_where] = 1  # 避免被除数为0的错误
    mosaic_img = sum_array / count_array
    mosaic_img = np.ma.masked_where(mask_where, mosaic_img)

    if return_all:
        extrent_geo = [  # 地理覆盖范围(四个角点, 左上角点顺时针开始)
            [x_min, x_max, x_max, x_min],
            [y_max, y_max, y_min, y_min]
        ]
        return mosaic_img, [x_min, x_res, 0, y_max, 0, -y_res], mosaic_img_proj4, extrent_geo

    return mosaic_img



def img_warp(src_img: np.ndarray, out_path: str, transform: list, src_proj4: str, out_res: Union[float, None] = None,
             nodata_value: Union[int, float] = np.nan, resample: str = 'bilinear', dst_epsg=4326) -> None:
    """
    该函数用于对正弦投影下的栅格矩阵进行重投影(GLT校正), 得到WGS84坐标系下的栅格矩阵并输出为TIFF文件
    :param src_img: 待重投影的栅格矩阵
    :param out_path: 输出路径
    :param transform: 仿射变换参数([x_min, x_res, 0, y_max, 0, -y_res], 旋转参数为0是常规选项)
    :param out_res: 输出的分辨率(栅格方形)
    :param nodata_value: 设置为NoData的数值
    :param out_type: 输出的数据类型
    :param resample: 重采样方法(默认是最近邻, ['nearest', 'bilinear', 'cubic'])
    :param src_proj4: 表达源数据集(src_img)的坐标系参数(以proj4字符串形式)
    :return: None
    """

    # 输出数据类型
    if np.issubdtype(src_img.dtype, np.integer):
        out_type = gdal.GDT_Int16
        nodata_value = np.iinfo(np.int16).max
    elif np.issubdtype(src_img.dtype, np.floating):
        out_type = gdal.GDT_Float32
        nodata_value = np.nan
    else:
        raise ValueError("当前待校正数组类型为不支持的数据类型")

    # if nodata_value is None:
    #     nodata_value = np.iinfo(out_type)
    if isinstance(src_img, np.ma.MaskedArray):
        src_img = src_img.filled(nodata_value)

    resamples = {'nearest': gdal.GRA_NearestNeighbour, 'bilinear': gdal.GRA_Bilinear, 'cubic': gdal.GRA_Cubic}
    # 原始数据集创建(正弦投影)
    driver = gdal.GetDriverByName('MEM')  # 在内存中临时创建
    src_ds = driver.Create("", src_img.shape[1], src_img.shape[0], 1, out_type)  # 注意: 先传列数再传行数, 1表示单波段
    srs = osr.SpatialReference()
    srs.ImportFromProj4(src_proj4)
    """
    对于src_proj4, 依据元数据StructMetadata.0知:
        Projection=GCTP_SNSOID; ProjParams=(6371007.181000,0,0,0,0,0,0,0,0,0,0,0,0)
    或数据集属性(MODIS_Grid_8Day_1km_LST/Data_Fields/Projection)知:
        :grid_mapping_name = "sinusoidal";
        :longitude_of_central_meridian = 0.0; // double
        :earth_radius = 6371007.181; // double
    """
    src_ds.SetProjection(srs.ExportToWkt())  # 设置投影信息
    src_ds.SetGeoTransform(transform)  # 设置仿射参数
    b1 = src_ds.GetRasterBand(1)
    b1.WriteArray(src_img)  # 写入数据
    b1.ComputeStatistics(False)  # 计算统计数据, 方便显示
    b1.SetNoDataValue(nodata_value)
    # 重投影信息(默认WGS84)
    dst_srs = osr.SpatialReference()
    dst_srs.ImportFromEPSG(dst_epsg)
    # 重投影
    options = gdal.WarpOptions(
        dstSRS=dst_srs,  # 输出的空间参考系
        outputBounds=[-180, -60, 180, 90],
        xRes=out_res,  # 输出的X轴方向上的分辨率
        yRes=out_res,  # 输出的y轴方向上的分辨率
        dstNodata=nodata_value,  # 栅格矩阵中的无效值
        outputType=out_type,  # 输出的数据类型
        multithread=True,  # 多线程处理
        resampleAlg=resamples[resample],  # 重采样分辨率
        # warpMemoryLimit=100 * 1024 * 1024
    )
    dst_ds = gdal.Warp(out_path, src_ds, options=options)

    if dst_ds:  # 释放缓存和资源
        dst_ds.FlushCache()
        src_ds, dst_ds = None, None

def clip_mask(tiff_path, shp_path, out_path, out_res, resample_alg=2, remove_src=False, dst_nodata=None):
    """
    将输入的geotiff文件进行裁剪、掩膜
    :param tiff_path: 输入的geotiff文件的路径
    :param shp_path: 掩膜所需的shp文件的路径
    :param out_path: 处理好的tiff文件的输出路径
    :param out_res: 输出分辨率
    :param resample_alg: 重采样算法(0: 最近邻; 1: 双线性; 2: 三次卷积)
    :param remove_src: 是否删除源文件即tiff_path
    :return: None
    """

    options = gdal.WarpOptions(
        xRes=out_res,
        yRes=out_res,
        resampleAlg=resample_alg,  # 重采样算法
        cutlineDSName=shp_path,
        cropToCutline=True,  # True表示裁剪到矩形范围后继续掩膜, False表示只裁剪到矩形范围
        targetAlignedPixels=True,  # 对齐像元
        dstNodata=dst_nodata,
    )
    ds = gdal.Warp(out_path, tiff_path, options=options)
    ds = None

    if remove_src:
        os.remove(tiff_path)

    with rio.open(out_path) as f:
        b1 = f.read(1)


def write_png(arr: np.ndarray, out_path):
    """
    将栅格矩阵输出为png文件
    :param arr: 栅格矩阵
    :param out_path: 输出路径
    :return: None
    """

    plt.imsave(out_path, arr)