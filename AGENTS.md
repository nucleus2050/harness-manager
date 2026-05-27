# AGENTS.md

## 项目概览

本项目正在从 Skill Package Manager 升级为 Harness Manager。

Harness Manager 是一个本地 Windows 桌面应用，用来管理完成某项任务所需的资源集合。一个 Harness 是可复用的任务工具包。当前设计方向中，一个 Harness 可以包含：

- `AGENTS.md` 指令
- MCP 配置资产
- Skill 资产

Hook 支持暂缓实现，因为 Codex、Claude Code、OpenCode 以及其他工具在 Hook 模型和安装约定上差异较大。

## 核心产品设计

### Harness

Harness 表示某个任务或工作流所需的完整上下文和工具集合，例如代码审查、前端开发、写作、数据分析或某个项目专用工作流。

Harness 是早期 Package 概念的升级版。迁移过程中必须保持现有 Skill 管理流程可用，不能破坏已经能工作的导入、安装、卸载和导出能力。

### Asset

Asset 是工具管理的可复用资源。第一阶段升级包含以下资产类型：

- `agents_md`：以 AGENTS.md 内容形式保存的项目或任务指令。
- `mcp`：MCP server 配置片段或配置文件。
- `skill`：现有的 Skill 目录资产。

未来可能加入的 `hook` 类型暂不在当前阶段实现。

### 导入来源

应用支持从以下来源导入资产：

- Codex 默认目录或自定义目录
- Claude Code 默认目录或自定义目录
- OpenCode 默认目录或自定义目录
- 用户添加的自定义目录
- 离线 Harness 包

对于已知工具目录，导入时应直接使用已配置路径。只有自动发现失败、配置缺失或路径无效时，才要求用户选择目录。

## 架构

应用采用分层 Python 架构：

- `src/skillpkg/app_paths.py`：解析应用运行根目录和运行时目录。
- `src/skillpkg/db.py`：SQLite schema 初始化和事务处理。
- `src/skillpkg/repositories.py`：数据库 CRUD 访问层。
- `src/skillpkg/services.py`：核心文件系统和数据库用例。
- `src/skillpkg/file_ops.py`：安全复制、删除、压缩和解压工具。
- `src/skillpkg/fingerprint.py`：确定性的资产 fingerprint 计算。
- `src/skillpkg/client_detection.py`：支持工具的默认路径检测。
- `src/skillpkg/gui/`：PySide6 用户界面、弹窗、样式和 controller 连接。
- `tests/`：pytest 测试，覆盖路径、数据库、服务、归档、GUI 文案/样式契约和导入来源行为。

核心服务必须保持独立于 Qt。GUI 代码应通过 controller/service 调用业务能力，不应直接执行数据库或文件系统业务逻辑。

## 技术栈

- 语言：Python 3.11+
- GUI：PySide6 / Qt Widgets
- 数据库：Python 标准库 `sqlite3` 管理 SQLite
- 测试：pytest
- 打包：通过 `scripts/build.ps1` 使用 PyInstaller
- 运行数据：存储在应用工作目录下

## 运行目录方向

当前运行目录仍有部分 Skill 导向结构。Harness Manager 的目标运行目录为：

```text
HarnessManager/
  data/
    harness.db
  assets/
    agents/
      <asset_id>/AGENTS.md
    mcp/
      <asset_id>/mcp.json
    skills/
      <asset_id>/...
  exports/
    <harness-name>.harness.zip
  config/
    settings.json
```

迁移期间可以保留现有 `skills/` 和 `.skillpkg.zip` 行为，但新的设计和实现应逐步转向 `assets/` 和 `.harness.zip`。

## Agent 开发规则

1. `AGENTS.md` 必须自维护。当技术架构、产品设计或主要功能发生变化时，Agent 需要提出更新本文件，但必须先获得用户明确同意，不能擅自写入。
2. 每次任务完成都必须提交 git。提交前必须运行与本次变更相关的验证命令，并确认工作区状态。
3. 在迁移到 Harness Manager 的过程中，必须保护当前已工作的 Skill 流程，避免大规模重写导致导入、安装、卸载、导出或测试行为损坏。
4. 核心逻辑必须在不依赖 PySide6 的情况下可测试。业务逻辑应放在 services/repositories，GUI 代码保持轻量。
5. 文件系统操作属于高风险操作。必须校验路径，避免路径穿越，禁止删除记录范围之外的路径，并保留基于 fingerprint 的卸载安全检查。
6. 用户界面中的用户可见文案必须使用中文，除非用户明确要求使用其他语言。
7. 在 Hook 的跨工具模型被明确设计并批准前，不要实现 Hook 支持。
8. `AGENTS.md` 本身必须使用中文维护。

## 验证要求

普通代码变更运行：

```powershell
pytest -q
python -m compileall -q src tests
```

仅 GUI 变更且不方便实际启动窗口时，还应验证导入，例如：

```powershell
python -c "from skillpkg.gui.main_window import MainWindow; print('gui import ok')"
```

构建相关变更需要验证 `scripts/build.ps1` 语法和 PyInstaller 调用方式。
