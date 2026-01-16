"""
环境配置脚本

用法:
    .venv/Scripts/python.exe scripts/setup_env.py

功能:
    1. 从 resources/packages 安装预编译的 TA-Lib
    2. 安装其他需要从 veighna_studio 复制的包
"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESOURCES_PACKAGES = PROJECT_ROOT / "resources" / "packages"
VENV_SITE_PACKAGES = PROJECT_ROOT / ".venv" / "Lib" / "site-packages"


def install_local_packages():
    """从 resources/packages 安装本地包"""
    if not RESOURCES_PACKAGES.exists():
        print(f"错误: {RESOURCES_PACKAGES} 不存在")
        return False
    
    if not VENV_SITE_PACKAGES.exists():
        print(f"错误: {VENV_SITE_PACKAGES} 不存在，请先创建虚拟环境")
        return False
    
    print("=" * 60)
    print("从 resources/packages 安装本地包")
    print("=" * 60)
    
    installed = []
    for item in RESOURCES_PACKAGES.iterdir():
        if item.is_dir():
            target = VENV_SITE_PACKAGES / item.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
            installed.append(item.name)
            print(f"  已安装: {item.name}")
    
    print("=" * 60)
    print(f"完成！安装了 {len(installed)} 个包")
    print("=" * 60)
    return True


def verify_talib():
    """验证 TA-Lib 是否正常工作"""
    print("\n验证 TA-Lib...")
    try:
        import talib
        import numpy as np
        data = np.random.random(100)
        result = talib.SMA(data, timeperiod=10)
        print(f"  TA-Lib 测试通过！SMA 计算结果: {result[-1]:.4f}")
        return True
    except Exception as e:
        print(f"  TA-Lib 测试失败: {e}")
        return False


def main():
    # 安装本地包
    if not install_local_packages():
        sys.exit(1)
    
    # 验证 TA-Lib
    verify_talib()
    
    print("\n环境配置完成！")


if __name__ == "__main__":
    main()
