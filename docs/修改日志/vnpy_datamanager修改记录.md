# vnpy_datamanager 模块修改记录

## 基本信息

- **模块版本**: vnpy_datamanager-1.0.8
- **修改日期**: 2025-12-24, 2025-12-25
- **修改文件**: 
  - `src/vnpy_datamanager-1.0.8/vnpy_datamanager/engine.py`
  - `src/vnpy_datamanager-1.0.8/vnpy_datamanager/ui/widget.py`

## 修改记录

### engine.py

#### ManagerEngine.download_bar_data (修改方法)

**新增参数**:
- `end: datetime | None = None` - 结束日期参数，默认值为 None（使用当前时间）
- `skip_existing: bool = True` - 智能跳过已有数据标志，默认值为 True

**方法内部新增字段**:
- `user_specified_end: bool` - 用户是否指定结束日期
  - 修改前: 无此字段
  - 修改后: 根据 `end` 参数判断，`end is None` 时为 `False`，否则为 `True`
- `should_use_smart_detection: bool` - 是否使用智能检测
  - 修改前: 无此字段
  - 修改后: `skip_existing and not user_specified_end`

**方法逻辑修改**:
- 修改前: 无智能检测逻辑，直接下载指定时间范围的数据
- 修改后: 
  1. 判断用户是否指定结束日期，设置 `user_specified_end`
  2. 仅在 `should_use_smart_detection=True` 时查询已有数据范围
  3. 根据已有数据范围智能调整下载范围，避免重复下载

### widget.py

#### ManagerWidget.__init__ (修改方法)

**修改字段**:
- `self.download_dialogs`
  - 修改前: 无此字段（或为 `self.download_dialog: DownloadDialog | None = None`）
  - 修改后: `self.download_dialogs: list = []` - 支持管理多个下载对话框实例

#### ManagerWidget.init_tree (修改方法)

**修改字段**:
- `labels` 列表长度
  - 修改前: 10 列
  - 修改后: 11 列（新增一列用于"更新"按钮）

#### ManagerWidget.refresh_tree (修改方法)

**新增功能**:
- 在数据树的每一行添加"更新"按钮
- 修改前: 只有"查看"、"导出"、"删除"按钮
- 修改后: 添加"更新"按钮，按钮布局为：查看(列7) → 导出(列8) → 更新(列9) → 删除(列10)

#### ManagerWidget.update_single_data (新增方法)

**新增方法**:
```python
def update_single_data(
    self,
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime
) -> None
```

**功能**: 更新单个数据项，从已有数据的结束时间开始下载到当前时间
- 显示确认对话框
- 调用 `engine.download_bar_data` 从已有数据的结束时间开始下载
- 使用 `skip_existing=True` 避免重复下载
- 下载完成后显示成功消息并刷新数据树

#### ManagerWidget.download_data (修改方法)

**修改功能**:
- 修改前: 使用 `dialog.exec_()`，只能打开一个对话框，阻塞等待
- 修改后: 使用 `dialog.show()`，支持同时打开多个下载对话框，非阻塞
- 新增: 将对话框添加到 `self.download_dialogs` 列表管理
- 新增: 连接 `destroyed` 信号，自动清理已关闭的对话框引用

#### ManagerWidget._on_dialog_destroyed (新增方法)

**新增方法**:
```python
def _on_dialog_destroyed(self) -> None
```

**功能**: 清理已销毁的对话框引用，从 `self.download_dialogs` 列表中移除 None 引用

#### ManagerWidget.update_data (修改方法)

**修改调用**:
- 修改前: `self.engine.download_bar_data(overview.symbol, overview.exchange, overview.interval.value, overview.end, self.output)`
- 修改后: `self.engine.download_bar_data(overview.symbol, overview.exchange, overview.interval.value, overview.end, self.output, end=None, skip_existing=True)`

#### DownloadDialog.__init__ (修改方法)

**新增字段**:
- `self.end_date_edit: QtWidgets.QDateEdit` - 结束日期选择器
- `self.use_end_date_checkbox: QtWidgets.QCheckBox` - "指定结束日期"复选框

**删除字段**:
- `self.skip_existing_checkbox: QtWidgets.QCheckBox` - "智能跳过已有数据"复选框

**新增属性设置**:
- `self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)` - 关闭时自动清理资源

**UI布局修改**:
- 修改前: 只有开始日期选择器
- 修改后: 添加结束日期选择器和"指定结束日期"复选框，移除"智能跳过已有数据"复选框

#### DownloadDialog.download (修改方法)

**修改字段**:
- `skip_existing` 的计算方式
  - 修改前: `skip_existing: bool = self.skip_existing_checkbox.isChecked()`
  - 修改后: `skip_existing: bool = not self.use_end_date_checkbox.isChecked()`

**修改逻辑**:
- 修改前: 根据用户勾选的复选框决定是否跳过已有数据
- 修改后: 根据是否指定结束日期自动判断，未指定结束日期时进行智能检测

#### DownloadDialog.on_finished (修改方法)

**修改字段**:
- 状态标签文本
  - 修改前: `f"✓ 下载完成！共下载 {count} 条数据"`
  - 修改后: `f"[完成] 下载完成！共下载 {count} 条数据"`

**新增功能**:
- 修改前: 显示完成消息后，对话框不自动关闭
- 修改后: 显示完成消息后，调用 `self.accept()` 自动关闭对话框

#### DownloadWorker._output_callback (修改方法)

**保留字段**:
- `progress_info` 信号定义保留，但不再实际使用（不影响功能）
