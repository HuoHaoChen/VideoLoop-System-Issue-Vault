---
id: P-20260913-171938
type: problem
title: DSH 沙箱 workspace-write 拒绝 hermes CLI 写 ~/.hermes/logs/agent.log，导致外部独立审计无法启动
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
created: 2026-09-13
tags: [problem]
---

# 🟢 DSH 沙箱 workspace-write 拒绝 hermes CLI 写 ~/.hermes/logs/agent.log，导致外部独立审计无法启动

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> DSH 的 `workspace-write` 文件沙箱会拦住 `hermes -z` 启动：hermes 需要写自己的日志 `~/.hermes/logs/agent.log`，而该路径在会话工作区之外，于是进程在真正开始推理前就 `EXIT=1`、stdout 0 字节。**这不是 hermes 的故障，是 DSH 沙箱与 hermes 的交互坑**；提升至 `danger-full-access` 后同一命令 `EXIT=0` 正常返回。

---

> [!quote] 发生了什么

**事实链：**

```text
1. 用户在 D3 V6 任务中授权 DSH 直调 Hermes-B 做外部独立审计（prompt 已落盘）。
2. DSH 以后台任务执行：hermes -z "$(cat POST_PIN_HERMES_B_REAUDIT_PROMPT.md)"
3. 返回 EXIT=1，stdout 0 字节。stderr:
   hermes -z: agent failed: [Errno 1] Operation not permitted:
   '/Users/huohaochen/.hermes/logs/agent.log'
4. 判定为沙箱策略拒绝（非工具 bug）——DSH 当前文件策略为 workspace-write，
   而 ~/.hermes/logs/ 位于 /Users/huohaochen/Workspace 之外。
5. 按「一次一提升」规程原样重试，申请 danger-full-access 并说明理由。
6. 获批后同一命令 EXIT=0，stdout 2699 字节，返回完整审计结论。
```

**影响**：任何「DSH 直调外部 AI 工具做独立审计」的编排都会静默失败——
如果只看 stdout 会误判为「审计无输出」。本次因检查了 stderr 才定位到根因。

---

| 判断 | 依据 |
|:-----|:-----|
| ==判断== | 依据 |
|:-----|:-----|
| 是**策略拒绝**，不是 hermes 崩溃 | stderr 为 `Operation not permitted`（EPERM），且明确指向写入路径；hermes 二进制本身可执行（`--help` 正常） |
| 阻塞点在**启动阶段**，尚未进入推理 | stdout 恰好 0 字节，且无任何会话 ID 产生 |
| 提权后**功能完好** | 同一命令、同一 prompt、同一工作目录，`danger-full-access` 下 `EXIT=0` 并返回 2699 字节完整审计报告 |
| 不是权限位/所有权问题 | 报错是沙箱 EPERM 而非 `EACCES`；文件系统层面对当前用户可写 |

---

> [!warning] 可能偏差
> - 本次只验证了 `hermes -z` 的一次性模式；`hermes chat` / TUI 等其它入口未验证，可能存在额外路径依赖。
> - 仅验证了 `~/.hermes/logs/agent.log` 这一个被拒路径；hermes 可能还依赖其它工作区外路径（配置、缓存、secrets），未逐一探明。
> - 「提权即可」是**规避方案**，不是根治；根治需为 hermes 的运行期路径开白名单，本次未做，也未验证白名单是否可行。
> - 未测量提权带来的实际风险面（danger-full-access 下 DSH 可写任意路径）。

---

> [!note]- 过程层（复盘时展开）
> **原话**（stderr 逐字）：
> `hermes -z: agent failed: [Errno 1] Operation not permitted: '/Users/huohaochen/.hermes/logs/agent.log'`
> 
> **关键分歧**：
> - 初判「hermes 失败」→ 复核后修正为「hermes 被沙箱拦截」。前者会误导人去修 hermes，后者才指向 DSH 策略。
> - 另一处易犯的错：只看 stdout（0 字节）就报「审计无结论」。本次强制检查了 stderr，才拿到真实原因。
> 
> **标尺**：[[裁判独立性协议]] —— 外部审计通道不可用时，不得用「同工具自审」顶替，应先修复通道或如实上报未完成。
> 
> **关联**：[[C-20260913-172013]]