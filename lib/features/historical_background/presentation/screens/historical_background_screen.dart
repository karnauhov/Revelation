import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';

class HistoricalBackgroundScreen extends StatelessWidget {
  const HistoricalBackgroundScreen({super.key});

  static const iconAssetPath = 'assets/images/UI/history.svg';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final title = l10n.historical_background_screen;

    return PlannedFeatureScreen(
      title: title,
      subtitle: l10n.historical_background_header,
      message: l10n.planned_feature_message(title),
      iconAssetPath: iconAssetPath,
    );
  }
}
