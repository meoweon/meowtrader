"""
ConfigManager - 配置加载与合并

职责:
- 合并默认配置、版本配置、用户配置、客户配置
- 输出最终运行配置
"""

import json
import sys
from pathlib import Path
from typing import Any

from ..registry.editions import Edition


def _get_default_config_dir() -> Path:
    """
    获取默认配置目录
    
    支持 PyInstaller 打包后的路径
    """
    # 处理 PyInstaller 打包后的路径
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的情况
        base_path = Path(sys._MEIPASS)
        possible_config_dirs = [
            base_path / "config",  # 临时解压目录中的 config
            Path(sys.executable).parent / "config",  # exe 同级目录的 config
        ]
        for config_dir in possible_config_dirs:
            if config_dir.exists() and config_dir.is_dir():
                return config_dir
    
    # 开发环境：使用 __file__ 相对路径
    return Path(__file__).parent.parent.parent / "config"


class ConfigManager:
    """
    配置管理器
    
    配置合并优先级（从低到高）：
    1. 默认配置
    2. 版本配置（basic/pro/custom）
    3. 用户配置
    4. 运行时参数
    """
    
    def __init__(self, config_dir: Path | None = None) -> None:
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，默认为 meowtrader/config
        """
        if config_dir is None:
            config_dir = _get_default_config_dir()
        self.config_dir = config_dir
        self._config: dict[str, Any] = {}
    
    def load(self, edition: Edition = Edition.PRO) -> dict[str, Any]:
        """
        加载并合并配置
        
        Args:
            edition: 产品版本
            
        Returns:
            合并后的配置字典
        """
        # 1. 加载默认配置
        self._config = self._load_defaults()
        
        # 2. 合并版本配置
        edition_config = self._load_edition_config(edition)
        self._merge(edition_config)
        
        # 3. 合并用户配置
        user_config = self._load_user_config()
        self._merge(user_config)
        
        return self._config
    
    def _load_defaults(self) -> dict[str, Any]:
        """加载默认配置"""
        defaults_dir = self.config_dir / "defaults"
        if not defaults_dir.exists():
            return self._get_builtin_defaults()
        
        config = {}
        for file in defaults_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                config.update(data)
        return config
    
    def _load_edition_config(self, edition: Edition) -> dict[str, Any]:
        """加载版本配置"""
        edition_file = self.config_dir / f"edition.{edition.value}.json"
        if not edition_file.exists():
            return {}
        
        with open(edition_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _load_user_config(self) -> dict[str, Any]:
        """加载用户配置"""
        user_file = self.config_dir / "user.json"
        if not user_file.exists():
            return {}
        
        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _merge(self, override: dict[str, Any]) -> None:
        """深度合并配置"""
        self._config = self._deep_merge(self._config, override)
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """
        递归深度合并字典
        
        合并规则：
        - 字典：递归合并
        - 列表（如 apps, gateways）：按 name 字段合并，如果 name 相同则覆盖
        - 其他类型：直接覆盖
        """
        result = base.copy()
        for key, value in override.items():
            if key in result:
                # 处理列表类型（apps, gateways 等）
                if isinstance(result[key], list) and isinstance(value, list):
                    # 按 name 字段合并列表
                    result[key] = self._merge_list(result[key], value)
                # 处理字典类型
                elif isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge(result[key], value)
                else:
                    # 其他类型直接覆盖
                    result[key] = value
            else:
                result[key] = value
        return result
    
    def _merge_list(self, base_list: list, override_list: list) -> list:
        """
        合并两个配置列表（如 apps, gateways）
        
        规则：
        - 如果 override 中的项在 base 中存在（name 相同），则覆盖
        - 如果 override 中的项在 base 中不存在，则添加
        - base 中不在 override 中的项保留
        """
        # 创建 base 的索引（按 name）
        base_dict = {item.get("name"): item for item in base_list if item.get("name")}
        
        # 用 override 覆盖 base
        for item in override_list:
            name = item.get("name")
            if name:
                base_dict[name] = item
        
        # 返回合并后的列表（保持 override 中的顺序，然后添加 base 中独有的项）
        result = []
        override_names = {item.get("name") for item in override_list if item.get("name")}
        
        # 先添加 override 中的项（保持顺序）
        for item in override_list:
            if item.get("name"):
                result.append(item)
        
        # 再添加 base 中独有的项
        for item in base_list:
            name = item.get("name")
            if name and name not in override_names:
                result.append(item)
        
        return result
    
    def _get_builtin_defaults(self) -> dict[str, Any]:
        """获取内置默认配置"""
        return {
            "product": {
                "name": "MeowTrader",
                "version": "0.1.0",
            },
            "gateways": [
                {"name": "okx"},
                {"name": "binance_spot"},
                {"name": "binance_linear"},
                {"name": "binance_inverse"},
            ],
            "apps": [
                {"name": "cta_strategy"},
                {"name": "cta_backtester"},
                {"name": "data_manager"},
                {"name": "risk_manager"},
                {"name": "paper_account"},
                {"name": "portfolio_strategy"},
                {"name": "chart_wizard"},
                {"name": "web_trader"},
                {"name": "rpc_service"},
                {"name": "algotrading"},
                {"name": "datarecorder"},
                {"name": "excelrtd"},
                {"name": "optionmaster"},
                {"name": "portfoliomanager"},
                {"name": "scripttrader"},
                {"name": "spreadtrading"},
            ],
            "database": {
                "driver": "sqlite",
            },
            "ui": {
                "theme": "dark",
                "language": "zh_CN",
            },
            "logging": {
                "level": "INFO",
                "console": True,
                "file": True,
            },
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def save_user_config(self, config: dict[str, Any]) -> None:
        """保存用户配置"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        user_file = self.config_dir / "user.json"
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
