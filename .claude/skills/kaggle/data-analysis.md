# Data Analysis and Preprocessing Skills

Efficient data analysis patterns for machine learning competitions.

## Exploratory Data Analysis Workflow
- **Initial assessment**: Shape, data types, memory usage, basic statistics
- **Target analysis**: Distribution, outliers, class balance, correlation patterns
- **Missing value patterns**: Systematic vs random missingness, correlation with other features
- **Feature relationships**: Correlation matrices, feature-target associations, multicollinearity detection

## Data Quality Assessment
- **Outlier detection**: Z-score, IQR, isolation forest for systematic identification
- **Duplicate analysis**: Exact duplicates, near-duplicates with fuzzy matching
- **Consistency checks**: Value range validation, logical constraints, cross-feature validation
- **Distribution analysis**: Compare train/test distributions, detect dataset shift

## Feature Preprocessing Techniques
- **Numerical features**: Scaling (standard, robust, quantile), transformation (log, Box-Cox), binning
- **Categorical features**: Encoding strategies based on cardinality and relationship to target
- **Text features**: Cleaning, tokenization, vectorization (TF-IDF, embeddings)
- **Datetime features**: Decomposition, cyclical encoding, time-based aggregations

## Advanced Preprocessing Patterns
- **Missing value imputation**: Simple (mean/median), advanced (KNN, iterative), indicator variables
- **Feature scaling**: Choose method based on data distribution and model requirements
- **Dimensionality reduction**: PCA for correlated features, feature selection for high-dimensional data
- **Data balancing**: SMOTE, undersampling, cost-sensitive learning for imbalanced targets

## Validation Data Strategy
- **Split validation**: Maintain temporal order, respect group structure, stratify by target
- **Adversarial validation**: Train classifier to distinguish train from test data
- **Cross-validation design**: Choose strategy based on data structure and business context
- **Holdout management**: Reserve final validation set for unbiased model assessment

## Data Pipeline Design
- **Preprocessing order**: Handle missing values, outliers, then transformations
- **Feature store**: Consistent preprocessing across train/validation/test
- **Pipeline testing**: Validate preprocessing on small samples before full dataset
- **Reproducibility**: Fixed random seeds, version control for preprocessing scripts