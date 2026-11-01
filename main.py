from __future__ import annotations

import argparse
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from polars_lazyframe_analysis.data import ROWS, ensure_demo_csv  # noqa: E402
from polars_lazyframe_analysis.query import build_query, pushdowns_disabled  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Сравнение наивного и оптимизированного планов Polars LazyFrame"
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=8,
        help="примерное число строк входного CSV (кратно 8)",
    )
    parser.add_argument(
        "--engine",
        choices=("auto", "streaming", "in-memory"),
        default="streaming",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="показать диагностическое логирование движка",
    )
    parser.add_argument("--region", default="Siberia")
    parser.add_argument("--min-amount", type=float, default=100.0)
    parser.add_argument("--min-orders", type=int, default=2)
    parser.add_argument(
        "--group-by-channel",
        action="store_true",
        help="добавить channel в ключ группировки и наблюдать изменение projection pushdown",
    )
    parser.add_argument(
        "--execute-without-pushdowns",
        action="store_true",
        help="выполнить запрос с отключёнными predicate/projection pushdown",
    )
    args = parser.parse_args()

    repeats = max(1, (args.rows + 7) // 8)
    csv_path = ensure_demo_csv(ROOT / "data" / "sales.csv", repeats=repeats)
    query = build_query(
        csv_path,
        region=args.region,
        min_amount=args.min_amount,
        min_orders=args.min_orders,
        group_by_channel=args.group_by_channel,
    )

    if args.verbose:
        pl.Config.set_verbose(True)

    print(f"Polars: {pl.__version__}")
    print(f"Источник: {csv_path} ({len(ROWS) * repeats} строк)")

    print("\n=== 1. Наивный логический план ===")
    print(query.explain(optimized=False))

    print("\n=== 2. План без predicate/projection pushdown ===")
    print(query.explain(optimizations=pushdowns_disabled()))

    print("\n=== 3. Оптимизированный логический план ===")
    print(query.explain(engine=args.engine))

    print("\n=== 4. collect(): оптимизация, физический план, выполнение ===")
    optimizations = (
        pushdowns_disabled() if args.execute_without_pushdowns else pl.QueryOptFlags()
    )
    result = query.collect(engine=args.engine, optimizations=optimizations)
    print(result)

if __name__ == "__main__":
    main()
