# Исследование Polars LazyFrame

- **Автор:** Захарова Ксения
- **Стек:** аналитика
- **Библиотека:** Polars
- **Версия:** `2.0.0`
- **Тег:** [`py-2.0.0`](https://github.com/pola-rs/polars/tree/py-2.0.0)
- **Commit:** [`22a147de3d2bb2e44b97338a2510816c7105c9f2`](https://github.com/pola-rs/polars/commit/22a147de3d2bb2e44b97338a2510816c7105c9f2)
- **Репозиторий библиотеки:** <https://github.com/pola-rs/polars>
- **Исследуемый механизм:** `LazyFrame`, логический план и pushdown-оптимизации

Polars — библиотека и движок обработки табличных данных. В проекте исследуется
путь ленивого запроса от Python API и `DslPlan` до arena-based IR, проходов
predicate/projection pushdown и выполнения выбранным движком.

## Запуск проекта

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python main.py --engine streaming
```

Запуск тестов:
```bash
pytest -q
```

```bash
python main.py --engine streaming
```

Сравнить движки без изменения запроса:
```bash
python main.py --engine in-memory
```

Изменить проекцию и ключи группировки:
```bash
python main.py --group-by-channel --min-orders 1
```

Выполнить запрос с отключёнными predicate/projection pushdown:
```bash
python main.py --execute-without-pushdowns
```

В выводе оптимизированного плана ожидается:
```text
PROJECT 5/8 COLUMNS
SELECTION: ...
```

Показывают, что scan читает только нужные столбцы и применяет допустимый
предикат на уровне источника. Фильтр по `orders` остаётся после `group_by`, потому
что этот столбец появляется только после агрегации

## Исходный код Polars
- [`LazyFrame` и `collect_with_engine`](https://github.com/pola-rs/polars/blob/py-2.0.0/crates/polars-lazy/src/frame/mod.rs)
- [порядок проходов оптимизатора](https://github.com/pola-rs/polars/blob/py-2.0.0/crates/polars-plan/src/plans/optimizer/mod.rs)
- [predicate pushdown](https://github.com/pola-rs/polars/tree/py-2.0.0/crates/polars-plan/src/plans/optimizer/predicate_pushdown)
- [projection pushdown](https://github.com/pola-rs/polars/tree/py-2.0.0/crates/polars-plan/src/plans/optimizer/projection_pushdown)
- [streaming physical plan](https://github.com/pola-rs/polars/tree/py-2.0.0/crates/polars-stream/src/physical_plan)


## Использование ИИ

ИИ применялся для:

- первичного поиска файлов Polars, связанных с `LazyFrame`, `DslPlan`, IR и
  проходами оптимизатора
- подготовки черновой структуры презентации и формулировок
- создания основы демонстрационного CSV, кода примера и тестов