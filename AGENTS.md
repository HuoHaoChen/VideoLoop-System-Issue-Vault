# AGENTS.md — 统一问题反馈引擎 v4 协作规范

给所有在此仓库工作的 AI（Codex / ChatGPT / 子代理）。人类规则见 README-For-Humans.md。

- 仓库定位：AI/智能体使用问题的「问题与解法」唯一事实源；卡片正本在 20-Cards/，规则在 config/，schema 在 schema.json
- 铁律1：新问题先 `kedb.py check` 查库，命中=复发（挂 ke_ref，不重复建卡）
- 铁律2：解决方案优先——已解决的 P 卡必须写 solution（validate_loop.py 会 WARN）
- 铁律3：解法是动态真相源（待验证→已验证/被推翻），不是第一真相源；不得改写课程方法论
- 铁律4：不得自行修改 schema.json / known_error_db.json / config/四工具反馈接入协议.md（规则变更走 13_rule_candidates）
- 铁律5：不得执行任何 git 命令（提交由外部主会话统一执行）
- 自动捕获：launchd 每小时跑 watcher.py，日志里的错误会自动建卡，无需手动投递
- 校验：改完跑 `python3 scripts/validate_loop.py .`，必须 0 FAIL
- 协议全文：config/四工具反馈接入协议.md

---

# SIFE / 经验三层边界与调用路径（SIFE-RECOVERY-02，2026-10-01 起，append-only 区块）

契约全文（唯一事实源）：`~/Workspace/03-资产/SIFE_EXPERIENCE_BOUNDARY_CONTRACT_V1.md`

三层分工（**不合并**）：
- SIFE = `SYSTEM_PROBLEM_AND_FEEDBACK_CANONICAL`，路径 `~/Desktop/Project/系统问题反馈引擎`
  —— 存「发生过什么」（原始问题 / 失败 / 修正 / Known Error 原始证据）。**不等于**可复用经验。
- Workspace 可复用经验索引 = `ACTIVE_REUSABLE_EXPERIENCE_INDEX`，`~/Workspace/03-资产/可复用经验索引.md`
  —— 任务开始时**唯一**的经验查询入口。
- Task Hub / SharedHub = `ORCHESTRATOR_AND_REFERENCE_CONSUMER`
  —— 在正确阶段调用经验并记录 experience ID / evidence reference / result；不复制内容、不宣布真理。

调用路径：
- TASK START：先查可复用经验索引（只读索引行）。**不得**在任务开始时扫描 SIFE 的 884 张卡。
- 仅当出现 failure / system issue / known-error investigation 时，才查
  `python3 ~/Desktop/Project/系统问题反馈引擎/scripts/kedb.py check "症状关键词"`。
- TASK END：用到的经验必须回写验证台账；新问题进 SIFE；
  新的「经验候选」只能记为 `CANDIDATE / PENDING_REVIEW`，**不得**自动进入 Active 索引。

禁止：自动 promotion / 自动 retirement / 新建第二经验库 / 物理合并三系统。
边界：软规则，不改变任何硬路由。
