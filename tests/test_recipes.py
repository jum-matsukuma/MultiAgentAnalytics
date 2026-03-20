"""Tests for the recipes module."""

from __future__ import annotations

import polars as pl
import pytest

from edatool.recipes.ab_test import ABTestRecipe
from edatool.recipes.base import RecipeBase
from edatool.recipes.registry import get_recipe, list_recipes

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def ab_data() -> pl.DataFrame:
    """Sample A/B test data with a continuous metric."""
    import random

    random.seed(42)
    control = [random.gauss(10.0, 2.0) for _ in range(100)]
    treatment = [random.gauss(11.0, 2.0) for _ in range(100)]
    return pl.DataFrame(
        {
            "group": ["control"] * 100 + ["treatment"] * 100,
            "revenue": control + treatment,
        }
    )


@pytest.fixture()
def ab_binary_data() -> pl.DataFrame:
    """Sample A/B test data with a binary metric."""
    import random

    random.seed(42)
    control = [1 if random.random() < 0.10 else 0 for _ in range(200)]
    treatment = [1 if random.random() < 0.15 else 0 for _ in range(200)]
    return pl.DataFrame(
        {
            "variant": ["A"] * 200 + ["B"] * 200,
            "converted": control + treatment,
        }
    )


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestRegistry:
    def test_list_recipes_returns_ab_test(self) -> None:
        recipes = list_recipes()
        names = [r.name for r in recipes]
        assert "ab-test" in names

    def test_get_recipe_existing(self) -> None:
        recipe = get_recipe("ab-test")
        assert recipe is not None
        assert isinstance(recipe, ABTestRecipe)

    def test_get_recipe_missing(self) -> None:
        assert get_recipe("nonexistent") is None


# ---------------------------------------------------------------------------
# ABTestRecipe validation tests
# ---------------------------------------------------------------------------


class TestABTestValidation:
    def test_valid_data(self, ab_data: pl.DataFrame) -> None:
        recipe = ABTestRecipe()
        result = recipe.validate(
            ab_data,
            group="group",
            metric="revenue",
            control="control",
            treatment="treatment",
        )
        assert result.valid
        assert len(result.errors) == 0

    def test_missing_column(self, ab_data: pl.DataFrame) -> None:
        recipe = ABTestRecipe()
        result = recipe.validate(
            ab_data,
            group="nonexistent",
            metric="revenue",
            control="control",
            treatment="treatment",
        )
        assert not result.valid
        assert any("not found" in e for e in result.errors)

    def test_missing_group_value(self, ab_data: pl.DataFrame) -> None:
        recipe = ABTestRecipe()
        result = recipe.validate(
            ab_data,
            group="group",
            metric="revenue",
            control="control",
            treatment="missing_group",
        )
        assert not result.valid
        assert any("missing_group" in e for e in result.errors)

    def test_missing_required_param(self, ab_data: pl.DataFrame) -> None:
        recipe = ABTestRecipe()
        result = recipe.validate(
            ab_data,
            group="",
            metric="revenue",
            control="control",
            treatment="treatment",
        )
        assert not result.valid

    def test_small_sample_warning(self) -> None:
        small_df = pl.DataFrame(
            {
                "group": ["A"] * 10 + ["B"] * 10,
                "value": list(range(20)),
            }
        )
        recipe = ABTestRecipe()
        result = recipe.validate(
            small_df,
            group="group",
            metric="value",
            control="A",
            treatment="B",
        )
        assert result.valid
        assert len(result.warnings) > 0


# ---------------------------------------------------------------------------
# ABTestRecipe run tests
# ---------------------------------------------------------------------------


class TestABTestRun:
    def test_continuous_metric(self, ab_data: pl.DataFrame) -> None:
        recipe = ABTestRecipe()
        result = recipe.run(
            ab_data,
            group="group",
            metric="revenue",
            control="control",
            treatment="treatment",
        )
        assert result.recipe_name == "ab-test"
        assert "A/B Test Summary" in result.sections
        assert "Statistical Test" in result.sections
        assert "Effect Size" in result.sections
        assert "Conclusion" in result.sections

        # Treatment mean should be higher
        stats = result.sections["Group Statistics"]
        assert "treatment" in str(stats)

        # With this seed and effect, should be significant
        test_section = result.sections["Statistical Test"]
        p_str = test_section["p-value"]
        p_value = float(p_str)
        assert p_value < 0.05

    def test_binary_metric(self, ab_binary_data: pl.DataFrame) -> None:
        recipe = ABTestRecipe()
        result = recipe.run(
            ab_binary_data,
            group="variant",
            metric="converted",
            control="A",
            treatment="B",
        )
        assert result.recipe_name == "ab-test"
        summary = result.sections["A/B Test Summary"]
        assert "z-test" in summary["Test"]

    def test_to_markdown(self, ab_data: pl.DataFrame) -> None:
        recipe = ABTestRecipe()
        result = recipe.run(
            ab_data,
            group="group",
            metric="revenue",
            control="control",
            treatment="treatment",
        )
        md = result.to_markdown()
        assert "## A/B Test Summary" in md
        assert "## Conclusion" in md

    def test_to_json(self, ab_data: pl.DataFrame) -> None:
        recipe = ABTestRecipe()
        result = recipe.run(
            ab_data,
            group="group",
            metric="revenue",
            control="control",
            treatment="treatment",
        )
        import json

        data = json.loads(result.to_json())
        assert data["recipe"] == "ab-test"
        assert "sections" in data

    def test_suggested_visualizations(self, ab_data: pl.DataFrame) -> None:
        recipe = ABTestRecipe()
        result = recipe.run(
            ab_data,
            group="group",
            metric="revenue",
            control="control",
            treatment="treatment",
        )
        viz = recipe.suggest_visualizations(result)
        assert len(viz) == 2
        assert viz[0].chart_type == "histogram"
        assert viz[1].chart_type == "bar"

    def test_invalid_data_returns_validation_errors(self) -> None:
        recipe = ABTestRecipe()
        df = pl.DataFrame({"x": [1, 2, 3]})
        result = recipe.run(
            df,
            group="missing",
            metric="x",
            control="A",
            treatment="B",
        )
        assert "Validation Failed" in result.sections


# ---------------------------------------------------------------------------
# RecipeBase interface tests
# ---------------------------------------------------------------------------


class TestRecipeBase:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            RecipeBase()  # type: ignore[abstract]

    def test_ab_test_is_recipe_base(self) -> None:
        recipe = ABTestRecipe()
        assert isinstance(recipe, RecipeBase)

    def test_parameters_defined(self) -> None:
        recipe = ABTestRecipe()
        param_names = [p.name for p in recipe.parameters]
        assert "group" in param_names
        assert "metric" in param_names
        assert "control" in param_names
        assert "treatment" in param_names
