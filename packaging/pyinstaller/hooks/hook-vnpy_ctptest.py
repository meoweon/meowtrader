"""
PyInstaller hook for vnpy_ctptest

收集 vnpy_ctptest 的二进制文件（DLL 和 PYD）
"""
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

# 收集所有动态库（.dll 和 .pyd）
binaries = collect_dynamic_libs('vnpy_ctptest')

# 收集数据文件
datas = collect_data_files('vnpy_ctptest')
