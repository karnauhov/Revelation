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
        leading: SizedBox(
          width: iconWidth,
          height: iconHeight,
          child: SvgPicture.asset(
            institution.idIcon.isNotEmpty
                ? "assets/images/UI/${institution.idIcon}.svg"
                : 'assets/images/UI/institution.svg',
            width: iconWidth,
            height: iconHeight,
            placeholderBuilder: (BuildContext context) =>
                CircularProgressIndicator(),
          ),
        ),
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
}
