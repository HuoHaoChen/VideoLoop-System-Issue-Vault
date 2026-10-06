---
id: P-20260911-045633
type: problem
title: launchd 进程读不了 ~/Desktop（macOS TCC），管线静默空转 6 小时 22 分
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
created: 2026-09-11
tags: [problem]
---

# 🟢 launchd 进程读不了 ~/Desktop（macOS TCC），管线静默空转 6 小时 22 分

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> macOS 的 TCC（隐私保护）**只对 `~/Desktop` 这类受保护目录做路径级拦截，且对 launchd 拉起的进程一律拒绝**。后果不是报错中断，而是**静默空转**：进程活着、日志在写、每 60 秒失败一轮，永远零产出——最容易骗过「看进程还在跑就以为没事」的人。

---

> [!quote] 发生了什么

**事实链：**

```
2026-09-10 22:28  课程蒸馏转写管线以 LaunchAgent 方式启动（com.ip.brain.distill）
2026-09-11 00:34  TRANSCRIPT_01 产出
2026-09-11 01:21  TRANSCRIPT_02 产出
2026-09-11 01:57  TRANSCRIPT_03 产出
2026-09-11 02:00+ 之后每 60 秒一轮全部失败，直到 04:40 被人工发现

        ↓ 为什么前 3 集成功了？往下看

那 3 集并非管线产物，而是 22:26 一次「沙箱内本地试跑」被 kill 后
遗留的孤儿池子进程（父进程在 DSH 上下文，能读桌面）跑完的。
即：真正的 launchd 管线从第一秒起就从未成功过。

        ↓ 一次性探针 job（Aqua 上下文，独立于任何沙箱）实测

open("~/Desktop/.../第一天.mp4","rb")   → FAIL PermissionError [Errno 1] Operation not permitted
av.open(同一文件)                        → FAIL 同上
/bin/ls "~/Desktop/.../第二期3天/"       → FAIL Operation not permitted（目录列举都被拒）
/bin/ls /Users/huohaochen/.ipbrain/src/*/ → PASS 正常列出

        ↓ 对照历史

旧 ANSIR 管线 SOURCE_ROOT = ~/.ipbrain/src/安先生-...（镜像），
而不是 ~/Desktop/安先生-...。前一位作者撞过同一面墙，用镜像绕过了。
```

---

| 判断 | 依据 |
|:-----|:-----|
| ==判断== | 依据 |
| 根因是 TCC，不是脚本 bug | 探针 job 独立于任何沙箱与用户脚本，同一进程读桌面全拒、读 ~/.ipbrain 全通，唯一变量是路径 |
| 危害形态是「静默空转」 | 失败在 0.0–0.35 秒内发生、worker 每 60 秒重试一次、exit code 为 0；不专门读 transcribe-run.log 就看不出问题 |
| 「进程还在跑」不能当作健康信号 | 本次静默空转持续 6 小时 22 分（2026-09-10 22:28:13 launchd 启动 → 09-11 04:50 修复），期间 worker 与 launchd 状态全程 running、exit code 全为 0 |

---

> [!warning] 可能偏差
> - 只验证了 `~/Desktop`；`~/Documents`、`~/Downloads` 是否同样受限未逐个实测
> - 未测试「给 launchd 进程授予完全磁盘访问权限」这条替代路径（本次选择了镜像方案）
> - 孤儿进程解释是基于时间戳与进程树的推断，未逐进程取证

---

> [!note]- 过程层（复盘时展开）
> **原话**：
> 
> 
> **关键分歧**：
> 
> 
> **标尺**：launchd/后台任务的健康判据必须是「**产物增量**」，不是「进程存活」
>
> **归属**：DSH 在课程蒸馏续跑管线空转 6 小时 22 分后实测定位（`~/Workspace/01-进行中/课程蒸馏-续跑/`）
>
> **severity**：待人工定级（按协议 S1 只能由人定）