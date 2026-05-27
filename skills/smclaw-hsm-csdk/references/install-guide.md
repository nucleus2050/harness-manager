# HSM C SDK 安装和项目集成指南

用于用户要求生成 HSM C SDK 安装步骤、项目集成步骤、头文件/库文件说明、链接参数、运行时库路径或 Makefile 示例的场景。

进入本子任务后，先遵守 `references/common-rag-rules.md`。

## 子任务引导

```text
请选择要生成的安装集成内容：

1. 最小 C 项目结构
2. Windows 编译和运行配置
3. Linux 编译和运行配置
4. Makefile 示例
5. 其他，请说明
```

## 输出内容

- 最小 C 项目结构。
- `include` 路径说明。
- `lib` 路径说明。
- Windows `PATH` 说明。
- Linux `LD_LIBRARY_PATH` 说明。
- Makefile 或编译命令示例。
- 运行前检查清单。

## 规则

- 库名、头文件名、目录结构优先来自 RAG 或用户 SDK 包结构。
- 不确定库名或路径时，用“请按实际 SDK 包调整”标注，不假装确定。
- Windows/Linux 可以都给，但当前环境优先输出 Windows 友好的说明。
- 客户运行路径不假设存在 Python、Go、LibreOffice 等开发工具。

## Makefile 示例骨架

```makefile
CC ?= gcc
CFLAGS += -I./sdk/include -Wall -Wextra
LDFLAGS += -L./sdk/lib/linux/x86_64
LDLIBS += -lhsm -lcsp_session

all: demo

demo: demo.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

clean:
	rm -f demo
```

使用示例前必须说明：库目录和库名需要按用户实际 HSM C SDK 包调整。
