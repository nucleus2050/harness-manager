# HSM C SDK 单接口示例规则

用于用户要求生成某个 SDF/SDIF 接口的 C 调用示例，或一条不可拆分的最小调用链示例。

进入本子任务后，先遵守 `references/common-rag-rules.md`。

## 子任务引导

```text
请选择单接口示例类型：

1. 随机数接口，例如 SDF_GenerateRandom
2. 摘要接口，例如 SDF_HashInit/Update/Final
3. 签名或验签接口
4. 加密或解密接口
5. 其他，请说明具体 SDF/SDIF 函数名
```

## 生命周期

普通集成示例必须包含：

- `SDF_OpenDevice`
- `SDF_OpenSession`
- 目标接口调用
- 临时密钥句柄清理
- `SDF_CloseSession`
- `SDF_CloseDevice`

## 规则

- 必须先用 RAG 确认函数签名和参数。
- 不写 Unity 测试框架代码。
- 需要配套调用链时允许包含多个接口，例如 `SDF_HashInit`、`SDF_HashUpdate`、`SDF_HashFinal`。
- 设备内部密钥索引、权限码、用户 ID 等真实资源参数不能硬编码为确定值。
- 示例代码必须包含错误处理和资源释放路径。

## C 示例骨架

```c
#include <stdio.h>
#include <string.h>
#include "SDF.h"

int main(void)
{
    void *device = NULL;
    void *session = NULL;
    int ret = SDF_OpenDevice(&device);
    if (ret != 0) {
        printf("SDF_OpenDevice failed: 0x%08X\n", ret);
        return 1;
    }

    ret = SDF_OpenSession(device, &session);
    if (ret != 0) {
        printf("SDF_OpenSession failed: 0x%08X\n", ret);
        SDF_CloseDevice(device);
        return 1;
    }

    /* Call target SDF/SDIF API here after confirming signature from RAG. */

    SDF_CloseSession(session);
    SDF_CloseDevice(device);
    return 0;
}
```

输出时必须替换注释处为已由 RAG 确认的目标接口调用；如果无法确认，停止生成最终代码。
