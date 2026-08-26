---
id: P-20260826-194447
type: problem
title: Codex workspace-write 沙箱禁止写 .git（index.lock），git 提交须由外部执行
domain: 系统
ptype: 配置坑
level: 一般
status: 已解决
process_captured: true
recorded_by: dsh-A
source_tool: dsh
due: 2026-08-26
owner: huohaochen
created: 2026-08-26
tags: [problem]
---

# 🟢 Codex 沙箱禁止写 .git

==已解决== · 系统域 · <kbd>8/26</kbd>

---

> [!success]+ 结论
> Codex workspace-write 沙箱禁止在 .git/ 下创建 index.lock，AI 自跑 git add/commit 必失败（重试无效）。
> 解法：git 提交一律由外部（主会话或一键脚本）执行；任务书明确写"不要执行任何 git 命令"。

---

> [!quote] 发生了什么

**事实链：**

```
《借势》蒸馏任务要求 Codex 自提交
        ↓
报"环境禁止在 .git 创建 index.lock"，按要求重试一次仍失败
        ↓
外部 git commit/push 成功（e5dd8c8）✅
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==不是 git 配置问题== | 外部同一命令成功 |
| ==是沙箱写限制== | 报错为"环境禁止"，非 git 自身错误 |
| ==影响可控== | 提交挪到外部后全流程正常 |

---

> [!warning] 可能偏差
> - 未测试 Codex 其他沙箱模式（read-only / danger-full-access）下能否写 .git

