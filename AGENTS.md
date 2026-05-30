# AGENTS.md

## 项目概览

本项目已从 Skill Package Manager 迁移为 Harness Manager，中文产品概念统一为“任务套件管理器”。

任务套件管理器是一个本地 Windows 桌面应用，用来管理完成某项任务所需的资源集合。一个任务套件是可复用的任务工具包。当前设计方向中，一个任务套件可以包含：

- `AGENTS.md` 指令
- Agent 智能体配置资产
- MCP 配置资产
- Skill 资产

Hook 支持暂缓实现，因为 Codex、Claude Code、OpenCode 以及其他工具在 Hook 模型和安装约定上差异较大。

## 核心产品设计

### 任务套件

任务套件表示某个任务或工作流所需的完整上下文和工具集合，例如代码审查、前端开发、写作、数据分析或某个项目专用工作流。

任务套件是早期 Package 概念的升级版。迁移过程中必须保持现有 Skill 管理流程可用，不能破坏已经能工作的导入、安装、卸载和导出能力。用户界面中不要继续使用“软件包”作为核心名称。

### Asset

组件（Asset）是工具管理的可复用资源。第一阶段升级包含以下组件类型：

- `agents_md`：以 AGENTS.md 内容形式保存的项目或任务指令。
- `agent`：Codex、Claude Code 或 OpenCode 的单个 Agent / Subagent 定义文件。
- `mcp`：MCP server 配置片段或配置文件。
- `skill`：现有的 Skill 目录资产。

未来可能加入的 `hook` 类型暂不在当前阶段实现。

### 导入来源

应用支持从以下来源导入资产：

- Codex 默认目录或自定义目录
- Claude Code 默认目录或自定义目录
- OpenCode 默认目录或自定义目录
- 用户添加的自定义目录
- 离线任务套件包

对于已知工具目录，导入时应直接使用已配置路径。只有自动发现失败、配置缺失或路径无效时，才要求用户选择目录。

## 架构

应用采用分层 Python 架构：

- `src/harness_manager/app_paths.py`：解析应用运行根目录和运行时目录。
- `src/harness_manager/db.py`：SQLite schema 初始化和事务处理。
- `src/harness_manager/repositories.py`：数据库 CRUD 访问层。
- `src/harness_manager/services.py`：核心文件系统和数据库用例。
- `src/harness_manager/file_ops.py`：安全复制、删除、压缩和解压工具。
- `src/harness_manager/fingerprint.py`：确定性的资产 fingerprint 计算。
- `src/harness_manager/client_detection.py`：支持工具的默认路径检测。
- `src/harness_manager/gui/`：PySide6 用户界面、弹窗、样式和 controller 连接。
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
    agent_configs/
      <asset_id>/agent.toml
      <asset_id>/agent.md
    mcp/
      <asset_id>/mcp.json
    skills/
      <asset_id>/...
  exports/
    <任务套件名称>.harness.zip
  config/
    settings.json
```

迁移期间可以保留现有 `skills/` 目录以保护 Skill 流程，但新的导出包名和实现应转向 `assets/` 和 `.harness.zip`。

## Agent 开发规则

1. `AGENTS.md` 必须自维护。当技术架构、产品定位、核心边界或开发规则发生变化时，Agent 需要提出更新本文件，但必须先获得用户明确同意，不能擅自写入。
2. `AGENTS.md` 是项目地图，不是需求列表。具体功能、交互细节和阶段任务应写入需求文档、设计文档或计划文档，不应堆叠进本文件。
3. 每次任务完成都必须提交 git。提交前必须运行与本次变更相关的验证命令，并确认工作区状态。
4. 在迁移到 Harness Manager 的过程中，必须保护当前已工作的 Skill 流程，避免大规模重写导致导入、安装、卸载、导出或测试行为损坏。
5. 核心逻辑必须在不依赖 PySide6 的情况下可测试。业务逻辑应放在 services/repositories，GUI 代码保持轻量。
6. 文件系统操作属于高风险操作。必须校验路径，避免路径穿越，禁止删除记录范围之外的路径，并保留基于 fingerprint 的卸载安全检查。
7. 用户界面中的用户可见文案必须使用中文，除非用户明确要求使用其他语言。
8. 在 Hook 的跨工具模型被明确设计并批准前，不要实现 Hook 支持。
9. `AGENTS.md` 本身必须使用中文维护。

## 验证要求

普通代码变更运行：

```powershell
pytest -q
python -m compileall -q src tests
```

仅 GUI 变更且不方便实际启动窗口时，还应验证导入，例如：

```powershell
python -c "from harness_manager.gui.main_window import MainWindow; print('gui import ok')"
```

构建相关变更需要验证 `scripts/build.ps1` 语法和 PyInstaller 调用方式。
