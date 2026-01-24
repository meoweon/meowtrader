"""
General utility functions.
"""

import json
import sys
from datetime import datetime, time
from pathlib import Path
from collections.abc import Callable
from decimal import Decimal
from math import floor, ceil
from typing import overload, Literal

import numpy as np
import talib
from zoneinfo import ZoneInfo, available_timezones      # noqa

from .object import BarData, TickData
from .constant import Exchange, Interval
from .locale import _


# 默认使用上海时区，与 vn.py 原版保持一致
try:
    TZ_INFO = ZoneInfo("Asia/Shanghai")
except Exception:  # pragma: no cover - 极端环境降级
    TZ_INFO = datetime.now().astimezone().tzinfo


def extract_vt_symbol(vt_symbol: str) -> tuple[str, Exchange]:
    """
    :return: (symbol, exchange)
    """
    symbol, exchange_str = vt_symbol.rsplit(".", 1)
    return symbol, Exchange(exchange_str)


def generate_vt_symbol(symbol: str, exchange: Exchange) -> str:
    """
    return vt_symbol
    """
    return f"{symbol}.{exchange.value}"


def _get_trader_dir(temp_name: str) -> tuple[Path, Path]:
    """
    Get path where trader is running in.
    """
    cwd: Path = Path.cwd()
    temp_path: Path = cwd.joinpath(temp_name)

    # If .vntrader folder exists in current working directory,
    # then use it as trader running path.
    if temp_path.exists():
        return cwd, temp_path

    # Otherwise use home path of system.
    home_path: Path = Path.home()
    temp_path = home_path.joinpath(temp_name)

    # Create .vntrader folder under home path if not exist.
    if not temp_path.exists():
        temp_path.mkdir()

    return home_path, temp_path


TRADER_DIR, TEMP_DIR = _get_trader_dir(".vntrader")
sys.path.append(str(TRADER_DIR))


def get_file_path(filename: str) -> Path:
    """
    Get path for temp file with filename.
    """
    return TEMP_DIR.joinpath(filename)


def get_folder_path(folder_name: str) -> Path:
    """
    Get path for temp folder with folder name.
    """
    folder_path: Path = TEMP_DIR.joinpath(folder_name)
    if not folder_path.exists():
        folder_path.mkdir()
    return folder_path


def get_icon_path(filepath: str, ico_name: str) -> str:
    """
    Get path for icon file with ico name.
    """
    ui_path: Path = Path(filepath).parent
    icon_path: Path = ui_path.joinpath("ico", ico_name)
    return str(icon_path)


def load_json(filename: str) -> dict:
    """
    Load data from json file in temp path.
    """
    filepath: Path = get_file_path(filename)

    if filepath.exists():
        with open(filepath, encoding="UTF-8") as f:
            data: dict = json.load(f)
        return data
    else:
        save_json(filename, {})
        return {}


def save_json(filename: str, data: dict) -> None:
    """
    Save data into json file in temp path.
    """
    filepath: Path = get_file_path(filename)
    with open(filepath, mode="w+", encoding="UTF-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def write_log(msg: str, gateway_name: str = "") -> None:
    """
    通用日志输出函数

    说明:
    - 为 Hyperliquid SDK 兼容提供的简单实现
    - 仅写入 Python 日志，不创建额外的事件引擎
    """
    import logging

    logger = logging.getLogger("vnpy.trader.utility")
    if gateway_name:
        logger.info("[%s] %s", gateway_name, msg)
    else:
        logger.info("%s", msg)


def save_connection_status(gateway_name: str, status: bool, msg: str = "") -> None:
    """
    保存交易接口连接状态到本地 json 文件

    Args:
        gateway_name: 接口名称
        status: True 为已连接，False 为未连接
        msg: 可选说明信息（会写入日志）
    """
    if not gateway_name:
        return

    if msg:
        write_log(msg, gateway_name)

    data = load_json("connection_status.json")
    data[gateway_name] = bool(status)
    save_json("connection_status.json", data)


def save_redis_data(key: str, value: dict | list | str | int | float) -> None:
    """
    简化版的 Redis 数据保存函数

    原实现使用 Redis，这里退化为保存到本地 json 文件，主要用于 Hyperliquid 网关的
    最大下单量等辅助信息缓存。
    """
    if not key:
        return

    filename = f"{key}.json"
    save_json(filename, value if isinstance(value, dict) else {"value": value})


class _DummyErrorMonitor:
    """
    简单的错误通知代理

    用于兼容 Hyperliquid 网关中调用的 error_monitor.send_text，
    当前实现仅写入日志，不做外部推送。
    """

    def send_text(self, text: str) -> None:
        write_log(text, "ERROR")


# 供 Hyperliquid 网关使用的错误通知实例
error_monitor = _DummyErrorMonitor()


class GetFilePath:
    """
    兼容 Hyperliquid 网关的路径工具类。

    - recording_list: 从本地 json 文件读取需要录制的合约列表，文件名固定为 recording_list.json
    - 仅做最小实现，避免破坏 MeowTrader 现有逻辑。
    """

    def __init__(self) -> None:
        # 约定使用 .vntrader 目录下的 recording_list.json 作为配置来源
        data = load_json("recording_list.json")
        # 允许两种结构：
        # 1) 直接是列表 ["rb2405.SHFE", ...]
        # 2) 是字典 {"list": [...]}，则取其中的 list 字段
        if isinstance(data, list):
            self.recording_list: list[str] = [str(v) for v in data]
        elif isinstance(data, dict) and isinstance(data.get("list"), list):
            self.recording_list = [str(v) for v in data["list"]]
        else:
            self.recording_list = []


def get_local_datetime(timestamp: int | float | str | datetime) -> datetime:
    """
    将 Hyperliquid 返回的时间戳/字符串转换为本地时区的 datetime。

    兼容几种常见格式：
    - 毫秒时间戳（int/float，通常是 13 位）
    - 秒时间戳（int/float，10 位）
    - ISO8601 格式的字符串
    - 已经是 datetime 对象时原样返回（但会规范为 TZ_INFO 时区）
    """
    if isinstance(timestamp, datetime):
        dt = timestamp
    elif isinstance(timestamp, (int, float)):
        # 按长度判断是秒还是毫秒
        ts_int = int(timestamp)
        if ts_int > 10_000_000_000:  # 粗略认为是毫秒
            dt = datetime.fromtimestamp(ts_int / 1000, tz=TZ_INFO)
        else:
            dt = datetime.fromtimestamp(ts_int, tz=TZ_INFO)
    elif isinstance(timestamp, str):
        try:
            # 优先尝试直接由 fromisoformat 解析
            dt = datetime.fromisoformat(timestamp)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=TZ_INFO)
        except Exception:
            # 解析失败时退化为当前时间，避免抛异常导致整个网关崩溃
            dt = datetime.now(TZ_INFO)
    else:
        dt = datetime.now(TZ_INFO)

    # 统一返回本地时区时间（无 tzinfo，用于 vn.py 的 BarData/TickData）
    return dt.astimezone(TZ_INFO).replace(tzinfo=None)


def get_uuid() -> str:
    """
    生成一个简单的唯一 ID，用于本地订单编号等。

    这里采用 uuid4，足够满足网关内部使用需求。
    """
    import uuid

    return uuid.uuid4().hex


def is_target_contract(vt_symbol: str, gateway_name: str | None = None) -> bool:
    """
    判断合约是否为当前网关需要处理的目标合约。

    原 Hyperliquid 实现依赖更多上下文，这里做一个“保守不过滤”的兼容版本：
    - 始终返回 True，只用于从 recording_list 中筛选时不抛异常。
    - 如果后续需要精细过滤，可以在这里根据 vt_symbol/gateway_name 再加规则。
    """
    return True


def round_to(value: float, target: float) -> float:
    """
    Round price to price tick value.
    """
    decimal_value: Decimal = Decimal(str(value))
    decimal_target: Decimal = Decimal(str(target))
    rounded: float = float(int(round(decimal_value / decimal_target)) * decimal_target)
    return rounded


def floor_to(value: float, target: float) -> float:
    """
    Similar to math.floor function, but to target float number.
    """
    decimal_value: Decimal = Decimal(str(value))
    decimal_target: Decimal = Decimal(str(target))
    result: float = float(int(floor(decimal_value / decimal_target)) * decimal_target)
    return result


def ceil_to(value: float, target: float) -> float:
    """
    Similar to math.ceil function, but to target float number.
    """
    decimal_value: Decimal = Decimal(str(value))
    decimal_target: Decimal = Decimal(str(target))
    result: float = float(int(ceil(decimal_value / decimal_target)) * decimal_target)
    return result


def get_digits(value: float) -> int:
    """
    Get number of digits after decimal point.
    """
    value_str: str = str(value)

    if "e-" in value_str:
        _, buf = value_str.split("e-")
        return int(buf)
    elif "." in value_str:
        _, buf = value_str.split(".")
        return len(buf)
    else:
        return 0


class BarGenerator:
    """
    For:
    1. generating 1 minute bar data from tick data
    2. generating x minute bar/x hour bar data from 1 minute data
    Notice:
    1. for x minute bar, x must be able to divide 60: 2, 3, 5, 6, 10, 15, 20, 30
    2. for x hour bar, x can be any number
    """

    def __init__(
        self,
        on_bar: Callable,
        window: int = 0,
        on_window_bar: Callable | None = None,
        interval: Interval = Interval.MINUTE,
        daily_end: time | None = None
    ) -> None:
        """Constructor"""
        self.bar: BarData | None = None
        self.on_bar: Callable = on_bar

        self.interval: Interval = interval
        self.interval_count: int = 0

        self.hour_bar: BarData | None = None
        self.daily_bar: BarData | None = None

        self.window: int = window
        self.window_bar: BarData | None = None
        self.on_window_bar: Callable | None = on_window_bar

        self.last_tick: TickData | None = None

        self.daily_end: time | None = daily_end
        if self.interval == Interval.DAILY and not self.daily_end:
            raise RuntimeError(_("合成日K线必须传入每日收盘时间"))

    def update_tick(self, tick: TickData) -> None:
        """
        Update new tick data into generator.
        """
        new_minute: bool = False

        # Filter tick data with 0 last price
        if not tick.last_price:
            return

        if not self.bar:
            new_minute = True
        elif (
            (self.bar.datetime.minute != tick.datetime.minute)
            or (self.bar.datetime.hour != tick.datetime.hour)
        ):
            self.bar.datetime = self.bar.datetime.replace(
                second=0, microsecond=0
            )
            self.on_bar(self.bar)

            new_minute = True

        if new_minute:
            self.bar = BarData(
                symbol=tick.symbol,
                exchange=tick.exchange,
                interval=Interval.MINUTE,
                datetime=tick.datetime,
                gateway_name=tick.gateway_name,
                open_price=tick.last_price,
                high_price=tick.last_price,
                low_price=tick.last_price,
                close_price=tick.last_price,
                open_interest=tick.open_interest
            )
        elif self.bar:
            self.bar.high_price = max(self.bar.high_price, tick.last_price)
            if self.last_tick and tick.high_price > self.last_tick.high_price:
                self.bar.high_price = max(self.bar.high_price, tick.high_price)

            self.bar.low_price = min(self.bar.low_price, tick.last_price)
            if self.last_tick and tick.low_price < self.last_tick.low_price:
                self.bar.low_price = min(self.bar.low_price, tick.low_price)

            self.bar.close_price = tick.last_price
            self.bar.open_interest = tick.open_interest
            self.bar.datetime = tick.datetime

        if self.last_tick and self.bar:
            volume_change: float = tick.volume - self.last_tick.volume
            self.bar.volume += max(volume_change, 0)

            turnover_change: float = tick.turnover - self.last_tick.turnover
            self.bar.turnover += max(turnover_change, 0)

        self.last_tick = tick

    def update_bar(self, bar: BarData) -> None:
        """
        Update 1 minute bar into generator
        """
        if self.interval == Interval.MINUTE:
            self.update_bar_minute_window(bar)
        elif self.interval == Interval.HOUR:
            self.update_bar_hour_window(bar)
        else:
            self.update_bar_daily_window(bar)

    def update_bar_minute_window(self, bar: BarData) -> None:
        """"""
        # If not inited, create window bar object
        if not self.window_bar:
            dt: datetime = bar.datetime.replace(second=0, microsecond=0)
            self.window_bar = BarData(
                symbol=bar.symbol,
                exchange=bar.exchange,
                datetime=dt,
                gateway_name=bar.gateway_name,
                open_price=bar.open_price,
                high_price=bar.high_price,
                low_price=bar.low_price
            )
        # Otherwise, update high/low price into window bar
        else:
            self.window_bar.high_price = max(
                self.window_bar.high_price,
                bar.high_price
            )
            self.window_bar.low_price = min(
                self.window_bar.low_price,
                bar.low_price
            )

        # Update close price/volume/turnover into window bar
        self.window_bar.close_price = bar.close_price
        self.window_bar.volume += bar.volume
        self.window_bar.turnover += bar.turnover
        self.window_bar.open_interest = bar.open_interest

        # Check if window bar completed
        if not (bar.datetime.minute + 1) % self.window:
            if self.on_window_bar:
                self.on_window_bar(self.window_bar)

            self.window_bar = None

    def update_bar_hour_window(self, bar: BarData) -> None:
        """"""
        # If not inited, create window bar object
        if not self.hour_bar:
            dt: datetime = bar.datetime.replace(minute=0, second=0, microsecond=0)
            self.hour_bar = BarData(
                symbol=bar.symbol,
                exchange=bar.exchange,
                datetime=dt,
                gateway_name=bar.gateway_name,
                open_price=bar.open_price,
                high_price=bar.high_price,
                low_price=bar.low_price,
                close_price=bar.close_price,
                volume=bar.volume,
                turnover=bar.turnover,
                open_interest=bar.open_interest
            )
            return

        finished_bar: BarData | None = None

        # If minute is 59, update minute bar into window bar and push
        if bar.datetime.minute == 59:
            self.hour_bar.high_price = max(
                self.hour_bar.high_price,
                bar.high_price
            )
            self.hour_bar.low_price = min(
                self.hour_bar.low_price,
                bar.low_price
            )

            self.hour_bar.close_price = bar.close_price
            self.hour_bar.volume += bar.volume
            self.hour_bar.turnover += bar.turnover
            self.hour_bar.open_interest = bar.open_interest

            finished_bar = self.hour_bar
            self.hour_bar = None

        # If minute bar of new hour, then push existing window bar
        elif bar.datetime.hour != self.hour_bar.datetime.hour:
            finished_bar = self.hour_bar

            dt = bar.datetime.replace(minute=0, second=0, microsecond=0)
            self.hour_bar = BarData(
                symbol=bar.symbol,
                exchange=bar.exchange,
                datetime=dt,
                gateway_name=bar.gateway_name,
                open_price=bar.open_price,
                high_price=bar.high_price,
                low_price=bar.low_price,
                close_price=bar.close_price,
                volume=bar.volume,
                turnover=bar.turnover,
                open_interest=bar.open_interest
            )
        # Otherwise only update minute bar
        else:
            self.hour_bar.high_price = max(
                self.hour_bar.high_price,
                bar.high_price
            )
            self.hour_bar.low_price = min(
                self.hour_bar.low_price,
                bar.low_price
            )

            self.hour_bar.close_price = bar.close_price
            self.hour_bar.volume += bar.volume
            self.hour_bar.turnover += bar.turnover
            self.hour_bar.open_interest = bar.open_interest

        # Push finished window bar
        if finished_bar:
            self.on_hour_bar(finished_bar)

    def on_hour_bar(self, bar: BarData) -> None:
        """"""
        if self.window == 1:
            if self.on_window_bar:
                self.on_window_bar(bar)
        else:
            if not self.window_bar:
                self.window_bar = BarData(
                    symbol=bar.symbol,
                    exchange=bar.exchange,
                    datetime=bar.datetime,
                    gateway_name=bar.gateway_name,
                    open_price=bar.open_price,
                    high_price=bar.high_price,
                    low_price=bar.low_price
                )
            else:
                self.window_bar.high_price = max(
                    self.window_bar.high_price,
                    bar.high_price
                )
                self.window_bar.low_price = min(
                    self.window_bar.low_price,
                    bar.low_price
                )

            self.window_bar.close_price = bar.close_price
            self.window_bar.volume += bar.volume
            self.window_bar.turnover += bar.turnover
            self.window_bar.open_interest = bar.open_interest

            self.interval_count += 1
            if not self.interval_count % self.window:
                self.interval_count = 0

                if self.on_window_bar:
                    self.on_window_bar(self.window_bar)

                self.window_bar = None

    def update_bar_daily_window(self, bar: BarData) -> None:
        """"""
        # If not inited, create daily bar object
        if not self.daily_bar:
            self.daily_bar = BarData(
                symbol=bar.symbol,
                exchange=bar.exchange,
                datetime=bar.datetime,
                gateway_name=bar.gateway_name,
                open_price=bar.open_price,
                high_price=bar.high_price,
                low_price=bar.low_price
            )
        # Otherwise, update high/low price into daily bar
        else:
            self.daily_bar.high_price = max(
                self.daily_bar.high_price,
                bar.high_price
            )
            self.daily_bar.low_price = min(
                self.daily_bar.low_price,
                bar.low_price
            )

        # Update close price/volume/turnover into daily bar
        self.daily_bar.close_price = bar.close_price
        self.daily_bar.volume += bar.volume
        self.daily_bar.turnover += bar.turnover
        self.daily_bar.open_interest = bar.open_interest

        # Check if daily bar completed
        if bar.datetime.time() == self.daily_end:
            self.daily_bar.datetime = bar.datetime.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            if self.on_window_bar:
                self.on_window_bar(self.daily_bar)

            self.daily_bar = None

    def generate(self) -> BarData | None:
        """
        Generate the bar data and call callback immediately.
        """
        bar: BarData | None = self.bar

        if bar:
            bar.datetime = bar.datetime.replace(second=0, microsecond=0)
            self.on_bar(bar)

        self.bar = None
        return bar


class ArrayManager:
    """
    For:
    1. time series container of bar data
    2. calculating technical indicator value
    """

    def __init__(self, size: int = 100) -> None:
        """Constructor"""
        self.count: int = 0
        self.size: int = size
        self.inited: bool = False

        self.open_array: np.ndarray = np.zeros(size)
        self.high_array: np.ndarray = np.zeros(size)
        self.low_array: np.ndarray = np.zeros(size)
        self.close_array: np.ndarray = np.zeros(size)
        self.volume_array: np.ndarray = np.zeros(size)
        self.turnover_array: np.ndarray = np.zeros(size)
        self.open_interest_array: np.ndarray = np.zeros(size)

    def update_bar(self, bar: BarData) -> None:
        """
        Update new bar data into array manager.
        """
        self.count += 1
        if not self.inited and self.count >= self.size:
            self.inited = True

        self.open_array[:-1] = self.open_array[1:]
        self.high_array[:-1] = self.high_array[1:]
        self.low_array[:-1] = self.low_array[1:]
        self.close_array[:-1] = self.close_array[1:]
        self.volume_array[:-1] = self.volume_array[1:]
        self.turnover_array[:-1] = self.turnover_array[1:]
        self.open_interest_array[:-1] = self.open_interest_array[1:]

        self.open_array[-1] = bar.open_price
        self.high_array[-1] = bar.high_price
        self.low_array[-1] = bar.low_price
        self.close_array[-1] = bar.close_price
        self.volume_array[-1] = bar.volume
        self.turnover_array[-1] = bar.turnover
        self.open_interest_array[-1] = bar.open_interest

    @property
    def open(self) -> np.ndarray:
        """
        Get open price time series.
        """
        return self.open_array

    @property
    def high(self) -> np.ndarray:
        """
        Get high price time series.
        """
        return self.high_array

    @property
    def low(self) -> np.ndarray:
        """
        Get low price time series.
        """
        return self.low_array

    @property
    def close(self) -> np.ndarray:
        """
        Get close price time series.
        """
        return self.close_array

    @property
    def volume(self) -> np.ndarray:
        """
        Get trading volume time series.
        """
        return self.volume_array

    @property
    def turnover(self) -> np.ndarray:
        """
        Get trading turnover time series.
        """
        return self.turnover_array

    @property
    def open_interest(self) -> np.ndarray:
        """
        Get trading volume time series.
        """
        return self.open_interest_array

    @overload
    def sma(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def sma(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def sma(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        Simple moving average.
        """
        result_array: np.ndarray = talib.SMA(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def ema(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def ema(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def ema(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        Exponential moving average.
        """
        result_array: np.ndarray = talib.EMA(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def kama(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def kama(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def kama(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        KAMA.
        """
        result_array: np.ndarray = talib.KAMA(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def wma(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def wma(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def wma(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        WMA.
        """
        result_array: np.ndarray = talib.WMA(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def apo(self, fast_period: int, slow_period: int, matype: int = 0, array: Literal[False] = False) -> float: ...
    @overload
    def apo(self, fast_period: int, slow_period: int, matype: int = 0, *, array: Literal[True]) -> np.ndarray: ...
    def apo(
        self,
        fast_period: int,
        slow_period: int,
        matype: int = 0,
        array: bool = False
    ) -> float | np.ndarray:
        """
        APO.
        """
        result_array: np.ndarray = talib.APO(self.close, fast_period, slow_period, matype)      # type: ignore
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def cmo(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def cmo(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def cmo(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        CMO.
        """
        result_array: np.ndarray = talib.CMO(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def mom(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def mom(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def mom(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        MOM.
        """
        result_array: np.ndarray = talib.MOM(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def ppo(self, fast_period: int, slow_period: int, matype: int = 0, array: Literal[False] = False) -> float: ...
    @overload
    def ppo(self, fast_period: int, slow_period: int, matype: int = 0, *, array: Literal[True]) -> np.ndarray: ...
    def ppo(
        self,
        fast_period: int,
        slow_period: int,
        matype: int = 0,
        array: bool = False
    ) -> float | np.ndarray:
        """
        PPO.
        """
        result_array: np.ndarray = talib.PPO(self.close, fast_period, slow_period, matype)      # type: ignore
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def roc(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def roc(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def roc(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        ROC.
        """
        result_array: np.ndarray = talib.ROC(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def rocr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def rocr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def rocr(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        ROCR.
        """
        result_array: np.ndarray = talib.ROCR(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def rocp(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def rocp(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def rocp(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        ROCP.
        """
        result_array: np.ndarray = talib.ROCP(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def rocr_100(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def rocr_100(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def rocr_100(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        ROCR100.
        """
        result_array: np.ndarray = talib.ROCR100(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def trix(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def trix(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def trix(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        TRIX.
        """
        result_array: np.ndarray = talib.TRIX(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def std(self, n: int, nbdev: int = 1, array: Literal[False] = False) -> float: ...
    @overload
    def std(self, n: int, nbdev: int = 1, *, array: Literal[True]) -> np.ndarray: ...
    def std(self, n: int, nbdev: int = 1, array: bool = False) -> float | np.ndarray:
        """
        Standard deviation.
        """
        result_array: np.ndarray = talib.STDDEV(self.close, n, nbdev)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def obv(self, array: Literal[False] = False) -> float: ...
    @overload
    def obv(self, array: Literal[True]) -> np.ndarray: ...
    def obv(self, array: bool = False) -> float | np.ndarray:
        """
        OBV.
        """
        result_array: np.ndarray = talib.OBV(self.close, self.volume)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def cci(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def cci(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def cci(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        Commodity Channel Index (CCI).
        """
        result_array: np.ndarray = talib.CCI(self.high, self.low, self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def atr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def atr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def atr(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        Average True Range (ATR).
        """
        result_array: np.ndarray = talib.ATR(self.high, self.low, self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def natr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def natr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def natr(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        NATR.
        """
        result_array: np.ndarray = talib.NATR(self.high, self.low, self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def rsi(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def rsi(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def rsi(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        Relative Strenght Index (RSI).
        """
        result_array: np.ndarray = talib.RSI(self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def macd(self, fast_period: int, slow_period: int, signal_period: int, array: Literal[False] = False) -> tuple[float, float, float]: ...
    @overload
    def macd(self, fast_period: int, slow_period: int, signal_period: int, array: Literal[True]) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    def macd(
        self,
        fast_period: int,
        slow_period: int,
        signal_period: int,
        array: bool = False
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[float, float, float]:
        """
        MACD.
        """
        macd, signal, hist = talib.MACD(
            self.close, fast_period, slow_period, signal_period
        )
        if array:
            return macd, signal, hist
        return macd[-1], signal[-1], hist[-1]

    @overload
    def adx(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def adx(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def adx(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        ADX.
        """
        result_array: np.ndarray = talib.ADX(self.high, self.low, self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def adxr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def adxr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def adxr(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        ADXR.
        """
        result_array: np.ndarray = talib.ADXR(self.high, self.low, self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def dx(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def dx(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def dx(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        DX.
        """
        result_array: np.ndarray = talib.DX(self.high, self.low, self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def minus_di(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def minus_di(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def minus_di(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        MINUS_DI.
        """
        result_array: np.ndarray = talib.MINUS_DI(self.high, self.low, self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def plus_di(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def plus_di(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def plus_di(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        PLUS_DI.
        """
        result_array: np.ndarray = talib.PLUS_DI(self.high, self.low, self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def willr(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def willr(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def willr(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        WILLR.
        """
        result_array: np.ndarray = talib.WILLR(self.high, self.low, self.close, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def ultosc(self, time_period1: int = 7, time_period2: int = 14, time_period3: int = 28, array: Literal[False] = False) -> float: ...
    @overload
    def ultosc(self, time_period1: int = 7, time_period2: int = 14, time_period3: int = 28, *, array: Literal[True]) -> np.ndarray: ...
    def ultosc(
        self,
        time_period1: int = 7,
        time_period2: int = 14,
        time_period3: int = 28,
        array: bool = False
    ) -> float | np.ndarray:
        """
        Ultimate Oscillator.
        """
        result_array: np.ndarray = talib.ULTOSC(self.high, self.low, self.close, time_period1, time_period2, time_period3)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def trange(self, array: Literal[False] = False) -> float: ...
    @overload
    def trange(self, array: Literal[True]) -> np.ndarray: ...
    def trange(self, array: bool = False) -> float | np.ndarray:
        """
        TRANGE.
        """
        result_array: np.ndarray = talib.TRANGE(self.high, self.low, self.close)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def boll(self, n: int, dev: float, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def boll(self, n: int, dev: float, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def boll(
        self,
        n: int,
        dev: float,
        array: bool = False
    ) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
        """
        Bollinger Channel.
        """
        mid_array: np.ndarray = talib.SMA(self.close, n)
        std_array: np.ndarray = talib.STDDEV(self.close, n, 1)

        if array:
            up_array: np.ndarray = mid_array + std_array * dev
            down_array: np.ndarray = mid_array - std_array * dev
            return up_array, down_array
        else:
            mid: float = mid_array[-1]
            std: float = std_array[-1]
            up: float = mid + std * dev
            down: float = mid - std * dev
            return up, down

    @overload
    def keltner(self, n: int, dev: float, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def keltner(self, n: int, dev: float, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def keltner(
        self,
        n: int,
        dev: float,
        array: bool = False
    ) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
        """
        Keltner Channel.
        """
        mid_array: np.ndarray = talib.SMA(self.close, n)
        atr_array: np.ndarray = talib.ATR(self.high, self.low, self.close, n)

        if array:
            up_array: np.ndarray = mid_array + atr_array * dev
            down_array: np.ndarray = mid_array - atr_array * dev
            return up_array, down_array
        else:
            mid: float = mid_array[-1]
            atr: float = atr_array[-1]
            up: float = mid + atr * dev
            down: float = mid - atr * dev
            return up, down

    @overload
    def donchian(self, n: int, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def donchian(self, n: int, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def donchian(
        self, n: int, array: bool = False
    ) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
        """
        Donchian Channel.
        """
        up: np.ndarray = talib.MAX(self.high, n)
        down: np.ndarray = talib.MIN(self.low, n)

        if array:
            return up, down
        return up[-1], down[-1]

    @overload
    def aroon(self, n: int, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def aroon(self, n: int, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def aroon(
        self,
        n: int,
        array: bool = False
    ) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
        """
        Aroon indicator.
        """
        aroon_down, aroon_up = talib.AROON(self.high, self.low, n)

        if array:
            return aroon_up, aroon_down
        return aroon_up[-1], aroon_down[-1]

    @overload
    def aroonosc(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def aroonosc(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def aroonosc(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        Aroon Oscillator.
        """
        result_array: np.ndarray = talib.AROONOSC(self.high, self.low, n)

        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def minus_dm(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def minus_dm(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def minus_dm(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        MINUS_DM.
        """
        result_array: np.ndarray = talib.MINUS_DM(self.high, self.low, n)

        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def plus_dm(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def plus_dm(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def plus_dm(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        PLUS_DM.
        """
        result_array: np.ndarray = talib.PLUS_DM(self.high, self.low, n)

        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def mfi(self, n: int, array: Literal[False] = False) -> float: ...
    @overload
    def mfi(self, n: int, array: Literal[True]) -> np.ndarray: ...
    def mfi(self, n: int, array: bool = False) -> float | np.ndarray:
        """
        Money Flow Index.
        """
        result_array: np.ndarray = talib.MFI(self.high, self.low, self.close, self.volume, n)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def ad(self, array: Literal[False] = False) -> float: ...
    @overload
    def ad(self, array: Literal[True]) -> np.ndarray: ...
    def ad(self, array: bool = False) -> float | np.ndarray:
        """
        AD.
        """
        result_array: np.ndarray = talib.AD(self.high, self.low, self.close, self.volume)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def adosc(self, fast_period: int, slow_period: int, array: Literal[False] = False) -> float: ...
    @overload
    def adosc(self, fast_period: int, slow_period: int, array: Literal[True]) -> np.ndarray: ...
    def adosc(
        self,
        fast_period: int,
        slow_period: int,
        array: bool = False
    ) -> float | np.ndarray:
        """
        ADOSC.
        """
        result_array: np.ndarray = talib.ADOSC(self.high, self.low, self.close, self.volume, fast_period, slow_period)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def bop(self, array: Literal[False] = False) -> float: ...
    @overload
    def bop(self, array: Literal[True]) -> np.ndarray: ...
    def bop(self, array: bool = False) -> float | np.ndarray:
        """
        BOP.
        """
        result_array: np.ndarray = talib.BOP(self.open, self.high, self.low, self.close)

        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value

    @overload
    def stoch(self, fastk_period: int, slowk_period: int, slowk_matype: int, slowd_period: int, slowd_matype: int, array: Literal[False] = False) -> tuple[float, float]: ...
    @overload
    def stoch(self, fastk_period: int, slowk_period: int, slowk_matype: int, slowd_period: int, slowd_matype: int, array: Literal[True]) -> tuple[np.ndarray, np.ndarray]: ...
    def stoch(
        self,
        fastk_period: int,
        slowk_period: int,
        slowk_matype: int,
        slowd_period: int,
        slowd_matype: int,
        array: bool = False
    ) -> tuple[float, float] | tuple[np.ndarray, np.ndarray]:
        """
        Stochastic Indicator
        """
        k, d = talib.STOCH(
            self.high,
            self.low,
            self.close,
            fastk_period,
            slowk_period,
            slowk_matype,    # type: ignore
            slowd_period,
            slowd_matype     # type: ignore
        )
        if array:
            return k, d
        return k[-1], d[-1]

    @overload
    def sar(self, acceleration: float, maximum: float, array: Literal[False] = False) -> float: ...
    @overload
    def sar(self, acceleration: float, maximum: float, array: Literal[True]) -> np.ndarray: ...
    def sar(self, acceleration: float, maximum: float, array: bool = False) -> float | np.ndarray:
        """
        SAR.
        """
        result_array: np.ndarray = talib.SAR(self.high, self.low, acceleration, maximum)
        if array:
            return result_array

        result_value: float = result_array[-1]
        return result_value


def virtual(func: Callable) -> Callable:
    """
    mark a function as "virtual", which means that this function can be override.
    any base class should use this or @abstractmethod to decorate all functions
    that can be (re)implemented by subclasses.
    """
    return func
