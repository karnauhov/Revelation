import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import '../utils/common.dart';
import '../models/library_info.dart';

class LibraryCard extends StatelessWidget {
  final LibraryInfo library;

  const LibraryCard({super.key, required this.library});

  @override
  Widget build(BuildContext context) {
    const iconWidth = 48.0;
    const iconHeight = 48.0;

    return Card(
      margin: EdgeInsets.symmetric(vertical: 4),
      color: Theme.of(context).colorScheme.surfaceContainer,
      child: ListTile(
        visualDensity: VisualDensity.compact,
        minTileHeight: 0,
        onTap: () => launchLink(library.officialSite),
        leading: SizedBox(
          width: iconWidth,
          height: iconHeight,
          child: SvgPicture.asset(
            library.idIcon.isNotEmpty
                ? "assets/images/UI/${library.idIcon}.svg"
                : 'assets/images/UI/code.svg',
            width: iconWidth,
            height: iconHeight,
            placeholderBuilder: (BuildContext context) =>
                CircularProgressIndicator(),
          ),
        ),
        title: Text(
          library.name,
          style: Theme.of(context)
              .textTheme
              .titleMedium
              ?.copyWith(fontWeight: FontWeight.bold),
        ),
        subtitle: GestureDetector(
          onTap: () => launchLink(library.licenseLink),
          child: Text(
            "${AppLocalizations.of(context)!.license} (${library.license})",
            style: TextStyle(
              color: Theme.of(context).colorScheme.primary,
              decoration: TextDecoration.underline,
            ),
          ),
        ),
      ),
    );
  }
}
