---
id: P-20260826-194445
type: problem
title: Codex CLI 在受限沙箱下 app-server 启动失败（Operation not permitted），需全权限才可运行
domain: 系统
ptype: 工具失效
level: 重要
status: 已解决
process_captured: true
recorded_by: dsh-A
source_tool: dsh
due: 2026-08-26
owner: huohaochen
created: 2026-08-26
tags: [problem]
---

# 🟢 Codex CLI 受限沙箱下 app-server 启动失败

==已解决== · 系统域 · <kbd>8/26</kbd>

---

> [!success]+ 结论
> 根因：Codex CLI（0.149.0-alpha.4.1，内嵌于 ChatGPT.app）在受限沙箱（workspace-write）下无法初始化 in-process app-server，报 `failed to initialize in-process app-server client: Operation not permitted (os error 1)`。
> 与认证、网络无关（`auth.json` 正常、`--version` 可输出）。
> 解法：以 danger-full-access 运行 Codex 任务；提示词任务书照常，产出路径不变。

---

> [!quote] 发生了什么

**事实链：**

```
受限沙箱执行 codex exec（MOC-D 任务）
        ↓
"failed to initialize in-process app-server client: Operation not permitted (os error 1)"
        ↓
换 danger-full-access 重跑同一任务
        ↓
正常完成，产出运营/变现/平台规则 3 张 MOC ✅
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==不是认证问题== | auth.json 存在，--version 正常输出 |
| ==不是网络问题== | 报错是 OS 层 Operation not permitted；全权限后同网络成功 |
| ==沙箱权限是直接原因== | 唯一变量是执行权限，换权限后同任务成功 |

---

> [!warning] 可能偏差
> - 未用 dtrace/沙箱日志定位具体被拦的系统调用（IPC？进程创建？）
> - DSH 沙箱策略版本变化后表现可能不同，需重测

