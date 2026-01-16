"""
RuntimeManager - 生命周期与环境检测

职责:
- 检查运行环境（平台、依赖）
- 统一启动/退出流程
- 统一日志与诊断入口
- 配置 vendor 模块路径
"""

import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.product_engine import ProductEngine


def setup_vendor_path() -> None:
    """
    配置 vendor 模块路径
    
    将 vendor 目录添加到 sys.path，使得：
    - `from vnpy.xxx import` 能找到 vendor/vnpy/
    - `from vnpy_okx import` 能找到 vendor/gateways/vnpy_okx/
    - `from vnpy_ctastrategy import` 能找到 vendor/apps/vnpy_ctastrategy/
    
    支持 PyInstaller 打包后的路径（sys._MEIPASS）
    """
    # 处理 PyInstaller 打包后的路径
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的情况
        # sys._MEIPASS 是临时解压目录
        base_path = Path(sys._MEIPASS)
        # vendor 目录应该在打包后的应用目录中
        # 尝试多个可能的位置
        possible_vendor_dirs = [
            base_path / "vendor",  # 如果 vendor 被打包到临时目录
            Path(sys.executable).parent / "vendor",  # 如果 vendor 在 exe 同级目录
        ]
    else:
        # 开发环境：使用 __file__ 相对路径
        base_path = Path(__file__).parent.parent.parent
        possible_vendor_dirs = [base_path / "vendor"]
    
    # 查找存在的 vendor 目录
    vendor_dir = None
    for possible_dir in possible_vendor_dirs:
        if possible_dir.exists() and possible_dir.is_dir():
            vendor_dir = possible_dir.resolve()
            break
    
    if not vendor_dir:
        # 如果都找不到，回退到基于 __file__ 的路径
        vendor_dir = Path(__file__).parent.parent.parent / "vendor"
        vendor_dir = vendor_dir.resolve()
    
    # 添加 vendor 根目录（用于 vnpy 核心）
    vendor_path = str(vendor_dir)
    if vendor_path not in sys.path:
        sys.path.insert(0, vendor_path)
    
    # 添加 gateways 目录
    gateways_path = str(vendor_dir / "gateways")
    if gateways_path not in sys.path:
        sys.path.insert(0, gateways_path)
    
    # 添加 apps 目录
    apps_path = str(vendor_dir / "apps")
    if apps_path not in sys.path:
        sys.path.insert(0, apps_path)


# 在模块加载时自动配置路径
setup_vendor_path()


class RuntimeManager:
    """
    运行时管理器
    
    管理应用的启动、运行、退出流程
    """
    
    def __init__(self) -> None:
        self._engine: "ProductEngine | None" = None
        self._data_dir: Path | None = None
    
    def check_environment(self) -> dict[str, bool]:
        """
        检查运行环境
        
        Returns:
            环境检查结果
        """
        results = {
            "python_version": self._check_python_version(),
            "platform": self._check_platform(),
            "dependencies": self._check_dependencies(),
        }
        return results
    
    def _check_python_version(self) -> bool:
        """检查 Python 版本（要求 >= 3.10）"""
        return sys.version_info >= (3, 10)
    
    def _check_platform(self) -> bool:
        """检查平台支持"""
        return platform.system() in ("Windows", "Linux", "Darwin")
    
    def _check_dependencies(self) -> bool:
        """检查核心依赖是否可用"""
        required = [
            "PySide6",
            "qfluentwidgets",
        ]
        for package in required:
            try:
                __import__(package)
            except ImportError:
                return False
        return True
    
    def setup_data_directory(self, path: Path | None = None) -> Path:
        """
        设置数据目录
        
        Args:
            path: 数据目录路径，如果为 None 则使用默认路径
            
        Returns:
            实际使用的数据目录路径
        """
        if path is None:
            # 默认使用 .vntrader 目录（与 vnpy 兼容）
            path = Path.cwd() / ".vntrader"
        
        path.mkdir(parents=True, exist_ok=True)
        self._data_dir = path
        return path
    
    def setup_logging(self, level: str = "INFO", log_dir: Path | None = None) -> None:
        """
        配置日志系统
        
        Args:
            level: 日志级别
            log_dir: 日志目录
        """
        import logging
        
        if log_dir is None and self._data_dir:
            log_dir = self._data_dir / "log"
        
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置根日志记录器
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    
    def get_system_info(self) -> dict[str, str]:
        """获取系统信息"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
        }
    
    @property
    def data_dir(self) -> Path | None:
        """获取数据目录"""
        return self._data_dir
