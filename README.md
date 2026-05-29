# Harness Manager（任务套件管理器）

Harness Manager 是一个本地 Windows 桌面应用，用来管理完成某项任务所需的上下文和工具组件。它把分散在 Codex、Claude Code、OpenCode 等工具里的 `Skill`、`AGENTS.md` 和 MCP 配置整理成可复用的“任务套件”，并支持把套件部署到不同工具的默认目录或项目目录。

当前暂不实现 Hook 管理，因为不同工具的 Hook 标准和安装方式差异较大。

![Harness Manager 主界面](docs/images/harness-manager-01-overview.png)

> 截图使用示例数据生成，用于展示任务套件列表、组件统计、导入来源、组件详情和部署入口。

## 适合谁使用

- 同时使用 Codex、Claude Code、OpenCode，并希望复用同一套任务上下文的用户。
- 经常为不同任务准备不同 Skill、MCP 和 `AGENTS.md` 的开发者。
- 希望把某项工作需要的工具组件整理成可导入、可导出、可部署集合的团队。

## 推荐工作流

```text
导入或新建组件
  ↓
在组件库中维护 Skill / AGENTS.md / MCP
  ↓
创建任务套件并把组件加入套件
  ↓
按全局或项目范围部署到 Codex / Claude Code / OpenCode
  ↓
任务结束后可撤销部署，或导出 .harness.zip 离线共享
```

## 完整使用流程

下面的截图使用示例数据生成，展示了多个任务套件同时管理的典型流程。

### 1. 查看任务套件总览

左侧展示组件统计和导入来源，中间是多个任务套件，右侧展示当前选中套件已加入的 Skill、AGENTS.md 和 MCP。套件卡片上的图标用于切换部署范围并部署到 Codex、Claude Code 或 OpenCode。

![任务套件总览](docs/images/harness-manager-01-overview.png)

### 2. 选择不同任务套件查看详情

选中某个任务套件后，右侧会按组件类型分组展示具体加入了哪些 Skill、AGENTS.md 和 MCP，避免只看到“1 个、2 个”但不知道具体内容。

![任务套件详情](docs/images/harness-manager-02-harness-detail.png)

### 3. 在技能库维护 Skill

技能库列出当前应用管理的所有 Skill。每个 Skill 都可以从列表中加入任务套件、移出任务套件或删除；加入套件时会选择目标任务套件，已加入的组件不会重复加入。

![技能库](docs/images/harness-manager-03-skill-library.png)

### 4. 管理 AGENTS.md 组件

AGENTS.md 作为独立组件维护，可以直接新建，也可以从文件导入。列表展示名称、描述和内容摘要；一个任务套件最多加入一个 AGENTS.md。

![AGENTS.md 组件库](docs/images/harness-manager-04-agents-library.png)

### 5. 管理 MCP 配置

MCP 页面用于维护 MCP JSON 配置，支持显示名称、描述和配置摘要。MCP 作为组件加入任务套件，而不是直接绑定某个具体客户端。

![MCP 组件库](docs/images/harness-manager-05-mcp-library.png)

### 6. 调整设置和导入导出全量配置

设置页支持中英文切换、主题切换，以及全量配置导入导出。全量配置适合在不同机器之间迁移 Harness Manager 的数据库、组件资产和配置。

![设置页面](docs/images/harness-manager-06-settings.png)

## 这个项目解决什么实际问题

在使用多个 AI 编程工具时，同一类任务往往需要重复准备相同资源：

- 前端开发需要固定的一组 Skills、MCP server 和项目提示词。
- 代码审查需要另一组审查规则、上下文说明和辅助工具。
- 不同工具（Codex、Claude Code、OpenCode）有不同的默认目录和配置方式。
- 手工复制、安装和删除这些资源容易遗漏，也难以知道某个任务到底依赖了哪些组件。

Harness Manager 的目标是把这些资源抽象成“任务套件”：

- 先在组件库中维护 `Skill`、`AGENTS.md` 和 `MCP`。
- 再把组件加入某个任务套件。
- 最后把任务套件一键部署到目标工具。

这样可以减少重复配置，也能让某项工作的上下文、提示词和工具依赖更清晰。

## 快速开始

### 从源码启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m harness_manager
```

### 使用已安装命令启动

```powershell
harness-manager
```

### 打包 Windows 可执行文件

```powershell
.\scripts\build.ps1
```

打包完成后运行：

```text
dist/HarnessManager/HarnessManager.exe
```

应用需要对运行目录有写权限，因为 SQLite 数据库、组件资产、导出包和配置文件都会写入运行目录。

## 当前核心功能

### 任务套件

- 新建、编辑、删除任务套件。
- 一个任务套件可以包含：
  - 多个 `Skill`
  - 多个 `MCP`
  - 一个 `AGENTS.md`
- 选中任务套件后展示已加入的 Skill、AGENTS.md 和 MCP。
- 支持导出任务套件为 `.harness.zip`。
- 支持导入离线任务套件包。
- 删除任务套件只删除套件和关联关系，不删除组件库里的组件。
- 如果任务套件仍有已部署内容，会阻止删除，要求先撤销部署。

### Skill 管理

- 支持从 Codex、Claude Code、OpenCode 默认目录导入 Skill。
- 支持添加自定义 Skill 目录并导入。
- Skill 会复制到当前应用管理目录。
- Skill 可以加入或移出任务套件。
- 已加入所有可用任务套件时，加入按钮会显示为不可用状态。

### AGENTS.md 管理

- AGENTS.md 是组件库中的独立组件。
- 支持在界面中直接新建 AGENTS.md 内容。
- 支持从本地文件选择并导入 AGENTS.md / Markdown 文件。
- 列表中展示名称、描述和内容摘要，不展示技术 ID。
- 一个任务套件最多只能加入一个 AGENTS.md。

### MCP 管理

- MCP 是组件库中的独立配置组件。
- 支持新增和编辑 MCP JSON 配置。
- 支持填写显示名称和描述。
- 列表中展示显示名称、描述和配置摘要，不展示技术 ID。
- MCP 可以加入或移出任务套件。

### 部署与撤销

- 任务套件卡片上提供 Codex、Claude Code、OpenCode 的部署入口。
- 支持全局默认目录和项目级目录切换。
- 部署是有状态的：
  - 未部署时点击为部署。
  - 已部署时点击为撤销。
- 成功操作不弹二次提示，按钮状态和列表刷新即为反馈。
- 失败时会展示错误原因。
- 删除、移除文件等可能带来不可逆影响的操作会保留确认。

### 配置与备份

- 支持界面语言设置。
- 支持主题切换。
- 支持全量配置导入和导出。
- 支持通过环境变量配置日志等级：

```powershell
$env:HARNESS_MANAGER_LOG_LEVEL="DEBUG"
```

可用等级包括 `DEBUG`、`INFO`、`ERROR`，默认是 `INFO`。

## 技术架构

项目采用分层 Python 架构，核心业务逻辑不依赖 Qt，便于测试和维护。

```text
src/harness_manager/
  __main__.py              # 应用入口
  app_paths.py             # 运行目录和数据目录解析
  asset_paths.py           # 组件文件路径规则
  client_detection.py      # Codex / Claude Code / OpenCode 默认目录发现
  db.py                    # SQLite schema 初始化和事务辅助
  repositories.py          # 数据库访问层
  services.py              # 业务用例：导入、导出、部署、撤销、删除等
  file_ops.py              # 文件复制、删除、压缩、解压的安全封装
  fingerprint.py           # 目录 fingerprint 计算，用于安全撤销/卸载
  settings.py              # 语言、主题、全量配置导入导出
  logging_config.py        # 日志配置
  gui/
    main_window.py         # 主窗口与页面交互
    controllers.py         # GUI 到 service/repository 的薄封装
    dialogs.py             # 自定义弹窗
    styles.py              # Qt stylesheet 和主题 token
```

### 分层职责

- GUI 层只负责界面、交互和刷新。
- Controller 层负责把 GUI 操作转换为业务调用。
- Service 层负责核心业务流程和文件系统操作。
- Repository 层负责 SQLite CRUD。
- 文件系统操作集中在 `file_ops.py` 和 `services.py` 中，避免 GUI 直接操作关键目录。

### 数据存储

应用使用 SQLite 保存元数据，组件文件保存在应用运行目录下。

默认运行目录结构：

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
    <skill_id>/SKILL.md
  exports/
    <任务套件名称>.harness.zip
  config/
    settings.json
```

说明：

- 任务套件本身是数据库中的抽象概念。
- Skill、AGENTS.md、MCP 是组件资产。
- `.harness.zip` 是离线导入/导出的任务套件包。
- 撤销部署时会通过 fingerprint 判断目标文件是否被修改，避免误删用户改过的内容。

## 技术栈

- Python 3.11+
- PySide6 / Qt Widgets
- SQLite（Python 标准库 `sqlite3`）
- pytest
- PyInstaller

## 本地开发

建议在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

启动应用：

```powershell
python -m harness_manager
```

也可以使用安装后的命令：

```powershell
harness-manager
```

运行测试：

```powershell
pytest -q
python -m compileall -q src tests
```

仅验证 GUI 模块可导入：

```powershell
python -c "from harness_manager.gui.main_window import MainWindow; print('gui import ok')"
```

## 如何打包

项目通过 `scripts/build.ps1` 使用 PyInstaller 打包 Windows 桌面程序。

### 1. 安装依赖

```powershell
python -m pip install -e .[dev]
```

### 2. 执行打包脚本

```powershell
.\scripts\build.ps1
```

脚本实际执行的关键步骤包括：

```powershell
python -m PyInstaller `
  --noconfirm `
  --windowed `
  --name HarnessManager `
  --icon src/harness_manager/resources/app.ico `
  --paths src `
  src/harness_manager/__main__.py
```

### 3. 打包产物

打包完成后，可执行文件位于：

```text
dist/HarnessManager/HarnessManager.exe
```

建议把 `dist/HarnessManager/` 整个目录复制到一个可写目录中运行，例如：

```text
D:\Tools\HarnessManager\
```

应用会在运行目录下创建或使用 `data/`、`assets/`、`skills/`、`exports/`、`config/` 等目录。因此不要放在无写权限目录中运行。

## 安全策略

- 导入组件时复制到应用管理目录，不直接依赖原始来源目录。
- 解压离线包时检查路径穿越、文件数量、大小和压缩比。
- 撤销部署只处理有部署记录的路径。
- 如果部署目标被用户修改，撤销会标记为 modified，不会直接删除。
- 删除任务套件不会删除组件资产。
- 删除 Skill 会删除组件库中的 Skill 文件和关联关系，因此会要求确认。

## 当前限制

- Hook 管理暂不实现。
- 任务套件部署当前主要面向 Codex、Claude Code、OpenCode。
- AGENTS.md 在一个任务套件中限制为一个。
- 旧的 Package 相关代码仍有兼容保留，但用户界面统一使用“任务套件”概念。

## 开源协议

本项目采用 MIT License，详见 `LICENSE`。

项目依赖 PySide6 / Qt for Python 等第三方组件，第三方组件遵循其各自许可证；分发应用时需要同时关注相关依赖的许可证要求。
