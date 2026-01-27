"""
数据录制引擎

核心功能：接收 Tick 数据，录制 Tick 和生成 K 线
"""

import json
from threading import Thread
from queue import Queue, Empty
from copy import copy
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Optional
from pathlib import Path

from .models import TickData, BarData
from .bar_generator import BarGenerator
from ..database.base import Database
from ..database.csv_exporter import CSVExporter


class RecorderEngine:
    """
    数据录制引擎
    
    功能：
    1. 实时录制 Tick 数据
    2. 从 Tick 自动生成 K 线数据
    3. 批量保存到数据库
    4. 配置管理
    """
    
    def __init__(
        self,
        database: Optional[Database] = None,
        setting_file: str = "data_recorder_setting.json",
        log_callback: Optional[Callable[[str], None]] = None,
        output_format: str = "csv",  # 默认输出 CSV
        output_dir: str = "output"   # 输出目录
    ):
        """
        初始化
        
        Args:
            database: 数据库实例（可选，如果为 None 则只导出 CSV）
            setting_file: 配置文件路径
            log_callback: 日志回调函数
            output_format: 输出格式，"csv"（默认）、"db" 或 "both"
            output_dir: 输出目录（CSV 文件保存位置，默认 "output"）
        """
        self.database = database
        self.setting_file = setting_file
        self.log_callback = log_callback or print
        self.output_format = output_format  # "csv", "db", "both"
        self.output_dir = output_dir
        
        # 录制配置
        self.tick_recordings: set[str] = set()  # 要录制的 Tick 合约集合
        self.bar_recordings: set[str] = set()    # 要录制的 K 线合约集合
        
        # 数据缓存
        self.queue: Queue = Queue()
        self.thread: Optional[Thread] = None
        self.active: bool = False
        
        self.ticks: dict[str, list[TickData]] = defaultdict(list)
        self.bars: dict[str, list[BarData]] = defaultdict(list)
        self.bar_generators: dict[str, BarGenerator] = {}
        
        # CSV 导出缓存（按合约分组）
        self.csv_ticks: dict[str, list[TickData]] = defaultdict(list)
        self.csv_bars: dict[str, list[BarData]] = defaultdict(list)
        
        # 定时器
        self.timer_count: int = 0
        self.timer_interval: int = 10  # 每 10 个周期保存一次
        
        # 时间过滤
        self.filter_window: int = 60  # 60 秒
        self.filter_delta: timedelta = timedelta(seconds=self.filter_window)
        self.filter_dt: datetime = datetime.now()
        
        # 加载配置
        self.load_setting()
        
        # 创建输出目录
        if self.output_format in ("csv", "both"):
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def load_setting(self) -> None:
        """加载配置"""
        try:
            with open(self.setting_file, 'r', encoding='utf-8') as f:
                setting = json.load(f)
                self.tick_recordings = set(setting.get("tick", []))
                self.bar_recordings = set(setting.get("bar", []))
                self.filter_window = setting.get("filter_window", 60)
                self.filter_delta = timedelta(seconds=self.filter_window)
        except FileNotFoundError:
            self.save_setting()
        except Exception as e:
            self.log(f"加载配置失败: {e}")
    
    def save_setting(self) -> None:
        """保存配置"""
        setting = {
            "tick": list(self.tick_recordings),
            "bar": list(self.bar_recordings),
            "filter_window": self.filter_window
        }
        try:
            with open(self.setting_file, 'w', encoding='utf-8') as f:
                json.dump(setting, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"保存配置失败: {e}")
    
    def start(self) -> None:
        """启动录制"""
        if self.active:
            self.log("录制已启动，无需重复启动")
            return
        
        self.active = True
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()
        self.log("数据录制已启动")
    
    def stop(self) -> None:
        """停止录制"""
        if not self.active:
            return
        
        self.active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        # 保存剩余数据
        self._flush_data()
        
        self.log("数据录制已停止")
    
    def _run(self) -> None:
        """后台线程：保存数据到数据库或 CSV"""
        while self.active:
            try:
                task = self.queue.get(timeout=1)
                task_type, data = task
                
                if task_type == "tick":
                    if self.output_format in ("db", "both") and self.database:
                        self.database.save_tick_data(data)
                    if self.output_format in ("csv", "both"):
                        # CSV 导出在 on_timer 中批量处理
                        pass
                elif task_type == "bar":
                    if self.output_format in ("db", "both") and self.database:
                        self.database.save_bar_data(data)
                    if self.output_format in ("csv", "both"):
                        # CSV 导出在 on_timer 中批量处理
                        pass
                    
            except Empty:
                continue
            except Exception as e:
                self.log(f"保存数据时出错: {e}")
                import traceback
                self.log(traceback.format_exc())
    
    def _flush_data(self) -> None:
        """刷新剩余数据到数据库和 CSV"""
        # 保存所有缓存的 K 线到数据库
        if self.output_format in ("db", "both") and self.database:
            for bars in self.bars.values():
                if bars:
                    self.queue.put(("bar", bars))
            self.bars.clear()
            
            for ticks in self.ticks.values():
                if ticks:
                    self.queue.put(("tick", ticks))
            self.ticks.clear()
            
            # 等待队列处理完成
            import time
            time.sleep(0.5)
        
        # 导出剩余的 CSV 数据
        if self.output_format in ("csv", "both"):
            # 如果是 "csv" 模式，csv_bars/csv_ticks 和 bars/ticks 是同一份数据
            # 如果是 "both" 模式，csv_bars/csv_ticks 已经包含了所有数据（在 on_tick/_on_bar 中同时添加）
            # 所以需要合并剩余的 bars/ticks 到 csv_bars/csv_ticks（如果有的话）
            for vt_symbol, bars in self.bars.items():
                if bars:
                    self.csv_bars[vt_symbol].extend(bars)
            self.bars.clear()
            
            for vt_symbol, ticks in self.ticks.items():
                if ticks:
                    self.csv_ticks[vt_symbol].extend(ticks)
            self.ticks.clear()
            
            # 导出所有 CSV
            self._export_csv_batch()
    
    def add_tick_recording(self, vt_symbol: str) -> None:
        """添加 Tick 录制"""
        if vt_symbol in self.tick_recordings:
            self.log(f"已在 Tick 录制列表: {vt_symbol}")
            return
        
        self.tick_recordings.add(vt_symbol)
        self.save_setting()
        self.log(f"添加 Tick 录制: {vt_symbol}")
    
    def remove_tick_recording(self, vt_symbol: str) -> None:
        """移除 Tick 录制"""
        if vt_symbol not in self.tick_recordings:
            self.log(f"不在 Tick 录制列表: {vt_symbol}")
            return
        
        self.tick_recordings.remove(vt_symbol)
        self.save_setting()
        self.log(f"移除 Tick 录制: {vt_symbol}")
    
    def add_bar_recording(self, vt_symbol: str) -> None:
        """添加 K 线录制"""
        if vt_symbol in self.bar_recordings:
            self.log(f"已在 K 线录制列表: {vt_symbol}")
            return
        
        self.bar_recordings.add(vt_symbol)
        self.save_setting()
        self.log(f"添加 K 线录制: {vt_symbol}")
    
    def remove_bar_recording(self, vt_symbol: str) -> None:
        """移除 K 线录制"""
        if vt_symbol not in self.bar_recordings:
            self.log(f"不在 K 线录制列表: {vt_symbol}")
            return
        
        self.bar_recordings.remove(vt_symbol)
        self.save_setting()
        self.log(f"移除 K 线录制: {vt_symbol}")
    
    def on_tick(self, tick: TickData) -> None:
        """
        接收 Tick 数据（由外部调用）
        
        Args:
            tick: Tick 数据
        """
        # 时间过滤：过滤偏离本地时间戳过大的 Tick 数据
        tick_delta = abs(tick.datetime - self.filter_dt)
        if tick_delta >= self.filter_delta:
            return
        
        # 录制 Tick
        if tick.vt_symbol in self.tick_recordings:
            tick_copy = copy(tick)
            self.ticks[tick.vt_symbol].append(tick_copy)
            # 同时缓存到 CSV 导出列表
            if self.output_format in ("csv", "both"):
                self.csv_ticks[tick.vt_symbol].append(tick_copy)
        
        # 生成 K 线
        if tick.vt_symbol in self.bar_recordings:
            bg = self.bar_generators.get(tick.vt_symbol)
            if not bg:
                bg = BarGenerator(self._on_bar)
                self.bar_generators[tick.vt_symbol] = bg
            bg.update_tick(copy(tick))
    
    def _on_bar(self, bar: BarData) -> None:
        """K 线生成回调"""
        self.bars[bar.vt_symbol].append(bar)
        # 同时缓存到 CSV 导出列表
        if self.output_format in ("csv", "both"):
            self.csv_bars[bar.vt_symbol].append(bar)
    
    def on_timer(self) -> None:
        """
        定时器回调（由外部定期调用，例如每秒）
        
        建议调用频率：1 秒
        """
        # 更新时间过滤基准
        self.filter_dt = datetime.now()
        
        self.timer_count += 1
        if self.timer_count < self.timer_interval:
            return
        self.timer_count = 0
        
        # 批量保存数据到数据库
        if self.output_format in ("db", "both") and self.database:
            for bars in self.bars.values():
                if bars:
                    self.queue.put(("bar", bars))
            self.bars.clear()
            
            for ticks in self.ticks.values():
                if ticks:
                    self.queue.put(("tick", ticks))
            self.ticks.clear()
        
        # 批量导出 CSV（默认格式）
        if self.output_format in ("csv", "both"):
            # 导出 CSV（从 csv_bars 和 csv_ticks 导出）
            self._export_csv_batch()
            
            # 如果只导出 CSV，也需要清空 self.bars 和 self.ticks
            # 因为在 "csv" 模式下，它们和 csv_bars/csv_ticks 是同一份数据
            if self.output_format == "csv":
                self.bars.clear()
                self.ticks.clear()
    
    def log(self, msg: str) -> None:
        """日志输出"""
        self.log_callback(f"[DataRecorder] {msg}")
    
    def _export_csv_batch(self) -> None:
        """批量导出 CSV 文件"""
        # 导出 K 线数据
        for vt_symbol, bars in self.csv_bars.items():
            if bars:
                # 生成文件名：symbol_exchange_bar.csv
                symbol, exchange = vt_symbol.split('.')
                file_path = Path(self.output_dir) / f"{symbol}_{exchange}_bar.csv"
                # 追加模式（如果文件已存在）
                append = file_path.exists()
                CSVExporter.export_bar_data(bars, str(file_path), append=append)
                self.log(f"导出 K 线 CSV: {file_path} ({len(bars)} 条)")
        self.csv_bars.clear()
        
        # 导出 Tick 数据
        for vt_symbol, ticks in self.csv_ticks.items():
            if ticks:
                # 生成文件名：symbol_exchange_tick.csv
                symbol, exchange = vt_symbol.split('.')
                file_path = Path(self.output_dir) / f"{symbol}_{exchange}_tick.csv"
                # 追加模式（如果文件已存在）
                append = file_path.exists()
                CSVExporter.export_tick_data(ticks, str(file_path), append=append)
                self.log(f"导出 Tick CSV: {file_path} ({len(ticks)} 条)")
        self.csv_ticks.clear()
    
    def get_recording_status(self) -> dict:
        """
        获取录制状态
        
        Returns:
            包含录制列表的字典
        """
        return {
            "tick": sorted(list(self.tick_recordings)),
            "bar": sorted(list(self.bar_recordings)),
            "active": self.active,
            "output_format": self.output_format,
            "output_dir": self.output_dir
        }
