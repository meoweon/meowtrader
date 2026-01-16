"""
MeowTrader 打包脚本

用法:
    .venv/Scripts/python.exe  scripts/build.py                    # 打包开发版（默认 all）
    .venv/Scripts/python.exe  scripts/build.py --all              # 打包开发版（启用所有模块）
    .venv/Scripts/python.exe  scripts/build.py --basic            # 打包基础版
    .venv/Scripts/python.exe  scripts/build.py --pro              # 打包专业版
    .venv/Scripts/python.exe  scripts/build.py --custom          # 打包定制版
    .venv/Scripts/python.exe  scripts/build.py --debug            # 打包调试版（带控制台）
    .venv/Scripts/python.exe  scripts/build.py --clean            # 清理打包文件
    .venv/Scripts/python.exe  scripts/build.py --show             # 显示已安装的 vnpy 包

注意:
    - 构建会根据 config/edition.<edition>.json 配置文件自动获取依赖
    - 安装依赖请使用: uv sync --extra <gateway_name>
"""

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
# spec 文件会保存在 BUILD_DIR 中（通过 --specpath 指定）
SPEC_DIR = BUILD_DIR

# 应用信息
APP_NAME = "MeowTrader"
APP_VERSION = "0.1.0"

# 图标文件路径（优先级：resources/icon.ico > vendor/vnpy/trader/ui/ico/vnpy.ico）
# 如果使用自定义图标，请将 .ico 文件放在 meowtrader/resources/icon.ico
_ICON_CANDIDATES = [
    PROJECT_ROOT / "resources" / "icon.ico",  # 自定义图标（优先）
    PROJECT_ROOT / "vendor" / "vnpy" / "trader" / "ui" / "ico" / "lbkj.ico",  # 默认图标
]

# 查找存在的图标文件
APP_ICON = None
for icon_path in _ICON_CANDIDATES:
    if icon_path.exists():
        APP_ICON = icon_path
        break

# 如果都找不到，使用第一个作为默认（打包时会报错，但至少不会崩溃）
if APP_ICON is None:
    APP_ICON = _ICON_CANDIDATES[0]

# ==================== Gateway 名称到依赖包的映射 ====================
# 映射 gateway name 到 pyproject.toml 中的 optional-dependencies 名称
# 注意：vendor 中的 gateway（okx, binance_*）不需要额外依赖
GATEWAY_DEPENDENCY_MAP = {
    # 国内期货
    "ctp": "ctp",
    "ctp_test": "ctp_test",
    "mini": "mini",
    "femas": "femas",
    "uft": "uft",
    "esunny": "esunny",
    "tts": "tts",
    "rohon": "rohon",
    "jees": "jees",
    "tora_futures": "tora",  # 使用 tora 包
    # 国内股票/期权
    "xtp": "xtp",
    "tora_stock": "tora",  # 使用 tora 包
    "tora_option": "tora",  # 使用 tora 包
    "sopt": "sopt",
    "sec": "sec",
    "hts": "hts",
    # 国内贵金属
    "ksgold": "ksgold",
    # 国际/外盘
    "ib": "ib",
    "tap": "tap",
    "da": "da",
    # 数据服务
    "tqsdk": "tqsdk",
    "xt": "xt",
    # 特殊接口（rpc 在 vendor 中，不需要额外依赖）
}


def load_edition_config(edition: str) -> dict[str, Any]:
    """
    加载 edition 配置文件
    
    Args:
        edition: 版本名称 (all/basic/pro/custom)
    
    Returns:
        配置字典
    """
    config_file = PROJECT_ROOT / "config" / f"edition.{edition}.json"
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    
    with open(config_file, encoding="utf-8") as f:
        return json.load(f)


def get_dependencies_from_config(edition: str) -> list[str]:
    """
    从 edition 配置文件中获取依赖列表
    
    Args:
        edition: 版本名称 (all/basic/pro/custom)
    
    Returns:
        依赖包名列表（如 ["vnpy-ctp", "vnpy-ib"]）
    """
    config = load_edition_config(edition)
    gateways = config.get("gateways", [])
    
    # 收集需要的依赖
    dependencies = set()
    
    for gw_config in gateways:
        gw_name = gw_config.get("name")
        if not gw_name:
            continue
        
        # 检查是否需要额外依赖
        if gw_name in GATEWAY_DEPENDENCY_MAP:
            dep_name = GATEWAY_DEPENDENCY_MAP[gw_name]
            # 从 pyproject.toml 读取依赖版本
            deps = _get_dependency_from_pyproject(dep_name)
            dependencies.update(deps)
    
    return sorted(dependencies)


def _get_dependency_from_pyproject(extra_name: str) -> list[str]:
    """
    从 pyproject.toml 读取 optional-dependencies 中的依赖
    
    Args:
        extra_name: optional-dependencies 的名称（如 "ctp", "ib"）
    
    Returns:
        依赖列表（如 ["vnpy-ctp>=6.7.0"]）
    """
    try:
        import tomli  # Python 3.11+
    except ImportError:
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            # 降级方案：使用 json 或手动解析
            # 这里简化处理，直接返回包名
            package_map = {
                "ctp": ["vnpy-ctp>=6.7.0"],
                "ctp_test": ["vnpy-ctptest>=1.0.0"],
                "mini": ["vnpy-mini>=1.0.0"],
                "femas": ["vnpy-femas>=1.0.0"],
                "uft": ["vnpy-uft>=1.0.0"],
                "esunny": ["vnpy-esunny>=1.0.0"],
                "tts": ["vnpy-tts>=1.0.0"],
                "rohon": ["vnpy-rohon>=1.0.0"],
                "jees": ["vnpy-jees>=1.0.0"],
                "tora": ["vnpy-tora>=1.0.0"],
                "xtp": ["vnpy-xtp>=1.0.0"],
                "sopt": ["vnpy-sopt>=1.0.0"],
                "sec": ["vnpy-sec>=1.0.0"],
                "hts": ["vnpy-hts>=1.0.0"],
                "ksgold": ["vnpy-ksgold>=1.0.0"],
                "tap": ["vnpy-tap>=1.0.0"],
                "ib": ["vnpy-ib>=10.40.0"],
                "da": ["vnpy-da>=1.0.0"],
                "tqsdk": ["vnpy-tqsdk>=3.8.0"],
                "xt": ["vnpy-xt>=1.4.0"],
            }
            return package_map.get(extra_name, [])
    
    # 使用 tomli/tomllib 解析 pyproject.toml
    pyproject_file = PROJECT_ROOT / "pyproject.toml"
    if not pyproject_file.exists():
        return []
    
    with open(pyproject_file, "rb") as f:
        if "tomli" in sys.modules:
            data = tomli.load(f)
        else:
            data = tomllib.load(f)
    
    optional_deps = data.get("project", {}).get("optional-dependencies", {})
    return optional_deps.get(extra_name, [])


def list_editions():
    """列出可用的版本配置"""
    print("可用的版本配置:")
    print("-" * 60)
    editions = ["all", "basic", "pro", "custom"]
    for edition in editions:
        try:
            config = load_edition_config(edition)
            product_info = config.get("product", {})
            name = product_info.get("name", edition)
            gateways = config.get("gateways", [])
            apps = config.get("apps", [])
            deps = get_dependencies_from_config(edition)
            
            print(f"  {edition:10} - {name}")
            print(f"             Gateway: {len(gateways)} 个, App: {len(apps)} 个")
            if deps:
                print(f"             依赖: {', '.join(deps)}")
            else:
                print(f"             依赖: 无额外依赖（vendor 中已有）")
            print()
        except FileNotFoundError:
            print(f"  {edition:10} - 配置文件不存在")
            print()
    print("提示: 安装依赖请使用: uv sync --extra <gateway_name>")
    print()


def show_installed():
    """显示当前已安装的 vnpy 相关包"""
    print("当前已安装的 vnpy 包:")
    print("-" * 60)
    
    # 尝试使用 uv pip list（uv 是独立命令，不是 Python 模块）
    uv_cmd = shutil.which("uv")
    
    if uv_cmd:
        # 使用 uv 命令
        result = subprocess.run(
            ["uv", "pip", "list"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, encoding="utf-8"
        )
    else:
        # 回退到普通 pip
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, encoding="utf-8"
        )
    
    found = False
    for line in result.stdout.splitlines():
        line_lower = line.lower().strip()
        # 跳过表头
        if line_lower.startswith("package") or line_lower.startswith("---"):
            continue
        # 查找包含 vnpy 的行
        if "vnpy" in line_lower:
            # 格式化输出：包名 版本
            parts = line.split()
            if len(parts) >= 2:
                pkg_name = parts[0]
                pkg_version = parts[1]
                print(f"  {pkg_name:30} {pkg_version}")
            else:
                print(f"  {line}")
            found = True
    
    if not found:
        print("  (未找到 vnpy 相关包)")
        print("\n提示: 使用 '.venv/Scripts/python.exe  scripts/install.py --profile <profile>' 安装依赖")


def clean():
    """清理打包文件"""
    print("Cleaning build files...")
    
    # 处理权限错误（如 exe 正在运行）
    def handle_remove_readonly(func, path, exc):
        """处理只读文件的删除"""
        import stat
        if func in (os.unlink, os.remove, os.rmdir):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except (PermissionError, OSError):
                pass
    
    for path in [DIST_DIR, BUILD_DIR]:
        if path.exists():
            try:
                shutil.rmtree(path, onerror=handle_remove_readonly)
                print(f"  Removed: {path}")
            except PermissionError as e:
                print(f"  Warning: Cannot remove {path}: {e}")
                print("           请确保没有正在运行打包后的程序，然后手动删除该目录")
            except Exception as e:
                print(f"  Warning: Failed to remove {path}: {e}")
    
    # 清理 .spec 文件（可能在根目录或 build 目录）
    spec_patterns = [
        PROJECT_ROOT.glob("*.spec"),  # 根目录下的 .spec 文件（遗留）
        SPEC_DIR.glob("*.spec") if SPEC_DIR.exists() else [],  # build 目录下的 .spec 文件
    ]
    for pattern in spec_patterns:
        for spec in pattern:
            try:
                spec.unlink()
                print(f"  Removed: {spec}")
            except Exception as e:
                print(f"  Warning: Cannot remove {spec}: {e}")
    
    print("Clean completed!")


def check_pyinstaller() -> bool:
    """检查 PyInstaller 是否已安装"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"PyInstaller version: {version}")
            return True
    except Exception:
        pass
    
    print("错误: PyInstaller 未安装")
    print("请运行: uv pip install pyinstaller")
    print("或者: .venv/Scripts/python.exe scripts/install.py --dev")
    return False


def get_platform_suffix() -> str:
    """获取平台后缀"""
    import platform
    
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        if machine in ("amd64", "x86_64"):
            return "win64"
        elif machine in ("x86", "i386", "i686"):
            return "win32"
        else:
            return f"win-{machine}"
    elif system == "darwin":
        if machine == "arm64":
            return "macos-arm64"
        else:
            return "macos-x64"
    elif system == "linux":
        if machine in ("x86_64", "amd64"):
            return "linux-x64"
        elif machine == "aarch64":
            return "linux-arm64"
        else:
            return f"linux-{machine}"
    else:
        return f"{system}-{machine}"


def kill_running_processes():
    """尝试关闭可能正在运行的打包后的程序"""
    killed = []
    
    # 方法1: 使用 taskkill (Windows)
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["taskkill", "/f", "/im", "MeowTrader.exe"],
                capture_output=True,
                timeout=3,
                text=True
            )
            if result.returncode == 0:
                killed.append("MeowTrader.exe")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
    
    # 方法2: 尝试使用 psutil (如果已安装)
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                proc_name = proc.info['name'] or ''
                proc_exe = proc.info['exe'] or ''
                
                # 检查是否是 MeowTrader 相关进程
                if 'MeowTrader' in proc_name or (proc_exe and 'MeowTrader' in proc_exe):
                    try:
                        proc.kill()
                        killed.append(proc_name or proc_exe or f"PID {proc.info['pid']}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except ImportError:
        pass  # psutil 未安装，跳过
    
    if killed:
        print(f"已关闭正在运行的进程: {', '.join(set(killed))}")
        import time
        time.sleep(1)  # 等待进程完全关闭
        return True
    return False


def build(debug: bool = False, edition: str = "all"):
    """
    执行打包
    
    Args:
        debug: 是否调试模式（显示控制台）
        edition: 版本名称 (all/basic/pro/custom)
    
    Returns:
        应用名称（用于创建 zip）
    """
    # 检查 PyInstaller
    if not check_pyinstaller():
        return False
    
    # 加载配置
    try:
        config = load_edition_config(edition)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return False
    
    product_info = config.get("product", {})
    edition_name = product_info.get("name", edition)
    gateways = config.get("gateways", [])
    apps = config.get("apps", [])
    deps = get_dependencies_from_config(edition)
    
    # 构建应用名称
    suffix = edition if edition != "all" else ""
    app_name_full = f"{APP_NAME}-{suffix}" if suffix else APP_NAME
    
    print("=" * 60)
    print(f"Building {app_name_full} v{APP_VERSION}")
    print(f"Edition: {edition_name} ({edition})")
    print(f"Gateway: {len(gateways)} 个, App: {len(apps)} 个")
    if deps:
        print(f"Dependencies: {', '.join(deps)}")
    print("=" * 60)
    
    # 尝试关闭可能正在运行的程序
    try:
        kill_running_processes()
    except ImportError:
        # psutil 未安装，使用 taskkill 作为备选
        try:
            subprocess.run(
                ["taskkill", "/f", "/im", "MeowTrader.exe"],
                capture_output=True,
                timeout=2
            )
        except Exception:
            pass
    except Exception:
        pass  # 忽略错误，继续打包
    
    # 显示当前环境
    show_installed()
    
    # 确保 dist 目录存在
    DIST_DIR.mkdir(exist_ok=True)
    
    # 检查图标文件
    if not APP_ICON.exists():
        print(f"警告: 图标文件不存在: {APP_ICON}")
        print("提示: 将自定义图标文件放在 meowtrader/resources/icon.ico")
        print("      或使用默认图标: vendor/vnpy/trader/ui/ico/lbkj.ico")
        print("      图标格式必须是 .ico，建议包含多种尺寸（16x16, 32x32, 48x48, 256x256）")
        # 继续打包，但会使用默认图标或报错
    else:
        print(f"使用图标: {APP_ICON}")
    
    # PyInstaller 参数
    args = [
        sys.executable,
        "-m", "PyInstaller",
        "--name", app_name_full,
        "--noconfirm",
        "--clean",
        # 单目录模式（更快启动，便于更新）
        "--onedir",
        # 入口脚本
        str(PROJECT_ROOT / "app" / "desktop" / "main.py"),
        # 输出目录
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        # spec 文件保存位置（默认在当前目录，改为 build 目录）
        "--specpath", str(SPEC_DIR),
        # 图标
        "--icon", str(APP_ICON),
        # 添加 vendor 目录到搜索路径（让 PyInstaller 能找到 vendor 中的模块）
        "--paths", str(PROJECT_ROOT / "vendor"),
        "--paths", str(PROJECT_ROOT / "vendor" / "gateways"),
        "--paths", str(PROJECT_ROOT / "vendor" / "apps"),
        # 添加配置文件（打包时需要包含）
        "--add-data", f"{PROJECT_ROOT / 'config'}{os.pathsep}config",
    ]
    
    # 调试模式显示控制台
    if debug:
        args.append("--console")
        print("Mode: DEBUG (with console)")
    else:
        args.append("--windowed")
        print("Mode: RELEASE (no console)")
    
    # ==================== 隐式导入 ====================
    # PyInstaller 无法自动检测的模块
    hidden_imports = [
        # vnpy 核心
        "vnpy.event",
        "vnpy.event.engine",
        "vnpy.trader",
        "vnpy.trader.engine",
        "vnpy.trader.constant",
        "vnpy.trader.object",
        "vnpy.trader.utility",
        "vnpy.trader.setting",
        "vnpy.trader.converter",
        "vnpy.trader.gateway",
        "vnpy.trader.app",
        "vnpy.trader.ui",
        "vnpy.trader.ui.qt",  # 包含 create_qapp
        "vnpy.trader.ui.fluent_mainwindow",  # 包含 FluentMainWindow
        "vnpy.trader.ui.widget",
        "vnpy.trader.database",
        "vnpy.trader.datafeed",
        "vnpy.trader.optimize",
        "vnpy.trader.logger",
        "vnpy.trader.event",
        "vnpy.trader.locale",
        "vnpy.chart",
        "vnpy.chart.widget",
        "vnpy.chart.item",
        "vnpy.chart.axis",
        "vnpy.chart.base",
        "vnpy.chart.manager",
        "vnpy.rpc",
        "vnpy.rpc.client",
        "vnpy.rpc.server",
        "vnpy.rpc.common",
        # vnpy 数据库
        "vnpy_sqlite",
        "vnpy_rest",
        "vnpy_websocket",
        # vnpy 应用
        "vnpy_ctastrategy",
        "vnpy_ctabacktester",
        "vnpy_portfoliostrategy",
        "vnpy_spreadtrading",
        "vnpy_datamanager",
        "vnpy_riskmanager",
        "vnpy_paperaccount",
        "vnpy_chartwizard",
        "vnpy_webtrader",
        "vnpy_rpcservice",
        "vnpy_algotrading",
        "vnpy_optionmaster",
        "vnpy_scripttrader",
        "vnpy_datarecorder",
        "vnpy_portfoliomanager",
        "vnpy_excelrtd",
        # vnpy 网关
        "vnpy_binance",
        "vnpy_okx",
        # meowtrader
        "meowtrader.core",
        "meowtrader.core.engine",
        "meowtrader.core.config",
        "meowtrader.core.runtime",
        "meowtrader.core.registry",
        # PySide6 Fluent
        "qfluentwidgets",
        "qfluentwidgets.components",
        "qframelesswindow",
        # 其他
        "talib",
        "talib.stream",  # talib 流式处理子模块
        "peewee",
        "plotly",
        "pyqtgraph",
        "numpy",
        "pandas",
        "aiohttp",
        "zmq",
        "loguru",
        "tqdm",
        "deap",
        # Web 相关（vnpy_webtrader）
        "fastapi",
        "fastapi.routing",
        "fastapi.middleware",
        "uvicorn",
        "uvicorn.main",
        "uvicorn.config",
        "starlette",
        "starlette.routing",
        "starlette.middleware",
        "jose",
        "passlib",
        "passlib.context",
        # 其他工具
        "tzlocal",
        "exchange_calendars",
        "secrets",
        "importlib",
        "importlib.metadata",
        # 标准库（可能被动态导入）
        "sqlite3",
        "json",
        "email.mime",
        "email.mime.text",
        "email.mime.multipart",
        "http.server",
        "concurrent.futures",
        "multiprocessing",
        "multiprocessing.pool",
        # SSL/TLS 支持
        "ssl",
        "_ssl",
        "_hashlib",
        # setuptools/pkg_resources 相关（jaraco 是依赖）
        "pkg_resources",
        "pkg_resources.py2_warn",
        "jaraco",
        "jaraco.text",
        "jaraco.functools",
        "jaraco.context",
        "more_itertools",
    ]
    
    for mod in hidden_imports:
        args.extend(["--hidden-import", mod])
    
    # ==================== SSL DLL 文件 ====================
    # 手动添加 OpenSSL DLL 文件（解决 SSL 导入错误）
    python_base = Path(sys.base_prefix)
    dlls_dir = python_base / "DLLs"
    bin_dir = python_base / "bin"
    
    # OpenSSL DLL 文件名称（可能是不同的版本）
    ssl_dll_patterns = [
        "libssl*.dll",
        "libcrypto*.dll",
        "_ssl.pyd",  # Python SSL 扩展模块
    ]
    
    binaries_added = []
    for dll_dir in [dlls_dir, bin_dir]:
        if dll_dir.exists():
            for pattern in ssl_dll_patterns:
                for dll_file in dll_dir.glob(pattern):
                    if dll_file.is_file():
                        # 添加到二进制文件列表（. 表示放在根目录）
                        args.extend(["--add-binary", f"{dll_file}{os.pathsep}."])
                        binaries_added.append(dll_file.name)
                        break  # 每种模式只添加第一个匹配的文件
    
    if binaries_added:
        print(f"  Added SSL DLLs: {', '.join(binaries_added)}")
    
    # 收集 SSL 相关的所有 DLL 和数据文件
    args.extend(["--collect-all", "ssl"])
    
    # 收集 setuptools/pkg_resources 相关的所有模块（包括 jaraco）
    args.extend(["--collect-all", "setuptools"])
    args.extend(["--collect-all", "pkg_resources"])
    
    # ==================== 数据文件 ====================
    # 需要打包的非 Python 文件
    data_files = [
        # 配置文件
        (str(PROJECT_ROOT / "config"), "config"),
        # vendor 目录（确保所有 vendor 模块都被包含）
        (str(PROJECT_ROOT / "vendor"), "vendor"),
        # 图标文件
        (str(PROJECT_ROOT / "vendor" / "vnpy" / "trader" / "ui" / "ico"), "vnpy/trader/ui/ico"),
        # 注意：.vntrader 是运行时配置目录，不应打包
        # 每个用户应该有自己独立的配置目录
    ]
    
    # 添加各应用的图标
    apps_dir = PROJECT_ROOT / "vendor" / "apps"
    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir():
            ico_dir = app_dir / "ui"
            if ico_dir.exists():
                for ico_file in ico_dir.glob("*.ico"):
                    # 目标路径保持相对结构
                    target = f"{app_dir.name}/ui"
                    data_files.append((str(ico_file), target))
    
    for src, dst in data_files:
        if Path(src).exists():
            args.extend(["--add-data", f"{src}{os.pathsep}{dst}"])
    
    # ==================== 排除模块 ====================
    # 不需要打包的模块（减小体积）
    excludes = [
        "tkinter",
        "unittest",
        "test",
        "tests",
        "pip",
        "setuptools",
        "wheel",
    ]
    
    for mod in excludes:
        args.extend(["--exclude-module", mod])
    
    # ==================== 执行打包 ====================
    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(args[:10])}...")
    
    result = subprocess.run(args, cwd=PROJECT_ROOT)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("Build completed successfully!")
        print(f"Output: {DIST_DIR / app_name_full}")
        print("=" * 60)
        
        # 创建版本信息文件
        version_file = DIST_DIR / app_name_full / "VERSION.txt"
        version_file.write_text(f"{app_name_full} v{APP_VERSION}\nEdition: {edition_name} ({edition})\n")
        
        return app_name_full
    else:
        print("\n" + "=" * 60)
        print("Build FAILED!")
        print("=" * 60)
        return False


def create_zip(app_name_full: str = APP_NAME):
    """创建发布压缩包"""
    import zipfile
    from datetime import datetime
    
    app_dir = DIST_DIR / app_name_full
    if not app_dir.exists():
        print("Error: App directory not found. Run build first.")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d")
    platform_suffix = get_platform_suffix()
    zip_name = f"{app_name_full}-v{APP_VERSION}-{timestamp}-{platform_suffix}.zip"
    zip_path = DIST_DIR / zip_name
    
    print(f"Creating {zip_name}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in app_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(DIST_DIR)
                zf.write(file_path, arcname)
    
    print(f"Created: {zip_path}")
    print(f"Size: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MeowTrader Build Script")
    parser.add_argument("--debug", action="store_true", help="Build debug version with console")
    parser.add_argument("--clean", action="store_true", help="Clean build files")
    parser.add_argument("--zip", action="store_true", help="Create release zip file after build (方便分发)")
    
    # 版本选项
    parser.add_argument("--all", action="store_true", help="Build all edition (default, 开发版)")
    parser.add_argument("--basic", action="store_true", help="Build basic edition (基础版)")
    parser.add_argument("--pro", action="store_true", help="Build pro edition (专业版)")
    parser.add_argument("--custom", action="store_true", help="Build custom edition (定制版)")
    
    parser.add_argument("--list", action="store_true", help="List available editions")
    parser.add_argument("--show", action="store_true", help="Show installed vnpy packages")
    
    args = parser.parse_args()
    
    os.chdir(PROJECT_ROOT)
    
    if args.list:
        list_editions()
        return
    
    if args.show:
        show_installed()
        return
    
    if args.clean:
        clean()
        return
    
    # 确定使用的版本（默认 all）
    edition = "all"  # 默认
    edition_flags = {
        "all": args.all,
        "basic": args.basic,
        "pro": args.pro,
        "custom": args.custom,
    }
    
    # 检查快捷选项
    specified = [k for k, v in edition_flags.items() if v]
    if len(specified) > 1:
        print(f"错误: 不能同时指定多个版本: {', '.join(specified)}")
        return 1
    elif len(specified) == 1:
        edition = specified[0]
    
    result = build(debug=args.debug, edition=edition)
    
    if result and args.zip:
        create_zip(result)


if __name__ == "__main__":
    main()
