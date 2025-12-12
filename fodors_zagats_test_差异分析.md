# fodors_zagats_test 与 fodors_zagats 差异分析

## 发现的差异

### 1. ❌ 候选对数量差异很大（关键问题）

- **原始**: 2,915 个候选对
- **测试**: 10,734 个候选对
- **差异**: 测试数据多了 **268%**（7,819 个）

**原因分析：**
- 字符串格式不同导致 blocking 行为不同
- 原始数据：`'arnie morton\'s'`（单引号）
- 测试数据：`` ` arnie morton \ 's ' ``（反引号 + 转义）
- 这导致 tokenization 结果不同，blocking 产生了更多候选对

### 2. ⚠️ 特征数量差异

- **原始**: 73 个特征
- **测试**: 69 个特征
- **缺失**: 4 个特征（都是 addr 相关的）：
  - `addr_addr_exm` (exact match)
  - `addr_addr_jar` (jaro)
  - `addr_addr_jwn` (jaro winkler)
  - `addr_addr_lev_sim` (levenshtein similarity)

**原因：**
- 可能是 addr 字段格式问题，导致这些特征无法提取
- 或者 addr 字段有 None/NaN 值

### 3. ⚠️ 正样本数量差异

- **原始**: 112 个正样本
- **测试**: 109 个正样本
- **差异**: 3 个

**原因：**
- Matches 文件：原始 112 行，测试 110 行（差异 2 行）
- 但实际正样本：原始 112，测试 109（差异 3 个）
- 说明有些 matches 在 blocking 时被过滤掉了

### 4. ⚠️ F1 分数差异

- **原始**: F1 = 0.99
- **测试**: F1 = 0.96
- **差异**: 0.03

**原因：**
- 候选对太多（噪声增加）
- 特征缺失（4 个特征）
- 正样本缺失（3 个）

## 根本原因

**字符串格式问题**导致：
1. Blocking 产生更多候选对（噪声增加）
2. 某些特征无法提取（addr 相关特征缺失）
3. 可能影响 matches 的匹配

## 修复建议

### 方案 1: 修复字符串格式（推荐）

在数据处理时，统一字符串格式：

```python
# 在数据处理代码中，清理字符串
def clean_string(s):
    if pd.isna(s):
        return s
    # 移除反引号，统一使用单引号
    s = str(s).replace('`', "'")
    # 清理多余的转义和空格
    s = s.replace(" \\ '", "'")
    s = s.strip()
    return s

# 应用到所有字符串列
for col in ['name', 'addr', 'city', 'phone']:
    df[col] = df[col].apply(clean_string)
```

### 方案 2: 检查 addr 字段

检查 addr 字段是否有 None/NaN，如果有，需要处理：

```python
# 检查并填充
if df['addr'].isna().any():
    df['addr'] = df['addr'].fillna('')
```

### 方案 3: 检查 matches 文件

确保 matches 文件包含所有正样本：

```python
# 检查 matches 文件
matches = pd.read_csv('matches_fodors_zagats.csv')
print(f"Matches: {len(matches)}")
print(f"Unique matches: {len(matches.drop_duplicates())}")

# 确保列名正确
if 'ltable_id' in matches.columns and 'rtable_id' in matches.columns:
    matches = matches.rename(columns={'ltable_id': 'fodors_id', 'rtable_id': 'zagats_id'})
```

## 预期效果

修复后应该：
- ✅ 候选对数量接近 2,915（而不是 10,734）
- ✅ 特征数量接近 73（而不是 69）
- ✅ 正样本数量接近 112（而不是 109）
- ✅ F1 分数接近 0.99（而不是 0.96）

## 快速验证

修复后重新运行：

```bash
# 删除旧的特征文件
rm datasets/fodors_zagats_test/candset_features_df.csv

# 重新运行
python zeroer.py fodors_zagats_test
```

如果修复成功，应该看到：
- 候选对数量：~2,915
- 特征数量：~73
- F1 分数：~0.99

