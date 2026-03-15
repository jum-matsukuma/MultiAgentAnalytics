"""Machine learning utilities module."""

from typing import Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


class SimpleMLModel:
    """A simple machine learning model wrapper using scikit-learn."""

    def __init__(self, n_estimators: int = 100, random_state: Optional[int] = 42):
        """Initialize the model.
        
        Args:
            n_estimators: Number of trees in the random forest
            random_state: Random state for reproducibility
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators, random_state=random_state
        )
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> dict:
        """Train the model and return performance metrics.
        
        Args:
            X: Feature matrix
            y: Target vector
            test_size: Proportion of data to use for testing
            
        Returns:
            Dictionary containing training and test accuracy
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)

        return {
            "train_accuracy": accuracy_score(y_train, train_pred),
            "test_accuracy": accuracy_score(y_test, test_pred),
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions on new data.
        
        Args:
            X: Feature matrix
            
        Returns:
            Predicted class labels
            
        Raises:
            ValueError: If model is not trained
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        return self.model.predict(X)

    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature importance scores.
        
        Returns:
            Feature importance array or None if model not trained
        """
        if not self.is_trained:
            return None

        return self.model.feature_importances_
