# HSM C SDK 测试用例路由规则

用于识别 `/csdk_init` 初始化后的 C SDK Unity 测试工程请求，并路由到后续 `smclaw-csdk-test-writer`。

进入本子任务后，先遵守 `references/common-rag-rules.md`。

## 触发条件

- 用户提到 `/csdk_init`。
- 用户提到 `c-sdk-framework/tests`。
- 用户要求写 Unity 测试。
- 用户要求编译 C SDK 测试工程。
- 用户要求为 `SDF_` 或 `SDIF_` 接口生成测试用例。

## 行为

- 路由到后续 `smclaw-csdk-test-writer`。
- 复用 `test_harness/c-sdk/c-sdk-framework/prompt/skills/sdf-test-writer/SKILL.md` 的规则。
- 测试文件写入 `c-sdk-framework/tests/test_*.c`。
- 接口事实优先来自 `c-sdk-framework/sdk-api-docs/api.md`。
- 默认只执行 `make` 编译验证。
- 真实设备测试 `make test` 必须由用户明确授权。

## 转交提示

```text
这是 C SDK Unity 测试工程任务，应使用 smclaw-csdk-test-writer 规则处理。

处理前请确认：
- 是否已经运行 /csdk_init 初始化工程。
- 是否已经在 c-sdk-framework/sdk-api-docs/api.md 生成官方接口文档。
- 本次只编译 make，还是用户明确授权运行 make test。
```
