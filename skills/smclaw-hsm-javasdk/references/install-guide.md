# HSM Java SDK 安装和项目集成指南

用于用户要求生成 HSM Java SDK 安装步骤、项目集成步骤、本地 jar、classpath、JDK、`javac` 或 `java` 命令示例的场景。

进入本子任务后，先遵守 `references/common-rag-rules.md`。

## 子任务引导

```text
请选择要生成的 Java SDK 安装集成内容：

1. 最小 Java 项目结构
2. Windows classpath 编译和运行配置
3. Linux classpath 编译和运行配置
4. javac/java 命令示例
5. 其他，请说明
```

## 输出内容

- 最小 Java 项目结构。
- 本地 SDK jar 目录说明。
- `classpath` 组织方式。
- JDK、`javac`、`java` 命令检查。
- Windows `;` 和 Linux `:` classpath 分隔符差异。
- 编译命令和运行命令示例。
- 运行前检查清单。

## 规则

- 不使用 Maven/Gradle 作为默认方案。
- 不使用 Maven/Gradle 网络下载。
- jar 名称、依赖 jar、包结构优先来自 RAG、用户 SDK 包结构或 `/javasdk_init` 工程。
- 不确定 jar 名称或路径时，用“请按实际 SDK 包调整”标注，不假装确定。
- 客户运行路径不假设存在 Maven、Gradle、Python、Go、LibreOffice 等开发或建库工具。

## javac/java 示例骨架

Windows PowerShell：

```powershell
$cp = ".\lib\*;.\config"
javac -encoding UTF-8 -cp $cp -d .\build\classes .\src\Demo.java
java -cp ".\build\classes;$cp" Demo
```

Linux Bash：

```bash
CP="./lib/*:./config"
javac -encoding UTF-8 -cp "$CP" -d ./build/classes ./src/Demo.java
java -cp "./build/classes:$CP" Demo
```

使用示例前必须说明：jar 目录和配置目录需要按用户实际 HSM Java SDK 包调整。
