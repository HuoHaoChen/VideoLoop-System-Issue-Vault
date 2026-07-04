# videoloop-cal-scan V2 测试用例

> 目的：验证 V2 三大核心改动是否生效
> 跑通标准：所有 ✅ 用例必须按预期行为，❌ 用例必须不触发
> 测试人：
> 测试日期：

---

## 测试 1 · 触发词精准度

### 1.1 精准触发（应启动 skill）

| 输入 | 预期 | 实际 | 通过 |
|---|---|---|---|
| "建修改卡：API 空返回修复" | 启动扫描流程 | | |
| "CAL 扫描" | 启动扫描流程 | | |
| "建修改卡，关于 Hermes 误判问题" | 启动扫描流程 | | |

### 1.2 描述性语句（应不触发）

| 输入 | 预期 | 实际 | 通过 |
|---|---|---|---|
| "我改了一下视频剪辑" | 不触发，正常对话 | | |
| "我修复了电脑的 wifi" | 不触发 | | |
| "那个 bug 解决问题了" | 不触发 | | |
| "我记一条解法" | 不触发（V1 词已删） | | |
| "今天修了个小问题" | 不触发 | | |

### 1.3 混合场景

| 输入 | 预期 | 实际 | 通过 |
|---|---|---|---|
| "我改了一下，顺便建修改卡" | 触发（出现显式词） | | |
| "我修复了 wifi，对应 CAL 扫描" | 触发 | | |

---

## 测试 2 · 硬匹配准确性

### 2.1 强相关命中

**场景**：C 卡「Hermes 将 API 空返回误判为数据为空」（系统域）

**预期 CAL 命中**：

| CAL 卡 | 预期 | 实际 | 通过 |
|---|---|---|---|
| AI 自报不可信原则 | ⚠ 强相关（关键词「AI、误判」命中） | | |
| 问题即解药原则 | 📋 仅展示或无命中 | | |

**验证方法**：检查 `cal_scan_result.shown_strong` 字段

### 2.2 零命中

**场景**：C 卡「换了新键盘，手感不错」（运营域）

**预期**：本域 CAL 库若无相关内容，显示「本域尚无 CAL，跳过本节」

### 2.3 阈值边界

**场景**：C 卡标题与 CAL 仅共享 1 个关键词

**预期**：标为「📋 仅展示」，不进入强相关列表

**验证方法**：检查 `shown_strong` 为空，`shown_normal` 有该项

---

## 测试 3 · 逃生舱响应

### 3.1 [Esc] 不留痕

**操作**：触发扫描 → 选 [Esc]

**预期**：

- ✅ C 卡 frontmatter 无 `cal_scan_done`、`cal_scan_result` 字段
- ✅ CAL 卡 call_log 无追加

**验证方法**：

```bash
grep -E "cal_scan_done|cal_scan_result" <c_card_path>
# 期望：无输出
```

### 3.2 [2] 强制留痕

**操作**：触发扫描 → 选 [2] → 写理由「这是 API 实现 bug，和 AI 判断无关」

**预期**：

- ✅ C 卡有 `cal_scan_done=true` 和 `cal_scan_result.decision="skip_with_reason"`
- ✅ `skip_reason` 非空
- ✅ CAL 卡 call_log 无追加（只是 skip 不是 refer）

---

## 测试 4 · invalidate 自动重置

### 4.1 C 卡修改后失效

**操作**：

1. 建 C 卡 → 扫描 → 引用 CAL → 完成
2. 手动修改 C 卡内容，触发文件 mtime 更新
3. 再次「建修改卡」（编辑这张）

**预期**：

- ✅ skill 检测到文件 mtime 晚于 `cal_scan_at`
- ✅ 日志打印「CAL 扫描已失效：文件 mtime 晚于 cal_scan_at」
- ✅ `cal_scan_done` 自动重置为 `false`
- ✅ **不自动重启扫描**，等待显式触发

### 4.2 mtime vs frontmatter 优先级

**操作**：

1. 建 C 卡 → 扫描 → 引用 CAL → 完成（记录 `cal_scan_at`）
2. **只修改文件内容，不改 frontmatter 的 updated 字段**
3. 跑 `stat` 确认 mtime 已变：
   ```bash
   stat <c_card_path> | grep Modify
   ```
4. 触发「CAL 扫描」

**预期**：

- ✅ skill 通过 mtime 检测到失效
- ✅ 日志打印「CAL 扫描已失效：文件 mtime 晚于 cal_scan_at」
- ✅ 即使 frontmatter 的 updated 没变，也能正确失效

---

## 测试 5 · 日志格式对齐

### 5.1 引用后日志追加

**操作**：选 [1] 引用 CAL

**预期**：CAL 卡 call_log 追加一行，格式严格匹配现有规范：

```
| 2026-06-24 | <场景名> | <domain> | 待定 |
```

**验证方法**：

```bash
# 检查列数
grep "| 2026-06-24 |" <cal_card_path> | awk -F'|' '{print NF}'
# 期望：5（4 个分隔符 + 行尾空白）

# 检查表头一致性
head -5 <cal_card_path> | grep "| 日期 |"
# 期望：表头为 | 日期 | 场景 | domain | 事后验证 |
```

---

## 测试 6 · schema 校验

### 6.1 字段识别

**操作**：跑 `validate_loop.py`

**预期**：

- ✅ `cal_scan_done`、`cal_scan_at`、`cal_scan_result`、`referenced_cals` 不报「未知字段」
- ✅ 不新增 FAIL

**验证方法**：

```bash
cd ~/Desktop/VideoLoop
python3 scripts/validate_loop.py
```

### 6.2 引用 CAL 校验

**操作**：C 卡有 `referenced_cals` 但每条缺 `cal_id`

**预期**：validator 报 FAIL：`[CAL引用] ... 缺 cal_id`

---

## 测试通过标准

| 测试组 | 必须全部通过 |
|---|---|
| 测试 1（触发词） | ✅ |
| 测试 2（硬匹配） | ✅ |
| 测试 3（逃生舱） | ✅ |
| 测试 4（invalidate） | ✅ |
| 测试 5（日志格式） | ✅ |
| 测试 6（schema） | ✅ |

任何一项不通过，回滚到 V1 + 修问题。

---

## 测试记录

| 测试轮次 | 日期 | 通过项 | 失败项 | 备注 |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
