---
id: P-20260930-064653
type: problem
title: macOS 系统代理静默劫持 Python urllib 请求导致长请求被中断
domain: 执行环境
ptype: 网络/配置陷阱
level: S2
status: 已定位
process_captured: true
recorded_by: dsh-A
source_tool: dsh
solution: 需要真直连时显式禁用代理（urllib 传 proxies={} / 设 no_proxy / 用不含 ProxyHandler 的 opener），并在产物中如实记录实际出口路径。
solution_status: 已验证
solution_hits: 1
solution_level: 待验证
resolved_at: 2026-09-30
due: 
owner: huohaochen
created: 2026-09-30
tags: [problem, proxy, urllib, macOS, 长请求]
---

# 🟢 macOS 系统代理静默劫持 Python urllib 请求导致长请求被中断

==待处理== · 执行环境 · <kbd>S2</kbd>

---

> [!question]+ 结论
> 环境里**没有** `HTTP_PROXY`/`HTTPS_PROXY` 环境变量，但 Python `urllib` 仍会通过
> **macOS 系统代理设置**（`_scproxy`）走本机代理；长耗时请求会在约 300s 无字节返回时被中断，
> 而调用方看到的只是一个无类型的连接异常。

---

> [!quote] 发生了什么

**事实链：**

```
$ env | grep -i proxy          # 空 —— 没有任何代理环境变量
$ python3 -c "import urllib.request; print(urllib.request.getproxies())"
{'http': 'http://127.0.0.1:7897', 'https': 'http://127.0.0.1:7897'}   ← 来自系统设置
$ python3 -c "...proxy_bypass('api.xiaomimimo.com')"   → 假（不绕过）
$ lsof -p <python> -a -i
Python  <pid>  7u  IPv4 ... TCP localhost:58531->localhost:7897 (ESTABLISHED)
$ lsof -nP -iTCP:7897 -sTCP:LISTEN
efanapp <pid> ... TCP 127.0.0.1:7897 (LISTEN)
```

**后果（同日实测）：**

```
slot 1: 228.3s → HTTP 200 成功
slot 2: 301.0s → 0 字节、连接中断（配置超时为 900s，故非 socket timeout）
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==非环境变量驱动== | `env` 无代理变量，代理来自 macOS 系统设置 |
| ==非 socket 超时== | 301s 远小于配置的 900s，且收不到任何字节 |
| ==最可能机制== | 本机代理对长期无响应连接的约 300s 空闲中断（**假设**，未读代理配置证实） |
| ==静默性== | 调用方无法从异常判断是代理还是服务端问题（异常类型还被上层吞掉） |

---

> [!warning] 可能偏差
> - 「约 300s」是基于 **2 个样本** 的推断，不是代理配置实证；可能只是巧合。
> - 若开启 TUN 模式，流量可能走假 IP 路由（曾观察 `198.18.0.1 -> 42.177.83.94:443`）而非 HTTP 代理端口；两者都是本机代理介入。
> - 本机代理不等同于「第三方模型中转站」：端点与密钥仍是官方的；是否构成违规取决于约束定义。

---

> [!note]- 过程层（复盘时展开）
> **原话**：产物一度记载 `PROXY = NOT_USED`／`OFFICIAL_DIRECT_API`，与实测路径不一致。
>
> **关键分歧**：把「没有代理环境变量」误当作「没有走代理」。
>
> **标尺**：声明网络路径前必须实测出口（`getproxies()` + `lsof`），不能靠环境变量推断。
