# Границы модулей (RU)

Doc-Version: `2.1.0`  
Last-Updated: `2026-03-28`  
Source-Commit: `working-tree`

## Назначение

Определить, где должен лежать код и как направлены зависимости между слоями.

## Верхний уровень

- `lib/app` - bootstrap, startup shell, DI, router, верхнеуровневая сборка приложения
- `lib/core` - кросс-функциональные примитивы: ошибки, async guards, logging, audio, platform utilities, diagnostics
- `lib/infra` - реализации доступа к БД, remote и storage
- `lib/shared` - переиспользуемый UI, общие модели, localization helpers и общие утилиты
- `lib/features` - feature-first модули
- `lib/l10n` - ARB-файлы и generated localization-код

## Структура feature-модуля

Если feature нужен внутренний слойный разрез, используется схема:

- `presentation` - `bloc/`, `screens/`, `widgets/`
- `application` - orchestration и use-case сервисы
- `data` - repositories, data models и mapping

Feature может быть легче и не содержать все слои, но направление зависимостей не меняется.

## Правила зависимостей

- `presentation` может зависеть от feature-сервисов, репозиториев и DI-фабрик, но не от низкоуровневых infra manager-классов напрямую.
- `app/startup` может зависеть от app bootstrap/composition-кода и shared localization/theme-примитивов, но не должен переносить feature-специфичное владение state в корневой shell.
- В `presentation/bloc` и `application` не передаётся `BuildContext`.
- `application` не содержит виджеты.
- `data` может использовать infra gateways и storage-реализации.
- `infra` не импортирует feature presentation-код.
- `shared` остаётся переиспользуемым и не хранит feature-специфичную orchestration-логику.
- `core` остаётся feature-agnostic.

## Правила состояния

- Stateful presentation строится только на `Cubit`/`Bloc`.
- Для каждого UI-среза данных есть один source of truth.
- Не добавляются дублирующие cubit-ы и visibility-флаги, если состояние выводится из уже существующих данных.
- Async cubit-ы после `await` защищают применение state через `isClosed` и stale-request protection там, где возможна гонка.

## Базовая проверка

- `dart run scripts/check_forbidden_patterns.dart`
- `flutter analyze`
- `flutter test`
