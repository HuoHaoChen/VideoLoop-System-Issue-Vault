---
type: project
title: 
status: 进行中
created: 
persona_ref: 
worldview_ref: 
tags: [project]
---

# 📽️ 项目：

==进行中== · 领域 · <kbd>创建日期</kbd>

---

## 关联的问题卡

```dataview
TABLE status AS "状态", domain AS "领域"
FROM "20-Cards"
WHERE type = "problem" AND contains(file.outlinks, this.file.link)
SORT created DESC
```

## 关联的校准卡

```dataview
TABLE status AS "状态", method AS "方法"
FROM "20-Cards"
WHERE type = "calibration" AND contains(file.outlinks, this.file.link)
SORT created DESC
```

## 关联的世界观卡

```dataview
TABLE statement AS "世界观", status AS "状态"
FROM "20-Cards"
WHERE type = "worldview" AND contains(file.outlinks, this.file.link)
SORT created DESC
```

---

## 脚本 / Outline

### 选题方向

- [ ] 

### 脚本骨架

```
// Hook（前3秒）：

// 冲突/问题：

// 展开路径：

// 结论/行动：
```

### 引用素材

- 
