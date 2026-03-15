"""Tests for ml_utils module."""

import numpy as np
import pytest
from sklearn.datasets import make_classification

from mytools.ml_utils import SimpleMLModel


class TestSimpleMLModel:
    """Test cases for SimpleMLModel class."""

    def test_initialization(self):
        """Test model initialization."""
        model = SimpleMLModel(n_estimators=50, random_state=123)
        assert model.is_trained is False
        assert model.model.n_estimators == 50
        assert model.model.random_state == 123

    def test_train_with_sample_data(self):
        """Test model training with sample data."""
        # Generate sample data
        X, y = make_classification(
            n_samples=100, n_features=4, n_classes=2, random_state=42
        )

        model = SimpleMLModel(random_state=42)
        metrics = model.train(X, y, test_size=0.3)

        assert model.is_trained is True
        assert "train_accuracy" in metrics
        assert "test_accuracy" in metrics
        assert 0 <= metrics["train_accuracy"] <= 1
        assert 0 <= metrics["test_accuracy"] <= 1

    def test_predict_before_training(self):
        """Test prediction fails before training."""
        model = SimpleMLModel()
        X = np.random.randn(10, 4)

        with pytest.raises(ValueError, match="Model must be trained"):
            model.predict(X)

    def test_predict_after_training(self):
        """Test prediction works after training."""
        X, y = make_classification(
            n_samples=100, n_features=4, n_classes=2, random_state=42
        )

        model = SimpleMLModel(random_state=42)
        model.train(X, y)

        # Test prediction
        predictions = model.predict(X[:10])
        assert len(predictions) == 10
        assert all(pred in [0, 1] for pred in predictions)

    def test_feature_importance_before_training(self):
        """Test feature importance returns None before training."""
        model = SimpleMLModel()
        assert model.get_feature_importance() is None

    def test_feature_importance_after_training(self):
        """Test feature importance works after training."""
        X, y = make_classification(
            n_samples=100, n_features=4, n_classes=2, random_state=42
        )

        model = SimpleMLModel(random_state=42)
        model.train(X, y)

        importance = model.get_feature_importance()
        assert importance is not None
        assert len(importance) == 4
        assert np.sum(importance) == pytest.approx(1.0, rel=1e-10)
