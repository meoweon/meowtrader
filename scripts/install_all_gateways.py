"""
安装所有 Gateway 依赖（开发环境全量安装）

这个脚本会安装所有失败的 Gateway 依赖包
"""
import subprocess
import sys
import io
from pathlib import Path

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent

# 需要安装的 Gateway 依赖包
GATEWAY_PACKAGES = [
    "vnpy-ctptest>=1.0.0",
    "vnpy-femas>=1.0.0",
    "vnpy-uft>=1.0.0",
    "vnpy-tts>=1.0.0",
    "vnpy-rohon>=1.0.0",
    "vnpy-jees>=1.0.0",
    "vnpy-tora>=1.0.0",
    "vnpy-xtp>=1.0.0",
    "vnpy-sec>=1.0.0",
    "vnpy-hts>=1.0.0",
    "vnpy-ksgold>=1.0.0",
    "vnpy-da>=1.0.0",
    "vnpy-ib>=10.40.0",
    "ibapi",  # IB 官方 API
]

def main():
    print("=" * 60)
    print("安装所有 Gateway 依赖（开发环境全量安装）")
    print("=" * 60)
    
    # 使用 uv pip install 安装
    cmd = ["uv", "pip", "install"] + GATEWAY_PACKAGES
    
    print(f"\n执行: {' '.join(cmd)}\n")
    
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        encoding="utf-8",
        errors="replace"
    )
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ 所有依赖安装完成！")
        print("=" * 60)
        print("\n注意：")
        print("  - 部分 Gateway 可能需要额外的 DLL 文件（tts, rohon, sec, hts, jees）")
        print("  - vnpy_ib 可能需要特定版本的 ibapi（当前版本可能不兼容）")
        print("  - vnpy_da 需要 pyda，但 API 可能不匹配")
        print("  - vnpy_ksgold 需要额外的 C 扩展模块")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ 部分依赖安装失败")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
