# Revelation

Revelation is a Flutter app for studying the Book of Revelation.  
Application entry point: `lib/main.dart`.

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

### Русский

- [Обзор архитектуры](./docs/ru/architecture/overview.ru.md)
- [Границы модулей](./docs/ru/architecture/module-boundaries.ru.md)
- [Матрица управления состоянием](./docs/ru/architecture/state_management_matrix.ru.md)
- [Стратегия тестирования](./docs/ru/testing/strategy.ru.md)
- [Бэклог оптимизации производительности](./docs/ru/performance/optimization_backlog.ru.md)
- [Исследование Откр. 1:1-3: этап 1](./docs/ru/studies/revelation-1-1-3-research.ru.md)

### Additional Notes

- [Operational Notes](./DEV_INFO.md)
- [Changelog](./CHANGELOG.md)
- [Privacy Policy](./PRIVACY_POLICY.md)
- [License Notice](./NOTICE)

---

<a href="https://www.revelation.website" target="_blank"><img src=".\_art\Sticker.jpg" width="512" height="256" /></a>
