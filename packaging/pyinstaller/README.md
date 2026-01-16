# PyInstaller 打包工具

本目录包含 MeowTrader 项目的 PyInstaller 打包脚本和工具。

## 文件说明

### build.py

主打包脚本，用于将 MeowTrader 打包为可执行文件。

**使用方法**：

```bash
# 方法 1：使用根目录的批处理脚本（推荐）
build.bat

# 方法 2：直接调用 Python 脚本
.venv/Scripts/python.exe packaging/pyinstaller/build.py
```

**可用选项**：

- `--all`：打包全量版（包含所有模块）
- `--basic`：打包基础版
- `--pro`：打包专业版
- `--custom`：打包定制版
- `--debug`：调试模式（带控制台窗口）
- `--clean`：清理打包文件
- `--zip`：打包后创建 ZIP 压缩包
- `--list`：列出可用的版本配置
- `--show`：显示已安装的 vnpy 包

### hooks/

PyInstaller 自定义 hooks 目录，包含以下 hooks：

- `hook-jaraco.py`：处理 jaraco 命名空间包
- `hook-pkg_resources.py`：处理 pkg_resources 和 jaraco vendor 依赖
- `hook-talib.py`：处理 TA-Lib 模块收集
- `hook-vnpy_ctp.py`：处理 vnpy_ctp 的 DLL
- `hook-vnpy_ctptest.py`：处理 vnpy_ctptest 的 DLL
- `hook-vnpy_jees.py`：处理 vnpy_jees 的 DLL

这些 hooks 会在打包时自动加载，无需手动指定。

## 打包流程

1. **读取配置**：从 `config/edition.*.json` 读取版本配置
2. **收集依赖**：根据配置动态收集 Gateway 和 App 模块
3. **处理 vendor 模块**：确保 `vendor/` 目录被正确包含
4. **处理 DLL**：收集 Gateway 所需的 DLL 文件
5. **执行打包**：使用 PyInstaller 进行打包
6. **后处理**：可选创建 ZIP 压缩包

## 输出目录

- **build/**：PyInstaller 的临时构建目录
- **dist/MeowTrader/**：打包后的可执行文件和依赖
- **dist/MeowTrader-v*.zip**：可选的 ZIP 压缩包

## 注意事项

1. 确保虚拟环境中已安装所有依赖
2. 某些 Gateway 需要从 `veighna_studio` 手动复制（如 `vnpy_mini`）
3. 首次打包可能需要较长时间（5-10 分钟）
4. 打包结果大小约 500 MB

## 故障排除

如果遇到问题，请查看：

- `build/MeowTrader/warn-MeowTrader.txt`：警告和错误日志
- `docs/学习笔记/打包依赖说明.md`：依赖问题排查
- `docs/学习笔记/打包目录结构说明.md`：目录结构说明
