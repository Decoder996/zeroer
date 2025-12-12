# fodors_zagats_test 数据处理问题分析

## 发现的问题

### 1. ❌ ID 映射不一致（关键问题）

**原始数据：**
- fodors ID: 534 - 1066（从 534 开始）
- zagats ID: 1 - 331（从 1 开始）

**测试数据：**
- fodors ID: 0 - 532（从 0 开始重新编号）
- zagats ID: 0 - 330（从 0 开始重新编号）

**问题：**
- 如果 matches 文件中的 ID 是基于原始 ID 的，需要相应调整
- 如果 matches 文件中的 ID 是基于新 ID 的，需要确保映射正确

### 2. ⚠️ 字符串格式问题

**原始格式：**
```
'arnie morton\'s of chicago'
```

**测试格式：**
```
` arnie morton \ 's of chicago '
```

**问题：**
- 使用了反引号而不是单引号
- 转义字符格式不同
- 可能影响特征提取（字符串相似度计算）

### 3. ⚠️ Matches 文件缺失 2 行

- 原始：112 行
- 测试：110 行
- 缺失：2 行

可能原因：
- 去重时丢失
- ID 转换时某些匹配无效

## 修复建议

### 方案 1: 修复 ID 映射

如果原始数据（datasets_raw）中的 ID 是从 0 开始的，但原始 fodors_zagats 中的 ID 是从 534 开始的，说明原始数据经过了 ID 偏移处理。

**修复步骤：**

1. **检查原始 raw 数据的 ID：**
```python
import pandas as pd
raw_fodors = pd.read_csv('datasets_raw/Structured/Fodors-Zagats/tableA.csv')
raw_zagats = pd.read_csv('datasets_raw/Structured/Fodors-Zagats/tableB.csv')
print("Raw fodors ID range:", raw_fodors['id'].min(), "-", raw_fodors['id'].max())
print("Raw zagats ID range:", raw_zagats['id'].min(), "-", raw_zagats['id'].max())
```

2. **如果 raw 数据 ID 从 0 开始，需要调整 matches 文件：**
   - 原始 fodors_zagats 的 fodors ID = raw ID + 534
   - 原始 fodors_zagats 的 zagats ID = raw ID + 0（或 +1）

3. **修复 matches 文件：**
```python
# 如果 raw 数据的 ID 从 0 开始
# 需要将 matches 中的 ID 加上偏移量
matches['fodors_id'] = matches['fodors_id'] + 534  # 或相应的偏移
```

### 方案 2: 修复字符串格式

**问题：** CSV 读取/写入时的转义问题

**修复：**
```python
# 读取时指定正确的引号字符
df = pd.read_csv('file.csv', quotechar="'", escapechar='\\')

# 或者清理字符串
df['name'] = df['name'].str.replace('`', "'").str.strip()
```

### 方案 3: 检查 matches 文件生成

**检查是否所有匹配都被包含：**
```python
# 检查 train/valid/test 中是否有重复
train_matches = train_df[train_df['label'] == 1][['ltable_id', 'rtable_id']]
valid_matches = valid_df[valid_df['label'] == 1][['ltable_id', 'rtable_id']]
test_matches = test_df[test_df['label'] == 1][['ltable_id', 'rtable_id']]

# 合并前检查
all_matches = pd.concat([train_matches, valid_matches, test_matches])
print(f"合并前总数: {len(all_matches)}")
print(f"去重后总数: {len(all_matches.drop_duplicates())}")
```

## 快速验证方法

运行 zeroER 并比较结果：

```bash
# 运行原始数据
python zeroer.py fodors_zagats

# 运行测试数据
python zeroer.py fodors_zagats_test

# 比较 F1 分数
# 如果差异很大，说明数据处理有问题
```

## 建议

1. **先检查原始 raw 数据的 ID 范围**
2. **确保 matches 文件中的 ID 与处理后的表 ID 一致**
3. **修复字符串格式问题**（可能影响特征提取）
4. **检查为什么少了 2 行 matches**

如果这些问题都修复了，`fodors_zagats_test` 应该和 `fodors_zagats` 产生相同的结果。

