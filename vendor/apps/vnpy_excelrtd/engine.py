
from vnpy.event import Event, EventEngine
from vnpy.rpc import RpcServer
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.object import TickData, ContractData, LogData, SubscribeRequest
from vnpy.trader.event import EVENT_TICK
from vnpy.trader.logger import logger


APP_NAME = "ExcelRtd"

EVENT_RTD_LOG = "eRtdLog"

REP_ADDRESS = "tcp://*:9001"
PUB_ADDRESS = "tcp://*:9002"


class RtdEngine(BaseEngine):
    """
    The engine for managing RTD objects and data update.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        # 创建并尝试启动服务器，如果端口被占用则记录警告但继续运行
        self.server: RpcServer | None = None
        try:
            self.server = RpcServer()
            self.server.register(self.subscribe)
            self.server.register(self.write_log)
            self.server.start(REP_ADDRESS, PUB_ADDRESS)
            logger.info(f"Excel RTD server started on {REP_ADDRESS} / {PUB_ADDRESS}")
        except Exception as e:
            logger.warning(
                f"Failed to start Excel RTD server (ports may be in use): {e}\n"
                f"Excel RTD functionality will be unavailable. "
                f"Please close other applications using ports 9001/9002 or restart the application."
            )
            # 设置 server 为 None，后续操作需要检查
            self.server = None

        self.subscribed: set[str] = set()

        self.register_event()

    def register_event(self) -> None:
        """
        Register event handler.
        """
        self.event_engine.register(EVENT_TICK, self.process_tick_event)

    def process_tick_event(self, event: Event) -> None:
        """
        Process tick event and update related RTD value.
        """
        if self.server is None:
            return  # 服务器未启动，跳过
        
        tick: TickData = event.data
        try:
            self.server.publish("tick", tick)
        except Exception as e:
            logger.warning(f"Failed to publish tick data to Excel RTD: {e}")

    def write_log(self, msg: str) -> None:
        """
        Output RTD related log message.
        """
        log: LogData = LogData(msg=msg, gateway_name=APP_NAME)
        event: Event = Event(EVENT_RTD_LOG, log)
        self.event_engine.put(event)

    def subscribe(self, vt_symbol: str) -> None:
        """
        Subscribe tick data update.
        """
        contract: ContractData | None = self.main_engine.get_contract(vt_symbol)
        if not contract:
            return

        if vt_symbol in self.subscribed:
            return
        self.subscribed.add(vt_symbol)

        req: SubscribeRequest = SubscribeRequest(
            contract.symbol,
            contract.exchange
        )
        self.main_engine.subscribe(req, contract.gateway_name)

    def close(self) -> None:
        """"""
        if self.server is not None:
            try:
                self.server.stop()
                self.server.join()
            except Exception as e:
                logger.warning(f"Error stopping Excel RTD server: {e}")
