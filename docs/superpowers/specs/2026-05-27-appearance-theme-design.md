# 外观主题设计

## 目标

为任务套件管理器增加外观主题设置，支持浅色、深色、跟随系统三种选项。默认使用跟随系统，设置保存到现有 `config/settings.json`，不影响现有语言设置和配置备份能力。

## 范围

- `AppSettings` 增加 `theme` 字段，合法值为 `light`、`dark`、`system`。
- 设置页新增“外观主题”区域，按钮文案为“浅色”“深色”“跟随系统”。
- `MainController` 暴露保存主题的接口。
- `build_stylesheet` 根据解析后的主题生成样式；跟随系统在 GUI 层通过 Qt 当前调色板判断浅深色。
- 不实现 Hook，不调整任务套件、Skill、MCP、AGENTS.md 的核心管理流程。

## 数据与错误处理

旧设置文件没有 `theme` 时回退为 `system`。非法 `theme` 值加载时回退为 `system`，保存非法值时抛出 `ValueError`。保存语言或主题时保留另一项设置，避免互相覆盖。

## 测试

使用 pytest 覆盖设置默认值、保存互不覆盖、非法值回退、controller 保存主题、浅深色 stylesheet 差异，以及设置页中文文案/方法存在。
