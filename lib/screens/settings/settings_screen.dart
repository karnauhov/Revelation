import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import '../../viewmodels/settings_view_model.dart';
import '../../utils/app_constants.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  @override
  Widget build(BuildContext context) {
    final settingsViewModel = Provider.of<SettingsViewModel>(context);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppLocalizations.of(context)!.settings_screen,
              style: theme.textTheme.headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(
              AppLocalizations.of(context)!.settings_header,
              style: theme.textTheme.labelSmall
                  ?.copyWith(fontWeight: FontWeight.normal),
            ),
          ],
        ),
        foregroundColor: colorScheme.primary,
      ),
      body: ListView(
        children: [
          Card(
            margin: const EdgeInsets.all(8.0),
            color: colorScheme.surfaceContainerHighest,
            child: ListTile(
              title: Text(
                AppLocalizations.of(context)!.language,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.primary,
                ),
              ),
              subtitle: Text(
                AppConstants.languages[
                        settingsViewModel.settings.selectedLanguage] ??
                    "",
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.secondary,
                ),
              ),
              trailing: Icon(
                Icons.arrow_forward_ios,
                color: colorScheme.primary,
              ),
              onTap: () async {
                final selected = await _showLanguageDialog(
                  context,
                  settingsViewModel.settings.selectedLanguage,
                );
                if (selected != null) {
                  settingsViewModel.changeLanguage(selected);
                }
              },
            ),
          )
        ],
      ),
    );
  }

  Future<String?> _showLanguageDialog(
      BuildContext context, String currentLanguage) async {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return showDialog<String>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: colorScheme.surface,
          content: SizedBox(
            width: double.maxFinite,
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: AppConstants.languages.keys.length,
              itemBuilder: (context, index) {
                final languageCode =
                    AppConstants.languages.keys.elementAt(index);
                final languageName = AppConstants.languages[languageCode]!;

                final isSelected = languageCode == currentLanguage;

                return ListTile(
                  title: Text(
                    languageName,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: isSelected
                          ? colorScheme.onPrimaryContainer
                          : colorScheme.primary,
                    ),
                  ),
                  selected: isSelected,
                  selectedTileColor: colorScheme.primaryContainer,
                  onTap: () {
                    Navigator.pop(context, languageCode);
                  },
                );
              },
            ),
          ),
        );
      },
    );
  }
}
