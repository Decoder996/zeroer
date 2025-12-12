#!/bin/bash
# Beer数据集全面优化测试脚本
# 当前最佳结果: F1=0.07 (使用transitivity)

echo "=========================================="
echo "Beer数据集全面优化测试"
echo "=========================================="
echo ""
echo "当前最佳结果:"
echo "  - F1: 0.07"
echo "  - Precision: 0.04"
echo "  - Recall: 0.45"
echo "  - 配置: init_threshold=0.8, c_bay=0.015, transitivity"
echo ""

# 测试1: 更严格的初始化 + 更强的正则化
echo "=========================================="
echo "测试 1: init_threshold=0.9, c_bay=0.02 (更严格)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.9 --c_bay 0.02 --run_transitivity --LR_dup_free --n_jobs 4 2>&1 | tail -15

echo ""
echo "=========================================="
echo "测试 2: init_threshold=0.95, c_bay=0.025 (最严格)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.95 --c_bay 0.025 --run_transitivity --LR_dup_free --n_jobs 4 2>&1 | tail -15

echo ""
echo "=========================================="
echo "测试 3: init_threshold=0.85, c_bay=0.02 (平衡严格)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.85 --c_bay 0.02 --run_transitivity --LR_dup_free --n_jobs 4 2>&1 | tail -15

echo ""
echo "=========================================="
echo "测试 4: init_threshold=0.7, c_bay=0.01 (论文默认，更宽松初始化)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.7 --c_bay 0.01 --run_transitivity --LR_dup_free --n_jobs 4 2>&1 | tail -15

echo ""
echo "=========================================="
echo "测试 5: init_threshold=0.6, c_bay=0.005 (更宽松初始化 + 弱正则化)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.6 --c_bay 0.005 --run_transitivity --LR_dup_free --n_jobs 4 2>&1 | tail -15

echo ""
echo "=========================================="
echo "测试 6: init_threshold=0.9, c_bay=0.01 (严格初始化 + 论文默认正则化)"
echo "=========================================="
python zeroer.py beer --init_threshold 0.9 --c_bay 0.01 --run_transitivity --LR_dup_free --n_jobs 4 2>&1 | tail -15

echo ""
echo "=========================================="
echo "所有测试完成！"
echo "=========================================="

