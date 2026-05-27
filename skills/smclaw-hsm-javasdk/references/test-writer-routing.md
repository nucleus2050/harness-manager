# HSM Java SDK 测试用例路由规则

用于识别 `/javasdk_init` 初始化后的 Java SDK 自包含测试工程请求，并路由到后续 `smclaw-javasdk-test-writer`。

进入本子任务后，先遵守 `references/common-rag-rules.md`。

## 触发条件

- 用户提到 `/javasdk_init`。
- 用户提到 `test-framework` 或 `test-framework/src/test/java`。
- 用户提到 `HsmSessionTestCase`、`@TestCase`、`TestRunner`、`TestConfig`。
- 用户要求编译 Java SDK 测试工程。
- 用户要求为 `ICipherClientSession` 或 Java SDK 方法生成测试用例。

## 行为

- 路由到后续 `smclaw-javasdk-test-writer`。
- 复用 `test_harness/java-sdk/prompt/skills/java-hsm-test-writer/SKILL.md` 的规则。
- 测试类写入 `test-framework/src/test/java/com/smclaw/hsmtest/tests/*.java`。
- 接口事实优先来自 `sdk-api-docs/api.md`。
- Java import、VO getter、enum、constant 优先来自 `sdk-api-docs/java-classes/README.md` 和 `.javap.txt`。
- 测试类通常继承 `HsmSessionTestCase`。
- 使用受保护字段 `crypto` 和 `session`。
- 不要臆造 `getSession()`。
- 默认只执行 `make` 编译验证。
- 真实设备测试 `make test` 必须由用户明确授权。

## 转交提示

```text
这是 Java SDK 自包含测试工程任务，应使用 smclaw-javasdk-test-writer 规则处理。

处理前请确认：
- 是否已经运行 /javasdk_init 初始化工程。
- 是否已经在 sdk-api-docs/api.md 生成官方接口文档。
- 是否已经生成 sdk-api-docs/java-classes/README.md 和 .javap.txt。
- 本次只编译 make，还是用户明确授权运行 make test。
```
