import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/theme.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/utils/app_constants.dart';
import 'package:revelation/viewmodels/settings_view_model.dart';

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
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                height: 0.9,
              ),
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
          // Language Selector
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
                    '',
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
          ),
          // Theme Selector
          Card(
            margin: const EdgeInsets.all(8.0),
            color: colorScheme.surfaceContainerHighest,
            child: ListTile(
              title: Text(
                AppLocalizations.of(context)!.color_theme,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.primary,
                ),
              ),
              subtitle: Text(
                locColorThemes(
                    context, settingsViewModel.settings.selectedTheme),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.secondary,
                ),
              ),
              trailing: Icon(
                Icons.arrow_forward_ios,
                color: colorScheme.primary,
              ),
              onTap: () async {
                final selected = await _showThemeDialog(
                  context,
                  settingsViewModel.settings.selectedTheme,
                );
                if (selected != null) {
                  settingsViewModel.changeTheme(selected);
                }
              },
            ),
          ),
          // Font Size Selector
          Card(
            margin: const EdgeInsets.all(8.0),
            color: colorScheme.surfaceContainerHighest,
            child: ListTile(
              title: Text(
                AppLocalizations.of(context)!.font_size,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.primary,
                ),
              ),
              subtitle: Text(
                locFontSizes(
                    context, settingsViewModel.settings.selectedFontSize),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.secondary,
                ),
              ),
              trailing: Icon(
                Icons.arrow_forward_ios,
                color: colorScheme.primary,
              ),
              onTap: () async {
                final selected = await _showFontSizeDialog(
                  context,
                  settingsViewModel.settings.selectedFontSize,
                );
                if (selected != null) {
                  settingsViewModel.changeFontSize(selected);
                }
              },
            ),
          ),
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
                final code = AppConstants.languages.keys.elementAt(index);
                final name = AppConstants.languages[code]!;
                final isSelected = code == currentLanguage;
                return ListTile(
                  title: Text(
                    name,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: isSelected
                          ? colorScheme.onPrimaryContainer
                          : colorScheme.primary,
                    ),
                  ),
                  selected: isSelected,
                  selectedTileColor: colorScheme.primaryContainer,
                  onTap: () => Navigator.pop(context, code),
                );
              },
            ),
          ),
        );
      },
    );
  }

  Future<String?> _showThemeDialog(BuildContext context, String current) async {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return showDialog<String>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: colorScheme.surface,
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: AppConstants.themes.keys.length,
            itemBuilder: (ctx, i) {
              final key = AppConstants.themes.keys.elementAt(i);
              final name = locColorThemes(context, key);
              final isSelected = key == current;
              final itemColorScheme = MaterialTheme.getColorTheme(key);
              return ListTile(
                title: Text(
                  name,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: isSelected
                        ? itemColorScheme.onPrimaryContainer
                        : itemColorScheme.primary,
                  ),
                ),
                selected: isSelected,
                selectedTileColor: itemColorScheme.primaryContainer,
                onTap: () => Navigator.pop(context, key),
              );
            },
          ),
        ),
      ),
    );
  }

  Future<String?> _showFontSizeDialog(
      BuildContext context, String current) async {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return showDialog<String>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: colorScheme.surface,
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: AppConstants.fontSizes.keys.length,
            itemBuilder: (ctx, i) {
              final key = AppConstants.fontSizes.keys.elementAt(i);
              final name = locFontSizes(context, key);
              final isSelected = key == current;
              final textTheme = MaterialTheme.getTextTheme(context, key);
              return ListTile(
                title: Text(
                  name,
                  style: textTheme.bodyMedium?.copyWith(
                    color: isSelected
                        ? colorScheme.onPrimaryContainer
                        : colorScheme.primary,
                  ),
                ),
                selected: isSelected,
                selectedTileColor: colorScheme.primaryContainer,
                onTap: () => Navigator.pop(context, key),
              );
            },
          ),
        ),
      ),
    );
  }
}
