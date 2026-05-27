# HTTP 单接口示例生成规则

用于用户明确要求生成某个 HTTP/REST 接口的语言级调用示例，例如 Python、Go、Java 或 PowerShell 脚本。

进入本子任务后，先同时遵守：

- `references/common-rag-rules.md`
- `references/environment-detection.md`

## 子任务引导

如果用户没有明确语言，先给出：

```text
请选择示例语言：

1. Python
2. Go
3. Java
4. PowerShell 脚本
5. 其他，请说明
```

用户可以自由输入，例如”Python requests + 函数封装”或”Java 11 HttpClient”。

## 生成流程

1. 按共同规则确认产品和版本。
2. 确认目标语言（用户明确则跳过菜单）。
3. 按环境探测规则检测对应语言工具链。
4. 围绕接口名、参数、路径查询 RAG，确认接口事实。
5. 接口事实完整时，按目标语言模板生成代码。
6. 接口事实不足时，停止生成并说明缺口。
7. 按输出结构组装最终结果。

## 默认策略

- Python 是默认推荐语言。
- Go/Java 只有用户明确选择或明确要求时生成。
- 生成 Go/Java 前探测 `go version`、`java -version`、`javac -version`。
- 未探测到 Go/Java 工具链时仍可给静态代码，但必须说明：当前环境未探测到可直接编译运行的工具链。
- 示例代码只覆盖单接口调用，不编排多个业务接口。

## 示例代码要求

- 函数名表达业务意图，例如 `call_hash_api`。
- URL、请求方法、参数名、响应字段来自 RAG。
- 连接地址、端口、协议来自用户输入或上下文。
- 对 HTTP 状态码和响应体做最小错误处理。
- 代码后解释每个关键参数，并引用 RAG 来源。

## Python 示例骨架

```python
import requests


def call_hash_api(base_url, data_hex, hash_alg="SM3"):
    url = base_url.rstrip("/") + "/path/from/rag"
    payload = {
        "hashAlg": hash_alg,
        "data": data_hex,
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    result = call_hash_api("http://192.168.1.10:8080", "616263")
    print(result)
```

## Go/Java 注意事项

- Go 示例优先使用标准库 `net/http`。
- Java 示例优先使用 Java 11 `java.net.http.HttpClient`。
- 如果当前环境未探测到工具链，不提供本机编译成功承诺。
- 不引入第三方库，除非用户明确要求。

## 输出结构

信息充足时：

- 已确认运行环境和工具链状态。
- 接口事实表。
- 可直接运行的代码或需调整工具链的静态代码。
- 运行和编译方式。
- 参数说明。
- RAG 来源引用。

信息不足时：

- 当前不能生成的原因。
- 缺少的接口事实或连接信息。
- 下一步需要用户提供的信息。
