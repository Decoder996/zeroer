#!/bin/bash
# Monitor Walmart-Amazon Dirty dataset run progress

echo "=== Walmart-Amazon Dirty 运行监控 ==="
echo ""

# Check if process is running
if pgrep -f "zeroer.py.*walmart_amazon_dirty" > /dev/null; then
    echo "✓ 程序正在运行"
    PID=$(pgrep -f "zeroer.py.*walmart_amazon_dirty" | head -1)
    echo "  进程ID: $PID"
    ps -p $PID -o etime,pcpu,pmem --no-headers 2>/dev/null | awk '{print "  运行时间:", $1, "CPU:", $2"%", "内存:", $3"%"}'
else
    echo "✗ 程序未运行"
    exit 1
fi

echo ""
echo "=== 文件状态 ==="

# Check feature files
if [ -f "datasets/walmart_amazon_dirty/candset_features_df.csv" ]; then
    SIZE=$(du -h datasets/walmart_amazon_dirty/candset_features_df.csv | cut -f1)
    LINES=$(wc -l < datasets/walmart_amazon_dirty/candset_features_df.csv 2>/dev/null || echo "0")
    echo "✓ 主特征文件已生成: $SIZE ($LINES 行)"
else
    echo "✗ 主特征文件未生成（正在生成中...）"
fi

if [ -f "datasets/walmart_amazon_dirty/pred.csv" ]; then
    SIZE=$(du -h datasets/walmart_amazon_dirty/pred.csv | cut -f1)
    echo "✓ 预测文件已生成: $SIZE"
else
    echo "✗ 预测文件未生成"
fi

echo ""
echo "=== 日志文件 ==="
if [ -f "walmart_amazon_dirty_trans.log" ]; then
    LINES=$(wc -l < walmart_amazon_dirty_trans.log 2>/dev/null || echo "0")
    if [ "$LINES" -gt 0 ]; then
        echo "日志行数: $LINES"
        echo "最后几行:"
        tail -5 walmart_amazon_dirty_trans.log
    else
        echo "日志文件为空（程序可能还在初始化）"
    fi
else
    echo "日志文件不存在"
fi

