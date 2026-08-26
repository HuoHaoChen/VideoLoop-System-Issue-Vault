# CAL 引用规则

> 生效日期：2026-07-01（V3.0）

## 硬规则

1. **C 卡涉及判断校准时，必须显式引用 CAL。**
   ```yaml
   calibration_ref: CAL-YYYYMMDD-HHMM
   ```

2. **asset_type = judgment_change 的 C 卡，calibration_ref 必填。**
   validator 检测：若 `asset_type=judgment_change` 且 `calibration_ref` 为空 → FAIL。

3. **operational_change（操作修改）不强制引用 CAL，但推荐。**
   操作修改如：脚本 bug 修复、配置调整、部署变更。

4. **开工前扫 CAL 是辅助，结构互锁才是机制。**
   「扫 CAL」是提醒机制；`calibration_ref` 是硬约束。

## CAL 生命周期

```
灵感 → CAL 创建 → C 卡引用 → C 卡结案验证 → 月度 Meta 复查
```

- 创建：灵感 → `new_card.py calibration`
- 引用：C 卡设置 `calibration_ref`
- 验证：C 卡结案时检查 CAL 是否准确
- 复查：月度 Meta 检查 CAL 引用次数和准确性

## validate_loop.py 新增校验

- `asset_type=judgment_change` 且 `calibration_ref` 为空 → FAIL
- CAL 引用指向不存在的 CAL ID → WARN
