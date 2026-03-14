import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/theme/material_theme.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/utils/common.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final aud = AudioController();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return BlocBuilder<SettingsCubit, SettingsState>(
      builder: (context, settingsState) {
        final settings = settingsState.settings;
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
                  style: theme.textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.normal,
                  ),
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
                  leading: Icon(Icons.translate, color: colorScheme.primary),
                  title: Text(
                    AppLocalizations.of(context)!.language,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: colorScheme.primary,
                    ),
                  ),
                  subtitle: Text(
                    AppConstants.languages[settings.selectedLanguage] ?? '',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.secondary,
                    ),
                  ),
                  trailing: Icon(
                    Icons.arrow_forward_ios,
                    color: colorScheme.primary,
                  ),
                  onTap: () async {
                    aud.playSound("click");
                    final selected = await _showLanguageDialog(
                      context,
                      settings.selectedLanguage,
                    );
                    if (!context.mounted) {
                      return;
                    }
                    if (selected != null) {
                      unawaited(
                        context.read<SettingsCubit>().changeLanguage(selected),
                      );
                    }
                  },
                ),
              ),
              // Theme Selector
              Card(
                margin: const EdgeInsets.all(8.0),
                color: colorScheme.surfaceContainerHighest,
                child: ListTile(
                  leading: Icon(Icons.color_lens, color: colorScheme.primary),
                  title: Text(
                    AppLocalizations.of(context)!.color_theme,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: colorScheme.primary,
                    ),
                  ),
                  subtitle: Text(
                    locColorThemes(context, settings.selectedTheme),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.secondary,
                    ),
                  ),
                  trailing: Icon(
                    Icons.arrow_forward_ios,
                    color: colorScheme.primary,
                  ),
                  onTap: () async {
                    aud.playSound("click");
                    final selected = await _showThemeDialog(
                      context,
                      settings.selectedTheme,
                    );
                    if (!context.mounted) {
                      return;
                    }
                    if (selected != null) {
                      unawaited(
                        context.read<SettingsCubit>().changeTheme(selected),
                      );
                    }
                  },
                ),
              ),
              // Font Size Selector
              Card(
                margin: const EdgeInsets.all(8.0),
                color: colorScheme.surfaceContainerHighest,
                child: ListTile(
                  leading: Icon(Icons.format_size, color: colorScheme.primary),
                  title: Text(
                    AppLocalizations.of(context)!.font_size,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: colorScheme.primary,
                    ),
                  ),
                  subtitle: Text(
                    locFontSizes(context, settings.selectedFontSize),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.secondary,
                    ),
                  ),
                  trailing: Icon(
                    Icons.arrow_forward_ios,
                    color: colorScheme.primary,
                  ),
                  onTap: () async {
                    aud.playSound("click");
                    final selected = await _showFontSizeDialog(
                      context,
                      settings.selectedFontSize,
                    );
                    if (!context.mounted) {
                      return;
                    }
                    if (selected != null) {
                      unawaited(
                        context.read<SettingsCubit>().changeFontSize(selected),
                      );
                    }
                  },
                ),
              ),
              // Sound Toggle
              Card(
                margin: const EdgeInsets.all(8.0),
                color: colorScheme.surfaceContainerHighest,
                child: ListTile(
                  leading: Icon(
                    settings.soundEnabled ? Icons.volume_up : Icons.volume_off,
                    color: colorScheme.primary,
                  ),
                  title: Text(
                    AppLocalizations.of(context)!.sound,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: colorScheme.primary,
                    ),
                  ),
                  subtitle: Text(
                    settings.soundEnabled
                        ? AppLocalizations.of(context)!.on
                        : AppLocalizations.of(context)!.off,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.secondary,
                    ),
                  ),
                  trailing: Switch(
                    value: settings.soundEnabled,
                    onChanged: (value) {
                      if (!value) {
                        aud.playSound("click");
                      }
                      unawaited(
                        context.read<SettingsCubit>().setSoundEnabled(value),
                      );
                      if (value) {
                        aud.playSound("click");
                      }
                    },
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Future<String?> _showLanguageDialog(
    BuildContext context,
    String currentLanguage,
  ) async {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return showDialog<String>(
      context: context,
      routeSettings: RouteSettings(name: "select_language_dialog"),
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
                return GestureDetector(
                  onTap: () async {
                    aud.playSound("click");
                    Navigator.pop(context, code);
                  },
                  child: MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: Container(
                      margin: EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                      padding: EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: isSelected ? colorScheme.primaryContainer : null,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        name,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: isSelected
                              ? colorScheme.onPrimaryContainer
                              : colorScheme.primary,
                        ),
                      ),
                    ),
                  ),
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
      routeSettings: RouteSettings(name: "select_theme_dialog"),
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
              return GestureDetector(
                onTap: () async {
                  aud.playSound("click");
                  Navigator.pop(context, key);
                },
                child: MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: Container(
                    margin: EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                    padding: EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? itemColorScheme.primaryContainer
                          : null,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      name,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: isSelected
                            ? itemColorScheme.onPrimaryContainer
                            : itemColorScheme.primary,
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }

  Future<String?> _showFontSizeDialog(
    BuildContext context,
    String current,
  ) async {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return showDialog<String>(
      context: context,
      routeSettings: RouteSettings(name: "select_font_size_dialog"),
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
              return GestureDetector(
                onTap: () async {
                  aud.playSound("click");
                  Navigator.pop(context, key);
                },
                child: MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: Container(
                    margin: EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                    padding: EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isSelected ? colorScheme.primaryContainer : null,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      name,
                      style: textTheme.bodyMedium?.copyWith(
                        color: isSelected
                            ? colorScheme.onPrimaryContainer
                            : colorScheme.primary,
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}
