import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:revelation/l10n/app_localizations.dart';
import '../../utils/common.dart';
import '../../models/library_info.dart';

class LibraryCard extends StatelessWidget {
  final LibraryInfo library;

  const LibraryCard({super.key, required this.library});

  @override
  Widget build(BuildContext context) {
    const iconWidth = 48.0;
    const iconHeight = 48.0;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      color: colorScheme.surfaceContainer,
      child: ListTile(
        visualDensity: VisualDensity.compact,
        minTileHeight: 0,
        onTap: () => launchLink(library.officialSite),
        leading: SizedBox(
          width: iconWidth,
          height: iconHeight,
          child: _buildIcon(colorScheme, iconWidth, iconHeight),
        ),
        title: Text(
          _getLocalizedName(context, library.name),
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: colorScheme.primary,
          ),
        ),
        subtitle: GestureDetector(
          onTap: () => launchLink(library.licenseLink),
          child: Text(
            "${AppLocalizations.of(context)!.license} (${library.license})",
            style: TextStyle(
              color: colorScheme.primary,
              decoration: TextDecoration.underline,
              decorationColor: colorScheme.primary,
            ),
          ),
        ),
      ),
    );
  }

  String _getLocalizedName(BuildContext context, String name) {
    final loc = AppLocalizations.of(context)!;
    return name
        .replaceAll('@Package', loc.package)
        .replaceAll('@Font', loc.font)
        .replaceAll('@Sound', loc.sound);
  }

  Widget _buildIcon(ColorScheme colorScheme, double width, double height) {
    if (library.idIcon.isEmpty) {
      return SvgPicture.asset(
        'assets/images/UI/code.svg',
        width: width,
        height: height,
        placeholderBuilder: (BuildContext context) =>
            const CircularProgressIndicator(),
        colorFilter: ColorFilter.mode(
          colorScheme.primary,
          BlendMode.srcIn,
        ),
      );
    }

    final assetPath = 'assets/images/UI/${library.idIcon}.svg';
    placeholder(BuildContext context) => const CircularProgressIndicator();

    if (library.idIcon.startsWith('lib')) {
      return SvgPicture.asset(
        assetPath,
        width: width,
        height: height,
        placeholderBuilder: placeholder,
      );
    }

    return SvgPicture.asset(
      assetPath,
      width: width,
      height: height,
      placeholderBuilder: placeholder,
      colorFilter: ColorFilter.mode(
        colorScheme.primary,
        BlendMode.srcIn,
      ),
    );
  }
}
