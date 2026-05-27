# HSM Java SDK 单接口示例规则

用于用户要求生成某个 HSM Java SDK 方法的普通 Java 调用示例，或一条不可拆分的最小调用链示例。

进入本子任务后，先遵守 `references/common-rag-rules.md`。

## 子任务引导

```text
请选择单接口示例类型：

1. 随机数接口，例如 generateRandom
2. 摘要接口
3. 签名或验签接口
4. 加密或解密接口
5. 其他，请说明具体 Java SDK 方法名
```

## 普通示例边界

普通集成示例应展示：

- SDK client 创建或获取。
- `AccessSession` 会话创建。
- 目标 Java SDK 方法调用。
- 返回 VO 或 byte[] 的最小处理。
- session 或资源关闭。

## 规则

- 必须先确认方法签名、返回值、VO getter、enum/constant 和 import。
- 不写 HsmSessionTestCase。
- 不写 `@TestCase` 测试框架代码。
- 不臆造 `getSession()`、`assertEquals()`、`assertThrows()` 等测试框架方法。
- 需要配套调用链时允许包含多个方法，例如摘要 init/update/final。
- 内部 key index、证书 index、权限码、userId 等真实资源参数不能硬编码为确定值。
- 示例代码必须包含最小错误处理和资源释放路径。

## 类型确认规则

- `ICipherClientSession`、`AccessSession`、VO、enum、constant 的 import 必须来自 RAG、`api.md` 或 `sdk-api-docs/java-classes/**/*.javap.txt`。
- 如果 `sdk-api-docs/java-classes` 中找不到完整包名，不要猜 import。
- 如果方法返回 VO，只调用已确认存在的 getter。
