---
id: P-20260926-172006
type: problem
title: Claude Code 非交互 (-p) 默认权限模式下无法写入工作区文件（原生 Edit 与 shell 写入均需审批）；但 --permission-mode acceptEdits 下原生 Edit 实测可写
domain: 待分类
ptype: 待分类
level: 待定
status: 未处理
process_captured: true
recorded_by: dsh-A
source_tool: dsh
solution: 
solution_status: 待解决
solution_hits: 0
solution_level: 待验证
resolved_at: 
due: 
owner: huohaochen
created: 2026-09-26
tags: [problem]
---

# 🟢 Claude Code 非交互 (-p) 默认权限模式下无法写入工作区文件（原生 Edit 与 shell 写入均需审批）；但 `--permission-mode acceptEdits` 下原生 Edit 实测可写

> [!important] 标题勘误（2026-09-26 追加）
> 原标题断言"`EXECUTOR=CLAUDE_CODE` 路由在无人在场时不可用"，**该断言已被后续实测部分证伪**，
> 现收窄为"**默认权限模式下**不可写"。文件名与 `id` 保持不变以免破坏引用。
> **请以本卡下方的"结论（已修订）"为准。**

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论（已修订 · 2026-09-26）
>
> **已确认（CONFIRMED）**：在**默认权限模式**下，`claude -p`（非交互、无人在场）**不能写文件** ——
> 不只是 shell 的 `cp`/`sed`，**原生 Edit 工具同样被拦**；
> 连**只读**的 `shasum` / `openssl dgst` 哈希命令也需要审批。
>
> **已确认（CONFIRMED）**：加一次性 `--permission-mode acceptEdits` 后，**原生 Edit 写入成功**。
> 实测：对一份**已冻结**文件执行**预先冻结的 7 处精确替换**，7/7 `APPLIED`、
> 无一次审批拒绝，且派发方独立核验（含"反向还原证明"）判定**只有目标文件按预期改变**。
>
> **因此**：
> - ❌ **不成立**："Claude Code 非交互模式无法承担**任何**无人值守写入。" —— 该断言**过度概括，已撤回**。
> - ✅ **成立**：默认权限模式下它不可写；`acceptEdits` 模式下它**可以**写，
>   但那是**预授权写入**（把"逐次人工确认"降级为"默认同意"），需要有人为误写负责。
> - ✅ **仍成立**：`acceptEdits` **不**授予 Bash/哈希命令权限（哈希仍被拦），
>   所以"**谁写**"与"**谁验**"应分离：执行器负责改，派发方独立负责哈希与比对。
>
> **可达成的结论上限**：本轮只证明
> `CLAUDE_NONINTERACTIVE_BOUNDED_EDIT_ROUTE = MECHANICALLY_VERIFIED`
> ——即"收窄工作目录 + 已冻结文件 + 预先冻结的替换集 + 单次 `acceptEdits`"这一**受限场景**。
> **不得**扩大声称为"所有 Claude 无人值守任务均已验证安全"。

---

> [!quote] 发生了什么

### A. 默认权限模式：4 次真实拒绝（逐字）

1. **`/tmp` 源路径**（工作区之外读取）：
```
The path is outside the working directories for this session
```
2. **工作区内 shell 写入（`cp`）**：
```
Claude Code asks before a shell command creates, changes or removes files there
```
3. **工作区内只读哈希（`shasum -a 256`；`openssl dgst -sha256` 同样）**：
```
This command requires approval
```
4. **工作区内原生 `Edit` 工具写文件（决定性）**：
```
Claude requested permissions to write to /Users/huohaochen/Workspace/01-进行中/2026-09-25-任务中枢-4PLUS1-重构/07-TEST02-任务分类与输入就绪/TEST02B_TASK_CLASS_ASSIGNMENT_PROTOCOL.md, but you haven't granted it yet.
```

**推论**：拒绝**不限于 shell 写入**。"改用原生 Edit/Write 而不是 `cp`"**在默认模式下不成立**。
且连"改完自己算 sha256 自证"也做不了（只读哈希命令同样需审批）。

**对照事实（证明不是环境坏了）**：同一进程内**只读**的 `wc -c -l` 与全文读取**获批**，
返回 `477 lines / 28398 bytes` 与冻结基线一致，且正确核验 7 处锚点各自唯一。
即 **读可用；写与哈希不可用**，是权限模型的确定性切分。

### B. `--permission-mode acceptEdits`：受限实测成功（2026-09-26 17:57:02–17:59:19）

**调用形状**（单次，未改任何 settings）：
```
cd  <收窄到目标所在目录：07-TEST02-任务分类与输入就绪/>
claude -p "<冻结派工单全文>" --permission-mode acceptEdits --output-format text
```
**执行器回报**：`EDIT_1..EDIT_7 = APPLIED`、`NATIVE_EDIT_TOOL_USED = YES`、
`APPROVAL_BLOCKED_EDIT = NO`、`SHELL_WRITE_USED = NO`、`OTHER_FILES_TOUCHED = NO`、
`HASH_COMMAND_RUN = NO`、`BLOCKERS = NONE`。

**派发方独立核验（不采信执行器自述）**：
- 7 处 `OLD` 残留 **0**；7 处 `NEW` 出现 **1**；
- **反向还原证明**：把结果按 `NEW→OLD` 逆替换后重算 sha256 = 原文哈希 ⇒
  证明"结果 = 原文 + 恰好这 7 处替换"，**无任何第 8 处改动**（强于 diff）；
- 体积核算：预测增量 `+2831` B = 实际 `+2831` B；行数 477 → 516；
- 目标目录内**仅 1 个文件**发生变化；mtime 落在派发窗口内。

---

| 判断 | 依据 |
|:-----|:-----|
| ==默认模式下"写"整体不可用，与工具选择无关== | 拒绝 2（shell `cp`）与拒绝 4（原生 `Edit`）为**两条独立路径**，均被拦 |
| ==`acceptEdits` 下原生 Edit 可用== | 7/7 `APPLIED`、零审批拒绝，且派发方反向还原证明通过 |
| =="无法承担任何无人值守写入"过度概括，已撤回== | 反例已实测：同一非交互形状 + `acceptEdits` 即可写入 |
| ==`acceptEdits` 不等于"免审批"，更不等于"可自验"== | 该模式只覆盖编辑；Bash/哈希命令仍被拦（执行器 `HASH_COMMAND_RUN = NO`） |
| ==读写分离是必要的工程结论== | 执行器可写但不可自证哈希 ⇒ 哈希与比对必须由派发方独立完成 |
| ==`exit code 0` 不能当作成功信号== | 默认模式那一轮 exit 0，但 7 处编辑全部 `BLOCKED`（它把拒绝当正常终局如实汇报） |

---

> [!warning] 可能偏差
> - **本轮只覆盖一种受限形状**：收窄 cwd + 已冻结文件 + 预先冻结的替换集 + 单次调用。
>   **未**验证：多文件批改、目标在 cwd 之外、需要 Bash 的施工（编译/测试/生成）、长任务中途需审批的场景。
> - `acceptEdits` 的本质是**预授权**：把"逐次人工确认"变成"本会话默认同意"。它解决了**效率**，**没有**解决**问责**——
>   "谁为一次误写负责"仍未被回答。
> - **未**测试 `bypassPermissions` / `--dangerously-skip-permissions`（属明确越界，不建议）。
> - **未**写入任何全局/项目 Claude settings，**未**把 `acceptEdits` 设为永久默认（授权明令禁止）。
> - 拒绝文本为执行器自行摘录；原始完整输出留存：
>   `~/Workspace/01-进行中/2026-09-25-任务中枢-4PLUS1-重构/99-独立审计/_tools/CLAUDE_TEST02B_DELTA1_raw.log`（默认模式，被拦）
>   `~/Workspace/01-进行中/2026-09-25-任务中枢-4PLUS1-重构/99-独立审计/_tools/CLAUDE_TEST02B_DELTA1_ACCEPTEDITS_raw.log`（acceptEdits，成功）

---

> [!note]- 过程层（复盘时展开）
> **原话**：
> - 默认模式那轮，执行器主动声明 `SHELL_WRITE_USED = NO`、`OTHER_FILES_TOUCHED = NO`、`OTHER_AGENT_USED = NO`，
>   逐字粘贴 4 段拒绝原文并 STOP；最后写："需要你授予该文件的写入权限（及可选的 `shasum` 只读权限）后重跑"。
> - `acceptEdits` 那轮，执行器回读 7 个区域并声明 `APPROVAL_BLOCKED_EDIT = NO`、`DENIAL_VERBATIM = NONE`，
>   其自报 `POST_BYTES = 31229` / `POST_LINES = 516` 与派发方实测**逐一吻合**；
>   它另主动提示：文件头元数据块的 `工具: dsh` / `状态: 待审` 未改，如需同步请另行下单
>   （**未被授权，故未执行**——派工单范围严格限定为 7 处替换）。
>
> **关键分歧 / 走过的弯路**：
> 1. 第一次结论下得太快："非交互 `claude -p` 无法写入"被外推成"该路由不可用"。
>    监督方正确地指出**证据不足**：`acceptEdits` 尚未测试。实测后结论**部分翻案**。
>    **教训**：拒绝证据只能支撑"在该配置下不可用"，不能支撑"在该执行器下不可用"；
>    下结论时必须把**配置变量**显式写进断言里。
> 2. 一度把"改用原生 Edit 而非 shell `cp`"当作规避方案 —— 默认模式下它不成立（拒绝 4）。
>    真正的解锁变量不是**工具**，而是**权限模式**。
> 3. 治理纪律在本轮起了作用：被拦时选择 STOP 并上报，**没有**自行发明解锁路径
>    （当时刻意未使用 `acceptEdits`，把"是否放宽权限"交回监督方裁决）——
>    这正是后来该模式被**授权实测**而非被**私自启用**的原因。
>
> **标尺**：[[反馈接入协议]] · `_tools/CLAUDE_TEST02B_DELTA1_raw.log`（被拦）· `_tools/CLAUDE_TEST02B_DELTA1_ACCEPTEDITS_raw.log`（成功）
>
> **仍待人类/第二裁判裁决（本卡不自评）**：
> a) 无人值守任务中，`acceptEdits` 是否作为**逐任务显式授权**的常规做法？还是仅限"受限实测"？
> b) 由谁为 `acceptEdits` 下的一次误写负责？是否需要"改动范围白名单 + 反向还原证明"成为**强制**验收项？
> c) 落盘是否仍应优先指派本地执行器（DSH）并要求**披露性回退**声明？
