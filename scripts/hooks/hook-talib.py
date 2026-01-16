"""
PyInstaller hook for talib (TA-Lib)

确保 talib.stream 和其他子模块被正确收集。
vnpy.trader.utility 需要 talib.stream。
"""

from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs

# 收集 talib 的所有子模块
hiddenimports = collect_submodules('talib')

# 确保关键模块被包含
hiddenimports += [
    'talib',
    'talib.stream',
    'talib.abstract',
    'talib.deprecated',
]

# 收集 talib 的动态库（.pyd 文件）
binaries = collect_dynamic_libs('talib')
