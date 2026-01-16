# MeowTrader

基于 [vnpy](https://www.vnpy.com/) 的量化交易软件。

## 特性

- 多版本支持：精简版 / 专业版 / 定制版
- 多入口支持：Desktop / Server / Web
- 多平台支持：Windows / Linux
- Fluent Design UI
- 模块化架构

## 目录结构

```
meowtrader/
├── app/                    # 入口层
│   ├── desktop/           # 桌面入口
│   ├── server/            # 服务端入口
│   ├── web/               # Web 入口
│   └── ui/                # UI 组件
│       ├── fluent/        # Fluent UI 组件
│       └── legacy/        # 传统 UI 组件
├── core/                   # 产品层
│   ├── engine/            # 产品引擎
│   ├── registry/          # 模块注册
│   ├── config/            # 配置管理
│   └── runtime/           # 运行时管理
├── vendor/                 # vnpy 模块
│   ├── vnpy/              # 核心框架
│   ├── gateways/          # 交易接口
│   ├── apps/              # 功能模块
│   ├── db/                # 数据库
│   └── libs/              # 工具库
├── extensions/             # 自研扩展
├── config/                 # 配置文件
├── resources/              # 打包资源（exe 图标等）
├── scripts/                # 构建脚本
└── docs/                   # 文档
```

## 安装 uv

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Linux / macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

或者使用 pip:
```bash
pip install uv
```

## 快速开始

### 1. 创建虚拟环境并安装依赖

```bash
# 在 meowtrader 目录下
cd meowtrader

# 创建虚拟环境（如果不存在）并同步依赖
uv sync

# 或者指定 Python 版本
uv sync --python 3.11
```

#### 尝试 Python 3.13

```bash
# 1. 创建 Python 3.13 虚拟环境
uv venv .venv313 --python 3.13

# 2. 激活并安装依赖
.venv313\Scripts\activate
uv sync
```

### 2. 激活虚拟环境

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

或者使用 uv 的 `run` 命令（无需激活环境）：

```bash
uv run python -m meowtrader.app.desktop
```

### 3. 安装开发依赖

```bash
# 安装开发依赖
uv sync --extra dev

# 安装所有可选依赖
uv sync --all-extras
```

### 4. 添加新依赖

```bash
# 添加运行时依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 添加可选依赖
uv add --optional postgresql package-name
```

### 5. 更新依赖

```bash
# 更新所有依赖到最新版本
uv sync --upgrade

# 更新特定包
uv add --upgrade package-name
```

### 6. 运行命令

**注意**: 如果遇到文件锁定错误（-2147024786），这是 Windows 临时性问题。可以：

#### 方式 A：直接使用虚拟环境（推荐）

```powershell
# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 运行主程序
python -m app.desktop

# 运行服务器
python -m app.server

# 运行 Web 服务
python -m app.web
```

#### 方式 B：使用 uv run（如果无文件锁定错误）

```powershell
# 运行主程序
uv run python -m app.desktop

# 或者尝试（可能会遇到文件锁定，重试即可）
uv run meowtrader
```

#### 开发命令

```powershell
# 运行测试
.venv\Scripts\python.exe -m pytest

# 代码格式化
.venv\Scripts\python.exe -m black meowtrader
.venv\Scripts\python.exe -m ruff check meowtrader
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `uv sync` | 创建虚拟环境并安装所有依赖 |
| `uv sync --dev` | 包含开发依赖 |
| `uv add <package>` | 添加依赖到 pyproject.toml |
| `uv remove <package>` | 移除依赖 |
| `uv run <command>` | 在虚拟环境中运行命令 |
| `uv lock` | 更新锁文件 |
| `uv pip install <package>` | 直接安装包（不修改 pyproject.toml） |

## 优势

1. **速度极快**: uv 使用 Rust 编写，比 pip 快 10-100 倍
2. **自动管理**: 自动创建和管理虚拟环境
3. **依赖解析**: 更快的依赖解析和冲突检测
4. **兼容性**: 完全兼容 pip 和 pyproject.toml
5. **锁文件**: 自动生成 `uv.lock` 确保可重现的构建

## 注意事项

- 虚拟环境默认创建在 `.venv/` 目录（已在 `.gitignore` 中）
- `uv.lock` 文件应该提交到版本控制，确保依赖版本一致
- 如果同时使用 pip，建议统一使用 uv 避免冲突

## 迁移指南

如果之前使用 pip/venv:

```bash
# 1. 删除旧的虚拟环境
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# 2. 使用 uv 创建新环境
uv sync

# 3. 后续使用 uv 命令管理依赖
```

## 版本说明

| 版本 | 说明 |
|------|------|
| Basic | 精简版，基础交易功能 |
| Pro | 专业版，完整功能 |
| Custom | 定制版，按需配置 |

## 开发

```powershell
# 安装开发依赖
uv sync --extra dev

# 运行测试
uv run pytest

# 代码格式化
uv run black meowtrader
uv run ruff check meowtrader

# 类型检查
uv run mypy meowtrader
```

## 故障排查

### 文件锁定错误（-2147024786）

这是 Windows 上的临时性问题，通常不影响已安装的包。如果遇到：

1. **继续使用**: 即使看到错误，包通常已经安装成功。直接激活虚拟环境使用即可：
   ```powershell
   .venv\Scripts\Activate.ps1
   python -m app.desktop
   ```

2. **清理重建**: 如果确实需要重新安装：
   ```powershell
   Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
   uv sync --no-cache
   ```

3. **以管理员运行**: 如果问题持续，以管理员身份运行 PowerShell。

更多详细排查指南，请查看 [TROUBLESHOOTING_UV.md](TROUBLESHOOTING_UV.md)。

## 更多信息

- [uv 官方文档](https://github.com/astral-sh/uv)
- [uv 使用指南](https://github.com/astral-sh/uv/blob/main/README.md)

## 许可证

MIT License
