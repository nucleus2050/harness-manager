# HTTP 接口公共 RAG 规则

本文件供 `smclaw-http-interface` 下所有 HTTP 生成子任务引用。接口事实必须来自 `smclaw-rag` MCP 或用户提供的官方资料；不得编造接口路径、请求方式、Header、参数名、必填项、响应字段或错误码含义。

## 产品和版本

- 回答前必须确认 `product` 和 `version`，例如 `HSM`、`v3.0.1.0`。
- 用户未明确产品时，先调用 `smclaw_list_products` 获取可用产品，再询问用户。
- 用户未明确版本时，先调用 `smclaw_list_versions` 获取该产品可用版本，再询问用户。
- 调用 `smclaw_rag_search` 时，`product` 和 `version` 只放在 MCP 参数中，不能重复写入 `query`。

## 检索策略

- 至少围绕用户原始意图查询一次，例如 `HTTP hash 接口 摘要 URL 参数 SM3`。
- 生成命令或代码前，再围绕结构化字段查询一次，例如 `HTTP REST API 请求方式 请求路径 请求参数 请求头 JSON body 响应`。
- 首轮结果不足时，将 `top_k` 提高到 10，或围绕候选接口名、算法名、文档名继续查询。
- 不要跨产品或跨版本混用 RAG 结果。

## 必须确认的接口事实

生成最终命令或代码前，至少确认：

- 接口名称。
- 请求方式，例如 `GET` 或 `POST`。
- 请求路径。
- 请求头和 `Content-Type`。
- Query 参数或 Body 字段。
- 必填参数。
- 响应字段或成功/失败判断方式。

无法从 RAG 结果确认的字段必须标记为证据不足；缺少关键字段时停止生成，说明缺少哪些依据。

## 来源引用

输出中必须引用来源，至少包含：

- `source_name`
- `source_path`
- `chunk_index`

如果结果包含 `heading`、`page_number`、`sheet_name` 或 `slide_number`，一并引用。

## 测试值

- 优先使用文档示例值。
- 没有示例时，可使用安全测试值，例如 `abc` 或十六进制 `616263`。
- 算法字段优先使用文档枚举中的常见值，例如 `SM3`。
- 密钥索引、证书 label、token、用户名、密码等真实资源参数，文档没有安全示例时必须询问用户。
- 不得为了可运行而伪造真实密钥、证书、token 或账户。
