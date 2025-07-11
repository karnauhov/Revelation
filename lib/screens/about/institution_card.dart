import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../../utils/common.dart';
import '../../models/institution_info.dart';

class InstitutionCard extends StatelessWidget {
  final InstitutionInfo institution;

  const InstitutionCard({super.key, required this.institution});

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
        onTap: () => launchLink(institution.officialSite),
        leading: _buildIcon(
            institution.idIcon, iconWidth, iconHeight, colorScheme.primary),
        title: Text(
          institution.name,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: colorScheme.primary,
          ),
        ),
        subtitle: _buildSourcesText(context),
      ),
    );
  }

  Widget _buildSourcesText(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final List<InlineSpan> children = [];
    final entries = institution.sources.entries.toList();

    for (var i = 0; i < entries.length; i++) {
      final text = entries[i].key;
      final url = entries[i].value.trim();
      if (url.isNotEmpty) {
        children.add(
          TextSpan(
            text: text,
            style: TextStyle(
                color: colorScheme.primary,
                decoration: TextDecoration.underline,
                decorationColor: colorScheme.primary),
            recognizer: TapGestureRecognizer()..onTap = () => launchLink(url),
          ),
        );
      } else {
        children.add(
          TextSpan(
            text: text,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: colorScheme.onSurface,
            ),
          ),
        );
      }

      if (i != entries.length - 1) {
        children.add(
          TextSpan(
            text: ', ',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: colorScheme.onSurface,
            ),
          ),
        );
      }
    }

    return RichText(
      text: TextSpan(
        children: children,
        style: theme.textTheme.bodyMedium?.copyWith(
          color: colorScheme.onSurface,
        ),
      ),
    );
  }

  Widget _buildIcon(
      String idIcon, double iconWidth, double iconHeight, Color color) {
    final iconPath = "assets/images/UI/${institution.idIcon}";

    if (idIcon.isNotEmpty && idIcon.toLowerCase().endsWith('.svg')) {
      return SizedBox(
        width: iconWidth,
        height: iconHeight,
        child: SvgPicture.asset(
          iconPath,
          width: iconWidth,
          height: iconHeight,
          placeholderBuilder: (BuildContext context) =>
              const CircularProgressIndicator(),
        ),
      );
    } else if (idIcon.isNotEmpty) {
      return SizedBox(
        width: iconWidth,
        height: iconHeight,
        child: Image.asset(
          iconPath,
          width: iconWidth,
          height: iconHeight,
          fit: BoxFit.contain,
        ),
      );
    } else {
      return SizedBox(
        width: iconWidth,
        height: iconHeight,
        child: SvgPicture.asset(
          "assets/images/UI/institution.svg",
          width: iconWidth,
          height: iconHeight,
          placeholderBuilder: (BuildContext context) =>
              const CircularProgressIndicator(),
          colorFilter: ColorFilter.mode(color, BlendMode.srcIn),
        ),
      );
    }
  }
}
