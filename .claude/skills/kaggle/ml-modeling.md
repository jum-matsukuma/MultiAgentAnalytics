# Machine Learning Modeling Skills

Core ML modeling capabilities for competitive data science.

## Algorithm Selection Patterns
- **Tabular data**: LightGBM/XGBoost for structured problems, CatBoost for categorical-heavy datasets
- **High-dimensional**: Ridge/Lasso regression, feature selection before tree models
- **Temporal data**: LSTM/GRU for sequences, lag features for traditional models
- **Mixed data types**: TabNet, entity embeddings for categorical features

## Training Strategies
- **Cross-validation**: StratifiedKFold for classification, GroupKFold for grouped data, TimeSeriesSplit for temporal
- **Early stopping**: Monitor validation loss, prevent overfitting in iterative algorithms
- **Regularization**: L1/L2 for linear models, dropout/batch norm for neural networks
- **Data augmentation**: Noise injection, resampling for robust models

## Hyperparameter Optimization
- **Search strategies**: Random search for exploration, Bayesian optimization for fine-tuning
- **Parameter ranges**: Start with default ranges, expand based on validation performance
- **Budget allocation**: More trials for most important parameters (learning rate, regularization)
- **Multi-objective**: Balance performance, training time, model complexity

## Ensemble Techniques
- **Model diversity**: Different algorithms, feature sets, training samples
- **Combination methods**: Simple averaging, weighted averaging, stacking with meta-learner
- **Weight optimization**: Ridge regression on out-of-fold predictions
- **Validation**: Ensure ensemble improves over individual models

## Performance Debugging
- **Overfitting detection**: Training vs validation curves, learning rate sensitivity
- **Feature importance**: SHAP values, permutation importance, model-specific importance
- **Prediction analysis**: Error distribution, residual patterns, outlier investigation
- **Robustness testing**: Performance on different data subsets, adversarial validation

## Model Interpretation
- **Global explanations**: Feature importance rankings, partial dependence plots
- **Local explanations**: SHAP values for individual predictions, LIME for complex models
- **Model comparison**: Compare decision boundaries, feature usage across different algorithms
- **Business insights**: Translate model findings into actionable domain knowledge