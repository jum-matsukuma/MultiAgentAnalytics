"""Tests for data_utils module."""

import numpy as np
import pandas as pd
import pytest

from mytools.data_utils import DataProcessor


class TestDataProcessor:
    """Test cases for DataProcessor class."""

    def test_initialization(self):
        """Test processor initialization."""
        processor = DataProcessor()
        assert processor.is_fitted is False

    def test_load_sample_data(self):
        """Test sample data generation."""
        processor = DataProcessor()
        X, y = processor.load_sample_data()

        assert X.shape == (1000, 4)
        assert y.shape == (1000,)
        assert set(y) == {0, 1}

    def test_preprocess_features_fit(self):
        """Test feature preprocessing with fitting."""
        processor = DataProcessor()
        X = np.random.randn(100, 3)

        X_scaled = processor.preprocess_features(X, fit=True)

        assert X_scaled.shape == X.shape
        assert processor.is_fitted is True
        # Check if standardized (mean ≈ 0, std ≈ 1)
        assert np.allclose(np.mean(X_scaled, axis=0), 0, atol=1e-10)
        assert np.allclose(np.std(X_scaled, axis=0), 1, atol=1e-10)

    def test_preprocess_features_transform_only(self):
        """Test feature preprocessing without fitting."""
        processor = DataProcessor()
        X_train = np.random.randn(100, 3)
        X_test = np.random.randn(50, 3)

        # Fit on training data
        processor.preprocess_features(X_train, fit=True)

        # Transform test data
        X_test_scaled = processor.preprocess_features(X_test, fit=False)

        assert X_test_scaled.shape == X_test.shape

    def test_preprocess_features_not_fitted(self):
        """Test preprocessing fails when not fitted."""
        processor = DataProcessor()
        X = np.random.randn(10, 3)

        with pytest.raises(ValueError, match="Scaler must be fitted"):
            processor.preprocess_features(X, fit=False)

    def test_encode_labels(self):
        """Test label encoding."""
        processor = DataProcessor()
        y = np.array(['cat', 'dog', 'cat', 'bird', 'dog'])

        y_encoded = processor.encode_labels(y, fit=True)

        assert len(y_encoded) == len(y)
        assert set(y_encoded) == {0, 1, 2}  # Three unique labels

    def test_create_dataframe_default_names(self):
        """Test DataFrame creation with default feature names."""
        processor = DataProcessor()
        X = np.random.randn(10, 3)
        y = np.random.randint(0, 2, 10)

        df = processor.create_dataframe(X, y)

        expected_columns = ['feature_0', 'feature_1', 'feature_2', 'target']
        assert df.columns.tolist() == expected_columns
        assert df.shape == (10, 4)

    def test_create_dataframe_custom_names(self):
        """Test DataFrame creation with custom feature names."""
        processor = DataProcessor()
        X = np.random.randn(10, 3)
        y = np.random.randint(0, 2, 10)
        feature_names = ['height', 'weight', 'age']

        df = processor.create_dataframe(X, y, feature_names)

        expected_columns = ['height', 'weight', 'age', 'target']
        assert df.columns.tolist() == expected_columns

    def test_get_data_summary(self):
        """Test data summary generation."""
        processor = DataProcessor()

        # Create sample DataFrame
        data = {
            'feature_1': [1, 2, 3, np.nan],
            'feature_2': [4, 5, 6, 7],
            'target': [0, 1, 0, 1]
        }
        df = pd.DataFrame(data)

        summary = processor.get_data_summary(df)

        assert summary['shape'] == (4, 3)
        assert summary['columns'] == ['feature_1', 'feature_2', 'target']
        assert summary['missing_values']['feature_1'] == 1
        assert summary['missing_values']['feature_2'] == 0
        assert summary['target_distribution'] == {0: 2, 1: 2}

    def test_get_data_summary_no_target(self):
        """Test data summary without target column."""
        processor = DataProcessor()

        data = {'feature_1': [1, 2, 3], 'feature_2': [4, 5, 6]}
        df = pd.DataFrame(data)

        summary = processor.get_data_summary(df)

        assert summary['target_distribution'] is None
