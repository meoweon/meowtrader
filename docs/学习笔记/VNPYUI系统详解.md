# VeighNa (vnpy) UI 系统详解

本文档详细介绍 VeighNa 框架的 UI 系统，包括名词解释、技术栈、核心概念、实现功能和工作机制。

---

## 📋 目录

- [名词解释](#名词解释)
- [技术栈](#技术栈)
- [核心概念](#核心概念)
- [实现功能](#实现功能)
- [工作机制](#工作机制)
- [UI 系统架构](#ui-系统架构)
- [设计模式](#设计模式)
- [Fluent Design 改造说明](#fluent-design-改造说明)
- [总结](#总结)

---

## 名词解释

### 1. Widget（控件/组件）

**定义**: Widget 是 Qt 框架中所有可见 UI 元素的基础类，是所有图形界面组件的基类。

**特点**:
- Widget 是 Qt 中最基础的 UI 元素
- 所有按钮、输入框、表格、窗口等都是 Widget
- Widget 可以包含其他 Widget，形成层次结构
- Widget 可以显示、隐藏、移动、调整大小

**在 vnpy 中的应用**:
- 交易面板（TradingWidget）
- 策略管理界面（CtaManager）
- 数据监控表格（TickMonitor、OrderMonitor 等）
- 所有可见的 UI 组件都是 Widget

### 2. MainWindow（传统风格，已移除）和 FluentMainWindow（Fluent 主窗口，当前使用）

**历史说明**:
- **MainWindow**（传统风格）: 曾经使用的主窗口实现，采用传统的 DockWidget 和菜单栏设计
  - 已从代码库中移除（2026-01-14）
  - 不再提供，仅作为历史记录保留在此文档中
  - 采用 QMainWindow 作为基类
  - 使用 DockWidget 组织监控面板
  - 使用菜单栏组织功能模块

**当前使用**:
- **FluentMainWindow**: 基于 Fluent Design 风格的现代化主窗口，继承自 `FluentWindow`
- **是 VeighNa Trader 当前唯一的主窗口实现**，采用现代化的 Fluent Design 设计语言

**FluentMainWindow 特点**:
- 采用 Fluent Design 设计语言（Windows 11 风格）
- 侧边导航栏（NavigationInterface）替代传统菜单栏
- 使用 StackedWidget 组织内容区域
- 支持标签页（TabWidget）组织相关功能
- 卡片式设置界面（CardWidget）
- 现代化的视觉效果和动画
- 深色主题支持
- 平滑的界面切换动画

**在 vnpy 中的应用**:
- **FluentMainWindow**: 当前唯一的主窗口实现，使用导航栏和标签页组织界面
- 包含所有监控面板（行情、委托、成交等）
- 管理所有 App Widget 的显示

### 3. NavigationInterface（导航栏）

**定义**: NavigationInterface 是 Fluent Design 风格的侧边导航栏，用于组织应用程序的主要功能。

**特点**:
- 侧边固定导航栏，功能一目了然
- 支持图标和文字显示
- 支持分组和分隔符
- 点击导航项切换不同的内容界面
- 自动高亮当前选中的导航项

**在 vnpy 中的应用**:
- 交易界面（TradingInterface）- 包含交易面板和行情监控
- 委托界面（OrderInterface）- 包含全部委托和活动委托
- 成交界面（TradeInterface）- 成交记录监控
- 持仓界面（PositionInterface）- 包含持仓和资金监控
- 日志界面（LogInterface）- 系统日志监控
- App 功能模块 - 动态加载的各个功能模块
- 设置界面（SettingsInterface）- 卡片式设置界面

### 4. QDialog（对话框）和 FramelessDialog（无边框对话框）

**定义**: 
- **QDialog**: Qt 标准的对话框窗口，用于用户交互
- **FramelessDialog**: Fluent Design 风格的无边框对话框，提供现代化的外观

**QDialog 特点**:
- **模态对话框**: 必须关闭才能继续操作主窗口（使用 exec() 方法）
- **非模态对话框**: 可以同时打开多个，不阻塞主窗口（使用 show() 方法）
- 通常用于配置、设置、信息显示等场景

**FramelessDialog 特点**:
- 无边框设计，更现代化
- 使用 StandardTitleBar 显示标题和按钮
- 支持自定义布局（使用 QGridLayout 或 QVBoxLayout）
- 自动适应 Fluent 主题颜色
- 标题栏按钮（最小化、最大化、关闭）支持主题色

**在 vnpy 中的应用**:
- 连接对话框（ConnectDialog）- 使用 FramelessDialog，用于连接 Gateway
- 设置编辑器（SettingEditor）- 用于编辑策略参数
- 关于对话框（AboutDialog）- 使用 FramelessDialog，显示系统信息
- 全局配置对话框（GlobalDialog）- 使用 FramelessDialog，编辑全局设置

### 5. Layout（布局管理器）

**定义**: Layout 是 Qt 的布局管理器，用于自动管理 Widget 的位置和大小。

**类型**:
- **QVBoxLayout**: 垂直布局，从上到下排列 Widget
- **QHBoxLayout**: 水平布局，从左到右排列 Widget
- **QGridLayout**: 网格布局，按行列排列 Widget
- **QFormLayout**: 表单布局，标签和控件成对排列

**特点**:
- 自动调整 Widget 的大小和位置
- 响应窗口大小变化
- 简化 UI 布局代码
- 支持嵌套布局

**在 vnpy 中的应用**:
- 所有 Widget 都使用布局管理器来组织子组件
- 策略管理界面使用垂直布局排列策略列表
- 交易面板使用网格布局排列输入控件
- 表单布局用于参数编辑对话框

### 6. Signal（信号）和 Slot（槽）

**定义**: Signal 和 Slot 是 Qt 的事件通信机制，用于对象之间的松耦合通信。

**特点**:
- **Signal（信号）**: 对象发出的事件通知
- **Slot（槽）**: 接收信号并执行相应操作的函数
- 一个信号可以连接多个槽
- 一个槽可以接收多个信号
- 支持跨线程通信（线程安全）

**在 vnpy 中的应用**:
- 事件引擎在后台线程发布事件
- 通过 Signal 将事件传递到主线程
- Widget 的 Slot 接收信号并更新 UI
- 保证线程安全的 UI 更新

### 7. Event（事件）和 EventEngine（事件引擎）

**定义**: Event 是 vnpy 框架中的事件对象，EventEngine 是事件驱动架构的核心。

**Event 特点**:
- 包含事件类型和数据
- 通过事件类型区分不同的事件
- 数据可以是任意对象（TickData、OrderData 等）

**EventEngine 特点**:
- 管理所有事件的发布和订阅
- 采用发布-订阅模式
- 支持异步事件处理
- 自动将事件路由到所有订阅者

**在 vnpy 中的应用**:
- Gateway 推送数据时创建 Event 并发布到 EventEngine
- Widget 订阅感兴趣的事件类型
- EventEngine 自动将事件分发到所有订阅者
- 实现模块间的解耦通信

### 8. BaseMonitor（监控基类）

**定义**: BaseMonitor 是用于显示实时数据的表格监控组件的基类。

**特点**:
- 继承自 FluentTableWidget（Fluent 风格的表格控件）
- 自动订阅指定类型的事件
- 自动更新表格数据（插入新行或更新已有行）
- 支持排序、保存 CSV、调整列宽等功能
- Fluent Design 风格：平滑滚动、行悬停/选中高亮、圆角背景、选中行左侧彩色指示条

**在 vnpy 中的应用**:
- TickMonitor - 监控 Tick 行情数据
- OrderMonitor - 监控委托数据（支持双击撤单）
- TradeMonitor - 监控成交数据
- PositionMonitor - 监控持仓数据
- AccountMonitor - 监控资金数据
- LogMonitor - 监控日志信息

**Fluent 风格特性**:
- 平滑滚动效果
- 行悬停和选中时的圆角高亮背景
- 选中行左侧的彩色指示条
- Fluent 风格的复选框
- 自动 Tooltip 显示

### 9. Cell（单元格）

**定义**: Cell 是表格中的单个单元格，用于格式化显示数据。

**类型**:
- **BaseCell**: 基础单元格，显示文本
- **EnumCell**: 枚举类型单元格，显示枚举值
- **DirectionCell**: 方向单元格，多/空方向带颜色显示
- **BidCell**: 买价单元格，红色显示
- **AskCell**: 卖价单元格，绿色显示
- **PnlCell**: 盈亏单元格，正负值不同颜色
- **TimeCell**: 时间单元格，格式化时间显示
- **DateCell**: 日期单元格，格式化日期显示
- **MsgCell**: 消息单元格，左对齐显示

**特点**:
- 格式化数据显示
- 根据数据类型设置颜色
- 存储原始数据对象（可通过 get_data() 获取）

### 10. BaseApp（应用基类）

**定义**: BaseApp 是所有 App 模块的元数据定义类，用于描述 App 的基本信息。

**元数据字段**:
- **app_name**: 唯一标识符（如 "CtaStrategy"）
- **app_module**: 模块路径（如 "vnpy_ctastrategy"）
- **app_path**: 文件路径
- **display_name**: 显示名称（如 "CTA策略"）
- **engine_class**: 引擎类
- **widget_name**: Widget 类名（如 "CtaManager"）
- **icon_name**: 图标文件名

**作用**:
- 定义 App 的元数据
- 主窗口通过元数据动态加载 Widget
- 实现模块化设计

### 11. Engine（引擎）

**定义**: Engine 是 App 的业务逻辑层，处理数据和业务逻辑。

**层次结构**:
- **MainEngine**: 主引擎，统一管理所有 Gateway 和 App
- **BaseEngine**: 基础引擎，所有 App 引擎的基类
- **App Engine**: 各个 App 的专用引擎（如 CtaEngine、BacktesterEngine）

**特点**:
- 处理业务逻辑
- 不直接操作 UI
- 通过 MainEngine 调用 Gateway
- 通过 EventEngine 发布事件

---

## 技术栈

### 1. PySide6（Qt for Python）

**定义**: PySide6 是 Qt 框架的 Python 绑定，提供完整的 GUI 开发能力。

**特点**:
- 跨平台 GUI 框架（Windows、macOS、Linux）
- 丰富的 UI 组件库
- 强大的布局管理系统
- Signal/Slot 机制
- 支持样式表（CSS-like）

**在 vnpy 中的应用**:
- 所有 UI 组件都基于 PySide6
- 使用 QtWidgets 模块创建窗口和控件
- 使用 QtCore 模块的 Signal/Slot 机制
- 使用 QtGui 模块处理图形和字体

### 2. PySide6-Fluent-Widgets（Fluent Design 组件库）

**定义**: PySide6-Fluent-Widgets 是一个基于 PySide6 的 Fluent Design 风格组件库，提供现代化的 UI 组件。

**特点**:
- 符合 Microsoft Fluent Design 设计语言
- 提供深色和浅色主题支持
- 现代化的视觉效果（圆角、阴影、动画）
- 丰富的组件库（按钮、输入框、表格、菜单等）
- 自动适应主题颜色

**在 vnpy 中的应用**:
- 应用程序启动时自动应用 Fluent 深色主题
- 所有 Widget 使用 Fluent 组件（PushButton、LineEdit、TableWidget 等）
- 提供统一的现代化视觉体验
- 支持主题色自定义（默认使用 Microsoft Fluent 蓝色 #0078d4）

### 2.1 qdarkstyle（已弃用）

**说明**: 在 Fluent Design 改造后，qdarkstyle 已被 PySide6-Fluent-Widgets 替代，不再使用。

### 3. 事件驱动架构

**定义**: 事件驱动架构是一种软件架构模式，组件通过事件进行通信。

**特点**:
- 松耦合：组件不直接依赖
- 异步处理：事件可以异步处理
- 可扩展：易于添加新的事件类型和处理器
- 解耦：UI 和业务逻辑分离

**在 vnpy 中的应用**:
- EventEngine 作为事件总线
- Gateway 发布事件
- Widget 订阅事件
- 实现 UI 和业务逻辑的解耦

---

## 核心概念

### 1. Widget 层次结构

vnpy UI 系统采用层次化的 Widget 结构：

```
FluentMainWindow (Fluent 主窗口)
    ├── NavigationInterface (导航栏)
    │   └── 点击 → Interface (功能界面)
    │
    ├── StackedWidget (内容区域)
    │   ├── TradingInterface (交易界面)
    │   │   ├── TradingWidget (交易面板)
    │   │   └── TickMonitor (行情监控)
    │   │       └── BaseMonitor (监控基类)
    │   │           └── Cell (单元格)
    │   │
    │   ├── OrderInterface (委托界面)
    │   │   └── TabWidget
    │   │       ├── OrderMonitor (全部委托)
    │   │       └── ActiveOrderMonitor (活动委托)
    │   │
    │   └── App Widgets (动态加载)
    │       └── Widget (App 窗口)
    │
    └── Dialog (对话框)
```

### 2. Widget 和 Engine 的分离

vnpy 采用 MVC（Model-View-Controller）架构的变体：

- **Widget（View）**: 负责 UI 显示和用户交互
- **Engine（Controller）**: 负责业务逻辑处理
- **MainEngine（Model）**: 负责数据管理和统一接口

**通信流程**:
```
用户操作 → Widget → Engine → MainEngine → Gateway
                ↓
            EventEngine → Widget (更新 UI)
```

### 3. 事件驱动的 UI 更新

UI 通过事件引擎自动更新，无需轮询：

```
Gateway 推送数据
    ↓
EventEngine 发布事件
    ↓
Qt Signal（线程安全）
    ↓
Widget Slot 接收事件
    ↓
更新 UI 显示
```

### 4. 动态加载机制

App Widget 通过元数据动态加载：

```
BaseApp 定义元数据
    ↓
FluentMainWindow 读取元数据
    ↓
动态导入 UI 模块
    ↓
获取 Widget 类
    ↓
创建 Widget 实例
    ↓
添加到导航栏并显示
```

---

## 实现功能

### 1. 主窗口功能

#### 1.1 MainWindow（传统风格，已移除）

**历史说明**:
- 此主窗口实现已在 2026-01-14 从代码库中移除
- 以下内容仅作为历史记录保留

**功能列表**（历史）:
- 提供应用程序的主框架
- 管理 Dock Widget 的布局
- 提供菜单栏（系统、功能、帮助）
- 提供工具栏（快速访问常用功能）
- 保存和恢复窗口布局
- 管理所有 App Widget 的生命周期

**特点**（历史）:
- 支持多 Dock Widget 布局
- 用户可以自由调整 Dock 位置
- 窗口状态自动保存和恢复
- 单例模式管理 App Widget

#### 1.2 FluentMainWindow（Fluent Design 风格，当前使用）

**功能列表**:
- 提供 Fluent Design 风格的现代化主框架
- 侧边导航栏（NavigationInterface）组织功能
- 使用 StackedWidget 管理内容区域
- 使用标签页（TabWidget）组织相关功能
- 卡片式设置界面（CardWidget）
- 保存和恢复窗口布局
- 管理所有 App Widget 的生命周期

**界面组织**:
- **TradingInterface（交易界面）**: 左侧交易面板，右侧行情表格，使用 QSplitter 分割
- **OrderInterface（委托界面）**: 使用 TabWidget，包含全部委托和活动委托两个标签页
- **PositionInterface（持仓界面）**: 使用 TabWidget，包含持仓和资金两个标签页
- **SettingsInterface（设置界面）**: 使用 CardWidget 展示接口连接卡片
- **导航栏**: 包含交易、委托、成交、持仓、日志等核心功能，以及 App 功能模块

**特点**:
- 现代化的导航栏设计
- 标签页组织，节省空间
- 卡片式设置，更清晰
- 平滑的界面切换动画
- 窗口状态自动保存和恢复
- 单例模式管理 App Widget
- 深色主题支持
- Fluent Design 风格，符合 Windows 11 设计语言

### 2. 监控面板功能

**说明**: 在传统 `MainWindow` 中，这些功能通过 DockWidget 实现；在当前的 `FluentMainWindow` 中，这些功能通过 NavigationInterface 和 StackedWidget 组织。

**功能列表**:
- 行情监控（实时显示 Tick 数据）
- 委托监控（显示所有委托，支持双击撤单）
- 成交监控（显示所有成交记录）
- 持仓监控（显示当前持仓）
- 资金监控（显示账户资金）
- 日志监控（显示系统日志）
- 交易面板（手动下单）

**特点**:
- 自动订阅事件并更新数据
- 支持排序、筛选、导出 CSV
- 列宽可调整并保存
- **当前实现**: 通过 FluentMainWindow 的 NavigationInterface 和 StackedWidget 组织
- **历史实现**: 通过 MainWindow 的 DockWidget 实现（已移除）

### 3. App Widget 功能

**功能列表**:
- CTA 策略管理（添加、启动、停止策略）
- 回测管理（配置和运行回测）
- 数据管理（下载和管理历史数据）
- 风险管理（配置风控参数）
- 组合策略管理（管理组合策略）
- 图表工具（显示 K 线图）
- Web 交易终端（Web 界面）
- RPC 服务（远程调用接口）

**特点**:
- 每个 App 有独立的 Widget
- **当前实现**: 通过 FluentMainWindow 的 NavigationInterface 动态加载
- **历史实现**: 通过 MainWindow 的菜单栏动态加载（已移除）
- 单例模式（每个 App 只有一个实例）
- 可以同时打开多个 App Widget

### 4. 对话框功能

**功能列表**:
- 连接对话框（配置和连接 Gateway）
- 设置编辑器（编辑策略参数）
- 关于对话框（显示系统信息）
- 全局配置对话框（编辑全局设置）
- 合约查询对话框（查询可用合约）

**特点**:
- 模态对话框（阻塞操作）
- 表单布局（标签+控件）
- 数据验证（输入验证）
- 设置保存（自动保存配置）

### 5. 监控表格功能

**功能列表**:
- 实时数据更新（自动插入新行或更新已有行）
- 数据排序（点击列标题排序）
- 数据筛选（按条件筛选）
- 导出 CSV（保存表格数据）
- 列宽调整（调整列宽并保存）
- 右键菜单（快捷操作）

**特点**:
- 高性能（支持大量数据）
- 自动更新（事件驱动）
- 用户友好（排序、筛选、导出）

---

## 工作机制

### 1. 应用程序启动流程

```
1. 创建 Qt 应用程序
   - 应用暗色主题
   - 设置字体和图标
   - 配置异常处理

2. 创建事件引擎
   - 启动事件处理线程
   - 启动定时器线程

3. 创建主引擎
   - 初始化核心引擎（LogEngine、OmsEngine、EmailEngine）
   - 添加 Gateway
   - 添加 App

4. 创建主窗口（FluentMainWindow）
   - 创建 NavigationInterface（导航栏）
   - 创建 StackedWidget（内容区域）
   - 创建核心功能界面（交易、委托、成交等）
   - 动态加载 App Widgets 到导航栏
   - 恢复窗口布局

5. 显示主窗口并运行事件循环
```

### 2. 事件驱动的数据流

```
数据流向（Gateway → UI）:
1. Gateway 接收到数据（Tick、Order、Trade 等）
2. Gateway 创建 Event 对象
3. Gateway 调用 EventEngine.put() 发布事件
4. EventEngine 将事件放入队列
5. EventEngine 的工作线程处理事件
6. EventEngine 调用所有订阅者的处理器
7. Widget 的 Signal 被触发（线程安全）
8. Widget 的 Slot 在主线程执行
9. Widget 更新 UI 显示

用户操作流向（UI → Gateway）:
1. 用户在 Widget 中操作（点击按钮、输入数据等）
2. Widget 调用 Engine 的方法
3. Engine 调用 MainEngine 的方法
4. MainEngine 调用 Gateway 的方法
5. Gateway 执行操作（下单、撤单等）
6. Gateway 推送结果事件
7. 事件流回 UI 更新显示
```

### 3. Widget 动态加载机制

```
1. App 定义元数据（BaseApp）
   - app_module: "vnpy_ctastrategy"
   - widget_name: "CtaManager"

2. FluentMainWindow 读取所有 App
   - 遍历 main_engine.get_all_apps()

3. 动态导入 UI 模块
   - import_module("vnpy_ctastrategy.ui")

4. 获取 Widget 类
   - getattr(ui_module, "CtaManager")

5. 创建导航项
   - 绑定 open_widget() 函数
   - 传入 Widget 类和 App 名称
   - 添加到 NavigationInterface

6. 用户点击导航项
   - 调用 open_widget()
   - 检查 Widget 是否已创建（单例）
   - 如果未创建，创建新实例
   - 显示 Widget（Dialog 用 exec()，Widget 用 show()）
```

### 4. 监控表格更新机制

```
1. BaseMonitor 初始化
   - 定义 event_type（如 EVENT_TICK）
   - 定义 data_key（如 "vt_symbol"）
   - 定义 headers（列定义）

2. 注册事件
   - 创建 Qt Signal
   - 连接 Signal 到 process_event() Slot
   - 注册到 EventEngine

3. 事件到达
   - EventEngine 调用 Signal.emit()
   - Signal 触发 Slot（线程安全）
   - process_event() 在主线程执行

4. 更新表格
   - 检查 data_key 是否已存在
   - 如果存在：更新已有行的单元格
   - 如果不存在：插入新行
   - 使用对应的 Cell 类型格式化显示

5. 用户交互
   - 双击单元格：触发特定操作（如撤单）
   - 右键菜单：排序、导出、调整列宽
   - 列宽调整：自动保存到 QSettings
```

### 5. 窗口状态管理

```
保存窗口状态:
1. 用户调整窗口布局（调整大小、导航栏状态等）
2. 关闭窗口时触发 closeEvent()
3. 调用 save_window_setting()
4. 使用 QSettings 保存窗口状态和几何信息
5. 保存到系统注册表（Windows）或配置文件

恢复窗口状态:
1. 应用程序启动时
2. 调用 load_window_setting()
3. 从 QSettings 读取窗口状态
4. 恢复窗口布局和大小
5. 用户看到上次关闭时的布局

**说明**: 
- **当前实现**: FluentMainWindow 保存和恢复导航栏状态、窗口大小等
- **历史实现**: MainWindow 保存和恢复 DockWidget 布局（已移除）
```

---

## UI 系统架构

### 1. 整体架构图

#### 1.1 MainWindow（传统风格，已移除）

**历史说明**: 此架构已在 2026-01-14 移除，以下内容仅作为历史记录保留。

```
┌─────────────────────────────────────────┐
│           MainWindow (主窗口)            │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ DockWidget│  │ DockWidget│  │  Menu  ││
│  │ (行情)    │  │ (委托)    │  │        ││
│  └──────────┘  └──────────┘  └────────┘│
│  ┌──────────────────────────────────┐  │
│  │      App Widgets (动态加载)       │  │
│  │  CtaManager, BacktesterManager   │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
           │                    │
           │ 调用方法            │ 订阅事件
           ▼                    ▼
┌──────────────────┐    ┌──────────────┐
│   MainEngine     │    │ EventEngine  │
│  (统一接口)      │    │ (事件总线)   │
└──────────────────┘    └──────────────┘
           │                    │
           │ 调用方法            │ 发布事件
           ▼                    ▼
┌──────────────────┐    ┌──────────────┐
│    Gateway       │◄───┤   Gateway   │
│  (交易接口)      │    │  (推送数据)  │
└──────────────────┘    └──────────────┘
```

#### 1.2 FluentMainWindow（Fluent Design 风格，当前使用）架构

```
┌─────────────────────────────────────────────────────┐
│         FluentMainWindow (Fluent 主窗口)            │
│  ┌──────────┐  ┌──────────────────────────────────┐│
│  │Navigation│  │    StackedWidget (内容区域)      ││
│  │Interface │  │  ┌────────────────────────────┐ ││
│  │(导航栏)  │  │  │ TradingInterface           │ ││
│  │          │  │  │ ┌────────┐ ┌────────────┐ │ ││
│  │• 交易    │  │  │ │交易面板│ │ 行情表格   │ │ ││
│  │• 委托    │  │  │ └────────┘ └────────────┘ │ ││
│  │• 成交    │  │  └────────────────────────────┘ ││
│  │• 持仓    │  │  ┌────────────────────────────┐ ││
│  │• 日志    │  │  │ OrderInterface (TabWidget) │ ││
│  │──────────│  │  │ Tab1: 全部委托            │ ││
│  │• App功能 │  │  │ Tab2: 活动委托            │ ││
│  │──────────│  │  └────────────────────────────┘ ││
│  │• 设置    │  │  ┌────────────────────────────┐ ││
│  │• 帮助    │  │  │ SettingsInterface         │ ││
│  │          │  │  │ (CardWidget 卡片式)      │ ││
│  └──────────┘  │  └────────────────────────────┘ ││
│                 └──────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
           │                    │
           │ 调用方法            │ 订阅事件
           ▼                    ▼
┌──────────────────┐    ┌──────────────┐
│   MainEngine     │    │ EventEngine  │
│  (统一接口)      │    │ (事件总线)   │
└──────────────────┘    └──────────────┘
           │                    │
           │ 调用方法            │ 发布事件
           ▼                    ▼
┌──────────────────┐    ┌──────────────┐
│    Gateway       │◄───┤   Gateway   │
│  (交易接口)      │    │  (推送数据)  │
└──────────────────┘    └──────────────┘
```

### 2. Widget 层次结构

#### 2.1 MainWindow（传统风格，已移除）层次结构

**历史说明**: 此层次结构已在 2026-01-14 移除，以下内容仅作为历史记录保留。

```
MainWindow
├── DockWidget (行情)
│   └── TickMonitor
│       └── QTableWidget
│           └── Cell (单元格)
│
├── DockWidget (委托)
│   └── OrderMonitor
│       └── QTableWidget
│           └── Cell (单元格)
│
├── Menu (功能)
│   └── 点击 → CtaManager (App Widget)
│       ├── StrategyManager (策略管理面板)
│       ├── LogMonitor (日志监控)
│       └── StopOrderMonitor (停止单监控)
│
└── Dialog (对话框)
    └── ConnectDialog
        └── QFormLayout
            └── QLineEdit, QComboBox 等
```

#### 2.2 FluentMainWindow（Fluent Design 风格，当前使用）层次结构

```
FluentMainWindow (FluentWindow)
├── NavigationInterface (侧边导航栏)
│   ├── 交易 (TradingInterface)
│   ├── 委托 (OrderInterface)
│   ├── 成交 (TradeInterface)
│   ├── 持仓 (PositionInterface)
│   ├── 日志 (LogInterface)
│   ├── ──────── (分隔符)
│   ├── App 功能模块
│   ├── ──────── (分隔符)
│   ├── 设置 (SettingsInterface)
│   └── 帮助 (Help Menu)
│
└── StackedWidget (内容区域)
    ├── TradingInterface
    │   ├── QSplitter
    │   │   ├── TradingWidget (交易面板)
    │   │   └── TickMonitor (FluentTableWidget)
    │   │       └── Cell (单元格)
    │
    ├── OrderInterface
    │   └── TabWidget
    │       ├── Tab1: OrderMonitor (全部委托)
    │       │   └── FluentTableWidget
    │       └── Tab2: ActiveOrderMonitor (活动委托)
    │           └── FluentTableWidget
    │
    ├── PositionInterface
    │   └── TabWidget
    │       ├── Tab1: PositionMonitor (持仓)
    │       └── Tab2: AccountMonitor (资金)
    │
    ├── SettingsInterface
    │   └── CardWidget (卡片式设置)
    │       ├── Gateway 连接卡片
    │       └── 全局配置卡片
    │
    └── Dialog (对话框)
        └── ConnectDialog (FramelessDialog)
            └── QGridLayout + BodyLabel
                └── LineEdit, ComboBox 等 (Fluent 组件)
```

### 3. 数据流向图

```
┌─────────┐     发布事件      ┌──────────┐     触发 Signal     ┌─────────┐
│ Gateway │ ────────────────► │EventEngine│ ─────────────────► │ Widget  │
│         │                   │          │                     │         │
└─────────┘                   └──────────┘                     └─────────┘
     ▲                                                               │
     │                                                               │
     │ 调用方法                                                       │ 调用方法
     │                                                               │
     └──────────────────────────────────────────────────────────────┘
                            MainEngine
```

---

## 设计模式

### 1. 单例模式（Singleton Pattern）

**应用场景**:
- App Widget 管理：每个 App 的 Widget 只创建一个实例
- MainEngine：整个应用程序只有一个主引擎
- EventEngine：整个应用程序只有一个事件引擎

**实现方式**:
- FluentMainWindow 维护 widgets 字典
- 首次打开时创建，后续直接使用已有实例

### 2. 观察者模式（Observer Pattern）

**应用场景**:
- 事件订阅：Widget 订阅感兴趣的事件
- 数据更新：Gateway 推送数据，Widget 自动更新

**实现方式**:
- EventEngine 作为被观察者（Subject）
- Widget 作为观察者（Observer）
- 通过 register() 注册，通过 put() 通知

### 3. 工厂模式（Factory Pattern）

**应用场景**:
- Widget 动态创建：通过 BaseApp 元数据创建 Widget
- Cell 创建：根据数据类型创建对应的 Cell

**实现方式**:
- BaseApp 定义元数据（工厂配置）
- FluentMainWindow 根据元数据动态创建 Widget（工厂方法）

### 4. 模板方法模式（Template Method Pattern）

**应用场景**:
- BaseMonitor：定义监控表格的通用流程
- 子类实现具体的数据处理逻辑

**实现方式**:
- BaseMonitor 定义 process_event() 模板方法
- 子类定义 headers、event_type、data_key 等配置

### 5. 适配器模式（Adapter Pattern）

**应用场景**:
- Cell 类型：适配不同数据类型到表格显示
- Event 适配：将 Gateway 数据适配为 Event

**实现方式**:
- 不同类型的 Cell 适配不同的数据类型
- Gateway 将原始数据适配为 Event 对象

---

## Fluent Design 改造说明

### 改造概述

VeighNa Trader 的 UI 系统已从传统的 Qt 风格全面升级为 Fluent Design 风格，使用 PySide6-Fluent-Widgets 库实现现代化的用户界面。

**改造日期**: 2026-01-14  
**改造范围**: vnpy 核心 UI 模块  
**改造策略**: 全面替换，使用 Fluent Design 推荐方式

### 主要变化

#### 1. 主题系统
- **改造前**: 使用 qdarkstyle 提供暗色主题
- **改造后**: 使用 PySide6-Fluent-Widgets 的 Fluent 主题系统
- **效果**: 全局应用 Fluent Design 深色主题，设置 Fluent 蓝色（#0078d4）作为强调色

#### 2. 组件替换

| 原组件 | Fluent 组件 | 说明 |
|--------|------------|------|
| `QPushButton` | `PushButton` | 按钮 |
| `QLineEdit` | `LineEdit` | 输入框 |
| `QComboBox` | `ComboBox` | 下拉框 |
| `QCheckBox` | `CheckBox` | 复选框 |
| `QTableWidget` | `TableWidget` | 表格 |
| `QMenu` | `RoundMenu` | 右键菜单 |
| `QAction` | `Action` | 菜单项 |
| `QLabel` | `BodyLabel` | 标签（表单） |
| `QDialog` | `FramelessDialog` | 对话框（自定义布局） |
| `QMessageBox` | `MessageBox` | 消息框 |

#### 3. 主窗口架构

**当前实现**:
- **主窗口**: FluentMainWindow 使用 NavigationInterface（导航栏）和 StackedWidget（内容区域）
- **效果**: 现代化的导航栏设计，标签页组织，卡片式设置界面

**历史实现**:
- **主窗口**: MainWindow 使用 DockWidget 和菜单栏（已移除，2026-01-14）
- **效果**: 传统的 DockWidget 布局，用户可以自由调整 Dock 位置

#### 4. 用户体验改进

**视觉改进**:
- ✅ 现代化外观：Fluent Design 风格，符合 Windows 11 设计语言
- ✅ 深色主题：全局深色主题，保护眼睛
- ✅ 平滑动画：菜单弹出、界面切换都有平滑动画
- ✅ 圆角设计：表格、菜单、卡片都使用圆角设计
- ✅ 高亮效果：行悬停、选中都有视觉反馈

**交互改进**:
- ✅ 导航栏：侧边导航栏，功能一目了然
- ✅ 标签页：相关功能使用标签页组织，节省空间
- ✅ 卡片式设置：设置界面使用卡片展示，更清晰
- ✅ 右键菜单：圆角菜单，带图标，更美观

### Fluent Design 与 Qt 组件的关系

#### 核心理解

**重要观点**: PySide6-Fluent-Widgets **不是** Qt 的完全替代品，而是 **基于 PySide6 的扩展库**。

Fluent Design 改造的目标是替换**用户可见的可视化 UI 组件**，而不是替换所有 Qt 类。某些基础组件（如布局管理器、容器组件）必须继续使用 Qt 原生组件。

#### 组件分类与替换策略

##### 1. 必须保留的 Qt 原生组件（基础设施）

这些组件**没有 Fluent 替代品**，必须继续使用 Qt 原生组件：

| 组件类型 | Qt 类 | 为什么不能替换 | 使用场景 |
|---------|-------|---------------|---------|
| **容器组件** | `QWidget` | 作为纯容器使用时，不需要任何可视化样式 | `TradingInterface(QWidget)`、`OrderInterface(QWidget)` 等 |
| **布局管理器** | `QVBoxLayout`<br>`QHBoxLayout`<br>`QGridLayout`<br>`QFormLayout` | 布局管理器不是可视化组件，只是管理子组件的位置和大小 | 所有 Widget 的布局组织 |
| **分割器** | `QSplitter` | 没有 Fluent 替代品 | `TradingInterface` 中分割交易面板和行情表格 |
| **命名空间** | `Qt` | 提供常量（如 `Qt.Horizontal`、`Qt.AlignCenter`） | 布局方向、对齐方式等 |
| **图标类** | `QIcon` | 图标类，必须使用 Qt 的 | 加载图标文件 |

**示例代码**:
```python
# ✅ 正确：TradingInterface 作为容器使用 QWidget
class TradingInterface(QWidget):
    def __init__(self, ...):
        super().__init__(parent)
        # 使用 QSplitter 分割布局
        splitter = QSplitter(Qt.Horizontal)  # Qt 命名空间
        splitter.addWidget(self.trading_widget)  # Fluent 组件
        splitter.addWidget(self.tick_monitor)    # Fluent 组件
        
        layout = QHBoxLayout(self)  # Qt 布局管理器
        layout.addWidget(splitter)
```

##### 2. 应该替换为 Fluent 组件的（可视化组件）

这些组件**有 Fluent 替代品**，应该使用 Fluent 组件以获得现代化的视觉效果：

| Qt 组件 | Fluent 组件 | 替换原因 | 使用场景 |
|---------|-----------|---------|---------|
| `QPushButton` | `PushButton` | 提供 Fluent 风格的按钮样式、动画效果 | 所有按钮 |
| `QLineEdit` | `LineEdit` | 提供 Fluent 风格的输入框样式 | 文本输入 |
| `QComboBox` | `ComboBox` | 提供 Fluent 风格的下拉框样式 | 下拉选择 |
| `QCheckBox` | `CheckBox` | 提供 Fluent 风格的复选框样式 | 选项选择 |
| `QTableWidget` | `TableWidget` | 提供 Fluent 风格的表格样式（圆角、高亮等） | 数据监控表格 |
| `QMenu` | `RoundMenu` | 提供圆角菜单、图标支持 | 右键菜单 |
| `QAction` | `Action` | 提供图标和样式支持 | 菜单项 |
| `QLabel` | `BodyLabel` | 自动适应主题颜色（深色/浅色） | 表单标签 |
| `QDialog` | `FramelessDialog` | 提供无边框对话框、自定义标题栏 | 对话框窗口 |
| `QMessageBox` | `MessageBox` | 提供 Fluent 风格的消息框 | 提示消息 |

**示例代码**:
```python
# ✅ 正确：使用 Fluent 组件
from qfluentwidgets import PushButton, LineEdit, ComboBox, BodyLabel

button = PushButton("开始回测")  # Fluent 按钮
line_edit = LineEdit()            # Fluent 输入框
combo = ComboBox()                # Fluent 下拉框
label = BodyLabel("交易策略")     # Fluent 标签（自动适应主题）
```

##### 3. 特殊情况：App Widget 窗口

对于**独立窗口**的 App Widget（如 `BacktesterManager`、`CtaManager`），应该使用 `FramelessWindow` 而不是 `QWidget`：

| 场景 | 基类 | 原因 |
|------|------|------|
| **独立窗口** | `FramelessWindow` | 需要 Fluent 风格的窗口样式、标题栏 |
| **容器组件** | `QWidget` | 只是容器，不需要窗口样式 |

**示例代码**:
```python
# ✅ 正确：独立窗口使用 FramelessWindow
from qframelesswindow import FramelessWindow
from qframelesswindow.titlebar import StandardTitleBar

class BacktesterManager(FramelessWindow):
    def __init__(self, ...):
        super().__init__()
        # 设置 Fluent 风格的标题栏
        self.setTitleBar(StandardTitleBar(self))
        # 设置深色背景
        self.setStyleSheet("background-color: rgb(32, 32, 32);")
```

#### 为什么不能完全删除 PySide6 导入？

**核心原因**:

1. **qfluentwidgets 基于 PySide6**: Fluent 组件库本身就是基于 PySide6 构建的，它扩展了 Qt 组件，而不是替代它们。

2. **布局管理器是基础设施**: `QVBoxLayout`、`QHBoxLayout` 等布局管理器不是可视化组件，它们只是管理子组件的位置和大小，没有"样式"可言，因此不需要 Fluent 替代品。

3. **容器组件是透明的**: `QWidget` 作为容器使用时，本身不显示任何内容，只是作为其他组件的容器。真正的样式来自内部的 Fluent 组件。

4. **Qt 命名空间是必需的**: `Qt.Horizontal`、`Qt.AlignCenter` 等常量是 Qt 框架的基础设施，必须使用。

#### 设计原则总结

```
Fluent Design 改造的设计原则：

1. 可视化组件 → 使用 Fluent 组件
   ├── 用户可见的 UI 元素
   ├── 按钮、输入框、表格、菜单等
   └── 需要样式和视觉效果

2. 基础设施组件 → 使用 Qt 原生组件
   ├── 布局管理器（QVBoxLayout、QHBoxLayout）
   ├── 容器组件（QWidget 作为容器）
   ├── 分割器（QSplitter）
   └── 命名空间和常量（Qt）

3. 独立窗口 → 使用 FramelessWindow
   └── App Widget 独立窗口需要 Fluent 风格
```

#### 实际应用示例

**正确示例** - `TradingInterface`:
```python
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
from qfluentwidgets import TabWidget  # Fluent 组件

class TradingInterface(QWidget):  # ✅ QWidget 作为容器
    def init_ui(self):
        # ✅ QSplitter 分割布局
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.trading_widget)  # 内部使用 Fluent 组件
        splitter.addWidget(self.tick_monitor)     # 内部使用 Fluent 组件
        
        # ✅ QHBoxLayout 管理布局
        layout = QHBoxLayout(self)
        layout.addWidget(splitter)
```

**正确示例** - `BacktesterManager`:
```python
from qframelesswindow import FramelessWindow  # ✅ 独立窗口
from qfluentwidgets import PushButton, LineEdit, BodyLabel  # ✅ Fluent 组件
from PySide6.QtWidgets import QVBoxLayout, QGridLayout  # ✅ 布局管理器

class BacktesterManager(FramelessWindow):  # ✅ 独立窗口
    def init_ui(self):
        # ✅ 使用 Fluent 组件
        button = PushButton("开始回测")
        line_edit = LineEdit()
        label = BodyLabel("交易策略")
        
        # ✅ 使用 Qt 布局管理器
        layout = QVBoxLayout(self)
        layout.addWidget(button)
```

#### 常见误解澄清

**误解 1**: "所有 Qt 组件都应该替换为 Fluent 组件"  
**正确理解**: 只有**用户可见的可视化组件**需要替换，基础设施组件（布局、容器）继续使用 Qt 原生组件。

**误解 2**: "TradingInterface(QWidget) 应该改为 TradingInterface(FluentWidget)"  
**正确理解**: `TradingInterface` 只是一个透明容器，不需要任何样式。真正的 Fluent 样式来自内部的 `TradingWidget` 和 `TickMonitor` 等组件。

**误解 3**: "可以完全删除 PySide6 的导入"  
**正确理解**: 不能删除，因为布局管理器、容器、命名空间等基础设施必须使用 Qt 原生组件。

### 架构说明

**当前状态**:
- ✅ 系统统一使用 `FluentMainWindow` 作为主窗口（自 2026-01-14 起）
- ✅ `MainWindow`（传统风格）已从代码库中移除
- ✅ 采用 Fluent Design 设计语言，提供现代化的用户体验
- ✅ 所有业务逻辑代码与 UI 解耦，易于维护

**历史说明**:
- `MainWindow`（传统 DockWidget 风格）曾经是系统的主窗口实现
- 在 Fluent Design 改造完成后，已完全移除，不再提供
- 如需了解历史架构，请参考本文档中的历史记录部分

### 依赖要求

**新增依赖**:
- `PySide6-Fluent-Widgets` >= 1.10.5
- `qframelesswindow` (Fluent Widgets 的依赖)

**移除依赖**:
- `qdarkstyle` (不再需要)

---

## 总结

### 核心特点

1. **模块化设计**: 每个 App 有独立的 Widget，通过元数据动态加载
2. **事件驱动**: UI 通过事件引擎自动更新，无需轮询
3. **线程安全**: 使用 Qt Signal/Slot 机制保证跨线程安全
4. **用户友好**: 导航栏设计、状态保存、深色主题
5. **可扩展**: 易于添加新的 App 和 Widget
6. **现代化 UI**: Fluent Design 风格，提供更好的用户体验

### 关键概念

- **Widget**: 所有 UI 组件的基础
- **FluentMainWindow**: 应用程序的主窗口（Fluent Design 风格，当前使用）
- **MainWindow**: 传统风格主窗口（已移除，仅作为历史记录）
- **NavigationInterface**: 侧边导航栏，组织应用程序功能
- **StackedWidget**: 内容区域，管理不同功能界面
- **EventEngine**: 事件驱动架构的核心
- **BaseMonitor**: 监控表格的基类（使用 FluentTableWidget）
- **BaseApp**: App 的元数据定义

### 工作流程

1. **启动**: 创建 Qt 应用 → 应用 Fluent 主题 → 创建引擎 → 创建主窗口 → 显示
2. **数据流**: Gateway → EventEngine → Signal → Widget
3. **用户操作**: Widget → Engine → MainEngine → Gateway
4. **动态加载**: BaseApp 元数据 → 动态导入 → 创建 Widget

### 设计优势

- **解耦**: UI 和业务逻辑分离
- **灵活**: 用户可以自由调整布局
- **扩展**: 易于添加新功能
- **维护**: 代码结构清晰，易于维护
- **现代化**: Fluent Design 风格，提供更好的用户体验

---

**文档版本**: 2.0  
**最后更新**: 2026-01-14  
**适用版本**: VeighNa 4.3.0+  
**UI 风格**: Fluent Design（PySide6-Fluent-Widgets）
