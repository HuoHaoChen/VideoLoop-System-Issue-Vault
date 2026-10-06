---
id: P-20261004-233530
type: problem
title: Claude Code 长会话在约 20 分钟处 Connection lost mid-response（同一 session 复现 2 次）
domain: 待分类
ptype: 待分类
level: 待定
status: 未处理
process_captured: false
recorded_by: dsh-A
source_tool: dsh
solution: 
solution_status: 待解决
solution_hits: 0
solution_level: 待验证
resolved_at: 
due: 
owner: huohaochen
created: 2026-10-04
tags: [problem]
---

# 🟢 Claude Code 长会话在约 20 分钟处 Connection lost mid-response（同一 session 复现 2 次）

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> Claude Code `-p`（print）长会话在**总时长约 1202 秒**处稳定断流：`terminal_reason=api_error`、
> `result="API Error: Connection lost mid-response"`、`is_error=true`、退出码 1。
> 同一 session 连续复现 2 次，**报错文本与总耗时几乎相同**（1205076 ms / 1202281 ms，相差 2.8 秒），
> 故不是随机网络抖动，而是**确定性上限**。该轮所有产物均未写出（`out/` 为空、读取根逐字节未改）。
> 本次路线为 `mode=official`（Pro 订阅），**排除第三方 relay 因素**。

---

> [!quote] 发生了什么

**事实链：**

```
TASK      TEST07-TH-RT-002-CLEAN-BASELINE-AND-FORMAL-LOOKUP-PHASE1-V1 · PHASE 1A/1C
EXECUTOR  NEW CLEAN Claude Code 2.1.282 · model claude-opus-5 · cwd=/tmp/th_rt_002_phase1/readroot
ROUTE     claude-route log: run mode=official source=probe reason=quota-ok
          （未走 provider-thirdparty.json 的第三方通道。注意：本机 `claude` 是包装器
            ~/.claude/bin/claude_route.py，按额度自动降级；本次未触发降级）

RUN #1  session=47291e03-7709-4500-9340-a2f354288b80
        num_turns=9  duration_ms=1205076  cost=$1.501017  is_error=true
        terminal_reason=api_error  result="API Error: Connection lost mid-response."
RUN #2  同 session --resume
        num_turns=4  duration_ms=1202281  cost=$1.8372025  is_error=true
        terminal_reason=api_error  result="API Error: Connection lost mid-response."

副产物取证
        out/ 目录 = 空（两次均未产出任何交付物）
        readroot 白名单 12 件 sha256 全部未变（未产生半成品写入）
        两次 stderr 均为空

相关可调参数（从 2.1.282 Mach-O 二进制 strings 提取）
        API_TIMEOUT_MS                      默认 600000（10 min）
        CLAUDE_STREAM_IDLE_TIMEOUT_MS       下限 300000（5 min）
        CLAUDE_BYTE_STREAM_IDLE_TIMEOUT_MS  可覆盖 byte watchdog
        firstParty byte-watchdog 窗口 RW=180000（3 min），钳制区间 [1e4, 1800000]
        ⇒ 三个已发现上限都**不是** 20 分钟，故 1202 s 的确切来源未能从客户端常量对上，
          只登记「实测稳定复现于 ~1202 s」这一事实，不臆测成因。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==确定性上限，非随机抖动== | 两次总耗时 1205076 / 1202281 ms（差 2.8 s），报错文本逐字相同，同 session 复现 |
| ==与路线无关== | claude-route 日志两次均 `mode=official source=probe reason=quota-ok`，未使用第三方通道 |
| ==不是任务语义失败== | `num_turns` 9 与 4，`permission_denials=[]`，无工具被拒；失败前无任何交付物写出 |
| ==按航次最省的重试是正确的== | 读取根逐字节未变、out/ 为空 ⇒ 无半成品，`--resume` 同 session 不产生状态污染 |
| ==单次调用规模是可控变量== | 同一任务拆成「只写交付 1」的窄范围后仍可继续（见修改卡） |

---

> [!warning] 可能偏差
> - 
> - 

---

> [!note]- 过程层（复盘时展开）
> **原话**：
> 
> 
> **关键分歧**：
> 
> 
> **标尺**：[[]]