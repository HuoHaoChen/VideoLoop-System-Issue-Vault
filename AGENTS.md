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
