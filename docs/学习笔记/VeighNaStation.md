# VeighNa Studio 项目目录结构文档

## 项目概述

VeighNa Studio 是一个完整的 Python 量化交易开发环境，基于 VeighNa（原 vnpy）框架构建。本文档详细说明了项目的目录结构。

---

## 根目录结构

```
veighna_studio/
├── DLLs/                    # Python DLL 依赖库
│   ├── _asyncio.pyd         # 异步IO模块
│   ├── _bz2.pyd             # bzip2压缩模块
│   ├── _ctypes.pyd          # C类型库
│   ├── _decimal.pyd         # 高精度小数模块
│   ├── _elementtree.pyd     # XML解析模块
│   ├── _hashlib.pyd         # 哈希库
│   ├── _lzma.pyd            # LZMA压缩模块
│   ├── _multiprocessing.pyd # 多进程模块
│   ├── _overlapped.pyd      # 重叠IO模块
│   ├── _queue.pyd           # 队列模块
│   ├── _socket.pyd          # 套接字模块
│   ├── _sqlite3.pyd         # SQLite数据库模块
│   ├── _ssl.pyd             # SSL/TLS模块
│   ├── _uuid.pyd            # UUID模块
│   ├── _wmi.pyd             # Windows管理工具
│   ├── _zoneinfo.pyd        # 时区信息模块
│   ├── libcrypto-3.dll       # OpenSSL加密库
│   ├── libffi-8.dll         # 外部函数接口库
│   ├── libssl-3.dll         # OpenSSL SSL库
│   ├── pyexpat.pyd          # XML解析器
│   ├── select.pyd           # 选择器模块
│   ├── sqlite3.dll          # SQLite数据库
│   ├── unicodedata.pyd      # Unicode数据
│   └── winsound.pyd         # Windows声音模块
├── etc/                     # 配置文件目录
│   └── jupyter/             # Jupyter配置
│       ├── jupyter_notebook_config.d/
│       └── jupyter_server_config.d/
├── include/                 # Python C 扩展头文件
│   ├── cpython/             # CPython头文件
│   └── internal/            # 内部头文件
│       └── mimalloc/       # 内存分配器
├── install/                 # 安装包目录（wheel文件存储）
├── Lib/                     # Python 标准库和第三方库
│   ├── site-packages/       # 第三方包目录
│   └── ...                  # Python标准库
├── libs/                    # Python 链接库
│   ├── python3.lib          # Python 3链接库
│   └── python313.lib        # Python 3.13链接库
├── Scripts/                 # 可执行脚本目录
├── share/                   # 共享资源文件
├── LICENSE.txt              # 许可证文件
├── NEWS.txt                 # 新闻/更新日志
├── python.exe               # Python 解释器
├── pythonw.exe              # Python 窗口模式解释器
├── python3.dll              # Python 3 动态链接库
├── python313.dll            # Python 3.13 动态链接库
├── readme.rst               # 说明文件
├── studio_logo.ico          # VeighNa Studio 图标
├── uninstall.exe            # 卸载程序
├── vcruntime140.dll         # Visual C++ 运行时库
└── vcruntime140_1.dll       # Visual C++ 运行时库
```

---

## 核心目录详解

### 1. Scripts/ - 可执行脚本目录

包含所有可执行工具和命令行程序：

```
Scripts/
├── veighna.exe              # VeighNa 命令行工具
├── station.exe              # VeighNa Station 启动器
├── pip.exe                  # Python 包管理器
├── jupyter.exe              # Jupyter 启动器
├── jupyter-lab.exe          # JupyterLab 启动器
├── ipython.exe              # IPython 交互式解释器
├── pyside6-*.exe            # PySide6 Qt 工具集
├── uvicorn.exe              # ASGI 服务器
├── fastapi.exe              # FastAPI 工具
└── ...                      # 其他工具脚本
```

### 2. Lib/site-packages/ - Python 包目录

这是项目的核心目录，包含所有 Python 包和模块。

#### 2.1 VeighNa 核心框架

```
Lib/site-packages/vnpy/
├── __init__.py              # 包初始化文件
├── event/                    # 事件驱动框架
│   ├── __init__.py
│   └── engine.py            # 事件引擎核心
├── trader/                   # 交易核心模块
│   ├── __init__.py
│   ├── app.py               # 应用基类
│   ├── constant.py          # 常量定义（方向、状态、交易所等）
│   ├── converter.py         # 开平仓转换器
│   ├── database.py          # 数据库接口
│   ├── datafeed.py          # 数据源接口
│   ├── engine.py            # 主引擎和基础引擎
│   ├── event.py             # 事件类型定义
│   ├── gateway.py           # 网关基类
│   ├── logger.py            # 日志系统
│   ├── object.py            # 数据对象定义（Tick/Order/Trade等）
│   ├── optimize.py          # 参数优化
│   ├── setting.py           # 配置管理
│   ├── utility.py           # 工具函数
│   ├── locale/              # 国际化支持
│   │   ├── en/              # 英文翻译
│   │   └── generate_*.bat   # 翻译文件生成脚本
│   └── ui/                  # 用户界面
│       ├── fluent_mainwindow.py   # Fluent Design 风格主窗口
│       ├── widget.py        # UI 组件
│       └── qt.py            # Qt 导入封装
├── chart/                    # 图表模块
│   ├── axis.py              # 坐标轴
│   ├── base.py              # 基础类
│   ├── item.py              # 图表项
│   ├── manager.py           # 图表管理器
│   └── widget.py            # 图表组件
├── alpha/                    # 因子研究模块
│   ├── dataset/             # 数据集处理
│   │   ├── cs_function.py  # 横截面函数
│   │   ├── ta_function.py  # 技术分析函数
│   │   ├── ts_function.py  # 时间序列函数
│   │   └── datasets/        # 示例数据集
│   ├── model/               # 机器学习模型
│   │   ├── models/          # 具体模型实现
│   │   │   ├── lasso_model.py
│   │   │   ├── lgb_model.py
│   │   │   └── mlp_model.py
│   │   └── template.py      # 模型模板
│   └── strategy/            # 策略框架
│       ├── backtesting.py   # 回测引擎
│       ├── template.py      # 策略模板
│       └── strategies/      # 示例策略
└── rpc/                      # RPC 通信模块
    ├── client.py            # RPC 客户端
    ├── server.py            # RPC 服务器
    └── common.py            # 通用功能
```

#### 2.2 VeighNa Station

```
Lib/site-packages/veighna_station/
├── __init__.pyc             # 编译后的初始化文件
├── __main__.pyc             # 主入口
├── config.pyc               # 配置管理
├── info.pyc                 # 信息显示
├── login.pyc                # 登录功能
├── fluent_mainwindow.pyc           # Fluent Design 风格主窗口
├── run.pyc                  # 运行入口
├── trader.pyc               # 交易器
├── update.pyc               # 更新功能
├── utility.pyc              # 工具函数
├── version.pyc              # 版本信息
├── widget.pyc               # UI 组件
└── station.ico              # 图标文件
```

#### 2.3 交易接口模块 (Gateway)

所有交易接口模块遵循 `vnpy_*` 命名规范：

```
Lib/site-packages/
├── vnpy_ctp/                 # CTP 期货接口
│   ├── __init__.py
│   ├── api/                 # CTP API 封装
│   │   ├── ctp_constant.py  # CTP 常量定义
│   │   ├── *.dll            # CTP 动态链接库
│   │   └── *.pyd            # Python 扩展模块
│   └── gateway/
│       └── ctp_gateway.py   # CTP 网关实现
├── vnpy_ctptest/            # CTP 测试接口
├── vnpy_binance/            # 币安交易所接口
│   ├── __init__.py
│   ├── spot_gateway.py      # 现货网关
│   ├── linear_gateway.py    # 线性合约网关
│   └── inverse_gateway.py   # 反向合约网关
├── vnpy_okx/                # OKX 交易所接口
│   └── okx_gateway.py
├── vnpy_ib/                 # Interactive Brokers 接口
├── vnpy_xtp/                # 迅投 XTP 接口
├── vnpy_tora/               # 华鑫证券 TORA 接口
├── vnpy_rohon/              # 融航接口
├── vnpy_da/                 # 达钱接口
├── vnpy_mini/               # 迷你期货接口
├── vnpy_tts/                # TTS 接口
├── vnpy_tqsdk/              # 天勤接口
├── vnpy_uft/                # UFT 接口
├── vnpy_tap/                # TAP 接口
├── vnpy_femas/              # 飞马接口
├── vnpy_jees/               # 极速接口
├── vnpy_lstar/              # Lstar 接口
├── vnpy_xt/                 # 迅投 XT 接口
├── vnpy_hts/                # HTS 接口
└── ...                      # 其他交易接口
```

#### 2.4 功能应用模块 (App)

```
Lib/site-packages/
├── vnpy_ctastrategy/         # CTA 策略模块
│   ├── __init__.py
│   ├── base.py              # 基础定义
│   ├── engine.py            # 策略引擎
│   ├── template.py          # 策略模板
│   ├── backtesting.py       # 回测功能
│   ├── strategies/          # 示例策略
│   │   ├── double_ma_strategy.py      # 双均线策略
│   │   ├── boll_channel_strategy.py    # 布林带策略
│   │   ├── dual_thrust_strategy.py     # 双重推力策略
│   │   ├── atr_rsi_strategy.py         # ATR RSI 策略
│   │   ├── turtle_signal_strategy.py   # 海龟信号策略
│   │   ├── king_keltner_strategy.py    # 肯特纳通道策略
│   │   ├── multi_signal_strategy.py    # 多信号策略
│   │   ├── multi_timeframe_strategy.py # 多周期策略
│   │   └── test_strategy.py            # 测试策略
│   ├── ui/                  # 用户界面
│   │   ├── widget.py        # 策略管理界面
│   │   └── rollover.py      # 换月功能
│   └── locale/              # 国际化
├── vnpy_ctabacktester/      # CTA 回测模块
│   ├── engine.py            # 回测引擎
│   └── ui/
│       └── widget.py        # 回测界面
├── vnpy_datamanager/        # 数据管理模块
│   ├── engine.py            # 数据管理引擎
│   └── ui/
│       └── widget.py        # 数据管理界面
├── vnpy_riskmanager/        # 风险管理模块
├── vnpy_portfoliostrategy/  # 组合策略模块
├── vnpy_portfoliomanager/   # 组合管理模块
├── vnpy_optionmaster/       # 期权大师模块
├── vnpy_spreadtrading/      # 价差交易模块
├── vnpy_scripttrader/       # 脚本交易模块
├── vnpy_algotrading/        # 算法交易模块
├── vnpy_chartwizard/        # 图表向导模块
├── vnpy_datarecorder/       # 数据记录模块
├── vnpy_sopt/               # 期权交易模块
├── vnpy_sopttest/           # 期权测试模块
└── ...                      # 其他功能模块
```

#### 2.5 数据源模块

```
Lib/site-packages/
├── vnpy_rqdata/             # 米筐数据源
├── vnpy_tushare/            # Tushare 数据源
├── vnpy_wind/               # Wind 数据源
├── vnpy_ifind/              # iFind 数据源
├── vnpy_mcdata/             # MC 数据源
├── vnpy_polygon/            # Polygon 数据源
├── vnpy_gm/                 # 掘金数据源
└── vnpy_tinysoft/           # 天软数据源
```

#### 2.6 数据库模块

```
Lib/site-packages/
├── vnpy_sqlite/             # SQLite 数据库
├── vnpy_mysql/              # MySQL 数据库
├── vnpy_postgresql/         # PostgreSQL 数据库
├── vnpy_mongodb/            # MongoDB 数据库
└── vnpy_taos/               # TDengine 数据库
```

#### 2.7 其他工具模块

```
Lib/site-packages/
├── vnpy_rest/               # REST API 客户端
├── vnpy_websocket/          # WebSocket 客户端
├── vnpy_rpcservice/         # RPC 服务
├── vnpy_webtrader/          # Web 交易界面
├── vnpy_excelrtd/           # Excel RTD 实时数据
└── vnpy_paperaccount/       # 模拟账户
```

#### 2.8 第三方依赖库

```
Lib/site-packages/
├── PySide6/                 # Qt 6 Python 绑定
├── pandas/                  # 数据分析库
├── numpy/                   # 数值计算库
├── scipy/                   # 科学计算库
├── matplotlib/             # 绘图库
├── pyqtgraph/               # 高性能绘图库
├── talib/                  # 技术分析库
├── jupyterlab/             # JupyterLab
├── fastapi/                # Web 框架
├── uvicorn/                # ASGI 服务器
├── pymongo/                # MongoDB 驱动
├── requests/                # HTTP 库
├── websockets/             # WebSocket 库
├── loguru/                 # 日志库
└── ...                     # 其他依赖库
```

---

## 配置文件目录

### DLLs/ - Python扩展模块

包含所有Python C扩展模块（.pyd文件）和系统依赖的DLL文件：

```
DLLs/
├── _asyncio.pyd             # 异步IO支持
├── _bz2.pyd                 # bzip2压缩
├── _ctypes.pyd              # C类型调用
├── _decimal.pyd             # 高精度小数
├── _elementtree.pyd         # XML解析
├── _hashlib.pyd             # 哈希算法
├── _lzma.pyd                # LZMA压缩
├── _multiprocessing.pyd     # 多进程支持
├── _overlapped.pyd          # Windows重叠IO
├── _queue.pyd               # 队列数据结构
├── _socket.pyd              # 网络套接字
├── _sqlite3.pyd             # SQLite数据库
├── _ssl.pyd                 # SSL/TLS加密
├── _uuid.pyd                # UUID生成
├── _wmi.pyd                 # Windows管理工具
├── _zoneinfo.pyd            # 时区信息
├── libcrypto-3.dll          # OpenSSL加密库
├── libffi-8.dll             # 外部函数接口
├── libssl-3.dll             # OpenSSL SSL库
├── pyexpat.pyd              # Expat XML解析器
├── select.pyd               # 文件描述符选择
├── sqlite3.dll              # SQLite数据库引擎
├── unicodedata.pyd          # Unicode字符数据
└── winsound.pyd             # Windows声音API
```

### etc/ - 配置文件

```
etc/
└── jupyter/                 # Jupyter 配置
    ├── jupyter_notebook_config.d/
    │   └── jupyterlab.json
    └── jupyter_server_config.d/
        ├── jupyter_server_terminals.json
        ├── jupyter-lsp-jupyter-server.json
        ├── jupyterlab.json
        └── notebook_shim.json
```

### include/ - C扩展头文件

```
include/
├── cpython/                 # CPython核心头文件
└── internal/                # Python内部头文件
    └── mimalloc/            # mimalloc内存分配器
        └── mimalloc/
```

### libs/ - 链接库文件

```
libs/
├── python3.lib             # Python 3链接库
└── python313.lib           # Python 3.13链接库
```

### install/ - 安装包目录

存储安装时使用的wheel包文件（.whl），通常为空或包含安装包备份。

### share/ - 共享资源

```
share/
├── applications/            # 应用程序配置
│   └── jupyterlab.desktop
├── icons/                   # 图标文件
│   └── hicolor/
│       └── scalable/
│           └── apps/
│               └── jupyterlab.svg
└── jupyter/                 # Jupyter 资源
    ├── kernels/            # Jupyter 内核配置
    │   └── python3/
    ├── lab/                # JupyterLab 资源
    │   ├── schemas/        # 配置文件模式
    │   ├── static/         # 静态资源
    │   └── themes/         # 主题文件
    └── nbconvert/          # 笔记本转换模板
        └── templates/
```

---

## 重要文件说明

### 可执行文件

- `python.exe` - Python 3.13 解释器
- `pythonw.exe` - Python 窗口模式（无控制台）
- `veighna.exe` - VeighNa 命令行工具
- `station.exe` - VeighNa Station 启动器
- `jupyter-lab.exe` - JupyterLab 启动器

### 核心模块文件

- `vnpy/trader/engine.py` - 主引擎和基础引擎类
- `vnpy/trader/gateway.py` - 网关基类
- `vnpy/trader/object.py` - 数据对象定义
- `vnpy/event/engine.py` - 事件引擎
- `vnpy_ctastrategy/template.py` - CTA 策略模板
- `vnpy_ctastrategy/engine.py` - CTA 策略引擎

### 配置文件

- `vnpy/trader/setting.py` - 系统配置
- `vnpy_ctastrategy/cta_strategy_setting.json` - 策略配置（运行时生成）
- `vnpy_ctastrategy/cta_strategy_data.json` - 策略数据（运行时生成）

---

## 完整模块列表

### 交易接口模块 (Gateway) - 共24个

1. `vnpy_ctp` - CTP期货接口
2. `vnpy_ctptest` - CTP测试接口
3. `vnpy_binance` - 币安交易所接口
4. `vnpy_okx` - OKX交易所接口
5. `vnpy_ib` - Interactive Brokers接口
6. `vnpy_xtp` - 迅投XTP接口
7. `vnpy_tora` - 华鑫证券TORA接口
8. `vnpy_rohon` - 融航接口
9. `vnpy_da` - 达钱接口
10. `vnpy_mini` - 迷你期货接口
11. `vnpy_tts` - TTS接口
12. `vnpy_tqsdk` - 天勤接口
13. `vnpy_uft` - UFT接口
14. `vnpy_tap` - TAP接口
15. `vnpy_femas` - 飞马接口
16. `vnpy_jees` - 极速接口
17. `vnpy_lstar` - Lstar接口
18. `vnpy_xt` - 迅投XT接口
19. `vnpy_hts` - HTS接口

### 功能应用模块 (App) - 共15个

1. `vnpy_ctastrategy` - CTA策略模块
2. `vnpy_ctabacktester` - CTA回测模块
3. `vnpy_datamanager` - 数据管理模块
4. `vnpy_datarecorder` - 数据记录模块
5. `vnpy_riskmanager` - 风险管理模块
6. `vnpy_portfoliostrategy` - 组合策略模块
7. `vnpy_portfoliomanager` - 组合管理模块
8. `vnpy_optionmaster` - 期权大师模块
9. `vnpy_spreadtrading` - 价差交易模块
10. `vnpy_scripttrader` - 脚本交易模块
11. `vnpy_algotrading` - 算法交易模块
12. `vnpy_chartwizard` - 图表向导模块
13. `vnpy_sopt` - 期权交易模块
14. `vnpy_sopttest` - 期权测试模块

### 数据源模块 (Datafeed) - 共7个

1. `vnpy_rqdata` - 米筐数据源
2. `vnpy_tushare` - Tushare数据源
3. `vnpy_wind` - Wind数据源
4. `vnpy_ifind` - iFind数据源
5. `vnpy_mcdata` - MC数据源
6. `vnpy_polygon` - Polygon数据源
7. `vnpy_gm` - 掘金数据源
8. `vnpy_tinysoft` - 天软数据源

### 数据库模块 (Database) - 共5个

1. `vnpy_sqlite` - SQLite数据库
2. `vnpy_mysql` - MySQL数据库
3. `vnpy_postgresql` - PostgreSQL数据库
4. `vnpy_mongodb` - MongoDB数据库
5. `vnpy_taos` - TDengine数据库

### 工具模块 - 共6个

1. `vnpy_rest` - REST API客户端
2. `vnpy_websocket` - WebSocket客户端
3. `vnpy_rpcservice` - RPC服务
4. `vnpy_webtrader` - Web交易界面
5. `vnpy_excelrtd` - Excel RTD实时数据
6. `vnpy_paperaccount` - 模拟账户

**总计：51个vnpy模块**

---

## 模块命名规范

### Gateway 模块

- 命名格式：`vnpy_<接口名称>`
- 示例：`vnpy_ctp`, `vnpy_binance`, `vnpy_okx`
- 必须实现 `BaseGateway` 接口

### App 模块

- 命名格式：`vnpy_<功能名称>`
- 示例：`vnpy_ctastrategy`, `vnpy_datamanager`
- 必须实现 `BaseApp` 接口

### 数据源模块

- 命名格式：`vnpy_<数据源名称>`
- 示例：`vnpy_rqdata`, `vnpy_tushare`
- 必须实现 `BaseDatafeed` 接口

### 数据库模块

- 命名格式：`vnpy_<数据库名称>`
- 示例：`vnpy_sqlite`, `vnpy_mysql`
- 必须实现 `BaseDatabase` 接口

---

## 数据存储位置

运行时生成的数据文件通常存储在用户目录下：

```
用户目录/.veighna/
├── cta_strategy_setting.json    # CTA 策略配置
├── cta_strategy_data.json       # CTA 策略数据
├── vnpy_trader_setting.json     # 交易配置
└── database/                     # 数据库文件
    └── *.db
```

---

## 开发建议

### 添加新的 Gateway

1. 在 `Lib/site-packages/` 下创建 `vnpy_<name>/` 目录
2. 实现 `BaseGateway` 接口
3. 在 `__init__.py` 中导出网关类

### 添加新的 App

1. 在 `Lib/site-packages/` 下创建 `vnpy_<name>/` 目录
2. 实现 `BaseApp` 和对应的 `BaseEngine`
3. 创建 UI 组件（可选）
4. 在 `__init__.py` 中导出应用类

### 开发策略

1. 在 `vnpy_ctastrategy/strategies/` 下创建策略文件
2. 继承 `CtaTemplate` 类
3. 实现必要的回调方法
4. 在策略管理界面中加载

---

## 版本信息

- **VeighNa 版本**: 4.2.0
- **Python 版本**: 3.13
- **PySide6 版本**: 最新稳定版
- **文档生成日期**: 2025年

---

## 注意事项

1. **不要直接修改** `Lib/site-packages/` 下的核心模块文件
2. **策略文件**应放在用户目录下，而不是系统目录
3. **配置文件**会在首次运行时自动生成
4. **数据库文件**建议定期备份
5. **Gateway DLL** 文件需要与 Python 版本匹配

---

## 相关资源

- VeighNa 官方文档: https://www.vnpy.com
- VeighNa GitHub: https://github.com/vnpy/vnpy
- Python 官方文档: https://www.python.org/doc/

---

*本文档基于 VeighNa Studio 实际目录结构生成，如有更新请及时同步修改。*