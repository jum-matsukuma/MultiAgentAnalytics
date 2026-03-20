"""A/B test analysis recipe."""

from __future__ import annotations

import math
from typing import Any

import polars as pl

from edatool.core.dtypes import is_numeric
from edatool.recipes.base import (
    Parameter,
    RecipeBase,
    RecipeResult,
    ValidationResult,
    VizSpec,
)


def _t_test(a: list[float], b: list[float]) -> tuple[float, float]:
    """Two-sample Welch's t-test. Returns (t_statistic, p_value)."""
    n_a, n_b = len(a), len(b)
    mean_a = sum(a) / n_a
    mean_b = sum(b) / n_b
    var_a = sum((x - mean_a) ** 2 for x in a) / (n_a - 1) if n_a > 1 else 0.0
    var_b = sum((x - mean_b) ** 2 for x in b) / (n_b - 1) if n_b > 1 else 0.0

    se_sq = var_a / n_a + var_b / n_b
    se = math.sqrt(se_sq) if se_sq > 0 else 0.0
    if se == 0:
        return 0.0, 1.0

    t_stat = (mean_a - mean_b) / se

    # Welch-Satterthwaite degrees of freedom
    num = (var_a / n_a + var_b / n_b) ** 2
    denom_a = (var_a / n_a) ** 2 / (n_a - 1) if n_a > 1 else 0.0
    denom_b = (var_b / n_b) ** 2 / (n_b - 1) if n_b > 1 else 0.0
    denom = denom_a + denom_b
    df = num / denom if denom > 0 else max(n_a, n_b) - 1

    p_value = _t_to_p(abs(t_stat), df)
    return t_stat, p_value


def _t_to_p(t: float, df: float) -> float:
    """Approximate two-tailed p-value from t-distribution."""
    if df <= 0:
        return 1.0
    # For df > 30, use normal approximation; otherwise use a rough beta approx
    if df > 30:
        # Normal approximation
        z = t
        p = 2.0 * _normal_sf(z)
        return min(p, 1.0)
    # Rough approximation using the incomplete beta function relationship
    x = df / (df + t * t)
    p = _regularized_incomplete_beta(df / 2.0, 0.5, x)
    return min(p, 1.0)


def _normal_sf(z: float) -> float:
    """Survival function of standard normal (1 - CDF)."""
    if z < 0:
        return 1.0 - _normal_sf(-z)
    # Rational approximation (Abramowitz & Stegun 26.2.17)
    b0 = 0.2316419
    b1 = 0.319381530
    b2 = -0.356563782
    b3 = 1.781477937
    b4 = -1.821255978
    b5 = 1.330274429
    t = 1.0 / (1.0 + b0 * z)
    phi = math.exp(-z * z / 2.0) / math.sqrt(2.0 * math.pi)
    return phi * t * (b1 + t * (b2 + t * (b3 + t * (b4 + t * b5))))


def _regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta function via continued fraction (Lentz's method)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0

    # Use the front factor
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1 - x)) / a

    # Continued fraction (Lentz's method)
    f = 1.0
    c = 1.0
    d = 1.0 - (a + b) * x / (a + 1)
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    f = d

    for m in range(1, 201):
        # Even step
        numerator = m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m))
        d = 1.0 + numerator * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        c = 1.0 + numerator / c
        if abs(c) < 1e-30:
            c = 1e-30
        f *= c * d

        # Odd step
        numerator = -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + numerator * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        c = 1.0 + numerator / c
        if abs(c) < 1e-30:
            c = 1e-30
        delta = c * d
        f *= delta

        if abs(delta - 1.0) < 1e-10:
            break

    return front * f


def _proportion_z_test(
    successes_a: int, n_a: int, successes_b: int, n_b: int
) -> tuple[float, float]:
    """Two-proportion z-test. Returns (z_statistic, p_value)."""
    p_a = successes_a / n_a if n_a > 0 else 0.0
    p_b = successes_b / n_b if n_b > 0 else 0.0
    p_pool = (successes_a + successes_b) / (n_a + n_b) if (n_a + n_b) > 0 else 0.0

    can_compute = n_a > 0 and n_b > 0 and 0 < p_pool < 1
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b)) if can_compute else 0.0
    if se == 0:
        return 0.0, 1.0

    z = (p_a - p_b) / se
    p_value = 2.0 * _normal_sf(abs(z))
    return z, min(p_value, 1.0)


def _cohens_d(a: list[float], b: list[float]) -> float:
    """Cohen's d effect size for two groups."""
    n_a, n_b = len(a), len(b)
    if n_a < 2 or n_b < 2:
        return 0.0
    mean_a = sum(a) / n_a
    mean_b = sum(b) / n_b
    var_a = sum((x - mean_a) ** 2 for x in a) / (n_a - 1)
    var_b = sum((x - mean_b) ** 2 for x in b) / (n_b - 1)
    pooled_std = math.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
    if pooled_std == 0:
        return 0.0
    return (mean_a - mean_b) / pooled_std


def _confidence_interval(
    a: list[float], b: list[float], confidence: float = 0.95
) -> tuple[float, float, float]:
    """Confidence interval for the difference in means. Returns (diff, lower, upper)."""
    n_a, n_b = len(a), len(b)
    mean_a = sum(a) / n_a
    mean_b = sum(b) / n_b
    diff = mean_a - mean_b

    var_a = sum((x - mean_a) ** 2 for x in a) / (n_a - 1) if n_a > 1 else 0.0
    var_b = sum((x - mean_b) ** 2 for x in b) / (n_b - 1) if n_b > 1 else 0.0
    se = math.sqrt(var_a / n_a + var_b / n_b)

    # z-critical for common confidence levels
    z_map = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z_crit = z_map.get(confidence, 1.96)

    margin = z_crit * se
    return diff, diff - margin, diff + margin


def _effect_size_label(d: float) -> str:
    """Interpret Cohen's d."""
    ad = abs(d)
    if ad < 0.2:
        return "negligible"
    elif ad < 0.5:
        return "small"
    elif ad < 0.8:
        return "medium"
    else:
        return "large"


class ABTestRecipe(RecipeBase):
    """A/B test analysis: statistical test, effect size, confidence interval."""

    name = "ab-test"
    description = (
        "A/B test analysis with statistical testing, effect size (Cohen's d), "
        "and confidence intervals. Supports both continuous metrics (t-test) "
        "and binary metrics (proportion z-test)."
    )
    parameters = [
        Parameter(
            name="group",
            description="Column that identifies A/B groups",
            type="column",
        ),
        Parameter(
            name="metric",
            description="Column with the metric to compare",
            type="column",
        ),
        Parameter(
            name="control",
            description="Value in group column representing the control group",
            type="string",
        ),
        Parameter(
            name="treatment",
            description="Value in group column representing the treatment group",
            type="string",
        ),
        Parameter(
            name="confidence",
            description="Confidence level for intervals",
            type="float",
            required=False,
            default=0.95,
        ),
        Parameter(
            name="alpha",
            description="Significance level",
            type="float",
            required=False,
            default=0.05,
        ),
    ]

    def validate(self, df: pl.DataFrame, **params: Any) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        group: str = params.get("group", "")
        metric: str = params.get("metric", "")
        control: str = str(params.get("control", ""))
        treatment: str = str(params.get("treatment", ""))

        # Check required params
        if not group:
            errors.append("Parameter 'group' is required")
        if not metric:
            errors.append("Parameter 'metric' is required")
        if not control:
            errors.append("Parameter 'control' is required")
        if not treatment:
            errors.append("Parameter 'treatment' is required")

        if errors:
            return ValidationResult(valid=False, errors=errors)

        # Check columns exist
        errors.extend(self._check_columns_exist(df, [group, metric]))
        if errors:
            return ValidationResult(valid=False, errors=errors)

        # Check group values exist
        group_values = df[group].cast(pl.Utf8).unique().to_list()
        if control not in group_values:
            errors.append(
                f"Control value '{control}' not found in column '{group}'. "
                f"Available values: {group_values[:10]}"
            )
        if treatment not in group_values:
            errors.append(
                f"Treatment value '{treatment}' not found in column '{group}'. "
                f"Available values: {group_values[:10]}"
            )

        if errors:
            return ValidationResult(valid=False, errors=errors)

        # Check metric is numeric
        if not is_numeric(df[metric].dtype):
            errors.append(
                f"Metric column '{metric}' must be numeric, got {df[metric].dtype}"
            )

        # Check sample sizes
        control_df = df.filter(pl.col(group).cast(pl.Utf8) == control)
        treatment_df = df.filter(pl.col(group).cast(pl.Utf8) == treatment)

        if control_df.height < 2:
            errors.append(f"Control group has {control_df.height} rows (need >= 2)")
        if treatment_df.height < 2:
            errors.append(f"Treatment group has {treatment_df.height} rows (need >= 2)")

        if control_df.height < 30:
            warnings.append(
                f"Control group has only {control_df.height} rows. "
                "Small samples may produce unreliable results."
            )
        if treatment_df.height < 30:
            warnings.append(
                f"Treatment group has only {treatment_df.height} rows. "
                "Small samples may produce unreliable results."
            )

        return ValidationResult(
            valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def run(self, df: pl.DataFrame, **params: Any) -> RecipeResult:
        validation = self.validate(df, **params)
        if not validation.valid:
            return RecipeResult(
                recipe_name=self.name,
                sections={"Validation Failed": validation.errors},
            )

        group: str = params["group"]
        metric: str = params["metric"]
        control: str = str(params["control"])
        treatment: str = str(params["treatment"])
        confidence: float = params.get("confidence", 0.95)
        alpha: float = params.get("alpha", 0.05)

        control_df = df.filter(pl.col(group).cast(pl.Utf8) == control)
        treatment_df = df.filter(pl.col(group).cast(pl.Utf8) == treatment)

        control_vals = control_df[metric].drop_nulls().to_list()
        treatment_vals = treatment_df[metric].drop_nulls().to_list()

        n_control = len(control_vals)
        n_treatment = len(treatment_vals)
        mean_control = sum(control_vals) / n_control
        mean_treatment = sum(treatment_vals) / n_treatment

        # Detect if binary metric (all values are 0 or 1)
        all_values = set(control_vals + treatment_vals)
        is_binary = all_values <= {0, 1, 0.0, 1.0}

        if is_binary:
            successes_c = sum(1 for v in control_vals if v == 1 or v == 1.0)
            successes_t = sum(1 for v in treatment_vals if v == 1 or v == 1.0)
            test_stat, p_value = _proportion_z_test(
                successes_c, n_control, successes_t, n_treatment
            )
            test_name = "Two-proportion z-test"
        else:
            test_stat, p_value = _t_test(control_vals, treatment_vals)
            test_name = "Welch's t-test"

        effect_d = _cohens_d(control_vals, treatment_vals)
        diff, ci_lower, ci_upper = _confidence_interval(
            control_vals, treatment_vals, confidence
        )

        significant = p_value < alpha

        # Build sections
        sections: dict[str, Any] = {}

        sections["A/B Test Summary"] = {
            "Test": test_name,
            "Control group": f"'{control}' (n={n_control:,})",
            "Treatment group": f"'{treatment}' (n={n_treatment:,})",
            "Metric": metric,
            "Significance level (alpha)": alpha,
        }

        sections["Group Statistics"] = {
            f"Control mean ({control})": f"{mean_control:.4f}",
            f"Treatment mean ({treatment})": f"{mean_treatment:.4f}",
            "Difference (treatment - control)": f"{mean_treatment - mean_control:.4f}",
            "Relative change": (
                f"{(mean_treatment - mean_control) / mean_control * 100:+.2f}%"
                if mean_control != 0
                else "N/A (control mean is 0)"
            ),
        }

        sections["Statistical Test"] = {
            "Test statistic": f"{test_stat:.4f}",
            "p-value": f"{p_value:.6f}",
            "Significant": f"{'Yes' if significant else 'No'} (alpha={alpha})",
        }

        sections["Effect Size"] = {
            "Cohen's d": f"{effect_d:.4f}",
            "Interpretation": _effect_size_label(effect_d),
        }

        ci_pct = int(confidence * 100)
        sections[f"{ci_pct}% Confidence Interval"] = {
            "Difference": f"{diff:.4f}",
            "Lower bound": f"{ci_lower:.4f}",
            "Upper bound": f"{ci_upper:.4f}",
            "Includes zero": "Yes" if ci_lower <= 0 <= ci_upper else "No",
        }

        # Conclusion
        if significant:
            direction = "higher" if mean_treatment > mean_control else "lower"
            conclusion = (
                f"The treatment group ('{treatment}') shows a statistically "
                f"significant {direction} {metric} compared to control "
                f"('{control}') with p={p_value:.4f} and "
                f"{_effect_size_label(effect_d)} effect size "
                f"(d={effect_d:.3f})."
            )
        else:
            conclusion = (
                f"No statistically significant difference was found between "
                f"'{treatment}' and '{control}' for {metric} "
                f"(p={p_value:.4f}, alpha={alpha})."
            )
        sections["Conclusion"] = conclusion

        if validation.warnings:
            sections["Warnings"] = validation.warnings

        # Suggested visualizations
        viz: list[VizSpec] = [
            VizSpec(
                chart_type="histogram",
                params={"column": metric, "group_by": group},
                description=f"Distribution of {metric} by group",
            ),
            VizSpec(
                chart_type="bar",
                params={
                    "x": group,
                    "y": metric,
                    "values": {control: mean_control, treatment: mean_treatment},
                },
                description=f"Mean {metric} by group with error bars",
            ),
        ]

        return RecipeResult(
            recipe_name=self.name,
            sections=sections,
            visualizations=viz,
        )
