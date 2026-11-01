from __future__ import annotations

import csv
from pathlib import Path


ROWS = [
    (1, "Siberia", "paid", "Anna", 120.0, 0.10, "web", "2026-01-10"),
    (2, "Siberia", "paid", "Anna", 220.0, 0.05, "store", "2026-01-11"),
    (3, "Siberia", "paid", "Boris", 150.0, 0.00, "web", "2026-01-12"),
    (4, "Siberia", "paid", "Boris", 130.0, 0.10, "partner", "2026-01-13"),
    (5, "Siberia", "cancelled", "Anna", 999.0, 0.00, "web", "2026-01-14"),
    (6, "Ural", "paid", "Clara", 600.0, 0.15, "store", "2026-01-15"),
    (7, "Siberia", "paid", "Dmitry", 80.0, 0.00, "web", "2026-01-16"),
    (8, "Siberia", "paid", "Boris", 240.0, 0.20, "store", "2026-01-17"),
]


def ensure_demo_csv(path: Path, repeats: int = 1) -> Path:
    """CSV с лишними столбцами для демонстрации projection pushdown"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "order_id",
                "region",
                "status",
                "manager",
                "amount",
                "discount",
                "channel",
                "created_at",
            ]
        )
        for repeat in range(repeats):
            for row in ROWS:
                writer.writerow((row[0] + repeat * len(ROWS), *row[1:]))
    return path

