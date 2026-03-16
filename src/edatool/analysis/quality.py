"""Data quality check module for edatool."""

from __future__ import annotations

import polars as pl

from edatool.core.types import QualityIssue, QualityReport


def quality_check(
    df: pl.DataFrame,
    high_cardinality_threshold: float = 0.95,
) -> QualityReport:
    """Run data quality checks on a DataFrame.

    Checks performed:
    - Missing values: columns with > 0 nulls.
      Severity: error if null% > 50, warning if > 10, info otherwise.
    - Duplicate rows: count of exactly duplicated rows.
    - Constant columns: columns with only 1 unique value (warning).
    - High cardinality: columns where unique_count / row_count > threshold (info).

    Args:
        df: Input Polars DataFrame.
        high_cardinality_threshold: Ratio above which a column is flagged as
            high-cardinality.  Defaults to 0.95.

    Returns:
        QualityReport containing all detected issues.
    """
    issues: list[QualityIssue] = []
    total_rows = df.height

    # --- Missing values ---
    for col in df.columns:
        null_count = df[col].null_count()
        if null_count > 0:
            null_pct = null_count / total_rows * 100 if total_rows > 0 else 0.0
            if null_pct > 50:
                severity = "error"
            elif null_pct > 10:
                severity = "warning"
            else:
                severity = "info"
            issues.append(
                QualityIssue(
                    category="missing",
                    description=(
                        f"{null_count:,} missing values ({null_pct:.1f}%)"
                    ),
                    severity=severity,
                    column=col,
                    detail={"null_count": null_count, "null_percent": null_pct},
                )
            )

    # --- Duplicate rows ---
    duplicate_count = total_rows - df.unique().height if total_rows > 0 else 0
    if duplicate_count > 0:
        dup_pct = duplicate_count / total_rows * 100
        issues.append(
            QualityIssue(
                category="duplicate",
                description=(
                    f"{duplicate_count:,} duplicate rows ({dup_pct:.1f}%)"
                ),
                severity="warning",
                column=None,
                detail={"duplicate_count": duplicate_count},
            )
        )

    # --- Constant columns and high cardinality ---
    for col in df.columns:
        unique_count = df[col].n_unique()

        if unique_count == 1:
            issues.append(
                QualityIssue(
                    category="constant",
                    description=(
                        f"Column has only 1 unique value"
                    ),
                    severity="warning",
                    column=col,
                    detail={"unique_count": unique_count},
                )
            )
        elif total_rows > 0 and unique_count / total_rows > high_cardinality_threshold:
            issues.append(
                QualityIssue(
                    category="high_cardinality",
                    description=(
                        f"{unique_count:,} unique values "
                        f"({unique_count / total_rows * 100:.1f}% of rows) — "
                        "may be an ID column"
                    ),
                    severity="info",
                    column=col,
                    detail={
                        "unique_count": unique_count,
                        "cardinality_ratio": unique_count / total_rows,
                    },
                )
            )

    return QualityReport(
        issues=issues,
        duplicate_row_count=duplicate_count,
        total_rows=total_rows,
    )
