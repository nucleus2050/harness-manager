# HSM Java SDK 配置向导

用于用户要求生成 HSM Java SDK 配置样例、`iniConfig.ini`、`test-env.properties` 或运行时配置说明的场景。

进入本子任务后，先遵守 `references/common-rag-rules.md`。

## 子任务引导

如果用户没有明确配置目标，先给出：

```text
请选择要生成的 HSM Java SDK 配置内容：

1. iniConfig.ini SDK 连接配置样例
2. test-env.properties 测试环境配置样例
3. 配置字段说明
4. 测试工程 /javasdk_init 的配置说明
5. 其他，请说明
```

## 两类配置

| 文件 | 用途 | 读取者 |
|:---|:---|:---|
| `config/iniConfig.ini` | HSM IP、端口、口令、TLS、SDK 日志路径 | 厂商 Java SDK |
| `config/test-env.properties` | key index、证书 index、私钥口令、userId、destructive 开关 | 测试框架 `TestConfig` |

## 规则

- 不直接修改用户配置文件。
- 不伪造真实设备地址、真实口令、生产密钥索引、证书索引或私钥口令。
- `iniConfig.ini` 和 `test-env.properties` 必须明确区分，不要混放。
- 如果字段含义无法从 RAG 或本地文档确认，标记证据不足。

## test-env.properties 示例

```properties
# SM2 内部密钥索引，用于测试或示例中的内部密钥访问
sm2.key.index=1

# 私钥访问权限码
private_key.password=11111111

# 证书签名索引
cert.sign.index=1

# 是否允许执行会修改设备状态的测试
allow.destructive_tests=false
```
