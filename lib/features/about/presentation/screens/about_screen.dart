import 'package:flutter/services.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:revelation/shared/ui/widgets/icon_link_item.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/about/presentation/bloc/about_cubit.dart';
import 'package:revelation/features/about/presentation/bloc/about_state.dart';
import 'package:revelation/features/about/presentation/screens/icon_url.dart';
import 'package:revelation/features/about/presentation/screens/institution_list.dart';
import 'package:revelation/features/about/presentation/screens/library_list.dart';
import 'package:revelation/features/about/presentation/screens/recommended_list.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/utils/common.dart';
import 'package:talker_flutter/talker_flutter.dart';

class AboutScreen extends StatefulWidget {
  const AboutScreen({super.key});

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
    _aboutCubit = AboutCubit();
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
                  _buildAppInfo(context, state),
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
                  if (!state.isAcknowledgementsExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Acknowledgments
                  _buildAcknowledgements(context, state),
                  if (!state.isRecommendedExpanded ||
                      !state.isAcknowledgementsExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Recommended
                  _buildRecommended(context, state),
                  if (!state.isChangelogExpanded ||
                      !state.isRecommendedExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Changelog
                  _buildChangelog(context, state),
                  if (!state.isChangelogExpanded)
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
                      "В© ${DateTime.now().year} ${AppConstants.author}. ${AppLocalizations.of(context)!.all_rights_reserved}.",
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

  Widget _buildAppInfo(BuildContext context, AboutState state) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Row(
      children: [
        SvgPicture.asset(
          "assets/images/UI/main-icon.svg",
          width: 96,
          height: 96,
        ),
        const SizedBox(width: 16),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppLocalizations.of(context)!.app_name,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.onSurface,
              ),
            ),
            Text(
              "${AppLocalizations.of(context)!.version} ${state.appVersion} (${state.buildNumber})",
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.normal,
                color: colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildContactsLinks(BuildContext context) {
    return Column(
      children: [
        IconLinkItem(
          iconPath: "assets/images/UI/email.svg",
          text: AppConstants.supportEmail,
          onTap: () => launchLink("mailto:${AppConstants.supportEmail}"),
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/www.svg",
          text: AppLocalizations.of(context)!.website,
          onTap: () => launchLink(AppConstants.websiteUrl),
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/github.svg",
          text: AppLocalizations.of(context)!.github_project,
          onTap: () => launchLink(AppConstants.projectUrl),
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
          onTap: () => launchLink(AppConstants.latestReleaseUrl),
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/shield.svg",
          text: AppLocalizations.of(context)!.privacy_policy,
          onTap: () {
            handleAppLink(context, 'topic:privacy_policy');
          },
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/license.svg",
          text: AppLocalizations.of(context)!.license,
          onTap: () {
            handleAppLink(context, 'topic:license');
          },
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/support_us.svg",
          text: AppLocalizations.of(context)!.support_us,
          onTap: () => launchLink(
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

    return ExpansionTile(
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
          Text(
            AppLocalizations.of(context)!.acknowledgements_title,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: colorScheme.primary,
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

    return ExpansionTile(
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
          Text(
            AppLocalizations.of(context)!.recommended_title,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: colorScheme.primary,
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

    return ExpansionTile(
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
          Text(
            AppLocalizations.of(context)!.changelog,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: colorScheme.primary,
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
                  onTapLink: (text, href, title) {
                    handleAppLink(context, href);
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
            try {
              StringBuffer sbEmail = StringBuffer();
              StringBuffer sbTechInfo = StringBuffer();
              sbEmail.write(AppLocalizations.of(context)!.bug_report_wish);
              sbEmail.write("\r\n\r\n");
              sbTechInfo.write("=======TIMESTAMP=======\r\n");
              sbTechInfo.write("${DateTime.now().toIso8601String()}\r\n\r\n");
              sbTechInfo.write("=======LOGS=======\r\n");
              sbTechInfo.write(GetIt.I<Talker>().history.text());
              sbTechInfo.write("\r\n");
              sbTechInfo.write(await collectSystemAndAppInfo(context: context));
              sbTechInfo.write("\r\n=======APP SETTINGS=======\r\n");
              settings.forEach((key, value) {
                sbTechInfo.writeln("$key: $value");
              });
              final emailBodyContent = Uri.encodeFull(sbEmail.toString());
              Clipboard.setData(ClipboardData(text: sbTechInfo.toString()));
              final openEmailResult = await launchLink(
                "mailto:${AppConstants.supportEmail}?subject=Revelation%20Bug%20Report&body=${emailBodyContent}",
              );
              if (!openEmailResult) {
                _showBugMessage();
              }
            } catch (ex, st) {
              log.handle(ex, st);
              _showBugMessage();
            }
          },
        ),
      ],
    );
  }

  void _showBugMessage() {
    final snackMessage =
        "${AppLocalizations.of(context)!.log_copied_message} ${AppConstants.supportEmail}";
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(snackMessage), duration: Duration(seconds: 10)),
    );
  }
}
