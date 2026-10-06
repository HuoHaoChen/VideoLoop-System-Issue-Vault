---
id: P-20261001-215530
type: problem
title: 豆包工作 DoubaoWork.app 无法被外部程序调用：无 CLI、启动器丢弃调试参数、深链不携带 prompt
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
created: 2026-10-01
tags: [problem]
---

# 🟢 豆包工作 DoubaoWork.app 无法被外部程序调用：无 CLI、启动器丢弃调试参数、深链不携带 prompt

==待处理== · 待分类 · <kbd>未设</kbd>

---

> [!question]+ 结论
> 

---

> [!quote] 发生了什么

**事实链：**

```

```

---

| 判断 | 依据 |
|:-----|:-----|
| ==判断== | 依据 |

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

## DSH 实测补充（2026-10-01，豆包工作 2.31.8 / Chromium 147）

**症状**：需要把本机 `DoubaoWork.app`（`com.work.pc.doubao`）当作可派工执行器调用，但找不到任何对外入口。

**逐项实测结论**：
1. 无独立 CLI（对比 WorkBuddy 有 `cli/bin/codebuddy`）。
2. `open -a DoubaoWork --args --remote-debugging-port=9222` → `open` 返回 0，但子进程 argv 里**没有**该 flag：启动器自行拼装浏览器命令行并丢弃外部参数。
3. 直接执行浏览器二进制 `.../DoubaoWork Browser` → 被 `saman` 修复/接管逻辑拦回，最终仍由 App shell 以 `--saman-from-chat=<pid>` 重新拉起。
4. 运行中实例**无** `DevToolsActivePort` 文件；两个监听端口（`127.0.0.1:49853` 返回 404、`52333` 直接 RST）都不是 CDP。
5. `doubaowork://` 深链存在且可用（linkrouter，路由如 `doubaoworkapp/active-chat`、`doubaowork-chat/chat`），但**未发现可携带 prompt 的参数路由**，且只回 `doubaowork-link-router-result`（已处理/未处理），拿不到 AI 回答。
6. AppleScript/System Events 被 macOS TCC 拦截（错误 `-10004`）；`NSAppleScriptEnabled=true` 不足以做 UI 自动化。
7. profile 偏好 `devtools.remote_debugging.{allowed,user-enabled}` 写入 `Default/Preferences` 并重启后，服务**未启动**（该构建还需策略层；`RemoteDebuggingAllowed` 策略名存在于二进制中）。

**根因**：豆包工作把「启动浏览器」收敛为 App shell 的内部职责，且所有对外接口（深链）只服务于「激活窗口」而非「提交任务」，所以不存在面向自动化的设计入口。

**踩坑记录（与建卡问题不同维度，一并登记）**：
- 脱离文档的 `cloneNode` 节点无布局，`innerText` **恒为空串**——用克隆节点做文本提取会静默得空。
- 用「隐藏操作栏最近祖先」去噪时，若操作栏嵌在内容容器内部，会把答案一起隐藏（同样返回空串）。
