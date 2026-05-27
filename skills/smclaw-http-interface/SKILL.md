---
name: smclaw-http-interface
description: 当用户明确要求为密码产品 HTTP/REST 接口生成可执行测试命令、脚本、单接口示例、代码或自动化用例草稿时使用。不要用于“参数怎么传、字段含义、接口说明、排障咨询”等仅需解释的问答。
---

# SMClaw HTTP 接口任务分发器

本技能只做 HTTP 生成类任务的入口和分发，不承载全部生成细节。进入具体任务后，必须读取对应 `references/*.md` 文件执行。

## 触发边界

使用本技能：

- 用户要求生成 HTTP/REST 接口测试命令。
- 用户要求生成 curl、PowerShell、Python、Go、Java 等 HTTP 调用示例。
- 用户要求为某个密码产品 HTTP 接口生成可执行脚本或自动化用例草稿。
- 用户用业务需求描述希望生成 HTTP 调用代码，例如“调用 SM2 签名接口对数据签名”。

不要使用本技能：

- “hash 接口参数怎么传”
- “这个字段是什么意思”
- “接口有哪些必填参数”
- “为什么返回这个错误码”
- “某个配置或接口说明是什么”
- 其他只需要解释、排障或事实查询的问题。

咨询类问题应使用 `smclaw-rag-usage` 或普通 RAG 问答，只做解释和来源引用，不进入命令或代码生成流程。

## 分发流程

1. 判断用户问题是否属于 HTTP 生成类任务。
2. 如果是咨询类问题，停止本技能流程。
3. 如果产品或版本缺失，按 `references/common-rag-rules.md` 先确认产品和版本。
4. 从用户输入识别任务类型：
   - `test-command`：测试命令、curl、PowerShell、快速调用、可复制执行。
   - `single-interface-example`：代码示例、语言示例、单接口集成。
   - `requirement-to-code`：业务需求、自然语言描述、先理解再生成。
5. 根据任务类型读取对应引用文件。
6. 如果任务类型不明确，先给用户选择菜单。

## 任务选择菜单

```text
你想生成哪类 HTTP 接口内容？

1. 可直接复制执行的测试命令
   适合 curl、PowerShell Invoke-RestMethod、快速验证接口连通和参数。

2. 单接口代码示例
   适合 Python、Go、Java 等语言中集成某一个 HTTP 接口。

3. 从业务需求生成 HTTP 调用代码
   适合“我要做 SM2 签名/验签/摘要”等自然语言需求，会先确认接口理解再生成代码。

4. 其他
   请直接描述你希望生成什么。
```

## 引用文件

所有生成类子任务必须先遵守：

- `references/common-rag-rules.md`
- `references/environment-detection.md`

按任务类型继续读取：

- 测试命令：`references/test-command.md`
- 单接口示例：`references/single-interface-example.md`
- 需求转 HTTP 调用代码：`references/requirement-to-code.md`

## 路由规则

| 用户意图 | 路由 |
|:---|:---|
| 生成 hash HTTP 接口 curl 命令 | `references/test-command.md` |
| 生成签名验签 HTTP 接口 PowerShell 测试命令 | `references/test-command.md` |
| 生成 Python HTTP 接口示例 | `references/single-interface-example.md` |
| 生成 Go/Java 单接口调用代码 | `references/single-interface-example.md` |
| 调用 SM2 签名接口对数据签名 | `references/requirement-to-code.md` |
| hash 接口参数怎么传 | 不使用本技能，转 `smclaw-rag-usage` |
| 字段是什么意思或接口报错 | 不使用本技能，转 `smclaw-rag-usage` |

## 禁止事项

- 禁止把咨询类问题强行转为命令或代码生成。
- 禁止在 RAG 未确认接口路径、方法、参数时生成最终命令或代码。
- 禁止使用占位符冒充可直接执行结果。
- 禁止让用户提供所有信息；只询问无法自动探测且运行必需的信息。
- 禁止跳过子任务引用文件。
- 禁止生成跨接口编排或多接口业务流程代码；当前只支持单接口生成。
