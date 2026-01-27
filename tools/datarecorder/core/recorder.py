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

from .models import TickData, BarData
from .bar_generator import BarGenerator
from ..database.base import Database


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
        database: Database,
        setting_file: str = "data_recorder_setting.json",
        log_callback: Optional[Callable[[str], None]] = None
    ):
        """
        初始化
        
        Args:
            database: 数据库实例
            setting_file: 配置文件路径
            log_callback: 日志回调函数
        """
        self.database = database
        self.setting_file = setting_file
        self.log_callback = log_callback or print
        
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
        
        # 定时器
        self.timer_count: int = 0
        self.timer_interval: int = 10  # 每 10 个周期保存一次
        
        # 时间过滤
        self.filter_window: int = 60  # 60 秒
        self.filter_delta: timedelta = timedelta(seconds=self.filter_window)
        self.filter_dt: datetime = datetime.now()
        
        # 加载配置
        self.load_setting()
    
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
        """后台线程：保存数据到数据库"""
        while self.active:
            try:
                task = self.queue.get(timeout=1)
                task_type, data = task
                
                if task_type == "tick":
                    self.database.save_tick_data(data)
                elif task_type == "bar":
                    self.database.save_bar_data(data)
                    
            except Empty:
                continue
            except Exception as e:
                self.log(f"保存数据时出错: {e}")
                import traceback
                self.log(traceback.format_exc())
    
    def _flush_data(self) -> None:
        """刷新剩余数据到数据库"""
        # 保存所有缓存的 K 线
        for bars in self.bars.values():
            if bars:
                self.queue.put(("bar", bars))
        self.bars.clear()
        
        # 保存所有缓存的 Tick
        for ticks in self.ticks.values():
            if ticks:
                self.queue.put(("tick", ticks))
        self.ticks.clear()
        
        # 等待队列处理完成
        import time
        time.sleep(0.5)
    
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
            self.ticks[tick.vt_symbol].append(copy(tick))
        
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
        
        # 批量保存数据
        for bars in self.bars.values():
            if bars:
                self.queue.put(("bar", bars))
        self.bars.clear()
        
        for ticks in self.ticks.values():
            if ticks:
                self.queue.put(("tick", ticks))
        self.ticks.clear()
    
    def log(self, msg: str) -> None:
        """日志输出"""
        self.log_callback(f"[DataRecorder] {msg}")
    
    def get_recording_status(self) -> dict:
        """
        获取录制状态
        
        Returns:
            包含录制列表的字典
        """
        return {
            "tick": sorted(list(self.tick_recordings)),
            "bar": sorted(list(self.bar_recordings)),
            "active": self.active
        }
