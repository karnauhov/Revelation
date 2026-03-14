# Module Boundaries (RU)

Doc-Version: `1.0.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Определить обязательные границы модулей и правила размещения файлов в `lib/`.

## 2. Canonical Top-Level Structure
- `lib/app` - bootstrap, DI, router, composition root.
- `lib/core` - платформенные и кросс-функциональные контракты (`errors`, `async`, `logging`, `platform`, `audio`, `diagnostics`).
- `lib/infra` - реализации доступа к БД/remote/storage.
- `lib/shared` - переиспользуемый UI и общие модели/утилиты без feature-бизнес-логики.
- `lib/features` - feature-first модули.
- `lib/l10n` - ARB и generated localization-код.

## 3. Feature Module Layout
Для каждого feature используется схема:
- `presentation` - экраны, виджеты, cubit/bloc и UI-coordination.
- `application` - orchestration/use-case/service логика.
- `data` - repositories, data contracts и маппинг.

## 4. Dependency Rules
- `presentation` не импортирует `infra` напрямую.
- `presentation` работает через feature repositories/services/cubit contracts.
- `application` не содержит UI-виджеты.
- `data` может зависеть от `infra` data source/gateway контрактов.
- `infra` не импортирует feature `presentation`.
- `shared` не содержит feature-специфичную orchestration-логику.
- `core` не зависит от feature-модулей.

## 5. File Placement Rules
1. App bootstrap/router/DI -> `lib/app/...`
2. Платформенные и кросс-функциональные контракты -> `lib/core/...`
3. Инфраструктурные реализации -> `lib/infra/...`
4. Переиспользуемый UI и общие модели -> `lib/shared/...`
5. Feature-логика -> `lib/features/<feature>/...`

## 6. Forbidden Paths
В `lib/` не допускается появление каталогов:
- `screens`, `viewmodels`, `repositories`, `services`
- `common_widgets`, `managers`, `controllers`
- `models`, `db`, `utils`

## 7. Enforcement
- Автоматическая проверка архитектурных ограничений: `dart run scripts/check_forbidden_patterns.dart`.
- Запрет `provider`/`ChangeNotifier` контролируется в CI и локальных проверках.
- Перед merge обязательны `flutter analyze` и `flutter test`.
