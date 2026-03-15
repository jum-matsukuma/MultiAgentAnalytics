"""Data processing utilities module."""

from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler


class DataProcessor:
    """A utility class for common data processing tasks."""

    def __init__(self):
        """Initialize the data processor."""
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_fitted = False

    def load_sample_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate sample classification data.
        
        Returns:
            Tuple of (features, targets)
        """
        np.random.seed(42)
        n_samples, n_features = 1000, 4

        # Generate random features
        X = np.random.randn(n_samples, n_features)

        # Generate targets based on a simple rule
        y = (X[:, 0] + X[:, 1] > 0).astype(int)

        return X, y

    def preprocess_features(
        self,
        X: np.ndarray,
        fit: bool = True
    ) -> np.ndarray:
        """Standardize features using StandardScaler.
        
        Args:
            X: Feature matrix
            fit: Whether to fit the scaler (True for training data)
            
        Returns:
            Standardized feature matrix
        """
        if fit:
            X_scaled = self.scaler.fit_transform(X)
            self.is_fitted = True
        else:
            if not self.is_fitted:
                raise ValueError("Scaler must be fitted before transforming")
            X_scaled = self.scaler.transform(X)

        return X_scaled

    def encode_labels(self, y: np.ndarray, fit: bool = True) -> np.ndarray:
        """Encode categorical labels to integers.
        
        Args:
            y: Label array
            fit: Whether to fit the encoder (True for training data)
            
        Returns:
            Encoded label array
        """
        if fit:
            return self.label_encoder.fit_transform(y)
        else:
            return self.label_encoder.transform(y)

    def create_dataframe(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[list] = None
    ) -> pd.DataFrame:
        """Create a pandas DataFrame from features and targets.
        
        Args:
            X: Feature matrix
            y: Target vector
            feature_names: Optional list of feature names
            
        Returns:
            DataFrame with features and target
        """
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(X.shape[1])]

        df = pd.DataFrame(X, columns=feature_names)
        df["target"] = y

        return df

    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """Get basic statistics about the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with data summary
        """
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.to_dict(),
            "target_distribution": df["target"].value_counts().to_dict()
            if "target" in df.columns else None
        }
