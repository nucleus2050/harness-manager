# HSM Java SDK 公共 RAG 规则

本文件供 `smclaw-hsm-javasdk` 下所有子任务引用。产品固定为 HSM，但文档版本必须由用户确认。Java SDK 方法签名、参数、返回值、包名、VO getter、enum 和 constant 必须来自 `smclaw-rag` MCP、用户提供的官方 HSM Java SDK 文档，或 `/javasdk_init` 工程生成的 `sdk-api-docs/api.md` 与 `sdk-api-docs/java-classes/**/*.javap.txt`；不得编造。

## 产品和版本

- 产品固定使用 `product=HSM`。
- 版本必须明确，例如 `v3.0.1.0`。
- 用户未给版本时，先列可用 HSM 版本或询问用户。
- 调用 `smclaw_rag_search` 时，`product=HSM`、`version=<用户确认版本>`，`query` 不重复写 HSM 和版本号。

## 检索策略

- 查询应聚焦 Java SDK、目标方法名、参数名、VO 类型、enum、constant 和配置文件。
- 单接口示例至少查询目标方法名和结构化字段，例如 `generateRandom Java SDK 方法签名 参数 返回值 接口手册`。
- 场景示例必须查询场景中每个 Java SDK 调用。
- 配置和安装问题优先查询 Java SDK 配置、`iniConfig.ini`、jar、classpath、JDK、运行环境。
- `api.md` 是官方接口说明来源；`javap.txt` 只用于确认 Java 类名、import、公共方法、getter、enum 和 constant。

## 必须确认的 Java SDK 事实

生成 Java 代码前必须确认：

- 方法名称和完整签名。
- 每个参数的类型和含义。
- 返回值类型和含义。
- 相关 VO 的完整包名和 getter。
- 相关 enum 或 constant 的完整包名和真实名称。
- 是否需要 SDK client、session 或配置加载。
- 是否需要关闭 session 或释放资源。

如果 RAG 或本地 Java SDK 文档未检索到目标方法，停止生成代码，要求用户补充接口文档、方法签名、参数说明和相关类型定义。

## 来源引用

输出必须包含来源，至少包含：

- `source_name`
- `source_path`
- `chunk_index`

如果使用本地 `/javasdk_init` 工程资料，也要列出：

- `sdk-api-docs/api.md`
- `sdk-api-docs/java-classes/README.md`
- 对应 `.javap.txt`

## 安全边界

- 不伪造真实设备地址、生产密钥索引、证书索引、权限码、userId 或口令。
- 内部 key index、证书 index、私钥口令、SM2/SM9 userId 等真实资源参数必须询问用户，或标注为测试默认值。
- 不自动修改用户工程文件。
- 不自动运行真实设备测试。
