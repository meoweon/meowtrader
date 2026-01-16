# 量化交易软件 TDD（产品化架构设计）

## 1. 目标与范围

### 1.1 目标
- 基于 vnpy 源码构建可打包、可分发的商业产品。
- 支持精简版/专业版/客户定制版。
- 支持多入口（桌面 UI / Web UI / Server / 无 UI）。
- 支持 Windows 与 Linux。

### 1.2 非目标
- 不包含具体策略逻辑实现细节。
- 不包含第三方数据源采购与授权方案。

---

## 2. 总体架构

### 2.1 分层
- 入口层：Desktop / Server / Web / CLI
- 产品层：统一引擎、模块注册、版本与授权、配置管理
- 内核层：vnpy 主引擎与生态模块

### 2.2 关键原则
- UI 与核心引擎解耦
- 模块配置化加载
- 版本/授权驱动功能开关
- 最小化对 vnpy 内核的直接修改

---

## 3. 目录结构设计

```
meowtrader/
  app/                              # 入口与 UI
    desktop/                        # 桌面入口
      main.py
    server/                         # 服务端入口
      main.py
    web/                            # Web 入口
      main.py
    ui/                             # Fluent UI 与其他 UI 适配层
      fluent/
      legacy/
    resources/                      # 图标、主题、字体、翻译
      icons/
      themes/
      fonts/
      i18n/
  core/                             # 产品层
    engine/                         # 统一引擎封装
      product_engine.py
    registry/                       # 模块注册与版本开关
      modules.py
      editions.py
      dependencies.py
    config/                         # 配置加载与合并
      defaults/
      loader.py
      schema/
    license/                        # 授权与版本控制
      license_manager.py
    runtime/                        # 生命周期与环境检测
      bootstrap.py
      environment.py
      diagnostics.py
  vendor/                           # vnpy 源码与生态模块
    vnpy/                           # 核心框架
    gateways/                       # 交易接口
      vnpy_okx/
      vnpy_binance/
    apps/                           # 功能模块
      vnpy_ctastrategy/
      vnpy_ctabacktester/
      vnpy_datamanager/
      vnpy_riskmanager/
      vnpy_webtrader/
      vnpy_rpcservice/
    db/                             # 数据库模块
      vnpy_sqlite/
      vnpy_postgresql/
    libs/                           # rest/websocket 等工具库
      vnpy_rest/
      vnpy_websocket/
  extensions/                       # 自研扩展模块
    gateways/
    apps/
    ui/
    strategies/
  packaging/                        # 打包与分发
    pyinstaller/
    nuitka/
    docker/
  scripts/                          # 工具脚本
    dev_run.py
    lint.py
    export_version.py
  config/                           # 发行配置
    edition.basic.json
    edition.pro.json
    edition.custom.json
    license.json
    user.json
  pyproject.toml
  README.md
```

---

## 4. 产品层设计

### 4.1 统一引擎封装
**目标**: 统一管理 MainEngine/EventEngine，提供稳定 API。

**职责**:
- 创建 EventEngine 与 MainEngine
- 按配置加载 Gateway/App/DB
- 统一生命周期管理（启动/关闭/资源释放）
- 提供统一接口给 UI 与服务

### 4.2 模块注册与加载
**设计**:
- 模块注册表（Gateway/App/DB 列表）
- 版本配置决定加载集合
- 支持客户定制版模块白名单

### 4.3 版本与授权
**设计**:
- 版本配置文件（基础/专业/客户）
- 授权策略影响模块可用性与 UI 可见性

---

## 4.4 关键类与模块接口定义

### 4.4.1 产品引擎接口（核心对外 API）
**职责**: 给 UI/服务提供稳定调用接口，不直接暴露 vnpy 内核。
- `start()`：启动产品（初始化引擎与模块）
- `shutdown()`：关闭产品（释放资源）
- `load_modules(config)`：按配置加载网关/App/数据库
- `get_main_engine()`：返回内部 MainEngine（仅供内部扩展）
- `get_event_engine()`：返回内部 EventEngine

### 4.4.2 模块注册接口
**职责**: 提供模块元信息与版本矩阵的映射。
- `register_gateway(name, class_path)`
- `register_app(name, class_path)`
- `register_database(name, class_path)`
- `get_module_set(edition)`：获取版本模块集合

### 4.4.3 入口接口
**职责**: 统一启动协议，支持多入口扩展。
- `run_desktop()`：桌面 UI 启动
- `run_server()`：无 UI 服务端启动
- `run_web()`：WebTrader/REST 启动

---

## 4.5 关键类职责分解

### 4.5.1 ProductEngine
**角色**: 产品层核心引擎，封装 vnpy MainEngine。
- 负责创建 `EventEngine` 与 `MainEngine`
- 负责模块加载与生命周期管理
- 对外提供稳定 API，屏蔽 vnpy 变化

### 4.5.2 ModuleRegistry
**角色**: 模块注册与版本矩阵管理。
- 维护 Gateway/App/DB/工具模块清单
- 维护版本矩阵映射
- 提供模块依赖校验

### 4.5.3 ConfigManager
**角色**: 配置加载与合并。
- 合并默认配置、版本配置、用户配置、客户配置
- 输出最终运行配置

### 4.5.4 LicenseManager
**角色**: 授权与版本控制。
- 校验授权与版本权限
- 输出功能开关与模块白名单

### 4.5.5 RuntimeManager
**角色**: 生命周期与环境检测。
- 检查运行环境（平台、依赖）
- 统一启动/退出流程
- 统一日志与诊断入口

---

## 5. 入口层设计

### 5.1 Desktop 入口
- 启动产品引擎
- 创建 Fluent UI
- 显示主界面

### 5.2 Server 入口
- 启动产品引擎
- 不加载 UI
- 启动 RPC/Web 服务

### 5.3 Web 入口
- 复用产品引擎
- 启动 WebTrader 或 API

---

## 6. 配置与环境

### 6.1 配置体系
- 默认配置
- 版本配置
- 用户配置
- 客户定制配置

### 6.2 路径策略
- Windows 与 Linux 路径分离
- 数据目录可配置（工作目录或用户目录）

---

## 6.3 配置文件结构（建议）

### 6.3.1 版本配置
- `config/edition.basic.json`
- `config/edition.pro.json`
- `config/edition.custom.json`

### 6.3.2 用户配置
- `config/user.json`

### 6.3.3 授权配置
- `config/license.json`

### 6.3.4 配置合并优先级
1. 默认配置
2. 版本配置
3. 用户配置
4. 客户定制配置
5. 授权限制

---

## 7. 模块策略

### 7.1 Gateway
- OKX / Binance 为默认支持
- 可扩展更多 Gateway

### 7.2 App
- CTA、回测、数据管理、风控为核心
- WebTrader / RPC 作为可选模块

### 7.3 Database
- SQLite 默认
- PostgreSQL 作为专业版选项

---

## 8. 打包与分发

### 8.1 Windows
- PyInstaller/Nuitka
- 生成安装包或可执行文件

### 8.2 Linux
- 可执行包或容器镜像

---

## 9. 关键流程

### 9.1 启动流程
1. 读取版本与授权
2. 初始化产品引擎
3. 加载模块
4. 启动入口

### 9.2 退出流程
1. 停止策略与服务
2. 断开网关
3. 保存状态
4. 释放资源

---

## 10. 风险与控制

### 10.1 风险
- vnpy 版本升级不兼容
- 模块依赖冲突
- 多入口维护成本高

### 10.2 控制
- 产品层封装隔离 vnpy
- 模块注册与配置统一管理
- 版本化测试与发布

---

## 11. 版本矩阵与模块依赖

### 11.1 版本矩阵（示例）
| 模块 | 精简版 | 专业版 | 客户定制版 |
|------|--------|--------|------------|
| vnpy 核心 | 必选 | 必选 | 必选 |
| OKX 网关 | 可选 | 可选 | 可选 |
| Binance 网关 | 可选 | 可选 | 可选 |
| CTA 策略 | 必选 | 必选 | 按需 |
| CTA 回测 | 关闭 | 可选 | 按需 |
| 数据管理 | 关闭 | 可选 | 按需 |
| 风控 | 可选 | 可选 | 按需 |
| 组合策略 | 关闭 | 可选 | 按需 |
| WebTrader | 关闭 | 可选 | 按需 |
| RPC 服务 | 关闭 | 可选 | 按需 |
| SQLite | 必选 | 可选 | 按需 |
| PostgreSQL | 关闭 | 可选 | 按需 |

### 11.2 模块依赖表（示例）
| 模块 | 依赖 | 说明 |
|------|------|------|
| vnpy 核心 | 无 | 必须最先加载 |
| Gateway | vnpy 核心 | 需 EventEngine |
| App | vnpy 核心 | 通过 MainEngine.add_app 加载 |
| 回测 | CTA 策略 | 依赖策略引擎与数据库 |
| 数据管理 | 数据库 | 依赖数据库模块 |
| 风控 | vnpy 核心 | 依赖订单与账户事件 |
| WebTrader | WebSocket/REST | 依赖网络模块 |
| RPC 服务 | ZeroMQ | 依赖 RPC 通信 |

---

## 11.3 当前项目模块注册清单

### 11.3.1 Core
- `vnpy` 4.3.0

### 11.3.2 Gateways
- `vnpy_okx`
- `vnpy_binance`

### 11.3.3 Apps
- `vnpy_ctastrategy`
- `vnpy_ctabacktester`
- `vnpy_datamanager`
- `vnpy_riskmanager`
- `vnpy_paperaccount`
- `vnpy_portfoliostrategy`
- `vnpy_chartwizard`
- `vnpy_webtrader`
- `vnpy_rpcservice`

### 11.3.4 Database
- `vnpy_sqlite`
- `vnpy_postgresql`

### 11.3.5 Tools
- `vnpy_rest`
- `vnpy_websocket`

---

## 12. 目录结构落地建议

### 12.1 保持 vnpy 内核独立
- `vendor/vnpy/` 存放 vnpy 主仓库源码
- 所有改动优先放在 `core/` 与 `app/`

### 12.2 产品层独立维护
- `core/engine/` 仅对外暴露产品 API
- `core/registry/` 负责版本矩阵与模块注册
- `core/config/` 提供配置合并与校验

### 12.3 UI 与入口分离
- `app/desktop/` 只负责桌面启动
- `app/server/` 只负责服务端启动
- `app/web/` 只负责 Web 启动

---

## 13. 接口分层建议

### 13.1 UI 只调用产品层
- UI 不直接访问 vnpy MainEngine
- UI 通过 ProductEngine 暴露的接口操作

### 13.2 产品层只调用 vnpy
- 产品层通过注册器加载 vnpy 模块
- 产品层不依赖具体 UI 实现

---

## 14. 版本交付策略

### 14.1 精简版交付
- 包含核心交易与 CTA 运行
- 只保留必要网关与基础 UI

### 14.2 专业版交付
- 增加回测、数据管理、风控
- 可选 WebTrader 与 RPC 服务

### 14.3 客户定制版交付
- 基于授权配置裁剪模块
- UI 可定制，入口可多选
