# vnpy_okx 模块修改记录

## 基本信息

- **模块版本**: vnpy_okx-2025.06.17
- **修改日期**: 2025-12-24, 2025-12-25
- **修改文件**: `src/vnpy_okx-2025.06.17/vnpy_okx/okx_gateway.py`

## 修改记录

### okx_gateway.py

#### OkxGateway.write_log (新增方法)

**新增方法**:
```python
def write_log(self, msg: str) -> None
```

**功能**: 转义日志消息中的花括号，防止 loguru 格式化错误
- 修改前: 无此方法，直接使用父类的 `write_log`
- 修改后: 重写方法，将 `{` 替换为 `{{`，`}` 替换为 `}}`，然后调用父类方法

**修改原因**: OKX API 返回的 JSON 数据包含花括号，loguru 会将其误认为格式占位符，导致 `KeyError`

#### WebsocketApi.connect_ (修改方法)

**修改调用**:
- 修改前: `self.init(host, proxy_host, proxy_port, 20)`
- 修改后: `self.init(host, proxy_host, proxy_port, 20, gateway_name=self.gateway_name)`

**新增参数**: `gateway_name=self.gateway_name`

#### RestApi._query_history (修改方法)

**方法内部新增字段**:
- `request_delay: float = 0.5` - 请求延迟（秒）
- `max_retries: int = 3` - 最大重试次数
- `retry_delay: float = 1.0` - 重试延迟（秒）

**修改字段**:
- `elapsed_time`
  - 修改前: `elapsed_time = (end_time - begin_dt_no_tz).total_seconds()`
  - 修改后: `downloaded_time_span = (end_time - begin_dt_no_tz).total_seconds()`
  - 修改原因: 更准确地表示已下载的时间跨度，变量名更清晰

**修改功能**:
1. **异常处理和重试机制**:
   - 修改前: 无异常处理，网络错误直接中断下载
   - 修改后: 添加 `try-except` 块，捕获网络异常，实现最多 3 次重试，每次重试间隔 1 秒

2. **时区比较修复**:
   - 修改前: `if begin_dt <= req.start:`
   - 修改后: `if begin_dt.replace(tzinfo=None) <= req.start.replace(tzinfo=None):`
   - 修改原因: 避免 offset-naive 和 offset-aware datetime 比较错误

3. **日志消息修改**:
   - 日志文本 "时间范围"
     - 修改前: `f"时间范围 {begin_dt_no_tz.strftime('%Y-%m-%d %H:%M:%S')} 至 {end_dt_no_tz.strftime('%Y-%m-%d %H:%M:%S')}"`
     - 修改后: `f"本批时间范围 {begin_dt_no_tz.strftime('%Y-%m-%d %H:%M:%S')} 至 {end_dt_no_tz.strftime('%Y-%m-%d %H:%M:%S')}"`
     - 修改原因: 明确这是当前批次的时间范围，而非整体下载范围
   
   - 日志符号
     - 修改前: `f"✓ 下载完成: ..."`, `f"✓ 查询完成: ..."`, `f"✗ 查询完成: ..."`
     - 修改后: `f"[完成] 下载完成: ..."`, `f"[完成] 查询完成: ..."`, `f"[失败] 查询完成: ..."`
     - 修改原因: `✓` 和 `✗` 符号在 Windows GBK 编码下无法正确编码，会导致 `UnicodeEncodeError`
