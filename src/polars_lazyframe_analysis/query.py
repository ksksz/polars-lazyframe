from __future__ import annotations

from pathlib import Path

import polars as pl


def build_query(
    csv_path: Path,
    *,
    region: str = "Siberia",
    min_amount: float = 100.0,
    min_orders: int = 2,
    group_by_channel: bool = False,
) -> pl.LazyFrame:
    """ленивый план без чтения CSV"""
    group_keys = ["manager", "channel"] if group_by_channel else ["manager"]

    return (
        pl.scan_csv(csv_path)
        .filter(
            (pl.col("region") == region)
            & (pl.col("status") == "paid")
            & (pl.col("amount") >= min_amount)
        )
        .with_columns(
            (pl.col("amount") * (1 - pl.col("discount"))).alias("net_amount")
        )
        .group_by(group_keys)
        .agg(
            pl.col("net_amount").sum().round(2).alias("revenue"),
            pl.len().alias("orders"),
        )
        .filter(pl.col("orders") >= min_orders)
        .sort("revenue", descending=True)
    )


def pushdowns_disabled() -> pl.QueryOptFlags:
    """отключить predicate и projection pushdown"""
    return pl.QueryOptFlags(
        predicate_pushdown=False,
        projection_pushdown=False,
    )
