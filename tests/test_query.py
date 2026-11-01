from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from polars_lazyframe_analysis.data import ensure_demo_csv  # noqa: E402
from polars_lazyframe_analysis.query import build_query, pushdowns_disabled  # noqa: E402


def test_query_result(tmp_path: Path) -> None:
    query = build_query(ensure_demo_csv(tmp_path / "sales.csv"))
    result = query.collect(engine="streaming")

    assert result.sort("manager").to_dict(as_series=False) == {
        "manager": ["Anna", "Boris"],
        "revenue": [317.0, 459.0],
        "orders": [2, 3],
    }


def test_pushdowns_change_scan_node(tmp_path: Path) -> None:
    query = build_query(ensure_demo_csv(tmp_path / "sales.csv"))
    optimized = query.explain(engine="streaming")
    without_pushdowns = query.explain(optimizations=pushdowns_disabled())

    assert "PROJECT 5/8 COLUMNS" in optimized
    assert "SELECTION:" in optimized
    assert "PROJECT */8 COLUMNS" in without_pushdowns


def test_pinned_polars_version() -> None:
    assert pl.__version__ == "2.0.0"


def test_group_by_channel_changes_schema_and_projection(tmp_path: Path) -> None:
    query = build_query(
        ensure_demo_csv(tmp_path / "sales.csv"),
        group_by_channel=True,
        min_orders=1,
    )
    result = query.collect(engine="streaming")
    plan = query.explain(engine="streaming")

    assert result.columns == ["manager", "channel", "revenue", "orders"]
    assert "PROJECT 6/8 COLUMNS" in plan


def test_query_parameters_change_result_without_eager_execution(tmp_path: Path) -> None:
    query = build_query(
        ensure_demo_csv(tmp_path / "sales.csv"),
        region="Ural",
        min_amount=500,
        min_orders=1,
    )

    assert isinstance(query, pl.LazyFrame)
    assert query.collect(engine="streaming").to_dict(as_series=False) == {
        "manager": ["Clara"],
        "revenue": [510.0],
        "orders": [1],
    }
