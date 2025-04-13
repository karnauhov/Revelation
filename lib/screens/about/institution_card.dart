import 'package:flutter/material.dart';
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

    return Card(
      margin: EdgeInsets.symmetric(vertical: 4),
      color: Theme.of(context).colorScheme.surfaceContainer,
      child: ListTile(
        visualDensity: VisualDensity.compact,
        minTileHeight: 0,
        onTap: () => launchLink(institution.officialSite),
        leading: _buildIcon(institution.idIcon, iconWidth, iconHeight),
        title: Text(
          institution.name,
          style: Theme.of(context)
              .textTheme
              .titleMedium
              ?.copyWith(fontWeight: FontWeight.bold),
        ),
        subtitle: GestureDetector(
          onTap: () => launchLink(institution.primarySourceLink),
          child: Text(
            institution.primarySource,
            style: TextStyle(
              color: Theme.of(context).colorScheme.primary,
              decoration: TextDecoration.underline,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildIcon(String idIcon, double iconWidth, double iconHeight) {
    if (idIcon.isNotEmpty && idIcon.toLowerCase().endsWith('.svg')) {
      return SizedBox(
        width: iconWidth,
        height: iconHeight,
        child: SvgPicture.asset(
          "assets/images/UI/${institution.idIcon}",
          width: iconWidth,
          height: iconHeight,
          placeholderBuilder: (BuildContext context) =>
              CircularProgressIndicator(),
        ),
      );
    } else if (idIcon.isNotEmpty) {
      return SizedBox(
        width: iconWidth,
        height: iconHeight,
        child: Image.asset(
          "assets/images/UI/${institution.idIcon}",
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
              CircularProgressIndicator(),
        ),
      );
    }
  }
}
