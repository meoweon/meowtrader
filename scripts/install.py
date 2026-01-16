"""
MeowTrader 依赖安装脚本

用法:
    .venv/Scripts/python.exe  scripts/install.py           # 安装基础依赖
    .venv/Scripts/python.exe  scripts/install.py --dev     # 安装开发依赖
    .venv/Scripts/python.exe  scripts/install.py --all     # 安装所有可选依赖
    .venv/Scripts/python.exe  scripts/install.py --extra ctp  # 安装指定可选依赖
"""

import shutil
import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


def check_uv() -> bool:
    """检查 uv 是否已安装"""
    uv_path = shutil.which("uv")
    if uv_path:
        # 获取版本
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True, text=True, encoding="utf-8"
        )
        if result.returncode == 0:
            print(f"Found uv: {result.stdout.strip()}")
            return True
    
    print("错误: uv 未安装")
    print("请先安装 uv: https://docs.astral.sh/uv/getting-started/installation/")
    print("  Windows: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
    print("  Linux/macOS: curl -LsSf https://astral.sh/uv/install.sh | sh")
    return False


def run_command(cmd: list[str], description: str = "") -> bool:
    """执行命令"""
    if description:
        print(f"\n{description}")
        print("-" * 60)
    
    print(f"执行: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        encoding="utf-8",
        errors="replace"
    )
    
    if result.returncode == 0:
        print("[OK] 成功")
        return True
    else:
        print("[FAIL] 失败")
        return False


def install_base_deps():
    """安装基础依赖"""
    print("\n" + "=" * 60)
    print("安装基础依赖...")
    print("=" * 60)
    
    # uv sync 会自动读取 pyproject.toml 并安装 dependencies 中的包
    return run_command(
        ["uv", "sync"],
        "同步项目依赖"
    )


def install_dev_deps():
    """安装开发依赖"""
    print("\n" + "=" * 60)
    print("安装开发依赖...")
    print("=" * 60)
    
    return run_command(
        ["uv", "sync", "--extra", "dev"],
        "安装开发工具"
    )


def get_available_extras() -> set[str]:
    """获取可用的 optional dependencies 名称"""
    try:
        import tomllib  # Python 3.11+
        with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)
    except ImportError:
        try:
            import tomli
            with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
                data = tomli.load(f)
        except ImportError:
            return set()
    
    optional_deps = data.get("project", {}).get("optional-dependencies", {})
    return set(optional_deps.keys())


def install_optional_deps(*extras: str):
    """安装可选依赖"""
    if not extras:
        return True
    
    # 验证 extras 是否存在
    available = get_available_extras()
    invalid = [e for e in extras if e not in available]
    if invalid:
        print(f"错误: 未知的可选依赖: {', '.join(invalid)}")
        print(f"可用选项: {', '.join(sorted(available))}")
        return False
    
    print("\n" + "=" * 60)
    print(f"安装可选依赖: {', '.join(extras)}")
    print("=" * 60)
    
    # 为每个 extra 调用 uv sync
    success = True
    for extra in extras:
        if not run_command(
            ["uv", "sync", "--extra", extra],
            f"安装 {extra} 依赖"
        ):
            success = False
    
    return success


def install_all_optional():
    """安装所有可选依赖"""
    # 从 pyproject.toml 读取所有 optional-dependencies
    try:
        import tomllib  # Python 3.11+
        with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)
    except ImportError:
        # Python 3.10 使用 tomli
        try:
            import tomli
            with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
                data = tomli.load(f)
        except ImportError:
            print("错误: 需要 tomllib (Python 3.11+) 或 tomli (Python 3.10)")
            print("安装 tomli: uv pip install tomli")
            return False
    
    optional_deps = data.get("project", {}).get("optional-dependencies", {})
    
    # 排除 dev 和组合依赖
    exclude = {"dev", "all-db", "all-datafeed"}
    extras = [k for k in optional_deps.keys() if k not in exclude]
    
    print("\n" + "=" * 60)
    print(f"安装所有可选依赖 ({len(extras)} 个)...")
    print("=" * 60)
    
    # 使用 uv pip install 逐个安装，跳过失败的
    success_count = 0
    fail_count = 0
    
    for extra in extras:
        deps = optional_deps[extra]
        if not deps:
            continue
        
        print(f"\n安装 {extra}...")
        cmd = ["uv", "pip", "install"] + deps
        result = run_command(cmd, "")
        
        if result:
            success_count += 1
        else:
            fail_count += 1
            print(f"  [跳过] {extra} 安装失败（可能版本冲突或包不存在）")
    
    print("\n" + "=" * 60)
    print(f"安装完成: 成功 {success_count} 个，失败 {fail_count} 个")
    print("=" * 60)
    
    return fail_count == 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MeowTrader 依赖安装脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  .venv/Scripts/python.exe  scripts/install.py                    # 安装基础依赖
  .venv/Scripts/python.exe  scripts/install.py --dev              # 安装开发依赖
  .venv/Scripts/python.exe  scripts/install.py --all              # 安装所有可选依赖
  .venv/Scripts/python.exe  scripts/install.py --extra ctp        # 安装 CTP 依赖
  .venv/Scripts/python.exe  scripts/install.py --extra ib         # 安装 IB 依赖
        """
    )
    
    parser.add_argument(
        "--dev", action="store_true",
        help="安装开发依赖"
    )
    
    parser.add_argument(
        "--all", action="store_true",
        help="安装所有可选依赖"
    )
    
    parser.add_argument(
        "--extra", action="append", metavar="NAME",
        help="安装指定的可选依赖（可多次使用，如 --extra ctp --extra ib）"
    )
    
    args = parser.parse_args()
    
    # 检查 uv 是否安装
    if not check_uv():
        return 1
    
    success = True
    
    # 基础依赖（总是安装）
    if not install_base_deps():
        success = False
    
    # 开发依赖
    if args.dev:
        if not install_dev_deps():
            success = False
    
    # 所有可选依赖
    if args.all:
        if not install_all_optional():
            success = False
    
    # 指定的可选依赖
    if args.extra:
        if not install_optional_deps(*args.extra):
            success = False
    
    # 总结
    print("\n" + "=" * 60)
    if success:
        print("[OK] 所有依赖安装完成!")
    else:
        print("[FAIL] 部分依赖安装失败，请检查错误信息")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
