# Beer 数据集优化总结

## 测试结果

所有参数组合的测试结果几乎相同：
- **F1**: 0.06
- **Precision**: 0.03
- **Recall**: 0.76-0.79

## 关键发现

1. ✅ **初始化问题已解决**：从 18.55% 降到 0.04-0.12%
2. ❌ **最终性能未改善**：所有测试结果相同
3. 📊 **预测分析**：预测了 978 个正样本，但只有 31 个是真阳性（947 个假阳性）

## 问题根源

Beer 数据集极度不平衡（68/461335 = 0.015%），对于无监督方法来说，这可能是极限情况。

## 可能的解决方案

### 1. 改进 Blocking（推荐尝试）

当前 `block_beer` 使用 `overlap_size=2`，可以尝试更严格：

```python
# 在 blocking_functions.py 中修改 block_beer 函数
# 将 overlap_size=2 改为 overlap_size=3
```

**注意**：这可能会漏掉更多正样本，但会减少候选对数量，可能提高 Precision。

### 2. 使用更高预测阈值

当前使用 0.5 作为预测阈值，可以尝试：
- 0.7：可能提高 Precision，但降低 Recall
- 0.8：进一步提高 Precision

### 3. 接受现实

Beer 数据集可能不适合无监督方法。论文中可能也没有报告 beer 的结果，或者结果也很低。

## 建议

1. **先尝试更极端参数**：
   ```bash
   python zeroer.py beer --init_threshold 0.95 --c_bay 0.03 --run_transitivity --LR_dup_free --n_jobs 4
   ```

2. **如果仍然无效，考虑改进 blocking**：
   - 修改 `blocking_functions.py` 中的 `block_beer` 函数
   - 将 `overlap_size=2` 改为 `overlap_size=3`
   - 重新生成特征并测试

3. **如果还是无效，可能需要**：
   - 使用半监督方法（少量标注数据）
   - 或者接受这是无监督方法的极限

## 结论

虽然初始化问题已解决，但 beer 数据集的极度不平衡特性使得无监督方法难以达到好的性能。这可能是数据集本身的特性，而不是参数问题。

