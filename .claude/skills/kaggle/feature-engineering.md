# Feature Engineering Patterns and Techniques

## Feature Engineering Framework

### Feature Development Lifecycle
1. **Hypothesis Generation**: [based on EDA insights and domain knowledge]
2. **Implementation**: [create and validate new features]
3. **Evaluation**: [assess feature importance and correlation]
4. **Optimization**: [refine feature creation logic]
5. **Integration**: [add to production pipeline]

### Feature Validation Strategy
- **Single Feature Impact**: [test individual feature contribution]
- **Feature Interaction**: [test combinations and interactions]
- **Stability Testing**: [validate across CV folds]
- **Generalization Check**: [ensure performance on holdout set]

## Core Feature Engineering Techniques

### Mathematical Transformations

#### Univariate Transformations
```python
# Power transformations
- log(x + 1)           # log transformation with offset
- sqrt(x)              # square root for right-skewed data
- x^2, x^3             # polynomial features
- 1/x                  # reciprocal transformation
- Box-Cox transform    # optimal power transformation
```

#### Normalization and Scaling
```python
# Scaling approaches
- StandardScaler       # zero mean, unit variance
- MinMaxScaler        # scale to [0,1] range  
- RobustScaler        # median and IQR based
- QuantileTransformer # uniform or normal distribution
- PowerTransformer    # make data more Gaussian
```

### Statistical Aggregations

#### Groupby Features
```python
# Target encoding patterns
- mean encoding by categorical feature
- frequency encoding for categories
- count encoding for groups
- standard deviation by groups
- quantile-based aggregations (25%, 50%, 75%)
```

#### Rolling Window Features (Time Series)
```python
# Time-based aggregations
- rolling mean (window=7, 14, 30 days)
- rolling std (volatility measures)
- rolling min/max (recent extremes)
- exponential weighted mean
- lag features (previous values)
```

### Interaction Features

#### Feature Combinations
```python
# Arithmetic operations
- feature_A + feature_B    # additive interaction
- feature_A * feature_B    # multiplicative interaction  
- feature_A - feature_B    # difference features
- feature_A / feature_B    # ratio features (avoid zero division)
```

#### Conditional Features
```python
# Logic-based features
- np.where(condition, value_if_true, value_if_false)
- categorical interactions (feature_A + '_' + feature_B)
- threshold-based binning
- percentile-based categorization
```

### Categorical Feature Engineering

#### Encoding Strategies
```python
# Basic encoding
- Label Encoding         # for ordinal categories
- One-Hot Encoding      # for nominal categories (low cardinality)
- Binary Encoding       # for high cardinality categories

# Advanced encoding  
- Target Encoding       # mean target by category
- Frequency Encoding    # count of each category
- Weight of Evidence    # log odds ratio encoding
- CatBoost Encoding     # ordered target encoding
```

#### Category Grouping
```python
# Rare category handling
- group rare categories into 'Other'
- similarity-based clustering of categories
- frequency-based binning
- target-based similarity grouping
```

### Domain-Specific Features

#### Text Features (if applicable)
```python
# Basic text features
- text length (character count)
- word count
- sentence count
- average word length

# Advanced text features
- TF-IDF vectorization
- sentiment scores
- readability scores
- named entity counts
```

#### Temporal Features (if applicable)
```python
# Time decomposition
- year, month, day, hour
- day of week, day of year
- is_weekend, is_holiday
- season (spring/summer/fall/winter)

# Cyclical encoding
- sin/cos transformation for cyclical features
- hour_sin, hour_cos for 24-hour cycle
- month_sin, month_cos for annual cycle
```

## Advanced Feature Engineering

### Automated Feature Generation

#### Polynomial Features
```python
from sklearn.preprocessing import PolynomialFeatures
# Generate interaction and polynomial features automatically
- degree=2: all pairwise interactions
- degree=3: three-way interactions (computationally expensive)
- include_bias=False to exclude constant term
```

#### Feature Tools Integration
```python
import featuretools as ft
# Automated feature engineering based on entity relationships
- aggregation primitives (sum, mean, count, etc.)
- transformation primitives (log, sqrt, etc.)
- deep feature synthesis for complex patterns
```

### Dimensionality Reduction Features

#### Principal Components
```python
from sklearn.decomposition import PCA
# Create principal components as new features
- PCA on numerical features
- PCA on encoded categorical features  
- PCA on interaction features
```

#### Clustering Features
```python
from sklearn.cluster import KMeans
# Distance-based features
- distance to cluster centers
- cluster membership as categorical feature
- cluster size as feature
```

### Target-Based Feature Engineering

#### Target Encoding Variants
```python
# Cross-validation target encoding
- mean target by category (with CV to prevent leakage)
- smoothed target encoding (Bayesian approach)
- leave-one-out encoding
- target encoding with noise
```

#### Residual Features
```python
# Model-based features
- residuals from simple model as features
- predictions from different algorithms as features
- feature importance scores as weights
```

## Feature Selection and Optimization

### Feature Importance Methods

#### Model-Based Importance
```python
# Tree-based importance
- feature_importances_ from RandomForest/XGBoost
- permutation importance (more reliable)
- SHAP values for feature attribution

# Linear model importance  
- coefficients from Ridge/Lasso regression
- L1 regularization for feature selection
```

#### Statistical Methods
```python
# Correlation-based selection
- correlation with target variable
- mutual information scores
- chi-square test for categorical features
- ANOVA F-test for numerical features
```

### Feature Selection Strategies

#### Univariate Selection
```python
from sklearn.feature_selection import SelectKBest, f_regression
# Select top k features based on statistical tests
- SelectKBest with f_regression for numerical targets
- SelectKBest with chi2 for categorical targets
```

#### Recursive Feature Elimination
```python
from sklearn.feature_selection import RFE
# Iteratively remove least important features
- RFE with cross-validation
- Recursive elimination with model retraining
```

#### Stability-Based Selection
```python
# Select features stable across CV folds
- features consistently important across folds
- features with low importance variance
- bootstrap-based feature selection
```

## Feature Engineering Best Practices

### Validation and Testing
- **Cross-Validation**: Always validate new features with CV
- **Feature Leakage**: Check for temporal or target leakage
- **Correlation Check**: Remove highly correlated features (>0.95)
- **Missing Value Impact**: Ensure robust handling of missing values

### Performance Considerations
- **Memory Usage**: Monitor memory consumption with large feature sets
- **Computation Time**: Balance feature complexity with training time
- **Feature Storage**: Efficient storage of engineered features
- **Pipeline Integration**: Ensure features work in production pipeline

### Documentation and Tracking
- **Feature Catalog**: Maintain inventory of all features created
- **Creation Logic**: Document feature engineering code and rationale
- **Performance Impact**: Track feature contribution to model performance
- **Version Control**: Track feature engineering pipeline versions

## Competition-Specific Patterns

### High-Performing Features (Update Based on Competition)
- **Feature Type 1**: [description and creation logic]
- **Feature Type 2**: [description and creation logic]  
- **Feature Type 3**: [description and creation logic]

### Failed Experiments
- **Failed Approach 1**: [what didn't work and why]
- **Failed Approach 2**: [lessons learned]
- **Overcomplicated Features**: [features that hurt performance]

### Breakthrough Features
- **Game-Changing Feature**: [feature that significantly improved performance]
- **Unexpected Correlation**: [surprising feature relationships discovered]
- **Domain Insight**: [feature based on problem domain understanding]

## Feature Engineering Pipeline

### Production Pipeline Structure
```python
class FeatureEngineer:
    def __init__(self):
        # Initialize scalers, encoders, etc.
        
    def engineer_features(self, df):
        # Apply all feature engineering steps
        # 1. Clean and preprocess
        # 2. Create derived features
        # 3. Apply transformations
        # 4. Handle missing values
        # 5. Scale/encode features
        return processed_df
```

### Feature Pipeline Stages
1. **Data Cleaning**: Handle missing values, outliers, data types
2. **Basic Features**: Create fundamental derived features
3. **Interaction Features**: Generate feature combinations
4. **Aggregation Features**: Create statistical summaries
5. **Encoding**: Apply categorical and numerical transformations
6. **Selection**: Remove redundant or harmful features
7. **Scaling**: Final scaling for model input

### Pipeline Validation
- **Unit Tests**: Test individual feature creation functions
- **Integration Tests**: Test full pipeline on sample data
- **Performance Tests**: Monitor pipeline execution time
- **Data Quality Tests**: Validate output feature distributions