# MCP 配置管理设计

## 目标

MCP 组件用于维护 MCP server 配置。配置不需要自动发现，用户可以在应用内手动新增、编辑和管理 MCP 配置，并在 MCP 列表页展示这些配置。MCP 组件可以继续加入或移出任务套件。

## 范围

第一版只实现本地 MCP 配置管理，不自动写入 Codex、Claude Code、OpenCode 等工具的真实配置文件。

包含：

- 新建 MCP 配置。
- 编辑 MCP 配置。
- 校验 JSON 配置是否合法。
- 保存 MCP 配置到应用安装目录下的 `assets/mcp/<asset_id>/mcp.json`。
- 在 SQLite 的 `assets` 表中保存 MCP 组件记录。
- 在 `assets.metadata_json` 中保存 MCP 元信息。
- 在 MCP 列表页展示配置卡片。
- 保持每个 MCP 卡片上的 `加入套件`、`移出套件` 操作。

不包含：

- 自动发现系统中已有 MCP 配置。
- 自动合并或写入目标工具配置文件。
- MCP server 启动、测试连接或健康检查。
- Hook 支持。

## 数据模型

继续复用 `assets` 表。

MCP 资产字段约定：

- `type = "mcp"`
- `name`：MCP 标题，要求非空且唯一。
- `source_type = "custom"`
- `relative_path`：指向保存的 JSON 文件。
- `fingerprint`：基于保存目录计算。
- `metadata_json`：保存结构化元信息。

`metadata_json` 示例：

```json
{
  "mcp_kind": "custom",
  "display_name": "Fetch Server",
  "config_filename": "mcp.json"
}
```

## MCP 配置内容

用户编辑完整 JSON 配置。第一版只校验 JSON 语法，不强制 MCP schema。

示例：

```json
{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-server-fetch"]
}
```

## UI 设计

MCP tab 改为配置管理页。

页面包含：

- 顶部操作：`新建 MCP 配置`
- MCP 配置列表：展示每个 MCP 的标题、类型、JSON 摘要。
- 每个 MCP 卡片操作：
  - `编辑`
  - `加入套件`
  - `移出套件`

新建/编辑弹窗参考 cc-switch 配置页，但保持当前应用浅色视觉系统：

- MCP 类型按钮：`自定义`、`fetch`、`time`、`memory`、`sequential-thinking`、`context7`
- `MCP 标题（唯一）`
- `显示名称`
- `完整 JSON 配置` 多行编辑区
- `格式化`
- `取消`
- `保存`

## 校验与错误处理

- MCP 标题不能为空。
- 新建时标题不能和已有 MCP 资产重复。
- 编辑时允许保持原标题，但不能改成其他已有标题。
- JSON 配置必须合法，否则弹出中文错误提示。
- 保存失败时不能留下半写入的数据库记录。

## 测试策略

- Repository 测试：按名称查找 MCP 资产，防止重复标题。
- Service 测试：新建、编辑、JSON 校验、文件写入、metadata 保存。
- Controller 测试：暴露新建、编辑 MCP 配置方法。
- GUI 文案契约测试：MCP tab 包含新建、编辑、格式化、JSON 配置等中文文案。
- 回归测试：任务套件关联、Skill 导入、AGENTS.md 导入仍然通过。
