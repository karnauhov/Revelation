# Phase P01 — Coverage Baseline Contract (RU)

Дата фиксации baseline: **March 15, 2026**.

## 1) Зафиксированные baseline-метрики

Источник данных: `coverage/lcov.info`, полученный после `flutter test --coverage`.

- `ALL_LIB`: **1751/10561 = 16.58%**
- `EFFECTIVE_LIB`: **1699/6621 = 25.66%**

## 2) Effective coverage scope (зафиксированный denominator policy)

Из `EFFECTIVE_LIB` исключаются:

1. Generated файлы:
`**/*.g.dart`, `**/*.freezed.dart`.
2. Generated localization:
`lib/l10n/**`.
3. Export-only barrel файлы:
файлы, где все meaningful-строки состоят только из `export ...`.
4. Platform glue shims:
`lib/core/platform/dependent.dart`, `lib/core/platform/file_downloader.dart`, `lib/infra/db/connectors/shared.dart`.

Примечание:
- На момент фиксации baseline категории `barrel` и `platform glue` не дали вклад в denominator из LCOV (0 файлов в отчёте LCOV), но policy зафиксирован заранее для повторяемости.

## 3) Target ladder (этапные цели)

Для `EFFECTIVE_LIB` принимается этапная шкала:

1. `>= 40%`
2. `>= 55%`
3. `>= 70%`
4. `>= 80%`
5. `>= 90%` (целевой уровень)

## 4) Воспроизводимый метод расчёта

Команды:

```bash
flutter test --coverage
dart run scripts/coverage_baseline.dart
```

Скрипт печатает:
- `ALL_LIB` и `EFFECTIVE_LIB`,
- количество исключённых файлов по каждой категории,
- список файлов `lib/**/*.dart`, отсутствующих в LCOV.

## 5) Ограничения baseline

`ALL_LIB` и `EFFECTIVE_LIB` считаются по `coverage/lcov.info`.
Если файл отсутствует в LCOV, скрипт показывает его в отдельном списке `missing in LCOV`, чтобы не терять прозрачность при анализе прогресса покрытия.
