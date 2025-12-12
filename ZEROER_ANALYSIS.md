# ZeroER 实现分析与问题诊断

## ZeroER 核心原理

ZeroER 是一个**无监督**的实体解析方法，使用 EM（Expectation-Maximization）算法，不需要任何标注数据。

### 核心流程

1. **Blocking（分块）**：使用 Magellan 的 OverlapBlocker 生成候选对
2. **特征提取**：使用 Magellan 提取相似度特征
3. **特征过滤**：只保留相似度特征，去除距离特征
4. **初始化**：使用阈值方法初始化正负样本
5. **EM 算法**：使用高斯混合模型迭代优化

### 关键代码位置

- **主入口**：`zeroer.py`
- **特征提取**：`data_loading_helper/feature_extraction.py`
- **EM 模型**：`model.py`
- **工具函数**：`utils.py`

## 可能的问题和解决方案

### 问题 1: 运行速度慢

**原因分析：**
- 候选对数量太多（blocking 太宽松）
- 特征数量太多
- EM 算法每次迭代需要计算协方差矩阵，复杂度 O(n×m²)

**解决方案：**
1. **改进 Blocking**：
   - 增加 `overlap_size` 参数（例如从 1 改为 2 或 3）
   - 使用更严格的 blocking 条件
   - 检查 blocking 函数是否正确

2. **减少特征数量**：
   - 检查 `gather_similarity_features` 是否正确过滤了不需要的特征
   - 考虑使用特征选择

3. **优化参数**：
   - 减少 `max_iter`（默认 40）
   - 如果不需要 transitivity，不要使用 `--run_transitivity`

### 问题 2: F1 分数极低

**原因分析：**
1. **特征提取问题**：
   - 从 deepmatcher 拷贝的代码可能不兼容
   - 特征没有正确归一化
   - 特征值范围不对（应该在 [0,1] 之间）

2. **初始化问题**：
   - 初始化阈值（0.8）可能不适合你的数据集
   - 初始正样本太少或太多

3. **Blocking 问题**：
   - Blocking 太严格，漏掉了太多正样本
   - Blocking 太宽松，引入了太多负样本

4. **特征质量问题**：
   - 特征值不在 [0,1] 范围内
   - 存在 NaN 或无穷大值
   - 特征之间相关性太强

**解决方案：**

#### 1. 检查特征提取

```python
# 在 zeroer.py 中添加调试代码
similarity_features_df = gather_similarity_features(candset_features_df)

# 检查特征范围
print("Feature ranges:")
print(similarity_features_df.min())
print(similarity_features_df.max())

# 检查是否有 NaN
print("NaN counts:", similarity_features_df.isna().sum().sum())

# 检查是否有无穷大
print("Inf counts:", np.isinf(similarity_features_df).sum().sum())
```

#### 2. 调整初始化阈值

在 `model.py` 的 `get_y_init_given_threshold` 函数中，默认阈值是 0.8。如果初始化正样本太少，可以降低阈值：

```python
# 在 utils.py 的 run_zeroer 函数中
y_init = get_y_init_given_threshold(similarity_features_df, threshold=0.6)  # 降低阈值
```

#### 3. 检查 Blocking 质量

```python
# 在 blocking_functions.py 中，确保 blocking 函数正确
# 检查生成的候选对数量是否合理
# 如果候选对太多，增加 overlap_size
# 如果候选对太少，减少 overlap_size
```

#### 4. 特征归一化

ZeroER 假设特征值在 [0,1] 范围内。如果特征值不在这个范围，需要归一化：

```python
# 在 gather_similarity_features 函数后添加
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
similarity_features_df = pd.DataFrame(
    scaler.fit_transform(similarity_features_df),
    columns=similarity_features_df.columns,
    index=similarity_features_df.index
)
```

#### 5. 检查 c_bay 参数

`c_bay` 参数控制协方差矩阵的正则化。默认值是 0.1，但可能需要调整：

```python
# 在 utils.py 中
c_bay = 0.015  # 尝试更小的值，如 0.015（论文中的默认值）
# 或
c_bay = 0.1    # 当前代码中的值
```

## 关键实现细节

### 1. 特征提取

ZeroER 使用 Magellan 提取特征，但只保留**相似度特征**，去除：
- 距离特征：`lev_dist`, `rdf`
- 非归一化特征：`aff`, `sw`, `swn`, `nmw`

**重要**：确保你的特征提取代码正确过滤了这些特征。

### 2. 初始化方法

```python
def get_y_init_given_threshold(similarity_features_df, threshold=0.8):
    x = similarity_features_df.values
    min_max_scaler = MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)  # 归一化到 [0,1]
    scaled_sum = getScaledSum(x_scaled)  # 计算归一化的特征和
    training_labels_ = scaled_sum > threshold  # 阈值判断
    return training_labels_
```

**关键点**：
- 先对每个特征归一化到 [0,1]
- 然后计算归一化的特征和
- 使用阈值判断初始标签

### 3. EM 算法

ZeroER 使用高斯混合模型：
- **E-step**：计算每个样本属于正类（匹配）的概率 P_M
- **M-step**：更新高斯分布的参数（均值、协方差）

**关键参数**：
- `c_bay`：协方差正则化参数（默认 0.1，论文中 0.015）
- `max_iter`：最大迭代次数（默认 40）

## 诊断步骤

### 步骤 1: 运行诊断脚本

```bash
python diagnose_zeroer.py <your_dataset>
```

这会检查：
- 特征文件是否存在
- 特征统计信息
- 是否有 NaN/Inf 值
- 初始化质量
- Blocking 质量

### 步骤 2: 检查特征

```python
import pandas as pd
df = pd.read_csv('datasets/<your_dataset>/candset_features_df.csv', index_col=0)
similarity_df = gather_similarity_features(df)

# 检查特征范围
print(similarity_df.describe())
print("Min:", similarity_df.min().min())
print("Max:", similarity_df.max().max())
```

### 步骤 3: 检查 Blocking

```python
# 检查候选对数量
print(f"Total candidate pairs: {len(candset_df)}")

# 如果有 gold labels，检查正样本比例
if 'gold' in candset_df.columns:
    pos_ratio = candset_df['gold'].sum() / len(candset_df)
    print(f"Positive ratio: {pos_ratio:.4f}")
```

### 步骤 4: 调整参数

根据诊断结果，调整：
1. Blocking 的 `overlap_size`
2. 初始化阈值
3. `c_bay` 参数
4. `max_iter` 参数

## 常见错误

### 错误 1: 特征值不在 [0,1] 范围

**症状**：F1 分数极低，EM 算法不收敛

**解决**：确保特征归一化

### 错误 2: 从 deepmatcher 拷贝的代码不兼容

**症状**：特征提取失败或特征格式不对

**解决**：使用 zeroER 原版的 `magellan_modified_feature_generation.py`

### 错误 3: Blocking 太宽松

**症状**：候选对数量巨大，运行极慢

**解决**：增加 `overlap_size`，使用更严格的 blocking

### 错误 4: 初始化正样本太少

**症状**：EM 算法无法找到正样本

**解决**：降低初始化阈值（从 0.8 降到 0.6 或 0.5）

## 与 DeepMatcher 的区别

1. **特征提取**：
   - ZeroER：使用 Magellan，只保留相似度特征
   - DeepMatcher：使用深度学习特征

2. **模型**：
   - ZeroER：无监督 EM 算法
   - DeepMatcher：有监督深度学习

3. **特征归一化**：
   - ZeroER：假设特征在 [0,1] 范围
   - DeepMatcher：可能有不同的归一化方式

**重要**：不要直接使用 DeepMatcher 的特征提取代码，应该使用 ZeroER 原版的 Magellan 特征提取。

## 调试建议

1. **先用 fodors_zagats 数据集测试**：确保代码能正常运行
2. **逐步调试**：
   - 先检查 blocking 是否正确
   - 再检查特征提取是否正确
   - 最后检查 EM 算法
3. **添加日志**：在关键步骤添加 print 语句
4. **可视化**：可视化特征分布、初始化结果等

## 参考

- ZeroER 论文：https://arxiv.org/abs/1908.06049
- Magellan 文档：https://sites.google.com/site/anhaidgroup/projects/magellan/py_entitymatching

