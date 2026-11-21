import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_catalog_cubit.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/theme/material_theme.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/localization/localization_utils.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({this.initialSection, super.key});
  final String? initialSection;

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final aud = AudioController();
  final _bibleSettingKey = GlobalKey();
  late final BibleCatalogCubit _catalog = AppDi.createBibleCatalogCubit();

  @override
  void initState() {
    super.initState();
    unawaited(_catalog.load());
    if (widget.initialSection == 'bible') {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        final target = _bibleSettingKey.currentContext;
        if (mounted && target != null) {
          unawaited(Scrollable.ensureVisible(target, alignment: 0.5));
        }
      });
    }
  }

  @override
  void dispose() {
    unawaited(_catalog.close());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return BlocBuilder<SettingsCubit, SettingsState>(
      builder: (context, settingsState) {
        final l10n = AppLocalizations.of(context)!;
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
          body: SingleChildScrollView(
            child: Column(
              children: [
                _SettingsRow(
                  icon: Icons.translate,
                  title: l10n.language,
                  value:
                      AppConstants.languages[settings.selectedLanguage] ?? '',
                  onTap: () async {
                    aud.playSound('click');
                    final selected = await _showLanguageDialog(
                      context,
                      settings.selectedLanguage,
                    );
                    if (context.mounted && selected != null) {
                      unawaited(
                        context.read<SettingsCubit>().changeLanguage(selected),
                      );
                    }
                  },
                ),
                _SettingsRow(
                  icon: Icons.color_lens,
                  title: l10n.color_theme,
                  value: locColorThemes(context, settings.selectedTheme),
                  onTap: () async {
                    aud.playSound('click');
                    final selected = await _showThemeDialog(
                      context,
                      settings.selectedTheme,
                    );
                    if (context.mounted && selected != null) {
                      unawaited(
                        context.read<SettingsCubit>().changeTheme(selected),
                      );
                    }
                  },
                ),
                _SettingsRow(
                  icon: Icons.format_size,
                  title: l10n.font_size,
                  value: locFontSizes(context, settings.selectedFontSize),
                  onTap: () async {
                    aud.playSound('click');
                    final selected = await _showFontSizeDialog(
                      context,
                      settings.selectedFontSize,
                    );
                    if (context.mounted && selected != null) {
                      unawaited(
                        context.read<SettingsCubit>().changeFontSize(selected),
                      );
                    }
                  },
                ),
                _SettingsRow(
                  icon: settings.soundEnabled
                      ? Icons.volume_up
                      : Icons.volume_off,
                  title: l10n.sound,
                  value: settings.soundEnabled ? l10n.on : l10n.off,
                  trailing: Switch(
                    value: settings.soundEnabled,
                    onChanged: (value) {
                      if (!value) aud.playSound('click');
                      unawaited(
                        context.read<SettingsCubit>().setSoundEnabled(value),
                      );
                      if (value) aud.playSound('click');
                    },
                  ),
                ),
                BlocBuilder<BibleCatalogCubit, BibleCatalogState>(
                  bloc: _catalog,
                  builder: (context, catalog) {
                    final chosen = BibleLibraryRepository.selectModule(
                      catalog.modules,
                      settings,
                    );
                    final preference = settings.defaultBibleModule;
                    final value = preference == 'auto'
                        ? [
                            l10n.bible_automatic,
                            if (chosen != null) chosen.displayTitle,
                          ].join(' · ')
                        : catalog.modules
                                  .where(
                                    (module) => module.fileName == preference,
                                  )
                                  .firstOrNull
                                  ?.displayTitle ??
                              preference;
                    return _SettingsRow(
                      key: _bibleSettingKey,
                      tileKey: const Key('default_bible_setting'),
                      icon: Icons.menu_book,
                      title: l10n.bible_default,
                      value: value,
                      onTap: () => _showBibleModuleDialog(context),
                    );
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _showBibleModuleDialog(BuildContext context) async {
    final settingsCubit = context.read<SettingsCubit>();
    final chosen = settingsCubit.state.settings.defaultBibleModule;
    unawaited(_catalog.load());
    final selected = await showDialog<String>(
      context: context,
      routeSettings: const RouteSettings(name: 'default_bible_dialog'),
      builder: (dialogContext) => BlocBuilder<BibleCatalogCubit, BibleCatalogState>(
        bloc: _catalog,
        builder: (context, catalog) {
          final l10n = AppLocalizations.of(context)!;
          final choices = <String, String>{
            'auto': l10n.bible_automatic,
            for (final info in catalog.modules)
              if (info.role != 'original')
                info.fileName:
                    '${info.displayTitle} · ${AppConstants.languages[info.language] ?? info.language}',
          };
          return AlertDialog(
            backgroundColor: Theme.of(context).colorScheme.surface,
            title: Text(l10n.bible_default),
            content: SizedBox(
              width: 420,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (catalog.loading) const LinearProgressIndicator(),
                  if (catalog.failed) Text(l10n.bible_catalog_failed),
                  Flexible(
                    child: ListView(
                      shrinkWrap: true,
                      children: [
                        for (final entry in choices.entries)
                          ListTile(
                            title: Text(entry.value),
                            subtitle: entry.key == 'auto'
                                ? Text(l10n.bible_automatic_hint)
                                : null,
                            selected: chosen == entry.key,
                            trailing: chosen == entry.key
                                ? const Icon(Icons.check)
                                : null,
                            onTap: () =>
                                Navigator.pop(dialogContext, entry.key),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: catalog.loading ? null : () => _catalog.load(),
                child: Text(l10n.bible_catalog_refresh),
              ),
              TextButton(
                onPressed: () => Navigator.pop(dialogContext),
                child: Text(l10n.close),
              ),
            ],
          );
        },
      ),
    );
    if (!context.mounted || selected == null) return;
    await settingsCubit.changeDefaultBibleModule(selected);
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

class _SettingsRow extends StatelessWidget {
  const _SettingsRow({
    required this.icon,
    required this.title,
    required this.value,
    this.onTap,
    this.trailing,
    this.tileKey,
    super.key,
  });

  final IconData icon;
  final String title;
  final String value;
  final VoidCallback? onTap;
  final Widget? trailing;
  final Key? tileKey;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    return Card(
      margin: const EdgeInsets.all(8),
      color: colors.surfaceContainerHighest,
      child: ListTile(
        key: tileKey,
        leading: Icon(icon, color: colors.primary),
        title: Text(
          title,
          style: theme.textTheme.bodyMedium?.copyWith(color: colors.primary),
        ),
        subtitle: Text(
          value,
          style: theme.textTheme.bodySmall?.copyWith(color: colors.secondary),
        ),
        trailing:
            trailing ?? Icon(Icons.arrow_forward_ios, color: colors.primary),
        onTap: onTap,
      ),
    );
  }
}
