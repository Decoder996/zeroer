#!/bin/bash
# Beer 数据集参数优化脚本
# 基于当前结果：F1=0.06, Precision=0.03, Recall=0.79
# 问题：初始化正样本太多（18.55%），Precision 太低

echo "=========================================="
echo "Beer 数据集参数优化测试"
echo "=========================================="
echo ""
echo "当前问题分析："
echo "  - 初始化正样本: 18.55% (太多，实际只有 0.01%)"
echo "  - Precision: 0.03 (太低，假阳性太多)"
echo "  - Recall: 0.79 (较高，找到大部分正样本)"
echo ""
echo "优化策略："
echo "  1. 提高 init_threshold (减少初始正样本)"
echo "  2. 提高 c_bay (更强正则化，减少假阳性)"
echo ""

# 测试不同的参数组合
echo "=========================================="
echo "测试 1: 提高 init_threshold 到 0.8 (代码默认)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.8 --c_bay 0.01 --run_transitivity --LR_dup_free --n_jobs 4

echo ""
echo "=========================================="
echo "测试 2: init_threshold=0.8, c_bay=0.02 (更强正则化)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.8 --c_bay 0.02 --run_transitivity --LR_dup_free --n_jobs 4

echo ""
echo "=========================================="
echo "测试 3: init_threshold=0.9 (更严格初始化)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.9 --c_bay 0.01 --run_transitivity --LR_dup_free --n_jobs 4

echo ""
echo "=========================================="
echo "测试 4: init_threshold=0.9, c_bay=0.02 (最严格)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.9 --c_bay 0.02 --run_transitivity --LR_dup_free --n_jobs 4

echo ""
echo "=========================================="
echo "测试 5: init_threshold=0.85, c_bay=0.015 (平衡)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.85 --c_bay 0.015 --run_transitivity --LR_dup_free --n_jobs 4

echo ""
echo "=========================================="
echo "优化测试完成！"
echo "=========================================="
echo ""
echo "建议："
echo "  1. 查看每个测试的初始化统计（应该 < 5%）"
echo "  2. 选择 Precision 和 F1 最高的组合"
echo "  3. 如果 Precision 仍然很低，考虑："
echo "     - 进一步提高 init_threshold (0.95)"
echo "     - 进一步提高 c_bay (0.03)"
echo ""

