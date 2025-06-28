# Prepare release

- Change version number:
  - [pubspec.yaml (version, msix_version)](./pubspec.yaml),
  - [setup.iss (MyAppVersion, MyAppBuild)](./setup.iss),
  - [revelation.desktop (Version)](/snap/gui/revelation.desktop),
  - [snapcraft.yaml (version)](./snapcraft.yaml)
- Commit for auto build
- Build snap package (snapcraft) and upload it to Assets on [GitHub Releases](https://github.com/karnauhov/Revelation/releases)
