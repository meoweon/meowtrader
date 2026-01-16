# VeighNa Station 接口机制和修改方法

## 一、接口发现机制

### 核心机制

VeighNa Station 使用**硬编码的接口列表**来显示交易接口，而不是动态扫描已安装的包。

### 关键文件位置

- **硬编码列表文件**: `C:\veighna_studio\Lib\site-packages\veighna_station\info.pyc`
- **关键变量**: `GATEWAY_INFO` (列表类型)

### 数据结构

`GATEWAY_INFO` 是一个列表，每个元素是一个字典，包含：

```python
{
    'name': '接口显示名称',
    'module': 'vnpy_xxx',      # 包名
    'class': 'XxxGateway',     # Gateway 类名
    'description': '接口描述'
}
```

### 当前接口列表（21个）

1. CTP (vnpy_ctp)
2. CTP测试 (vnpy_ctptest)
3. CTP Mini (vnpy_mini)
4. 飞马 (vnpy_femas)
5. CTP期权 (vnpy_sopt)
6. CTP期权测试 (vnpy_sopttest)
7. 顶点HTS (vnpy_hts)
8. 恒生UFT (vnpy_uft)
9. 中泰XTP (vnpy_xtp)
10. 华鑫奇点股票 (vnpy_tora)
11. 华鑫奇点期权 (vnpy_tora)
12. 盈透证券 (vnpy_ib)
13. 易盛9.0外盘 (vnpy_tap)
14. 直达期货 (vnpy_da)
15. 融航 (vnpy_lstar)
16. 融航 (vnpy_rohon)
17. 杰宜斯 (vnpy_jees)
18. TTS (vnpy_tts)
19. 迅投研 (vnpy_xt)
20. RQData (vnpy_rqdata)
21. RPC服务 (vnpy_rpcservice)

**注意**: OKX 和 Binance **不在**这个列表中！

## 二、Station 启动入口

### 启动流程

```
station.exe (或 python -m veighna_station)
  ↓
__main__.pyc
  ↓
run.pyc
  ↓
fluent_mainwindow.pyc (Fluent 主窗口)
  ↓
widget.pyc (使用 GATEWAY_INFO 显示接口列表)
```

### 关键文件说明

- `__main__.pyc` - 入口点，调用 `run_station()`
- `run.pyc` - 主运行逻辑，创建 FluentMainWindow
- `widget.pyc` - UI 组件，使用 `GATEWAY_INFO` 构建接口选择界面
- `info.pyc` - **硬编码列表所在**

## 三、问题原因

即使 `vnpy_okx` 和 `vnpy_binance` 已正确安装，Station 也不会显示它们，因为：

1. Station 使用硬编码列表，不会动态扫描已安装的包
2. 新接口需要 VeighNa 官方在 Station 更新时添加到列表中
3. 即使包已安装且可以正常导入，如果不在 `GATEWAY_INFO` 列表中，Station 也不会显示

## 四、能否修改？

### 答案：可以修改，但有限制

#### 运行时修改（可行）

- ✅ 可以在 Python 运行时修改 `info.GATEWAY_INFO`
- ✅ 修改后立即生效
- ❌ Station 重启后失效（因为从 .pyc 重新加载）

#### 持久化修改（困难）

- ❌ 直接修改 `.pyc` 文件很复杂（需要反编译、修改、重新编译）
- ❌ `.pyc` 是编译后的字节码，不是源代码
- ⚠️ 修改后可能被 Station 更新覆盖

### 为什么可以修改？

`GATEWAY_INFO` 是一个普通的 Python 列表对象，存储在模块的命名空间中。虽然定义在 `.pyc` 文件中，但一旦加载到内存，就可以像普通对象一样修改。

### 为什么重启后失效？

因为 Station 每次启动时都会从 `.pyc` 文件重新加载模块，`GATEWAY_INFO` 会重新初始化为硬编码的值。

## 五、解决方案

### 方案 1: 使用启动器脚本（推荐）⭐

**文件**: `station_launcher_correct.py`

**使用方法**:
```bash
python station_launcher_correct.py
```

**原理**: 
- 在 Station 启动前导入 `info` 模块
- 修改 `GATEWAY_INFO` 列表，添加 OKX 和 Binance 接口
- 然后启动 Station（使用 Python 模块方式，确保在同一进程中）

**优点**:
- 简单易用
- 不需要修改 Station 文件
- 每次启动自动应用
- 补丁在 Station 启动前应用，确保生效

**缺点**:
- 需要用启动器启动，不能直接用 `station.exe`
- 如果使用 `subprocess` 启动 `station.exe`，会在新进程中运行，补丁不会生效

**使用步骤**:
1. 运行 `python station_launcher_correct.py` 启动 Station
2. 或者创建快捷方式指向这个脚本
3. 每次启动会自动添加 OKX 和 Binance 接口到接口列表

**添加的接口**:
- OKX (vnpy_okx.OkxGateway)
- Binance现货 (vnpy_binance.BinanceSpotGateway)
- Binance合约 (vnpy_binance.BinanceLinearGateway)
- Binance反向合约 (vnpy_binance.BinanceInverseGateway)

### 方案 2: 创建快捷方式包装器

创建一个批处理文件 `start_station.bat`:
```batch
@echo off
cd /d "C:\Users\GALAX\Desktop\project\vnpy"
python station_launcher_correct.py
```

然后创建桌面快捷方式指向这个批处理文件。

### 方案 3: 等待官方更新

联系 VeighNa 官方，请求在下一版本中添加 OKX 和 Binance 接口支持。

### 方案 4: 使用脚本启动 VeighNa Trader（绕过 Station）

如果不需要使用 Station 的界面，可以直接用脚本启动 VeighNa Trader，可以加载任何已安装的接口。

## 六、技术细节

### 接口加载机制

1. **Station 启动时**:
   - 从 `info.pyc` 加载 `GATEWAY_INFO` 列表
   - `widget.pyc` 使用这个列表构建接口选择界面

2. **用户选择接口后**:
   - `trader.pyc` 负责动态导入和加载选中的接口
   - 使用 `importlib` 动态导入模块和类
   - 调用 `main_engine.add_gateway()` 注册接口

3. **补丁应用时机**:
   - 必须在 Station 启动前应用
   - 必须在同一 Python 进程中运行 Station
   - 如果使用 `subprocess` 启动 `station.exe`，补丁不会生效

### 验证补丁是否生效

启动 Station 后，在【交易】界面的【交易接口】列表中应该能看到：
- OKX
- Binance现货
- Binance合约
- Binance反向合约

如果看不到，检查：
1. 补丁是否在 Station 启动前应用
2. Station 是否在同一进程中运行（不是通过 `station.exe` 启动）
3. `vnpy_okx` 和 `vnpy_binance` 是否正确安装

## 七、常见问题

### Q: 为什么补丁应用了但 Station 中还是看不到接口？

A: 可能的原因：
1. Station 通过 `subprocess` 在新进程中启动，不会继承补丁
2. Station 在启动时重新加载了模块
3. 需要使用 `station_launcher_correct.py` 启动，而不是直接运行 `station.exe`

### Q: 能否永久修改 Station 的接口列表？

A: 理论上可以，但：
1. 需要反编译 `.pyc` 文件
2. 修改源代码
3. 重新编译
4. 技术难度高，且可能被 Station 更新覆盖

### Q: 每次都要用启动器启动吗？

A: 是的，因为 Station 每次启动都会重新加载模块。使用启动器是最简单可靠的方法。

## 八、运行目录设置

### Station 的运行目录机制

VeighNa Trader 的运行目录由 `vnpy.trader.utility._get_trader_dir()` 函数确定：
- 如果当前工作目录存在 `.vntrader` 文件夹，则使用当前工作目录
- 否则，使用用户主目录下的 `.vntrader` 文件夹

**关键问题**：Station 启动 Trader 时，Trader 是在**独立的子进程**中运行的。Station 使用 `QProcess` 或 `subprocess` 启动 Trader，子进程的工作目录由 Station 控制，而不是由启动 Station 的脚本控制。

**为什么启动器无法设置运行目录？**

1. Station 的代码是编译的（`.pyc` 文件），我们无法修改其启动 Trader 的逻辑
2. Station 启动 Trader 时，会在子进程中运行，子进程的工作目录由 Station 决定
3. 即使我们在启动 Station 前设置了工作目录，Station 启动 Trader 时也不会使用这个目录
4. Station 有自己的运行目录管理机制，通过界面设置并保存在配置中

### 设置运行目录的方法

**唯一可靠的方法：在 Station 界面中手动设置**

1. 启动 VeighNa Station（使用 `station_launcher_correct.py`）
2. 点击左侧的【交易】按钮
3. 在右下角找到【修改】按钮
4. 点击【修改】按钮，选择目标运行目录（例如：`C:\Users\GALAX\Desktop\project\vnpy`）
5. Station 会记住这个设置，并在启动 Trader 时使用正确的目录

**注意**：
- 确保目标目录中存在 `.vntrader` 文件夹（如果不存在，Station 会自动创建）
- 这个设置会保存在 Station 的配置中，下次启动时仍然有效
- 这是唯一可靠的方法，因为 Station 会控制 Trader 子进程的工作目录

### 验证运行目录

启动 Trader 后，可以在 Trader 窗口的标题栏中看到运行目录，格式为：
```
VeighNa Trader 社区版 - 4.2.0   [C:\Users\GALAX\Desktop\project\vnpy]
```

如果标题栏显示的不是目标目录，请在 Station 界面中重新设置。

## 九、总结

- **问题根源**: Station 使用硬编码的接口列表，不会自动发现新安装的接口
- **解决方案**: 使用 `station_launcher_correct.py` 启动器，在 Station 启动前自动添加接口
- **运行目录**: 
  - **无法通过启动器自动设置**（因为 Station 在子进程中启动 Trader，工作目录由 Station 控制）
  - **必须**在 Station 界面中手动点击【修改】按钮设置运行目录
  - Station 会记住这个设置，下次启动时仍然有效
- **限制**: 每次启动都需要使用启动器，不能直接用 `station.exe`
- **推荐**: 创建快捷方式指向启动器脚本，方便日常使用

