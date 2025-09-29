# @Author  : ChaoQiezi
# @Time    : 2025/9/28 下午10:20
# @Email   : chaoqiezi.one@qq.com
# @Wechat  : GIS茄子
# @FileName: dead_code

"""
This script is used to 
"""

import numpy as np
import pandas as pd

from utils import scatter_plot

# 准备数据
np.random.seed(42)
ds = np.random.rand(10, 2)
out_path = r'E:\MyTEMP\scatter.png'

df = pd.DataFrame(ds, columns=['dem', 'ndvi'])
df['gt_zero'] = True
scatter_plot(df, 'dem', 'ndvi', 'gt_zero', out_path, 'MyTemp', 'DEM', 'NDVI')
