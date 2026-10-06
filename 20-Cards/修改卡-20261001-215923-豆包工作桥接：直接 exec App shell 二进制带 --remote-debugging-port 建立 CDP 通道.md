---
id: C-20261001-215923
type: change
title: 豆包工作桥接：直接 exec App shell 二进制带 --remote-debugging-port 建立 CDP 通道
domain: 待分类
problems: []
status: 设计中
baseline_window: 
minimum_effect: 
confounds: 
significance: 方向性
borrows_from: 无
verdict: 待校准
calibrated: false
calibration_ref: 
process_captured: false
recorded_by: dsh-A
source_tool: dsh
evaluator: 第二裁判
due: 
created: 2026-10-01
tags: [change]
---

# 🔵 豆包工作桥接：直接 exec App shell 二进制带 --remote-debugging-port 建立 CDP 通道

> [!question] 一句话
> 

---

> [!danger] 改动
> **改前**：
> **改后**：

---

## ✅ 怎么做

- [ ] 
- [ ] 

---

> [!success] 预测
> 

---

> [!note]- 过程层（复盘时展开）
> **为什么选这个方案**
> 
> 
> **赌的假设**
> 
> 
> **标尺**
> [[]]

## 方案 DSH 实测（2026-10-01）

**可用通道**：直接 exec App shell 二进制并带上 flag——
`/Applications/DoubaoWork.app/Contents/MacOS/DoubaoWork --remote-debugging-port=9222`
（实测 CDP 9222 起来，`Chrome/147.0.7727.149`，`/json/list` 拿到 `doubaowork-chat/chat` 页面目标）

**桥接要点**：
1. 输入框 = `.tiptap.ProseMirror`（ProseMirror），用 `Input.insertText` 写入。
2. 发送**优先点** `[class*="send-btn-wrapper"]`；仅当点击后编辑器仍非空才补 Enter（新会话落地页 Enter 不提交）。
3. 回复取 `[data-message-role="assistant"]` 最后一个节点，且必须**剔除** `[class*="message-action-bar"]` 的文本（消耗/时间）。
4. 豆包发首条消息后页面会二次跳转（`/chat/<临时id>` → `/chat/local_<id>`），必须每轮重解析 CDP target 并重连。
5. 冷会话单次回复可能 >3 分钟，超时不宜低于 300 s。
6. 自动重启需**非沙箱**执行（要写 `~/Library/Application Support/DoubaoWork`）。

**产物**：`~/Workspace/01-进行中/doubaowork-bridge/`（`doubaowork-call.mjs` + `README.md` + `receipts/`），实测验收获 `RESULT_STATUS=PASS`，答案 `收口成功`，10.0 s。

**残留风险**：依赖未公开的 CDP 与 DOM 选择器，豆包升级可能失效（应表现为硬失败，不会假成功）；每次调用真实发消息、消耗额度。
