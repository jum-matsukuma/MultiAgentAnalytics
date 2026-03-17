"""Shared Polars dtype utilities for edatool."""

from __future__ import annotations

import polars as pl

NUMERIC_DTYPES = (
    pl.Int8, pl.Int16, pl.Int32, pl.Int64,
    pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    pl.Float32, pl.Float64,
)


def is_numeric(dtype: pl.DataType) -> bool:
    """Check if a Polars dtype is numeric."""
    return isinstance(dtype, NUMERIC_DTYPES)
