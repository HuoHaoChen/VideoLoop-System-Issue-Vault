# Notion - VideoLoop - Hermes - GitHub 工具边界

> 生效日期：2026-07-01（V3.0）

## 四个工具，四个平面，不是四个步骤

```
Notion         → 灵感处理 + 当前运行记录
VideoLoop      → 活跃校准引擎 + 判断资产沉淀
Hermes         → 执行代理 + 安全封装 + 卡片触发器
GitHub         → 规则版本源（schema / prompt / validator / changelog）
```

## Notion 的边界

### 做
- 小白 5 问任务卡
- 内容判断训练台账
- 发布前判断记录
- 发布后数据采集
- 数据截图 / 链接存储
- 当前内容状态
- 灵感加工协议执行

### 不做
- CAL 正本（正本在 VideoLoop）
- 动态真相源正本
- VideoLoop 卡片正本
- 判断资产最终升降级裁决
- 系统校准引擎

> 一句话：Notion 记录「这条内容发生了什么」；VideoLoop 判断「这件事说明我以后该怎么判」。

## VideoLoop 的边界

### 做
- P → C → CAL → Meta 活跃校准闭环
- 判断资产沉淀（S2/S3 → 25-Assets, 50-TruthSource）
- 卡片格式铁律执行
- validate_loop.py 闭环校验
- 动态真相源引用管理

### 不做
- 当前任务状态管理（Notion 做）
- 内容脚本生成（Hermes 做）
- 规则版本管理（GitHub 做）

## Hermes 的边界

### 做
- 按锁定假设和版本化协议构建内容
- 通过 notion_safe.py 安全读取 Notion
- 触发卡片创建（new_card.py）
- 输出构建日志、变量声明、风险提示
- CAL 扫描（videoloop-cal-scan skill）

### 不做
- 自选变量、自定选题
- 自评、自晋升
- 把 S0 假设说成事实
- 决定判断资产升降级

## GitHub 的边界

### 做（L0-Deploy）
- schema.json 版本管理
- prompt 模板版本管理
- rubric 版本管理
- 变量字典版本管理
- CHANGELOG 维护

### 不做（L3 休眠）
- 自动 validator（后续通电）
- 多人权限管理
- 发布流水线
- 外包 SOP

## 跨工具接口

### Notion → Hermes
- Hermes 通过 hermes-v2/notion_safe.py 安全读取
- 不可直接信任 API 返回为空 = 数据为空

### Hermes → VideoLoop
- Hermes 通过 new_card.py 创建卡片
- 不直接编辑卡片文件
- 卡片内容经 validate_loop.py 校验

### VideoLoop → GitHub
- schema.json 变更提交到 GitHub
- 规则变更走 CHANGELOG + release log
