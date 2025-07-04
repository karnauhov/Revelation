# Preparing the release

- Change version number:
  - [pubspec.yaml (version, msix_version)](./pubspec.yaml),
  - [setup.iss (MyAppVersion, MyAppBuild)](./setup.iss),
  - [revelation.desktop (Version)](/snap/gui/revelation.desktop),
  - [snapcraft.yaml (version)](./snapcraft.yaml)
- Fix [Changelog](CHANGELOG.md)
- Build snap package (`snapcraft_build.sh`), install local and check
- Commit for auto build
- Deploy on [revelation.website](https://github.com/karnauhov/Revelation.website)
- Deploy on [Snapcraft](https://snapcraft.io) and [GitHub Releases](https://github.com/karnauhov/Revelation/releases)
- Deploy on [Goole Play](https://play.google.com/console/u/1/developers/8693299089478158768/app/4975644827990074725/tracks/production)
- Deploy on [Microsoft Sore](https://partner.microsoft.com/ru-ru/dashboard/products/9NXHRR2P4087/overview)
