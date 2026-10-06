---
id: P-20261005-081508
type: problem
title: Hermes CLI 所有调用失败于 install state is not writable（锁文件属主为本机用户、目录可写，报错与磁盘权限不一致）
domain: 待分类
ptype: 待分类
level: 待定
status: 已定位
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
created: 2026-10-05
tags: [problem, hermes, cli, install-lock]
---

# 🟢 Hermes CLI 所有调用失败于 install state is not writable（锁文件属主为本机用户、目录可写，报错与磁盘权限不一致）

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> Hermes CLI 目前**任何**子命令都不可用：进程在启动前置检查阶段即退出，报「install state is not writable by this user」。
> 报错指向的锁文件**属主就是当前用户**、其所在目录也可写，**报错与磁盘权限事实不一致** ⇒ 这是疑似误判（或该检查探测的对象与报错文案不符），不是真实权限不足。
> 影响面：**不阻塞主线**（手改 `~/.hermes/config.yaml` 仍可完成全部配置类工作）；**阻塞运行期验收**（依赖 `hermes moa …` 等 CLI 路径的实跑验收无法进行）。

---

> [!quote] 发生了什么

**事实链：**

```
$ hermes --help
hermes: install state is not writable by this user (/Users/huohaochen/.hermes/installs/7b154c8e7368bb4d/.install.lock); run as the install owner or grant write access

$ hermes moa list
hermes: install state is not writable by this user (/Users/huohaochen/.hermes/installs/7b154c8e7368bb4d/pm-runtime/.prepare.lock); run as the install owner or grant write access

$ id -un
huohaochen

$ ls -la ~/.hermes/installs/7b154c8e7368bb4d/
drwxr-xr-x@ 7 huohaochen  staff  224 Oct  4 05:03 .
-rw-------@ 1 huohaochen  staff    0 Oct  2 13:18 .install.lock        ← 属主=当前用户，本人可写
drwxr-xr-x@ 3 huohaochen  staff   96 Oct  2 13:21 bootstrap
drwxr-xr-x@ 4 huohaochen  staff  128 Oct  4 05:03 environments
drwxr-xr-x@ 5 huohaochen  staff  160 Oct  2 13:18 pm-runtime           ← 目录属主=当前用户，drwxr-xr-x ⇒ 本人可写
```

**关键观察**：

1. 两次调用报的是**两个不同的锁文件**（`.install.lock` / `pm-runtime/.prepare.lock`），说明该检查会按子命令走到不同路径，但都判「not writable」。
2. 报错要求「run as the install owner」——**当前进程就是 install owner**。
3. 磁盘上未见任何属主为他人的锁或目录（`pm-runtime/` 下 `ls *.lock` 为空）。
4. 因此最可能是：该可写性探测的**判定逻辑**（如以 root/其他 uid 视角、以只读挂载判断、或对不存在文件用 `os.access` 在特定 umask 下误判）与文案不符。
5. 未验证事项：`hermes` 入口（`~/.local/bin/hermes`）是否为包装脚本并切换了执行身份/环境（未读该脚本内容）。

---

| 判断 | 依据 |
|:-----|:-----|
| ==CLI 全面不可用（非仅某子命令）== | `--help` 与 `moa list` 均在同一前置检查处失败 |
| ==不是真实权限不足== | `.install.lock` 属主=`huohaochen` 且 mode `-rw-------`；`pm-runtime/` 属主=`huohaochen` 且 `drwxr-xr-x` |
| ==疑似检查逻辑误判== | 文案要求「以 install owner 运行」，而进程已是该 owner |
| ==影响面：不阻塞主线，阻塞运行期验收== | 配置类工作可手改 `~/.hermes/config.yaml` 完成；依赖 CLI 的实跑验收不可进行 |

---

> [!warning] 可能偏差
> - 未读 `~/.local/bin/hermes` 包装脚本，**不排除**它在切换用户/环境后执行，从而让「install owner」判定在子进程视角下为假（此路径未排除）。
> - 未核对 Hermes 上游对该检查的实现（`hermes-agent` 内的 install-state 前置检查），根因仍是推断。
> - 报错路径随子命令变化，说明可能不是单一检查点；本卡只登记现象与权限事实，**不宣称已定位根因**。

---

> [!note]- 过程层（复盘时展开）
> **原话**（DSH 会话内，2026-10-05，Hermes MoA 审计栈核验任务）：
> 「`hermes` CLI 当前完全不可用：任何 `hermes` 调用都 fail 在 `install state is not writable by this user (.../pm-runtime/.prepare.lock)`，而该文件属主是你、目录也可写——报错与磁盘权限不一致，像是误判。」
>
> **关键分歧**：是「Hermes CLI 本身坏了」还是「本机 install 状态目录的权限/探测有问题」——目前证据只支持后者，但未读到检查实现，故不下定论。
>
> **标尺**：[[]]

---

## 影响面分级（本任务要求登记的字段）

```
MAINLINE_BLOCKED = NO
RUNTIME_ACCEPTANCE_BLOCKED = YES
```

- `MAINLINE_BLOCKED = NO`：不阻塞主线。Hermes 配置为 YAML 文件，可直接编辑；本轮 Hermes MoA 审计栈的**设计草案与 config patch 均已产出**，未因 CLI 故障而停。
- `RUNTIME_ACCEPTANCE_BLOCKED = YES`：阻塞运行期验收。凡需要实跑 `hermes …`（`hermes moa list` / 切换 preset / 跑 MoA 回合）的验收动作，当前**无法执行**，只能等 CLI 修复或改用其它入口。

## 本任务范围声明

```
FIX_IN_THIS_TASK = NO
FIX_SCOPE = 仅登记问题，不扩展修复
```

按《HERMES_MOA_AUDIT_STACK_NARROW_CORRECTION_V2》第 8 条：先建卡记录，**不在本任务中修复**。

## 关联

- 触发任务：`~/Workspace/01-进行中/2026-10-05-Hermes-MoA独立审计栈核验/`
- 已知错误库查重：`kedb.py check "hermes CLI install state is not writable"` → **无精确命中**（返回的 KE-002/KE-006/KE-007 均为关键词噪声，与本案无关）
- 同源风险：若后续要「修 Hermes CLI」，须先确认它是否与本卡第 5 条未验证项（包装脚本身份切换）相关

---

## 更正（2026-10-05，同日，`HERMES_MOA_AUDIT_STACK_RUNTIME_ACCEPTANCE_V1` 期间）

```
ROOT_CAUSE       = 外层文件沙箱拒绝子进程写 install state（真实 EACCES），非 Hermes 缺陷
CONSTRUCTION     = NO（零修复动作）
STATUS_CHANGE    = 未处理 → 已定位
SOLUTION_STATUS  = 待解决（Hermes 侧文案仍具误导性；见下）
```

**新证据链：**

1. 早期 DSH 文件策略 = `workspace-write`；此时 `hermes --version` / `hermes moa list` 均打印该错误。
2. 读码确认「该消息只在真实 `PermissionError(EACCES)` 时产生」：
   `pm/environments.py:34-46` 的 `install_state_permission_message()` 要求异常携带 `filename`，
   且该路径必须落在 install state 目录内；`tests/pm/test_install_state_permissions.py:30-32` 正是**主动注入 EACCES** 来复现该输出。
   ⇒ 不是"探测逻辑误判"，而是**写操作真的被拒绝**（由外层沙箱造成）。
3. DSH 文件策略切换为 `danger-full-access` 后，**未做任何 chmod / touch / 重装 / 删环境**，`hermes --version` 立即成功：

```
Hermes Agent v0.21.5+5648.gb5be2a3 (2026.9.24) · upstream b5be2a3c
Install method: git · Python: 3.14.7 · OpenAI SDK: 2.24.0
```

4. 期间 `~/.hermes/` 属主、权限、锁文件均未变化。

**原推断的更正**：本卡原写「报错与磁盘权限事实不一致 ⇒ 疑似误判」——**该推断部分错误**。
磁盘权限确实允许写，但**外层沙箱先一步拒绝**，`os.access` 视角的"可写"与沙箱内实际可写并不等价。
未验证项第 5 条（包装脚本身份切换）**已排除**：无需它解释现象。

**仍成立的可改进点（Hermes 上游）**：该文案把"沙箱/EDR 拒绝"表述为"install state 不可写，请以 install owner 运行或授权写权限"，
会把排查方向引到文件权限上（本次即如此，浪费了一轮误判）。更准确的表述应包含"若在沙箱/受限容器内运行，请检查文件系统策略"。

**残留风险**：任何在受限文件策略下调用 `hermes` 的场景都会复现同一报错；这不是 `hermes` 侧可自愈的问题，需在运行手册中固化「hermes 需非受限文件策略」。

