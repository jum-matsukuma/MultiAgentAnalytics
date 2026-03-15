# Evaluation Metrics and Validation Strategy

## Competition Metric Understanding

### Primary Evaluation Metric
**Metric**: [e.g., RMSE, AUC-ROC, F1-Score, Log Loss, Custom Metric]
**Formula**: [mathematical definition of the metric]
**Range**: [possible value range]
**Optimization Direction**: [minimize/maximize]

### Metric Properties
- **Sensitivity to Outliers**: [how metric responds to extreme values]
- **Class Balance Sensitivity**: [impact of imbalanced data]
- **Threshold Dependency**: [whether metric requires threshold selection]
- **Differentiability**: [whether metric is differentiable for gradient descent]

### Custom Metric Implementation
```python
def competition_metric(y_true, y_pred):
    """
    Implementation of the competition evaluation metric
    """
    # Example: Custom weighted RMSE
    weights = compute_sample_weights(y_true)
    squared_errors = (y_true - y_pred) ** 2
    weighted_mse = np.average(squared_errors, weights=weights)
    return np.sqrt(weighted_mse)
```

## Validation Strategy

### Cross-Validation Design

#### Standard Approaches
1. **StratifiedKFold** (Classification)
   ```python
   from sklearn.model_selection import StratifiedKFold
   cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
   ```

2. **KFold** (Regression)
   ```python
   from sklearn.model_selection import KFold
   cv = KFold(n_splits=5, shuffle=True, random_state=42)
   ```

3. **TimeSeriesSplit** (Temporal Data)
   ```python
   from sklearn.model_selection import TimeSeriesSplit
   cv = TimeSeriesSplit(n_splits=5)
   ```

4. **GroupKFold** (Grouped Data)
   ```python
   from sklearn.model_selection import GroupKFold
   cv = GroupKFold(n_splits=5)
   ```

#### Competition-Specific CV Strategy
**Chosen Method**: [selected CV approach with justification]
**Rationale**: [why this approach is appropriate for the competition]
**Validation Against LB**: [correlation strategy with leaderboard]

### Holdout Strategy
- **Holdout Size**: [percentage held out for final validation]
- **Selection Method**: [random/stratified/temporal split]
- **Usage**: [final model selection, ensemble weights, submission selection]

### Local Validation Correlation
- **LB Correlation Tracking**: [monitor correlation between CV and LB scores]
- **Target Correlation**: [aim for >0.8 correlation]
- **Troubleshooting**: [steps to take if correlation is low]

## Metric Optimization Strategies

### Direct Optimization
```python
# Example: Optimizing F1 score threshold
from sklearn.metrics import f1_score

def optimize_threshold(y_true, y_pred_proba):
    thresholds = np.linspace(0, 1, 101)
    best_f1 = 0
    best_threshold = 0.5
    
    for threshold in thresholds:
        y_pred = (y_pred_proba >= threshold).astype(int)
        f1 = f1_score(y_true, y_pred)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    
    return best_threshold, best_f1
```

### Multi-Metric Optimization
```python
def multi_metric_evaluation(y_true, y_pred):
    """
    Evaluate model on multiple metrics for comprehensive assessment
    """
    metrics = {
        'primary_metric': competition_metric(y_true, y_pred),
        'mse': mean_squared_error(y_true, y_pred),
        'mae': mean_absolute_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred),
        'correlation': np.corrcoef(y_true, y_pred)[0, 1]
    }
    return metrics
```

### Ensemble Optimization for Metric
```python
def optimize_ensemble_weights(predictions_list, y_true, metric_func):
    """
    Optimize ensemble weights to maximize specific metric
    """
    from scipy.optimize import minimize
    
    def objective(weights):
        weights = weights / np.sum(weights)  # normalize
        ensemble_pred = np.average(predictions_list, weights=weights, axis=0)
        return -metric_func(y_true, ensemble_pred)  # negative for minimization
    
    # Initial equal weights
    n_models = len(predictions_list)
    initial_weights = np.ones(n_models) / n_models
    
    # Optimize
    result = minimize(objective, initial_weights, method='SLSQP',
                     bounds=[(0, 1) for _ in range(n_models)])
    
    optimal_weights = result.x / np.sum(result.x)
    return optimal_weights
```

## Validation Framework Implementation

### CV Training Pipeline
```python
class CVTrainer:
    def __init__(self, cv_strategy, metric_func):
        self.cv_strategy = cv_strategy
        self.metric_func = metric_func
        self.results = []
    
    def train_cv(self, model, X, y, groups=None):
        oof_predictions = np.zeros(len(X))
        cv_scores = []
        
        for fold, (train_idx, val_idx) in enumerate(self.cv_strategy.split(X, y, groups)):
            # Split data
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Train model
            model.fit(X_train, y_train)
            
            # Predict
            val_pred = model.predict(X_val)
            oof_predictions[val_idx] = val_pred
            
            # Calculate fold score
            fold_score = self.metric_func(y_val, val_pred)
            cv_scores.append(fold_score)
            
            print(f"Fold {fold}: {fold_score:.6f}")
        
        # Overall CV score
        overall_score = self.metric_func(y, oof_predictions)
        
        return {
            'cv_scores': cv_scores,
            'mean_cv': np.mean(cv_scores),
            'std_cv': np.std(cv_scores),
            'overall_cv': overall_score,
            'oof_predictions': oof_predictions
        }
```

### Validation Monitoring
```python
class ValidationMonitor:
    def __init__(self):
        self.validation_history = []
        self.lb_correlation_history = []
    
    def log_validation_result(self, cv_score, lb_score=None, model_name=""):
        result = {
            'timestamp': datetime.now(),
            'model_name': model_name,
            'cv_score': cv_score,
            'lb_score': lb_score,
            'correlation': None
        }
        
        if lb_score is not None:
            cv_scores = [r['cv_score'] for r in self.validation_history if r['cv_score'] is not None]
            lb_scores = [r['lb_score'] for r in self.validation_history if r['lb_score'] is not None]
            
            if len(cv_scores) >= 3:  # Need at least 3 points for correlation
                correlation = np.corrcoef(cv_scores, lb_scores)[0, 1]
                result['correlation'] = correlation
                self.lb_correlation_history.append(correlation)
        
        self.validation_history.append(result)
        return result
    
    def get_correlation_trend(self):
        if len(self.lb_correlation_history) < 2:
            return "Insufficient data"
        
        recent_corr = np.mean(self.lb_correlation_history[-3:])
        return f"Recent correlation: {recent_corr:.3f}"
```

## Metric-Specific Strategies

### For Regression Metrics (RMSE, MAE)
- **Outlier Handling**: Robust scaling, outlier clipping
- **Target Transformation**: Log transformation, Box-Cox
- **Loss Function Alignment**: Use same metric as training loss when possible

### For Classification Metrics (AUC, F1, Accuracy)
- **Threshold Optimization**: Find optimal decision threshold
- **Class Balancing**: Handle imbalanced datasets
- **Probability Calibration**: Ensure predicted probabilities are well-calibrated

### For Ranking Metrics (NDCG, MAP)
- **Ranking Feature Engineering**: Features that preserve ranking order
- **LambdaRank Training**: Use ranking-specific loss functions
- **Query-wise Validation**: Validate at query level for ranking problems

## Advanced Validation Techniques

### Adversarial Validation
```python
def adversarial_validation(train_data, test_data):
    """
    Check if train and test distributions are similar
    """
    # Combine data and create labels
    combined_data = pd.concat([
        train_data.assign(is_test=0),
        test_data.assign(is_test=1)
    ]).reset_index(drop=True)
    
    # Train classifier to distinguish train from test
    X = combined_data.drop('is_test', axis=1)
    y = combined_data['is_test']
    
    auc_score = cross_val_score(
        RandomForestClassifier(random_state=42),
        X, y, cv=5, scoring='roc_auc'
    ).mean()
    
    print(f"Adversarial Validation AUC: {auc_score:.4f}")
    print("Interpretation:")
    if auc_score < 0.55:
        print("✓ Train and test distributions are very similar")
    elif auc_score < 0.65:
        print("⚠ Slight distribution difference")
    else:
        print("⚠ Significant distribution difference - check feature engineering")
    
    return auc_score
```

### Time-based Validation (for temporal data)
```python
def time_based_validation(data, time_col, validation_months=2):
    """
    Create time-based validation split
    """
    data_sorted = data.sort_values(time_col)
    
    # Calculate split point
    total_months = (data_sorted[time_col].max() - data_sorted[time_col].min()).days / 30
    split_point = data_sorted[time_col].max() - pd.DateOffset(months=validation_months)
    
    train_data = data_sorted[data_sorted[time_col] <= split_point]
    val_data = data_sorted[data_sorted[time_col] > split_point]
    
    print(f"Train period: {train_data[time_col].min()} to {train_data[time_col].max()}")
    print(f"Validation period: {val_data[time_col].min()} to {val_data[time_col].max()}")
    
    return train_data, val_data
```

## Validation Best Practices

### Data Leakage Prevention
- **Temporal Leakage**: Ensure no future information in features
- **Target Leakage**: Check for features that contain target information
- **Group Leakage**: Properly handle grouped/hierarchical data

### Robust Validation Design
- **Multiple Random Seeds**: Test stability across different CV splits
- **Bootstrap Validation**: Additional confidence intervals
- **Out-of-time Validation**: For temporal data validation

### Validation Debugging
```python
def debug_cv_correlation(cv_scores, lb_scores):
    """
    Debug low correlation between CV and LB scores
    """
    correlation = np.corrcoef(cv_scores, lb_scores)[0, 1]
    
    if correlation < 0.5:
        print("🚨 Low CV-LB correlation detected!")
        print("Potential causes:")
        print("1. Data leakage in CV setup")
        print("2. Different data distributions (train vs test)")
        print("3. Overfitting to CV folds")
        print("4. Incorrect metric implementation")
        print("5. Temporal aspects not captured in CV")
    
    return {
        'correlation': correlation,
        'cv_mean': np.mean(cv_scores),
        'lb_mean': np.mean(lb_scores),
        'cv_std': np.std(cv_scores),
        'lb_std': np.std(lb_scores)
    }
```

## Competition-Specific Validation Results

### Validation Performance Tracking

| Model | CV Score | CV Std | LB Score | Correlation | Notes |
|-------|----------|---------|-----------|-------------|--------|
| Baseline | [score] | [std] | [score] | [corr] | [observations] |
| Model v1 | [score] | [std] | [score] | [corr] | [changes made] |
| Model v2 | [score] | [std] | [score] | [corr] | [improvements] |
| Final Ensemble | [score] | [std] | [score] | [corr] | [final approach] |

### Key Validation Insights
- **Optimal CV Strategy**: [final chosen validation method]
- **Correlation Achievement**: [final CV-LB correlation]
- **Stability Analysis**: [model stability across folds]
- **Metric Optimization**: [threshold/parameter optimization results]