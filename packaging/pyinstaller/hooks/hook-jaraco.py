"""
PyInstaller hook for jaraco (namespace package in setuptools._vendor)

jaraco is a namespace package located in setuptools/_vendor/jaraco.
This hook ensures all jaraco submodules are correctly collected.
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os
from pathlib import Path

hiddenimports = [
    'jaraco.text',
    'jaraco.functools',
    'jaraco.context',
    'jaraco.collections',
]

# Collect all jaraco submodules
try:
    hiddenimports += collect_submodules('jaraco')
except Exception:
    pass

# Collect data files (e.g., Lorem ipsum.txt)
datas = []
try:
    datas += collect_data_files('jaraco.text')
except Exception:
    pass

# Also try to collect from setuptools._vendor.jaraco
try:
    import setuptools
    jaraco_dir = Path(setuptools.__file__).parent / '_vendor' / 'jaraco'
    if jaraco_dir.exists():
        datas.append((str(jaraco_dir), 'setuptools/_vendor/jaraco'))
except Exception:
    pass
