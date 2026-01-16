import csv
from datetime import datetime
from collections.abc import Callable

from vnpy.trader.engine import BaseEngine, MainEngine, EventEngine
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.object import BarData, TickData, ContractData, HistoryRequest
from vnpy.trader.database import BaseDatabase, get_database, BarOverview, DB_TZ
from vnpy.trader.datafeed import BaseDatafeed, get_datafeed
from vnpy.trader.utility import ZoneInfo

APP_NAME = "DataManager"


class ManagerEngine(BaseEngine):
    """"""

    def __init__(
        self,
        main_engine: MainEngine,
        event_engine: EventEngine,
    ) -> None:
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        self.database: BaseDatabase = get_database()
        self.datafeed: BaseDatafeed = get_datafeed()

    def import_data_from_csv(
        self,
        file_path: str,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        tz_name: str,
        datetime_head: str,
        open_head: str,
        high_head: str,
        low_head: str,
        close_head: str,
        volume_head: str,
        turnover_head: str,
        open_interest_head: str,
        datetime_format: str
    ) -> tuple:
        """"""
        with open(file_path) as f:
            buf: list = [line.replace("\0", "") for line in f]

        reader: csv.DictReader = csv.DictReader(buf, delimiter=",")

        bars: list[BarData] = []
        start: datetime | None = None
        count: int = 0
        tz: ZoneInfo = ZoneInfo(tz_name)

        for item in reader:
            if datetime_format:
                dt: datetime = datetime.strptime(item[datetime_head], datetime_format)
            else:
                dt = datetime.fromisoformat(item[datetime_head])
            dt = dt.replace(tzinfo=tz)

            turnover = item.get(turnover_head, 0)
            open_interest = item.get(open_interest_head, 0)

            bar: BarData = BarData(
                symbol=symbol,
                exchange=exchange,
                datetime=dt,
                interval=interval,
                volume=float(item[volume_head]),
                open_price=float(item[open_head]),
                high_price=float(item[high_head]),
                low_price=float(item[low_head]),
                close_price=float(item[close_head]),
                turnover=float(turnover),
                open_interest=float(open_interest),
                gateway_name="DB",
            )

            bars.append(bar)

            # do some statistics
            count += 1
            if not start:
                start = bar.datetime

        end: datetime = bar.datetime

        # insert into database
        self.database.save_bar_data(bars)

        return start, end, count

    def output_data_to_csv(
        self,
        file_path: str,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> bool:
        """"""
        bars: list[BarData] = self.load_bar_data(symbol, exchange, interval, start, end)

        fieldnames: list = [
            "symbol",
            "exchange",
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover",
            "open_interest"
        ]

        try:
            with open(file_path, "w") as f:
                writer: csv.DictWriter = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
                writer.writeheader()

                for bar in bars:
                    d: dict = {
                        "symbol": bar.symbol,
                        "exchange": bar.exchange.value,
                        "datetime": bar.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": bar.open_price,
                        "high": bar.high_price,
                        "low": bar.low_price,
                        "close": bar.close_price,
                        "turnover": bar.turnover,
                        "volume": bar.volume,
                        "open_interest": bar.open_interest,
                    }
                    writer.writerow(d)

            return True
        except PermissionError:
            return False

    def get_bar_overview(self) -> list[BarOverview]:
        """"""
        overview: list[BarOverview] = self.database.get_bar_overview()
        return overview

    def load_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> list[BarData]:
        """"""
        bars: list[BarData] = self.database.load_bar_data(
            symbol,
            exchange,
            interval,
            start,
            end
        )

        return bars

    def delete_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval
    ) -> int:
        """"""
        count: int = self.database.delete_bar_data(
            symbol,
            exchange,
            interval
        )

        return count

    def download_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: str,
        start: datetime,
        output: Callable,
        end: datetime | None = None,
        skip_existing: bool = True
    ) -> int:
        """
        Query bar data from datafeed.
        
        Args:
            symbol: 合约代码
            exchange: 交易所
            interval: K线周期
            start: 开始时间
            output: 输出回调函数
            end: 结束时间，None 表示使用当前时间
            skip_existing: 是否智能跳过已有数据（仅在未指定结束日期时生效）
        """
        # 判断用户是否指定结束日期
        user_specified_end: bool = end is not None
        
        # 是否使用智能检测：仅在未指定结束日期且启用跳过时使用
        should_use_smart_detection: bool = skip_existing and not user_specified_end
        
        # 如果启用智能检测，查询已有数据范围
        if should_use_smart_detection:
            overviews: list[BarOverview] = self.database.get_bar_overview()
            for overview in overviews:
                if (overview.symbol == symbol and 
                    overview.exchange == exchange and 
                    overview.interval == Interval(interval)):
                    # 如果已有数据，从已有数据的结束时间开始下载
                    if overview.end > start:
                        start = overview.end
                        output(f"检测到已有数据，将从 {start.strftime('%Y-%m-%d %H:%M:%S')} 开始下载")
                    break
        
        # 确定结束时间
        if end is None:
            end = datetime.now(DB_TZ)
        
        req: HistoryRequest = HistoryRequest(
            symbol=symbol,
            exchange=exchange,
            interval=Interval(interval),
            start=start,
            end=end
        )

        vt_symbol: str = f"{symbol}.{exchange.value}"
        contract: ContractData | None = self.main_engine.get_contract(vt_symbol)

        # If history data provided in gateway, then query
        if contract and contract.history_data:
            data: list[BarData] = self.main_engine.query_history(
                req, contract.gateway_name
            )
        # Otherwise use datafeed to query data
        else:
            data = self.datafeed.query_bar_history(req, output)

        if data:
            self.database.save_bar_data(data)
            return (len(data))

        return 0

    def download_tick_data(
        self,
        symbol: str,
        exchange: Exchange,
        start: datetime,
        output: Callable
    ) -> int:
        """
        Query tick data from datafeed.
        """
        req: HistoryRequest = HistoryRequest(
            symbol=symbol,
            exchange=exchange,
            start=start,
            end=datetime.now(DB_TZ)
        )

        data: list[TickData] = self.datafeed.query_tick_history(req, output)

        if data:
            self.database.save_tick_data(data)
            return (len(data))

        return 0
