"""Data loading module for edatool. Polars is the primary DataFrame library."""

from __future__ import annotations

from pathlib import Path

import polars as pl


def load(source: str | pl.DataFrame | "pd.DataFrame") -> pl.DataFrame:  # noqa: F821
    """Load data from various sources into a Polars DataFrame.

    Args:
        source: str path (CSV, Parquet, Excel, JSON), pl.DataFrame, or pd.DataFrame

    Returns:
        pl.DataFrame

    Raises:
        ValueError: If the source format is not supported.
        FileNotFoundError: If the file path does not exist.
    """
    if isinstance(source, pl.DataFrame):
        return source

    # pandas DataFrame – import lazily so pandas is optional
    try:
        import pandas as pd  # type: ignore[import]

        if isinstance(source, pd.DataFrame):
            return pl.from_pandas(source)
    except ImportError:
        pass

    if isinstance(source, str):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")

        suffix = path.suffix.lower()
        if suffix == ".csv":
            return pl.read_csv(source)
        elif suffix == ".parquet":
            return pl.read_parquet(source)
        elif suffix in (".xlsx", ".xls"):
            return pl.read_excel(source)
        elif suffix == ".json":
            return pl.read_json(source)
        else:
            raise ValueError(
                f"Unsupported file format '{suffix}'. "
                "Supported formats: .csv, .parquet, .xlsx, .xls, .json"
            )

    raise ValueError(
        f"Unsupported source type '{type(source).__name__}'. "
        "Expected: str path, pl.DataFrame, or pd.DataFrame"
    )
