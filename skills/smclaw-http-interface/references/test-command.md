# HTTP 测试命令生成规则

用于用户明确要求生成 HTTP/REST 接口测试命令、curl 命令、PowerShell 命令、Python 测试脚本或快速验证命令的场景。

进入本子任务后，先同时遵守：

- `references/common-rag-rules.md`
- `references/environment-detection.md`

## 子任务引导

如果用户没有明确命令类型，先给出：

```text
请选择测试命令类型：

1. PowerShell Invoke-RestMethod（Windows 推荐）
2. curl 命令
3. Python 脚本
4. 同时生成 PowerShell + curl + Python
5. 其他，请说明
```

用户可以直接输入自由文本，例如”只要 curl.exe，带 verbose”或”生成 Python requests 脚本”。

## 生成流程

1. 按共同规则确认产品和版本。
2. 确认命令类型（用户明确则跳过菜单）。
3. 按环境探测规则检测当前平台和可用工具。
4. 围绕接口名、参数、路径查询 RAG，确认接口事实。
5. 确认目标服务地址、端口、协议（缺失时只问连接信息）。
6. 按确认的事实和命令类型生成命令。
7. 按输出结构组装最终结果。

## 必要信息

- 产品和版本必须明确。
- 目标服务地址、端口、协议必须明确。
- 接口路径、请求方式、参数和响应字段必须来自 RAG。
- 密钥索引、证书、token、用户名密码等真实资源参数缺失时，先询问用户。

连接信息缺失时只问：

```text
请提供目标服务地址、端口和协议，例如：
IP/域名: 192.168.1.10
端口: 8080
协议: http 或 https
```

## PowerShell 模板

```powershell
$body = @{
  hashAlg = "SM3"
  data = "616263"
} | ConvertTo-Json -Compress

Invoke-RestMethod `
  -Method Post `
  -Uri "http://192.168.1.10:8080/path/from/rag" `
  -ContentType "application/json" `
  -Body $body
```

规则：

- 默认使用 `Invoke-RestMethod`。
- 只有用户明确要求 curl 时才使用 `curl.exe`。
- 不要输出 `<host>`、`<port>`、`REPLACE_ME` 并声称可直接复制执行。

## curl 模板

Windows CMD：

```bat
curl.exe -X POST "http://192.168.1.10:8080/path/from/rag" ^
  -H "Content-Type: application/json" ^
  -d "{\"hashAlg\":\"SM3\",\"data\":\"616263\"}"
```

Bash：

```bash
curl -X POST 'http://192.168.1.10:8080/path/from/rag' \
  -H 'Content-Type: application/json' \
  -d '{"hashAlg":"SM3","data":"616263"}'
```

## Python 模板

Python 3 + requests：

```python
import requests

url = "http://192.168.1.10:8080/path/from/rag"
payload = {"hashAlg": "SM3", "data": "616263"}

response = requests.post(url, json=payload, timeout=30)
response.raise_for_status()
print(response.text)
```

Python 3 标准库：

```python
import http.client
import json

conn = http.client.HTTPConnection("192.168.1.10", 8080, timeout=30)
payload = json.dumps({"hashAlg": "SM3", "data": "616263"}).encode("utf-8")
headers = {"Content-Type": "application/json"}
conn.request("POST", "/path/from/rag", body=payload, headers=headers)
response = conn.getresponse()
print(response.status, response.reason)
print(response.read().decode("utf-8", errors="replace"))
conn.close()
```

## 输出结构

- 已确认运行环境。
- 接口事实表。
- 可直接复制执行的命令或脚本。
- 运行方式。
- 参数说明。
- RAG 来源引用。
