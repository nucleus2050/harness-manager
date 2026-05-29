# 多项目管理设计

## 背景

当前项目模式只有一个 `selected_project_root` 临时状态。它能完成一次性项目部署，但无法管理多个项目，也无法让用户看到某个任务套件分别部署到了哪些项目、哪些智能体。因此需要把“项目”提升为一等对象，让 Harness Manager 既能管理全局部署，也能管理多个项目的部署视角。

## 目标

- 支持维护多个项目，每个项目有名称、路径和可选描述。
- 用户可以在“全局”和某个项目之间切换当前部署视角。
- 任务套件卡片上的 Claude Code、Codex、OpenCode 图标按当前视角展示部署状态。
- 在项目视角下点击智能体图标，将套件部署到当前项目；再次点击撤销该项目内的部署。
- 支持查看一个任务套件已经部署到哪些项目和智能体。
- 继续保护用户自行安装的工具和文件：撤销只删除 Harness Manager 管理的内容，只清理空目录。

## 非目标

- 不实现 Hook。
- 不自动扫描磁盘上的所有项目。
- 不把项目和任务套件强绑定；一个项目可以部署多个套件，一个套件也可以部署到多个项目。
- 不删除用户项目目录本身。

## 数据模型

新增 `projects` 表：

```sql
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  path TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

新增 `Project` model 和 `ProjectRepository`：

- `create(name, path, description)`：创建项目，路径按 resolve 后存储。
- `list_all()`：按更新时间倒序列出项目。
- `update(project_id, name, path, description)`：修改项目。
- `delete(project_id)`：只删除管理记录，不删除磁盘项目文件。
- `get(project_id)`：读取项目。

现有 `harness_deploy_records.target_path` 继续作为部署目标区分字段。全局模式保存智能体 skill 根目录；项目模式保存项目根目录。这样一个套件部署到多个项目时，会自然形成多条部署记录，无需迁移旧记录。

## 部署视角

引入部署视角对象：

```text
DeployContext
  scope: global | project
  project_id: str | None
  project_path: Path | None
```

GUI 中不再用单个 `selected_project_root` 表示项目目标，而是使用 `selected_project_id`。当 scope 为 project 时，必须选中一个项目记录；如果没有项目，引导用户添加项目。

## UI 设计

### 项目切换区

在任务套件页面顶部增加一个部署视角栏：

```text
部署视角  [全局] [项目：Harness Manager v]        [+ 添加项目] [管理项目]
```

- `全局`：代表智能体默认目录。
- `项目：xxx`：下拉选择已有项目。
- `+ 添加项目`：选择项目文件夹，自动以文件夹名作为默认项目名，可编辑描述。
- `管理项目`：打开项目管理弹窗，支持编辑名称、路径、描述，删除项目记录。

### 任务套件卡片

任务套件卡片继续保留 Claude Code / Codex / OpenCode 三个图标。图标状态根据当前部署视角计算：

- 全局视角：判断全局目标是否已部署。
- 项目视角：判断当前项目是否已部署。

图标 tooltip 需要明确目标：

- `部署到全局 Codex 默认目录`
- `部署到项目「xxx」的 Claude Code 配置`
- `已部署到项目「xxx」，点击撤销`

### 套件部署详情

在任务套件详情中新增“部署位置”列表：

```text
部署位置
全局：Codex 已部署，Claude Code 未部署，OpenCode 未部署
项目 Harness Manager：Codex 已部署，OpenCode 已部署
项目 Website：Claude Code 已部署
```

这个列表只读展示，不承担部署操作。具体部署仍在套件卡片图标上完成，避免入口过多。

## 业务流程

### 添加项目

1. 用户点击 `+ 添加项目`。
2. 选择项目文件夹。
3. 弹出项目编辑弹窗，默认名称为文件夹名。
4. 保存到 `projects` 表。
5. 自动切换到该项目视角。

### 项目视角部署

1. 用户选择项目视角和项目。
2. 点击某个套件上的智能体图标。
3. Controller 根据当前项目 path 调用 `toggle_harness_deploy(..., target_path=project.path, scope="project")`。
4. Service 使用已有 `_deploy_layout` 写入项目级路径。
5. 成功后刷新图标状态，不弹成功提示。

### 删除项目记录

删除项目只删除 Harness Manager 中的项目记录，不删除磁盘目录，不自动撤销已部署内容。若该项目仍有 active deployment，删除时显示确认说明：删除记录后，项目部署内容仍留在磁盘；后续可以重新添加同一路径继续管理。

## 错误处理

- 项目路径不存在：项目视角中标记“路径缺失”，部署按钮点击时提示错误，不自动创建整个项目根目录。
- 项目路径重复：创建或修改时报错。
- 项目路径不是目录：报错。
- 部署冲突：沿用现有 fingerprint/managed block 保护逻辑。
- 撤销遇到用户修改：沿用现有 `modified` 状态，不删除用户内容。

## 测试策略

- Repository 测试：创建、更新、删除、重复路径校验。
- Controller 测试：项目 CRUD 和项目视角部署调用。
- Service 测试：同一套件部署到两个项目时状态互不影响。
- GUI 契约测试：存在项目切换入口、添加项目入口、部署详情入口。
- 安全测试：撤销项目部署时保留非空目录和用户文件。

## 迁移策略

当前版本没有持久化项目记录，因此不需要迁移旧项目数据。保留 `selected_project_root` 相关逻辑的兼容窗口可以很短：实现多项目后删除该临时字段，统一改为 `selected_project_id`。
