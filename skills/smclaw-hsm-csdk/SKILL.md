---
name: smclaw-hsm-csdk
description: 当用户明确要求 HSM C SDK、SDF 或 SDIF 的配置、安装集成、C 代码示例、场景示例或 C SDK 测试用例时使用。不做 Java SDK，不做 CSP/CHSM，不用于纯参数含义或返回值解释类问答。
---

# SMClaw HSM C SDK 任务分发器

本技能只做 HSM C SDK / SDF / SDIF 生成类和集成类任务分发。具体规则必须进入对应 `references/*.md` 文件执行。

## 触发边界

使用本技能：

- 用户明确要求 HSM C SDK、SDF、SDIF 的配置、安装、集成或示例。
- 用户要求生成 C SDK 的 `hsmConfig.ini` 样例或配置说明。
- 用户要求 C SDK 的 Makefile、编译命令、头文件或库文件集成说明。
- 用户要求生成某个 SDF/SDIF 接口的 C 调用示例。
- 用户要求生成 HSM C SDK 的签名验签、摘要、加解密等场景示例。
- 用户要求在 `/csdk_init` 初始化后的 C SDK 测试工程中编写 Unity 测试用例。

不使用本技能：

- 不做 Java SDK。
- 不做 CSP/CHSM。
- 不处理 HTTP 接口命令或 HTTP 代码示例。
- “某个 SDF 参数是什么意思”
- “某个返回值代表什么”
- “某个结构体字段含义是什么”
- 其他只需要事实解释、参数说明或排障咨询的问题。

纯咨询类 SDK 问题应使用 `smclaw-rag-usage`，只做解释和来源引用，不进入代码、配置或测试生成流程。

## 分发流程

1. 判断是否属于 HSM C SDK / SDF / SDIF 相关任务。
2. 如果是 Java、CSP、CHSM 或 HTTP 任务，停止本技能流程。
3. 如果是纯咨询类问题，停止本技能流程，转 RAG 问答。
4. 确认 HSM 文档版本，例如 `v3.0.1.0`。
5. 从用户输入识别任务类型：
   - `config-guide`：配置样例、`hsmConfig.ini`、设备地址、端口、口令、日志。
   - `install-guide`：安装集成、头文件、库文件、链接参数、运行时路径、Makefile。
   - `single-interface-example`：单个 SDF/SDIF 接口或必要调用链的 C 示例。
   - `scenario-example`：签名验签、摘要、加解密等完整业务流程。
   - `test-writer-routing`：Unity 测试、`tests/` 目录、`/csdk_init` 工程、编译测试。
6. 根据任务类型读取对应引用文件。
7. 如果任务类型不明确，先给用户选择菜单。

## 任务选择菜单

```text
你想完成哪类 HSM C SDK 集成任务？

1. 生成 SDK 配置样例
   适合 hsmConfig.ini、设备 IP/端口、口令、运行时配置说明。

2. 生成安装和项目集成步骤
   适合头文件、库文件、链接参数、PATH/LD_LIBRARY_PATH、Makefile 示例。

3. 生成单接口调用示例
   适合 SDF_GenerateRandom、Hash、签名、验签、加解密等单个接口或一条最小调用链。

4. 生成场景化集成示例
   适合签名验签、加解密、摘要等完整业务流程。

5. 编写或修改 C SDK 测试用例
   适合 /csdk_init 初始化后的 c-sdk-framework/tests，用 Unity 编译验证。

6. 其他
   请直接描述你的 HSM C SDK 集成目标。
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
| 生成 hsmConfig.ini 配置样例 | `references/config-guide.md` |
| 生成 C SDK Makefile 集成步骤 | `references/install-guide.md` |
| 生成 SDF_GenerateRandom 示例 | `references/single-interface-example.md` |
| 生成 SDF_HashInit/Update/Final 示例 | `references/single-interface-example.md` |
| 生成 SM2 签名验签场景示例 | `references/scenario-example.md` |
| 给 SDF_Encrypt 写 Unity 测试 | `references/test-writer-routing.md` |
| 某个 SDF 参数是什么意思 | 不使用本技能，转 `smclaw-rag-usage` |

## 禁止事项

- 禁止处理 Java SDK。
- 禁止处理 CSP/CHSM SDK。
- 禁止把 SDK 咨询类问题强行转成代码生成。
- 禁止在 RAG 未确认函数签名、参数和结构体时生成最终 C 代码。
- 禁止自动修改用户工程文件。
- 禁止自动运行真实设备测试。
