---
name: smclaw-hsm-javasdk
description: 当用户明确要求 HSM Java SDK 的配置、安装集成、Java 代码示例、场景示例或 Java SDK 测试用例时使用。不做 C SDK，不做 CSP/CHSM，不做 Maven/Gradle 自动改造，不用于纯参数含义或返回值解释类问答。
---

# SMClaw HSM Java SDK 任务分发器

本技能只做 HSM Java SDK 生成类和集成类任务分发。具体规则必须进入对应 `references/*.md` 文件执行。

## 触发边界

使用本技能：

- 用户明确要求 HSM Java SDK 的配置、安装、集成或示例。
- 用户要求生成 Java SDK 的 `iniConfig.ini` 或 `test-env.properties` 样例或配置说明。
- 用户要求 Java SDK 的本地 jar、classpath、JDK、`javac`、`java` 命令或最小项目结构说明。
- 用户要求生成某个 HSM Java SDK 方法的调用示例。
- 用户要求生成 HSM Java SDK 的随机数、摘要、签名验签、加解密等场景示例。
- 用户要求在 `/javasdk_init` 初始化后的 Java SDK 测试工程中编写自包含测试用例。

不使用本技能：

- 不做 C SDK。
- 不做 CSP/CHSM。
- 不做 Maven/Gradle 自动改造。
- 不处理 HTTP 接口命令或 HTTP 代码示例。
- “某个 Java SDK 参数是什么意思”
- “某个返回值代表什么”
- “某个 VO 字段含义是什么”
- 其他只需要事实解释、参数说明或排障咨询的问题。

纯咨询类 Java SDK 问题应使用 `smclaw-rag-usage`，只做解释和来源引用，不进入代码、配置或测试生成流程。

## 分发流程

1. 判断是否属于 HSM Java SDK 相关任务。
2. 如果是 C SDK、CSP、CHSM 或 HTTP 任务，停止本技能流程。
3. 如果是 Maven/Gradle 工程自动改造，说明本技能不做自动改造，只能提供本地 jar/classpath 集成说明。
4. 如果是纯咨询类问题，停止本技能流程，转 RAG 问答。
5. 确认 HSM 文档版本，例如 `v3.0.1.0`。
6. 从用户输入识别任务类型：
   - `config-guide`：`iniConfig.ini`、`test-env.properties`、设备地址、端口、口令、测试环境值。
   - `install-guide`：本地 jar、classpath、JDK、`javac`、`java`、最小项目结构。
   - `single-interface-example`：单个 Java SDK 方法或必要调用链的 Java 示例。
   - `scenario-example`：随机数、摘要、签名验签、加解密等完整业务流程。
   - `test-writer-routing`：`/javasdk_init`、`test-framework`、`HsmSessionTestCase`、`@TestCase`、编译测试。
7. 根据任务类型读取对应引用文件。
8. 如果任务类型不明确，先给用户选择菜单。

## 任务选择菜单

```text
你想完成哪类 HSM Java SDK 集成任务？

1. 生成 SDK 配置样例
   适合 iniConfig.ini、设备 IP/端口、口令、测试环境 properties 配置说明。

2. 生成安装和项目集成步骤
   适合本地 jar、classpath、JDK、javac/java 命令、最小项目结构。

3. 生成单接口调用示例
   适合 generateRandom、摘要、签名、验签、加解密等单个 Java SDK 方法。

4. 生成场景化集成示例
   适合 SM2 签名验签、SM3 摘要、SM4 加解密等完整业务流程。

5. 编写或修改 Java SDK 测试用例
   适合 /javasdk_init 初始化后的 test-framework，用自包含测试框架编译验证。

6. 其他
   请直接描述你的 HSM Java SDK 集成目标。
```

## 引用文件

所有子任务必须先遵守：

- `references/common-rag-rules.md`

按任务类型继续读取：

- 配置样例：`references/config-guide.md`
- 安装集成：`references/install-guide.md`
- 单接口示例：`references/single-interface-example.md`
- 场景示例：`references/scenario-example.md`
- 测试用例路由：`references/test-writer-routing.md`

## 路由规则

| 用户意图 | 路由 |
|:---|:---|
| 生成 iniConfig.ini 配置样例 | `references/config-guide.md` |
| 生成 Java SDK classpath 集成步骤 | `references/install-guide.md` |
| 生成 generateRandom Java 示例 | `references/single-interface-example.md` |
| 生成 SM3 摘要 Java 示例 | `references/single-interface-example.md` |
| 生成 SM2 签名验签 Java 场景示例 | `references/scenario-example.md` |
| 给 generateRandom 写 Java SDK 测试 | `references/test-writer-routing.md` |
| 某个 Java SDK 参数是什么意思 | 不使用本技能，转 `smclaw-rag-usage` |

## 禁止事项

- 禁止处理 C SDK。
- 禁止处理 CSP/CHSM SDK。
- 禁止默认做 Maven/Gradle 自动改造。
- 禁止把 SDK 咨询类问题强行转成代码生成。
- 禁止在 RAG 或本地 Java SDK 文档未确认方法签名、import、VO getter、enum 或 constant 时生成最终 Java 代码。
- 禁止自动修改用户工程文件。
- 禁止自动运行真实设备测试。
