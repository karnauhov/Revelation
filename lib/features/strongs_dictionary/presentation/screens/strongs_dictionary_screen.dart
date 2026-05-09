import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';

class StrongsDictionaryScreen extends StatelessWidget {
  const StrongsDictionaryScreen({super.key});

  static const iconAssetPath = 'assets/images/UI/dictionary.svg';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final title = l10n.strongs_dictionary_screen;

    return PlannedFeatureScreen(
      title: title,
      subtitle: l10n.strongs_dictionary_header,
      message: l10n.planned_feature_message(title),
      iconAssetPath: iconAssetPath,
    );
  }
}
