# 项目级任务套件部署设计

## 背景

当前“项目”部署模式使用 Harness Manager 自身运行目录作为目标目录，无法把任务套件推送到用户真正选择的项目。需要改为由用户选择项目文件夹，再按不同智能体的项目级约定写入 skill、AGENTS/CLAUDE 指令和 MCP 配置。

## 目标

- 用户切换到项目模式后选择一个项目文件夹。
- 点击 Claude Code、Codex、OpenCode 图标时，将当前任务套件部署到该项目。
- 再次点击已部署图标时，从该项目撤销部署。
- 成功不弹窗，失败才显示统一错误提示。
- 保持全局部署行为不变。

## 项目级路径约定

| 组件 | Codex | Claude Code | OpenCode |
|---|---|---|---|
| Skill | `<project>/.agents/skills/<skill-id>/` | `<project>/.claude/skills/<skill-id>/` | `<project>/.opencode/skills/<skill-id>/` |
| 指令 | `<project>/AGENTS.md` | `<project>/CLAUDE.md` | `<project>/AGENTS.md` |
| MCP | `<project>/.codex/config.toml` | `<project>/.mcp.json` | `<project>/opencode.json` |

## 架构

新增部署布局概念：根据 `client_type + scope + target` 解析出 skill 根目录、指令文件和 MCP 文件。全局模式继续使用现有默认目录；项目模式使用用户选择的项目根目录。数据库部署记录仍以 skill 根目录作为 `target_path`，以具体写入路径作为 `installed_path`。

## 交互

任务套件卡片上的范围按钮在全局/项目之间切换。切换到项目模式且未选择项目时弹出目录选择器；已选择时显示项目名，点击范围按钮可重新选择或切回全局。部署图标状态按当前范围和目标目录刷新。

## 验证

新增服务层和 GUI 层测试，覆盖三种智能体项目级 skill、指令、MCP 路径，以及项目目录选择逻辑。运行 `pytest -q` 和 `python -m compileall -q src tests`。
