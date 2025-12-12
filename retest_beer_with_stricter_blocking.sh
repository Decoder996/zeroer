#!/bin/bash
# 使用更严格的 blocking (overlap_size=3) 重新测试 beer 数据集

echo "=========================================="
echo "Beer 数据集 - 使用更严格的 Blocking 重新测试"
echo "=========================================="
echo ""
echo "修改内容："
echo "  - Blocking overlap_size: 2 -> 3 (更严格)"
echo "  - 预期：减少候选对数量，可能提高 Precision"
echo "  - 风险：可能漏掉一些正样本（原注释说会漏掉 3 个）"
echo ""

# 删除旧的特征文件
echo "删除旧的特征文件..."
rm -f datasets/beer/candset_features_df.csv
rm -f datasets/beer/candset_features_df_l.csv
rm -f datasets/beer/candset_features_df_r.csv
rm -f datasets/beer/id_tuple_df_l.csv
rm -f datasets/beer/id_tuple_df_r.csv
rm -f datasets/beer/pred.csv
echo "✓ 旧特征文件已删除"
echo ""

# 使用最佳参数重新运行
echo "=========================================="
echo "使用更严格的 blocking 重新运行..."
echo "参数: init_threshold=0.9, c_bay=0.02"
echo "=========================================="
python zeroer.py beer --init_threshold 0.9 --c_bay 0.02 --run_transitivity --LR_dup_free --n_jobs 4

echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo ""
echo "请对比结果："
echo "  1. 候选对数量是否减少？"
echo "  2. Precision 是否提高？"
echo "  3. Recall 是否下降（因为漏掉了一些正样本）？"
echo "  4. F1 是否改善？"
echo ""

