import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';

class AllusionSearchScreen extends StatelessWidget {
  const AllusionSearchScreen({super.key});

  static const iconAssetPath = 'assets/images/UI/search_book.svg';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final title = l10n.allusion_search_screen;

    return PlannedFeatureScreen(
      title: title,
      subtitle: l10n.allusion_search_header,
      message: l10n.planned_feature_message(title),
      iconAssetPath: iconAssetPath,
    );
  }
}
