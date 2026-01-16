# vnpy_binance 模块修改记录

## 基本信息

- **模块版本**: vnpy_binance-2025.06.17
- **修改日期**: 2025-12-24
- **修改文件**: 
  - `src/vnpy_binance-2025.06.17/vnpy_binance/spot_gateway.py`
  - `src/vnpy_binance-2025.06.17/vnpy_binance/linear_gateway.py`
  - `src/vnpy_binance-2025.06.17/vnpy_binance/inverse_gateway.py`

## 修改记录

### spot_gateway.py

#### RestApi.query_history (修改方法)

**方法内部新增字段**:
- `request_delay: float = 0.5` - 请求延迟（秒）
- `max_retries: int = 3` - 最大重试次数
- `retry_delay: float = 1.0` - 重试延迟（秒）

**修改功能**:
1. **异常处理和重试机制**:
   - 修改前: 无异常处理，网络错误直接中断下载
   - 修改后: 添加 `try-except` 块，捕获网络异常（`SSLError`, `ConnectionError`, `TimeoutError` 等），实现最多 3 次重试，每次重试间隔 1 秒

2. **时区比较修复**:
   - 修改前: `if begin_dt <= req.start:`
   - 修改后: `if begin_dt.replace(tzinfo=None) <= req.start.replace(tzinfo=None):`
   - 修改原因: 避免 offset-naive 和 offset-aware datetime 比较错误

### linear_gateway.py

#### RestApi.query_history (修改方法)

**方法内部新增字段**:
- `request_delay: float = 0.5` - 请求延迟（秒）
- `max_retries: int = 3` - 最大重试次数
- `retry_delay: float = 1.0` - 重试延迟（秒）

**修改功能**:
1. **异常处理和重试机制**:
   - 修改前: 无异常处理，网络错误直接中断下载
   - 修改后: 添加 `try-except` 块，捕获网络异常，实现最多 3 次重试，每次重试间隔 1 秒

2. **时区比较修复**:
   - 修改前: `if begin_dt <= req.start:`
   - 修改后: `if begin_dt.replace(tzinfo=None) <= req.start.replace(tzinfo=None):`

### inverse_gateway.py

#### RestApi.query_history (修改方法)

**方法内部新增字段**:
- `request_delay: float = 0.5` - 请求延迟（秒）
- `max_retries: int = 3` - 最大重试次数
- `retry_delay: float = 1.0` - 重试延迟（秒）

**修改功能**:
1. **异常处理和重试机制**:
   - 修改前: 无异常处理，网络错误直接中断下载
   - 修改后: 添加 `try-except` 块，捕获网络异常，实现最多 3 次重试，每次重试间隔 1 秒

2. **时区比较修复**:
   - 修改前: `if begin_dt <= req.start:`
   - 修改后: `if begin_dt.replace(tzinfo=None) <= req.start.replace(tzinfo=None):`

**说明**: 三个 Binance 网关（现货、线性合约、反向合约）的修改完全相同，保持代码一致性。
