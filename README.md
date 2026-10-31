# Revelation

Revelation is a Flutter app for studying the Book of Revelation.  
Application entry point: `lib/main.dart`.

Use Flutter 3.47.2 (Dart 3.13.2), matching CI. Android builds use Java 17, AGP 9.1.0, Gradle 9.3.1, and Kotlin Gradle Plugin 2.4.0.

## Supported Platforms

- Web: [revelation.website](https://www.revelation.website)
- Android: [Google Play](https://play.google.com/store/apps/details?id=ai11.link.revelation)
- Windows: [Microsoft Store](https://apps.microsoft.com/detail/9NXHRR2P4087), [Latest release assets](https://github.com/karnauhov/Revelation/releases/latest)
- Linux: [Snapcraft](https://snapcraft.io/revelation-x)

## Repository Layout

- `lib/app` - app bootstrap, DI, router, composition root
- `lib/core` - cross-cutting contracts and platform abstractions
- `lib/infra` - database, remote, and storage implementations
- `lib/shared` - reusable UI, shared models, localization and helpers
- `lib/features` - feature-first modules
- `lib/l10n` - ARB files and generated localization code
- `assets/data`, `assets/images`, `assets/sounds` - bundled content and assets
- `web/db` - SQLite files used by the web build
- `scripts` - local maintenance and validation scripts

## Common Commands

- `flutter pub get`
- `dart format .`
- `flutter analyze`
- `flutter test`
- `dart run scripts/check_docs_sync.dart`
- `dart run build_runner build --delete-conflicting-outputs`
- `flutter gen-l10n`

## Documentation

### English

- [Architecture Overview](./docs/en/architecture/overview.en.md)
- [Module Boundaries](./docs/en/architecture/module-boundaries.en.md)
- [State Management Matrix](./docs/en/architecture/state_management_matrix.en.md)
- [Testing Strategy](./docs/en/testing/strategy.en.md)
- [Local release pipeline and canonical packages](./docs/en/release/local-release.en.md)
- [Markdown Extension Guide](./docs/en/content/markdown-extension-guide.en.md)

### Русский

- [Обзор архитектуры](./docs/ru/architecture/overview.ru.md)
- [Границы модулей](./docs/ru/architecture/module-boundaries.ru.md)
- [Матрица управления состоянием](./docs/ru/architecture/state_management_matrix.ru.md)
- [Стратегия тестирования](./docs/ru/testing/strategy.ru.md)
- [Локальный выпуск и единый каталог пакетов](./docs/ru/release/local-release.ru.md)
- [Руководство по расширению Markdown](./docs/ru/content/markdown-extension-guide.ru.md)
- [Дорожная карта модуля RST с номерами Стронга](./docs/ru/content/rst-strongs-module-roadmap.ru.md)
- [Дорожная карта украинского библейского модуля с номерами Стронга](./docs/ru/content/ukrainian-bible-strongs-module-roadmap.ru.md)
- [REV209: базовые показатели использования и гипотезы роста](./docs/ru/analytics/rev209-usage-baseline.ru.md)
- [REV235: материалы кампании украинского чтения и состояние запуска](./docs/ru/analytics/rev235-campaign.ru.md)
- [REV210: первый запуск и восстановление чтения](./docs/ru/testing/rev210-first-reading.ru.md)

### Additional Notes

- [Operational Notes](./DEV_INFO.md)
- [Changelog](./CHANGELOG.md)
- [Android WebView compatibility snapshot](./third_party/flutter_inappwebview_android/README.md)
- [REV142 validation state and review handoff](./.agents/task-state/REV142.md)
- [REV209 verified tracker review state](./.agents/task-state/REV209.md)
- [Privacy Policy](./PRIVACY_POLICY.md)
- [License Notice](./NOTICE)

### Project Task Skills

- [`$revelation-add-task`](./.agents/skills/revelation-add-task/SKILL.md) - add a feature, bug, or note through AI11 MCP with project/version verification, duplicate checks and one checklist.
- [`$revelation-task`](./.agents/skills/revelation-task/SKILL.md) - use AI11 MCP for an exact code, otherwise resume this chat's unfinished task or select READY work by the current plan, dependencies and gates, preserving project priorities.
- [`$revelation-pause`](./.agents/skills/revelation-pause/SKILL.md) - save a resumable handoff, update the current task through AI11 MCP, and propose a commit message only in the chat.
- [`$revelation-release`](./.agents/skills/revelation-release/SKILL.md) - use the shared local coordinator, isolated Windows/Linux jobs and the canonical package catalogue. REV301 rollout gates still apply.

---

<a href="https://www.revelation.website" target="_blank"><img src=".\_art\Sticker.jpg" width="512" height="256" /></a>
