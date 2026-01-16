"""
PyInstaller hook for pkg_resources

pkg_resources uses dynamic sys.path extension to access setuptools/_vendor/jaraco.
PyInstaller cannot automatically detect this import method.

This hook explicitly collects jaraco-related modules and adds the vendor directory.
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os
from pathlib import Path

# Hidden imports required by pkg_resources
hiddenimports = [
    # Modules directly used by pkg_resources
    'jaraco',
    'jaraco.text',
    'jaraco.functools',
    'jaraco.context',
    'jaraco.collections',
    # Standard tools
    'more_itertools',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
]

# Try to collect jaraco submodules
try:
    hiddenimports += collect_submodules('jaraco')
except Exception:
    pass

# Collect setuptools._vendor.jaraco
try:
    hiddenimports += collect_submodules('setuptools._vendor.jaraco')
except Exception:
    pass

# Add setuptools/_vendor directory as data
# pkg_resources dynamically adds this directory to sys.path at runtime
datas = []
try:
    import setuptools
    vendor_dir = Path(setuptools.__file__).parent / '_vendor'
    if vendor_dir.exists():
        # Add the entire _vendor directory
        datas.append((str(vendor_dir), 'setuptools/_vendor'))
except Exception:
    pass
