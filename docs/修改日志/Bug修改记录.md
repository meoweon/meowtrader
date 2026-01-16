# Bug 修改记录

本文档记录 MeowTrader 项目中发现并修复的 Bug。

---

## 2026-01-16: PyQt/PySide6 兼容性问题修复

### 问题描述

在运行 `python -m meowtrader.app.desktop` 时，点击导航栏中的 App 功能（如 RPC 服务）时出现错误：

```
AttributeError: module 'PySide6.QtCore' has no attribute 'pyqtSignal'
```

### 根本原因

vnpy 的某些模块使用了 PyQt 的 API（`pyqtSignal`、`exec_()`），而项目使用的是 PySide6，API 名称不同。

**API 差异**:
- PyQt: `pyqtSignal`, `exec_()`
- PySide6: `Signal`, `exec()`

### 修复内容

#### 1. `pyqtSignal` → `Signal`（2 个文件，4 处）

**文件 1**: `meowtrader/vendor/apps/vnpy_rpcservice/rpc_service/ui/widget.py`
- **位置**: 第 10 行
- **修改前**: `signal_log: QtCore.pyqtSignal = QtCore.pyqtSignal(Event)`
- **修改后**: `signal_log: QtCore.Signal = QtCore.Signal(Event)`

**文件 2**: `meowtrader/vendor/apps/vnpy_chartwizard/ui/widget.py`
- **位置**: 第 22-24 行
- **修改前**: 
  ```python
  signal_tick: QtCore.pyqtSignal = QtCore.pyqtSignal(Event)
  signal_spread: QtCore.pyqtSignal = QtCore.pyqtSignal(Event)
  signal_history: QtCore.pyqtSignal = QtCore.pyqtSignal(Event)
  ```
- **修改后**: 
  ```python
  signal_tick: QtCore.Signal = QtCore.Signal(Event)
  signal_spread: QtCore.Signal = QtCore.Signal(Event)
  signal_history: QtCore.Signal = QtCore.Signal(Event)
  ```

#### 2. `exec_()` → `exec()`（5 个文件，13 处）

**文件 1**: `meowtrader/vendor/apps/vnpy_datamanager/ui/widget.py`
- **位置**: 第 210, 268, 310 行
- **修改**: `dialog.exec_()` → `dialog.exec()`（3 处）

**文件 2**: `meowtrader/vendor/apps/vnpy_ctastrategy/ui/widget.py`
- **位置**: 第 168, 197, 315 行
- **修改**: `editor.exec_()` → `editor.exec()`（2 处），`dialog.exec_()` → `dialog.exec()`（1 处）

**文件 3**: `meowtrader/vendor/apps/vnpy_portfoliostrategy/ui/widget.py`
- **位置**: 第 133, 268 行
- **修改**: `editor.exec_()` → `editor.exec()`（2 处）

**文件 4**: `meowtrader/vendor/apps/vnpy_ctabacktester/ui/widget.py`
- **位置**: 第 477, 485, 493, 504 行
- **修改**: `self.trade_dialog.exec_()` → `self.trade_dialog.exec()`（1 处）
- **修改**: `self.order_dialog.exec_()` → `self.order_dialog.exec()`（1 处）
- **修改**: `self.daily_dialog.exec_()` → `self.daily_dialog.exec()`（1 处）
- **修改**: `self.candle_dialog.exec_()` → `self.candle_dialog.exec()`（1 处）

**文件 5**: `meowtrader/vendor/apps/vnpy_riskmanager/ui/widget.py`
- **位置**: 第 97 行
- **修改**: `super().exec_()` → `super().exec()`（1 处）

### 修复统计

| 问题类型 | 文件数 | 修复处数 |
|---------|-------|---------|
| `pyqtSignal` → `Signal` | 2 | 4 |
| `exec_()` → `exec()` | 5 | 13 |
| **总计** | **7** | **17** |

### 验证结果

修复后，所有模块可以正常导入和运行：
- ✅ 模块导入测试：全部通过
- ✅ 桌面启动：成功
- ✅ App 功能打开：正常（不再报错）

### 相关文件

- 修复文件：7 个 vendor 模块文件
- 测试脚本：`meowtrader/scripts/test_imports.py`

---

## 修复流程

### 发现方式

1. 运行桌面入口时触发错误
2. 错误堆栈指向 `vnpy_rpcservice` 模块
3. 通过 grep 搜索发现多个模块存在相同问题

### 修复方法

1. **搜索问题代码**: 使用 `grep` 搜索 `pyqtSignal` 和 `exec_()`
2. **批量替换**: 使用 `search_replace` 工具批量修复
3. **验证修复**: 运行测试脚本和桌面入口验证

### 预防措施

- ✅ 在 `pyproject.toml` 中明确依赖 `PySide6` 而非 `PyQt`
- ✅ 代码审查时注意检查 PyQt/PySide6 API 差异
- ✅ 运行测试脚本验证模块导入

---

## 其他检查项

### 已验证无问题的部分

- ✅ `pyqtgraph`: 独立图表库，与 PySide6 兼容，无需修改
- ✅ `QtCore.Qt` 枚举: PySide6 正常支持
- ✅ Signal/Slot 连接: 标准用法，无问题
- ✅ 其他 Qt API: 未发现其他兼容性问题

---

**最后更新**: 2026-01-16  
**修复版本**: MeowTrader 0.1.0
