---
id: P-20260930-064654
type: problem
title: API 凭据值含非 ASCII 字符导致 Bearer 头构造 UnicodeEncodeError
domain: 执行环境
ptype: 配置陷阱
level: S2
status: 已定位
process_captured: true
recorded_by: dsh-A
source_tool: dsh
solution: 写入凭据后立刻做 isascii() 校验；执行器在构造 header 前显式 isascii() 断言并 fail-closed 报错，不要等到 UnicodeEncodeError。
solution_status: 已验证
solution_hits: 1
solution_level: 待验证
resolved_at: 2026-09-30
due: 
owner: huohaochen
created: 2026-09-30
tags: [problem, credential, unicode, http-header]
---

# 🟢 API 凭据值含非 ASCII 字符导致 Bearer 头构造 UnicodeEncodeError

==待处理== · 执行环境 · <kbd>S2</kbd>

---

> [!question]+ 结论
> 凭据文件里写入的密钥值混入了**非 ASCII 字符**（实测为类别 `Lo` 的 CJK 字符，多为全角符号或
> 从聊天窗口复制带入的不可见字符）。`http.client` 构造 `Authorization: Bearer <key>` 时按 latin-1
> 编码 header ⇒ `UnicodeEncodeError`，**请求在物理上无法发出**，且症状表现为「预检莫名失败」。

---

> [!quote] 发生了什么

**事实链：**

```
# 凭据写入后，预检直接抛异常（不是 401/403，而是本地编码错误）
UnicodeEncodeError: 'latin-1' codec can't encode character ...

# 定位：值含 4 个非 ASCII 字符
[k for k in value if not k.isascii()] → 4 个字符，unicodedata.category = 'Lo'

# 修正后的守卫：写入/读取时即断言
assert key.isascii(), "CREDENTIAL_NOT_ASCII"
```

**特征：** 报错发生在**发起 HTTP 之前**，因此没有任何网络流量、没有 HTTP 状态码、没有服务端日志，
从「调用失败」的表象完全看不出是本地编码问题。

---

| 判断 | 依据 |
|:-----|:-----|
| ==非服务端问题== | 异常在 header 编码阶段抛出，请求未发出 |
| ==复制粘贴是高危来源== | 全角字符/零宽字符肉眼与 ASCII 极难区分 |
| ==必须 fail-closed== | 静默剥离或「容错编码」会把错误密钥发出去，产生更难诊断的 401 |

---

> [!warning] 可能偏差
> - 若使用 `requests`/`httpx`，行为可能不同（部分库对 header 值更宽松或报错信息更清楚）。
> - 「4 个字符」为本例实测值，不代表通用模式。
> - 仅在**布尔层面**记录，任何密钥特征（前缀/长度/哈希）都不应写入产物。

---

> [!note]- 过程层（复盘时展开）
> **原话**：首次绑定后预检「物理上无法进行」，一度怀疑是密钥无效或额度问题。
>
> **关键分歧**：把本地编码错误误读为远端拒绝。
>
> **标尺**：凭据类问题的第一步是 `isascii()` + 是否存在，而不是去问服务端。
