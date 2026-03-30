import 'dart:async';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:revelation/shared/ui/widgets/icon_link_item.dart';
import 'package:get_it/get_it.dart';
import 'package:intl/intl.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/about/presentation/bloc/about_cubit.dart';
import 'package:revelation/features/about/presentation/bloc/about_state.dart';
import 'package:revelation/features/about/presentation/widgets/icon_url.dart';
import 'package:revelation/features/about/presentation/widgets/institution_list.dart';
import 'package:revelation/features/about/presentation/widgets/library_list.dart';
import 'package:revelation/features/about/presentation/widgets/recommended_list.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/connectors/primary_source_file_info.dart';
import 'package:revelation/infra/db/connectors/shared.dart';
import 'package:revelation/infra/db/runtime/runtime_database_version_loader.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_basic_image_builder.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_config.dart';
import 'package:revelation/shared/utils/bug_report_utils.dart';
import 'package:revelation/shared/ui/markdown/markdown_utils.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/shared/ui/widgets/platform_expansion_tile.dart';
import 'package:talker_flutter/talker_flutter.dart';

typedef AboutLinkLauncher = BugReportLinkLauncher;
typedef AboutAppLinkHandler =
    Future<bool> Function(BuildContext context, String? href);
typedef AboutSystemInfoCollector = BugReportSystemInfoCollector;
typedef AboutDatabaseFileSizeLoader = Future<int?> Function(String dbFile);
typedef AboutDatabaseVersionLoader =
    Future<DatabaseVersionInfo?> Function(String dbFile);
typedef AboutPrimarySourceFilesLoader =
    Future<List<PrimarySourceFileInfo>> Function();
typedef AboutClipboardWriter = BugReportClipboardWriter;
typedef AboutCubitBuilder = AboutCubit Function(String initialLanguageCode);

AboutCubit _defaultAboutCubitBuilder(String initialLanguageCode) {
  return AboutCubit(initialLanguageCode: initialLanguageCode);
}

@immutable
class AboutScreenDependencies {
  const AboutScreenDependencies({
    this.launchLink = defaultBugReportLinkLauncher,
    this.appLinkHandler = handleAppLink,
    this.collectSystemAndAppInfo = defaultBugReportSystemInfoCollector,
    this.databaseFileSizeLoader = getLocalDatabaseFileSize,
    this.databaseVersionLoader = getPreferredDatabaseVersionInfo,
    this.primarySourceFilesLoader = getLocalPrimarySourceFilesInfo,
    this.writeClipboardText = defaultBugReportClipboardWriter,
  });

  final AboutLinkLauncher launchLink;
  final AboutAppLinkHandler appLinkHandler;
  final AboutSystemInfoCollector collectSystemAndAppInfo;
  final AboutDatabaseFileSizeLoader databaseFileSizeLoader;
  final AboutDatabaseVersionLoader databaseVersionLoader;
  final AboutPrimarySourceFilesLoader primarySourceFilesLoader;
  final AboutClipboardWriter writeClipboardText;
}

class AboutScreen extends StatefulWidget {
  const AboutScreen({
    super.key,
    AboutScreenDependencies? dependencies,
    this.diagnosticsIoTimeout = const Duration(seconds: 2),
    AboutCubitBuilder? aboutCubitBuilder,
  }) : dependencies = dependencies ?? const AboutScreenDependencies(),
       aboutCubitBuilder = aboutCubitBuilder ?? _defaultAboutCubitBuilder;

  final AboutScreenDependencies dependencies;
  final Duration diagnosticsIoTimeout;
  final AboutCubitBuilder aboutCubitBuilder;

  @override
  State<AboutScreen> createState() => _AboutScreenState();
}

class _AboutScreenState extends State<AboutScreen> {
  final ScrollController _scrollController = ScrollController();
  late final AboutCubit _aboutCubit;
  final aud = AudioController();
  bool _isDragging = false;
  Offset _lastOffset = Offset.zero;

  @override
  void initState() {
    super.initState();
    _aboutCubit = widget.aboutCubitBuilder(
      context.read<SettingsCubit>().state.settings.selectedLanguage,
    );
  }

  @override
  void dispose() {
    _aboutCubit.close();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final currentLocale = context.select(
      (SettingsCubit cubit) => cubit.state.settings.selectedLanguage,
    );
    final appSettings = context.select(
      (SettingsCubit cubit) => cubit.state.settings.toMap(),
    );
    final keepSectionDividersOnWindows =
        !isWeb() && getPlatform() == TargetPlatform.windows;

    return BlocProvider.value(
      value: _aboutCubit,
      child: BlocBuilder<AboutCubit, AboutState>(
        builder: (context, state) {
          if (state.isLoading) {
            return Scaffold(
              body: Center(
                child: CircularProgressIndicator(color: colorScheme.primary),
              ),
            );
          }

          Widget content = SafeArea(
            child: SingleChildScrollView(
              controller: _scrollController,
              padding: const EdgeInsets.fromLTRB(8, 0, 8, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // About the application
                  _buildAppInfo(context, state, currentLocale),
                  const SizedBox(height: 8),
                  Text(
                    AppLocalizations.of(context)!.app_description,
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: colorScheme.onSurface,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Divider(height: 1, color: colorScheme.outlineVariant),
                  // Marketplaces (Web)
                  if (isWeb()) _buildMarketplaces(context),
                  if (isWeb())
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Contacts Links
                  _buildContactsLinks(context),
                  Divider(height: 1, color: colorScheme.outlineVariant),
                  // Legal Links
                  _buildLegalLinks(context, currentLocale),
                  if (keepSectionDividersOnWindows ||
                      !state.isAcknowledgementsExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Acknowledgments
                  _buildAcknowledgements(context, state),
                  if (keepSectionDividersOnWindows ||
                      !state.isRecommendedExpanded ||
                      !state.isAcknowledgementsExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Recommended
                  _buildRecommended(context, state),
                  if (keepSectionDividersOnWindows ||
                      !state.isChangelogExpanded ||
                      !state.isRecommendedExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Changelog
                  _buildChangelog(context, state),
                  if (keepSectionDividersOnWindows ||
                      !state.isChangelogExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Bugs report
                  _buildBugsReport(context, appSettings),
                  Divider(height: 1, color: colorScheme.outlineVariant),
                  // Marketplaces (Desktop & Mobile)
                  if (!isWeb()) _buildMarketplaces(context),
                  if (!isWeb())
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Copyright
                  Center(
                    child: Text(
                      "© ${DateTime.now().year} ${AppConstants.author}. ${AppLocalizations.of(context)!.all_rights_reserved}.",
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: colorScheme.outline,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                  const SizedBox(height: 4),
                ],
              ),
            ),
          );

          // Scroll Handling for Desktop and Web
          if (isDesktop() || isWeb()) {
            content = Listener(
              onPointerDown: (event) {
                if (event.buttons == kPrimaryMouseButton) {
                  setState(() {
                    _isDragging = true;
                    _lastOffset = event.position;
                  });
                }
              },
              onPointerMove: (event) {
                if (_isDragging) {
                  final dy = event.position.dy - _lastOffset.dy;
                  _scrollController.jumpTo(_scrollController.offset - dy);
                  setState(() {
                    _lastOffset = event.position;
                  });
                }
              },
              onPointerUp: (event) {
                if (event.buttons == 0) {
                  setState(() {
                    _isDragging = false;
                  });
                }
              },
              child: content,
            );
          }

          return Scaffold(
            appBar: AppBar(
              title: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    AppLocalizations.of(context)!.about_screen,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      height: 0.9,
                    ),
                  ),
                  Text(
                    AppLocalizations.of(context)!.about_header,
                    style: theme.textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.normal,
                    ),
                  ),
                ],
              ),
              foregroundColor: colorScheme.primary,
            ),
            body: content,
          );
        },
      ),
    );
  }

  Widget _buildAppInfo(
    BuildContext context,
    AboutState state,
    String selectedLanguage,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final localizedLanguageCode = _localizedLanguageBadge(selectedLanguage);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SvgPicture.asset(
          "assets/images/UI/main-icon.svg",
          width: 96,
          height: 96,
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                l10n.app_name,
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onSurface,
                ),
              ),
              const SizedBox(height: 6),
              Wrap(
                key: const ValueKey('about-version-metadata'),
                spacing: 10,
                runSpacing: 4,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  _buildVersionInfoItem(
                    context,
                    key: const ValueKey('about-version-app'),
                    icon: const _AboutVersionIcon(icon: Icons.apps_rounded),
                    iconTopPadding: 3,
                    semanticsLabel: l10n.version,
                    tooltipMessage: _formatAppVersionTooltip(
                      context,
                      state.appBuildTimestamp,
                    ),
                    value: "${state.appVersion} (${state.buildNumber})",
                  ),
                  _buildVersionInfoItem(
                    context,
                    key: const ValueKey('about-version-common-db'),
                    icon: const _AboutVersionIcon(icon: Icons.storage_rounded),
                    iconTopPadding: 3,
                    semanticsLabel: l10n.common_data_update,
                    tooltipMessage: _formatDbVersionTooltip(
                      context,
                      label: l10n.common_data_update,
                      versionInfo: state.commonDbVersionInfo,
                    ),
                    value: _formatDbVersionValue(state.commonDbVersionInfo),
                  ),
                  _buildVersionInfoItem(
                    context,
                    key: const ValueKey('about-version-localized-db'),
                    icon: _AboutVersionIcon(
                      icon: Icons.storage_rounded,
                      badgeText: localizedLanguageCode,
                      badgeKey: const ValueKey(
                        'about-version-localized-db-code',
                      ),
                    ),
                    iconTopPadding: 7,
                    semanticsLabel: l10n.localized_data_update(
                      _localizedLanguageName(l10n, localizedLanguageCode),
                    ),
                    tooltipMessage: _formatDbVersionTooltip(
                      context,
                      label: l10n.localized_data_update(
                        _localizedLanguageName(l10n, localizedLanguageCode),
                      ),
                      versionInfo: state.localizedDbVersionInfo,
                    ),
                    value: _formatDbVersionValue(state.localizedDbVersionInfo),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildVersionInfoItem(
    BuildContext context, {
    required Key key,
    required Widget icon,
    required String semanticsLabel,
    required String value,
    String? tooltipMessage,
    double iconTopPadding = 0,
  }) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final versionTextStyle = theme.textTheme.titleMedium?.copyWith(
      fontWeight: FontWeight.normal,
      color: colorScheme.onSurfaceVariant,
    );

    Widget item = Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Padding(
          padding: EdgeInsets.only(top: iconTopPadding),
          child: icon,
        ),
        const SizedBox(width: 4),
        Text(value, style: versionTextStyle),
      ],
    );

    item = Semantics(
      container: true,
      label: '$semanticsLabel $value',
      child: item,
    );

    if (tooltipMessage != null) {
      final tooltipKey = GlobalKey<TooltipState>();
      item = Tooltip(
        key: tooltipKey,
        message: tooltipMessage,
        waitDuration: Duration.zero,
        triggerMode: TooltipTriggerMode.tap,
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: () {
            tooltipKey.currentState?.ensureTooltipVisible();
          },
          child: item,
        ),
      );
    }

    return KeyedSubtree(key: key, child: item);
  }

  String _formatDbVersionValue(DatabaseVersionInfo? versionInfo) {
    if (versionInfo == null) {
      return "-";
    }
    return "${versionInfo.schemaVersion} (${versionInfo.dataVersion})";
  }

  String _formatAppVersionTooltip(
    BuildContext context,
    DateTime? buildTimestamp,
  ) {
    final l10n = AppLocalizations.of(context)!;
    if (buildTimestamp == null) {
      return l10n.version;
    }
    final formattedDate = _formatTooltipDateTime(context, buildTimestamp);
    return "${l10n.app_version_from} $formattedDate";
  }

  String _formatDbVersionTooltip(
    BuildContext context, {
    required String label,
    required DatabaseVersionInfo? versionInfo,
  }) {
    if (versionInfo == null) {
      return label;
    }
    final l10n = AppLocalizations.of(context)!;
    final formattedDate = _formatTooltipDateTime(context, versionInfo.date);
    return "$label ${l10n.data_version_from} $formattedDate";
  }

  String _formatTooltipDateTime(BuildContext context, DateTime value) {
    final localeName = Localizations.localeOf(context).toString();
    return DateFormat.yMd(localeName).add_jms().format(value.toLocal());
  }

  String _localizedLanguageBadge(String selectedLanguage) {
    final normalized = selectedLanguage.toLowerCase();
    if (AppConstants.languages.containsKey(normalized)) {
      return normalized.toUpperCase();
    }
    return 'EN';
  }

  String _localizedLanguageName(AppLocalizations l10n, String languageCode) {
    switch (languageCode.toLowerCase()) {
      case 'en':
        return l10n.language_name_en;
      case 'es':
        return l10n.language_name_es;
      case 'uk':
        return l10n.language_name_uk;
      case 'ru':
        return l10n.language_name_ru;
      default:
        return l10n.language_name_en;
    }
  }

  Widget _buildContactsLinks(BuildContext context) {
    return Column(
      children: [
        IconLinkItem(
          iconPath: "assets/images/UI/email.svg",
          text: AppConstants.supportEmail,
          onTap: () => widget.dependencies.launchLink(
            "mailto:${AppConstants.supportEmail}",
          ),
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/www.svg",
          text: AppLocalizations.of(context)!.website,
          onTap: () => widget.dependencies.launchLink(AppConstants.websiteUrl),
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/github.svg",
          text: AppLocalizations.of(context)!.github_project,
          onTap: () => widget.dependencies.launchLink(AppConstants.projectUrl),
        ),
      ],
    );
  }

  Widget _buildLegalLinks(BuildContext context, String currentLocale) {
    return Column(
      children: [
        IconLinkItem(
          iconPath: "assets/images/UI/download.svg",
          text: AppLocalizations.of(context)!.installation_packages,
          onTap: () =>
              widget.dependencies.launchLink(AppConstants.latestReleaseUrl),
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/shield.svg",
          text: AppLocalizations.of(context)!.privacy_policy,
          onTap: () {
            widget.dependencies.appLinkHandler(context, 'topic:privacy_policy');
          },
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/license.svg",
          text: AppLocalizations.of(context)!.license,
          onTap: () {
            widget.dependencies.appLinkHandler(context, 'topic:license');
          },
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/support_us.svg",
          text: AppLocalizations.of(context)!.support_us,
          onTap: () => widget.dependencies.launchLink(
            AppConstants.websiteUrl +
                AppConstants.joinPartUrl.replaceFirst('@loc', currentLocale),
          ),
        ),
      ],
    );
  }

  Widget _buildMarketplaces(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Row(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            IconUrl(
              iconPath: "assets/images/UI/google_play.svg",
              url: AppConstants.googlePlayUrl,
              tooltip: "Google Play",
            ),
            IconUrl(
              iconPath: "assets/images/UI/microsoft_store.svg",
              url: AppConstants.microsoftStoreUrl,
              tooltip: "Microsoft Store",
            ),
            IconUrl(
              iconPath: "assets/images/UI/snapcraft.svg",
              url: AppConstants.snapcraftUrl,
              tooltip: "Snapcraft",
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildAcknowledgements(BuildContext context, AboutState state) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return PlatformExpansionTile(
      initiallyExpanded: state.isAcknowledgementsExpanded,
      onExpansionChanged: (expanded) {
        aud.playSound("click");
        context.read<AboutCubit>().setAcknowledgementsExpanded(expanded);
      },
      tilePadding: const EdgeInsets.fromLTRB(2, 0, 2, 0),
      minTileHeight: 30,
      title: Row(
        children: [
          SvgPicture.asset(
            "assets/images/UI/thank-you.svg",
            width: 24,
            height: 24,
            colorFilter: ColorFilter.mode(colorScheme.primary, BlendMode.srcIn),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              AppLocalizations.of(context)!.acknowledgements_title,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.primary,
              ),
            ),
          ),
        ],
      ),
      children: [
        const SizedBox(height: 4),
        if (AppLocalizations.of(context)!.acknowledgements_description_1 != "")
          Text(
            AppLocalizations.of(context)!.acknowledgements_description_1,
            style: theme.textTheme.bodyLarge?.copyWith(
              color: colorScheme.onSurface,
            ),
          ),
        const InstitutionList(),
        if (AppLocalizations.of(context)!.acknowledgements_description_2 != "")
          Text(
            AppLocalizations.of(context)!.acknowledgements_description_2,
            style: theme.textTheme.bodyLarge?.copyWith(
              color: colorScheme.onSurface,
            ),
          ),
        const LibraryList(),
      ],
    );
  }

  Widget _buildRecommended(BuildContext context, AboutState state) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return PlatformExpansionTile(
      initiallyExpanded: state.isRecommendedExpanded,
      onExpansionChanged: (expanded) {
        aud.playSound("click");
        context.read<AboutCubit>().setRecommendedExpanded(expanded);
      },
      tilePadding: const EdgeInsets.fromLTRB(2, 0, 2, 0),
      minTileHeight: 30,
      title: Row(
        children: [
          SvgPicture.asset(
            "assets/images/UI/like.svg",
            width: 24,
            height: 24,
            colorFilter: ColorFilter.mode(colorScheme.primary, BlendMode.srcIn),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              AppLocalizations.of(context)!.recommended_title,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.primary,
              ),
            ),
          ),
        ],
      ),
      children: [
        const SizedBox(height: 4),
        if (AppLocalizations.of(context)!.recommended_description != "")
          Text(
            AppLocalizations.of(context)!.recommended_description,
            style: theme.textTheme.bodyLarge?.copyWith(
              color: colorScheme.onSurface,
            ),
          ),
        const RecommendedList(),
      ],
    );
  }

  Widget _buildChangelog(BuildContext context, AboutState state) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return PlatformExpansionTile(
      minTileHeight: 30,
      tilePadding: const EdgeInsets.fromLTRB(2, 0, 2, 0),
      initiallyExpanded: state.isChangelogExpanded,
      onExpansionChanged: (expanded) {
        aud.playSound("click");
        context.read<AboutCubit>().setChangelogExpanded(expanded);
      },
      title: Row(
        children: [
          SvgPicture.asset(
            "assets/images/UI/changelog.svg",
            width: 24,
            height: 24,
            colorFilter: ColorFilter.mode(colorScheme.primary, BlendMode.srcIn),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              AppLocalizations.of(context)!.changelog,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.primary,
              ),
            ),
          ),
        ],
      ),
      children: [
        state.changelog.isNotEmpty
            ? Padding(
                padding: const EdgeInsets.all(4.0),
                child: MarkdownBody(
                  data: state.changelog,
                  styleSheet: getMarkdownStyleSheet(theme, colorScheme),
                  extensionSet: buildRevelationMarkdownExtensionSet(),
                  builders: buildRevelationMarkdownBuilders(
                    imageBuilder: buildBasicRevelationMarkdownImage,
                  ),
                  paddingBuilders: buildRevelationMarkdownPaddingBuilders(),
                  onTapLink: (text, href, title) {
                    widget.dependencies.appLinkHandler(context, href);
                  },
                ),
              )
            : Center(
                child: CircularProgressIndicator(color: colorScheme.primary),
              ),
      ],
    );
  }

  Widget _buildBugsReport(BuildContext context, Map<String, dynamic> settings) {
    return Column(
      children: [
        IconLinkItem(
          iconPath: "assets/images/UI/bug.svg",
          text: AppLocalizations.of(context)!.bug_report,
          onTap: () async {
            await submitBugReport(
              context: this.context,
              dependencies: BugReportDependencies(
                launchLink: widget.dependencies.launchLink,
                collectSystemAndAppInfo:
                    widget.dependencies.collectSystemAndAppInfo,
                writeClipboardText: widget.dependencies.writeClipboardText,
              ),
              diagnosticsBuilder: () async {
                final sbTechInfo = StringBuffer();
                sbTechInfo.write("=======TIMESTAMP=======\r\n");
                sbTechInfo.write("${DateTime.now().toIso8601String()}\r\n\r\n");
                sbTechInfo.write("=======LOGS=======\r\n");
                sbTechInfo.write(GetIt.I<Talker>().history.text());
                sbTechInfo.write("\r\n");
                final dataFilesSection =
                    await _collectDataFilesDiagnosticsSection();
                if (!mounted) {
                  return sbTechInfo.toString();
                }
                sbTechInfo.write(
                  await widget.dependencies.collectSystemAndAppInfo(
                    context: this.context,
                    dbFilesSection: dataFilesSection,
                  ),
                );
                sbTechInfo.write("\r\n=======APP SETTINGS=======\r\n");
                settings.forEach((key, value) {
                  sbTechInfo.writeln("$key: $value");
                });
                return sbTechInfo.toString();
              },
            );
          },
        ),
      ],
    );
  }

  Future<String> _collectDataFilesDiagnosticsSection() async {
    final lines = <String>[];
    lines.add('[DB FILES]');

    final dbFiles = <String>[
      AppConstants.commonDB,
      ...AppConstants.languages.keys.map(
        (lang) => AppConstants.localizedDB.replaceAll('@loc', lang),
      ),
    ];

    for (final dbFile in dbFiles) {
      int? sizeBytes;
      DatabaseVersionInfo? versionInfo;
      String? sizeError;
      String? versionInfoError;
      try {
        sizeBytes = await widget.dependencies
            .databaseFileSizeLoader(dbFile)
            .timeout(widget.diagnosticsIoTimeout);
      } catch (error, stackTrace) {
        log.handle(error, stackTrace);
        sizeError = _singleLineError(error);
      }
      try {
        versionInfo = await widget.dependencies
            .databaseVersionLoader(dbFile)
            .timeout(widget.diagnosticsIoTimeout);
      } catch (error, stackTrace) {
        log.handle(error, stackTrace);
        versionInfoError = _singleLineError(error);
      }

      final exists = sizeBytes != null || versionInfo != null;
      if (!exists && sizeError == null && versionInfoError == null) {
        lines.add('$dbFile: missing');
        continue;
      }

      final schemaVersion = versionInfo?.schemaVersion.toString() ?? 'n/a';
      final dataVersion = versionInfo?.dataVersion.toString() ?? 'n/a';
      final dateValue = versionInfo?.date.toUtc().toIso8601String() ?? 'n/a';
      final sizeValue = sizeBytes == null
          ? 'n/a'
          : '${_formatFileSize(sizeBytes)} ($sizeBytes bytes)';
      final errors = <String>[];
      if (versionInfoError != null) {
        errors.add('version_read_error=$versionInfoError');
      }
      if (sizeError != null) {
        errors.add('size_read_error=$sizeError');
      }
      final errorSuffix = errors.isEmpty ? '' : '; ${errors.join("; ")}';
      lines.add(
        '$dbFile: schema_version=$schemaVersion; data_version=$dataVersion; date=$dateValue; size=$sizeValue$errorSuffix',
      );
    }

    if (!isWeb()) {
      lines.add('');
      lines.add('[PRIMARY SOURCES FILES]');
      try {
        final primarySourcesLines =
            await _collectPrimarySourcesFilesDiagnosticsLines().timeout(
              widget.diagnosticsIoTimeout,
            );
        lines.addAll(primarySourcesLines);
      } catch (error, stackTrace) {
        log.handle(error, stackTrace);
        lines.add('primary_sources: read_error=${_singleLineError(error)}');
      }
    }

    return lines.join('\r\n');
  }

  Future<List<String>> _collectPrimarySourcesFilesDiagnosticsLines() async {
    final lines = <String>[];
    List<PrimarySourceFileInfo> fileInfos;
    try {
      fileInfos = await widget.dependencies.primarySourceFilesLoader();
    } catch (error, stackTrace) {
      log.handle(error, stackTrace);
      return ['primary_sources: read_error=${_singleLineError(error)}'];
    }

    if (fileInfos.isEmpty) {
      return const ['primary_sources: folder missing or empty'];
    }

    for (final fileInfo in fileInfos) {
      if (fileInfo.error != null) {
        lines.add(
          '${fileInfo.relativePath}: read_error=${_singleLineError(fileInfo.error!)}',
        );
        continue;
      }
      final sizeBytes = fileInfo.sizeBytes ?? 0;
      lines.add(
        '${fileInfo.relativePath}: size=${_formatFileSize(sizeBytes)} ($sizeBytes bytes)',
      );
    }
    return lines;
  }

  String _singleLineError(Object error) {
    return error.toString().replaceAll(RegExp(r'\s+'), ' ').trim();
  }

  String _formatFileSize(int bytes) {
    const units = ['B', 'KB', 'MB', 'GB'];
    var value = bytes.toDouble();
    var unitIndex = 0;
    while (value >= 1024 && unitIndex < units.length - 1) {
      value /= 1024;
      unitIndex++;
    }
    final precision = unitIndex == 0 ? 0 : 1;
    return '${value.toStringAsFixed(precision)} ${units[unitIndex]}';
  }
}

class _AboutVersionIcon extends StatelessWidget {
  const _AboutVersionIcon({required this.icon, this.badgeText, this.badgeKey});

  final IconData icon;
  final String? badgeText;
  final Key? badgeKey;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final badgeStyle = theme.textTheme.labelSmall?.copyWith(
      fontSize: 9,
      height: 1,
      fontWeight: FontWeight.w700,
      color: colorScheme.onSurfaceVariant,
    );

    return SizedBox(
      width: 24,
      height: badgeText == null ? 20 : 28,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 18, color: colorScheme.onSurfaceVariant),
          if (badgeText != null)
            Padding(
              padding: const EdgeInsets.only(top: 1),
              child: Text(
                badgeText!,
                key: badgeKey,
                style: badgeStyle,
                textAlign: TextAlign.center,
              ),
            ),
        ],
      ),
    );
  }
}
