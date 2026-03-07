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
- Deploy on [Snapcraft](https://snapcraft.io/revelation-x/listing) and [GitHub Releases](https://github.com/karnauhov/Revelation/releases). See [commands for deploy](https://dashboard.snapcraft.io/snaps/revelation-x/upload/), then [move release to latest/stable](https://snapcraft.io/revelation-x/releases) and save
- Deploy on [Goole Play](https://play.google.com/console/u/1/developers/8693299089478158768/app/4975644827990074725/tracks/production)
- Deploy on [Microsoft Sore](https://partner.microsoft.com/ru-ru/dashboard/products/9NXHRR2P4087/overview)

# Preparing new databases

- Upload DB file on [supabase](https://supabase.com/dashboard/project/adfdfxnzxmzyoioedwuy/storage/buckets/db)
- Copy DB file to folder web\db\...
- Deploy on [revelation.website](https://github.com/karnauhov/Revelation.website)

# Primary sources maintenance

- Primary sources are now maintained in SQLite, not in ARB files and not in `lib/repositories/primary_sources_repository.dart`
- The content tool is now a package in `scripts/content_tool/`
- Run it with `python -m scripts.content_tool`
- Use the `Первоисточники` section for create/edit/delete operations
- Preview images are stored as `common_resources` records in `revelation.sqlite`
- Localized metadata and localized link titles are stored in `revelation_<lang>.sqlite`
- Page images are expected under `%Documents%/revelation/primary_sources/...` with the same relative path as `page.image`
- Download page images and edit verse contours directly from the content tool package
- After changing primary source DB content, upload the updated DB files to Supabase, copy them into `web/db/`, and deploy the website
