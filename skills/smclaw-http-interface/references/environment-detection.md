# HTTP 接口环境探测规则

本文件供需要声明“可直接复制执行”或“可直接运行”的 HTTP 生成子任务引用。能本地探测的信息不要询问用户；探测失败不阻塞流程，但不能声称已验证可运行。

## Windows PowerShell

```powershell
$PSVersionTable.PSEdition
$env:OS
Get-Command curl.exe -ErrorAction SilentlyContinue
python --version
python -c "import requests; print(requests.__version__)"
py -3 --version
```

规则：

- PowerShell 默认生成 `Invoke-RestMethod`。
- 用户明确要求 curl 时使用 `curl.exe`，不要使用 PowerShell 的 `curl` 别名。
- Python 3 + `requests` 可用时优先使用 `requests`。
- Python 3 无 `requests` 时使用标准库 `http.client`。
- 只有 Python 2 可用时使用标准库 `httplib`。

## Linux/macOS Bash

```bash
uname -s
echo "$SHELL"
command -v curl
python3 --version
python3 -c "import requests; print(requests.__version__)"
python --version
python -c "import requests; print(requests.__version__)"
```

规则：

- Bash/zsh 默认生成 `curl` 命令。
- JSON 请求体用单引号包裹，避免 shell 转义复杂化。
- Python 规则与 Windows 一致。

## Go/Java

只有用户明确选择 Go 或 Java 时才探测：

```bash
go version
java -version
javac -version
```

未探测到工具链时，仍可提供静态代码，但必须写明：当前环境未探测到可直接编译运行的工具链。
