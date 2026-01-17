import 'package:flutter/foundation.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';
import 'package:provider/provider.dart';
import 'package:revelation/common_widgets/ad_mob_banner.dart';
import 'package:revelation/controllers/audio_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/screens/about/icon_url.dart';
import 'package:revelation/screens/about/recommended_list.dart';
import 'package:revelation/viewmodels/settings_view_model.dart';
import '../../common_widgets/icon_link_item.dart';
import 'library_list.dart';
import 'institution_list.dart';
import '../../viewmodels/about_view_model.dart';
import '../../utils/common.dart';
import '../../utils/app_constants.dart';

class AboutScreen extends StatefulWidget {
  const AboutScreen({super.key});

  @override
  State<AboutScreen> createState() => _AboutScreenState();
}

class _AboutScreenState extends State<AboutScreen> {
  final ScrollController _scrollController = ScrollController();
  final aud = AudioController();
  bool _isDragging = false;
  Offset _lastOffset = Offset.zero;

  @override
  void initState() {
    super.initState();
    if (isMobile()) {
      MobileAds.instance.initialize();
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final settingsViewModel = context.watch<SettingsViewModel>();
    final currentLocale = settingsViewModel.settings.selectedLanguage;

    return ChangeNotifierProvider(
      create: (_) => AboutViewModel(),
      child: Consumer<AboutViewModel>(
        builder: (context, viewModel, child) {
          if (viewModel.isLoading) {
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
                  _buildAppInfo(context, viewModel),
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
                  if (!viewModel.isAcknowledgementsExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Acknowledgments
                  _buildAcknowledgements(context, viewModel),
                  if (!viewModel.isRecommendedExpanded ||
                      !viewModel.isAcknowledgementsExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Recommended
                  _buildRecommended(context, viewModel),
                  if (!viewModel.isChangelogExpanded ||
                      !viewModel.isRecommendedExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Changelog
                  _buildChangelog(context, viewModel),
                  if (!viewModel.isChangelogExpanded)
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // Marketplaces (Desktop & Mobile)
                  if (!isWeb()) _buildMarketplaces(context),
                  if (!isWeb())
                    Divider(height: 1, color: colorScheme.outlineVariant),
                  // AdMob Banner
                  if (isMobile())
                    AdMobBanner(
                      width: MediaQuery.sizeOf(context).width * 1.0,
                      height: 50.0,
                      showsTestAd: kDebugMode,
                      androidAdUnitID: 'ca-app-pub-3945087976657115/2932040150',
                    ),
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

  Widget _buildAppInfo(BuildContext context, AboutViewModel viewModel) {
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
              "${AppLocalizations.of(context)!.version} ${viewModel.appVersion} (${viewModel.buildNumber})",
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
          onTap: () => context.push(
            '/topic',
            extra: {
              'name': AppLocalizations.of(context)!.privacy_policy,
              'description': AppLocalizations.of(
                context,
              )!.privacy_policy_description,
              'file': "privacy_policy",
            },
          ),
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/license.svg",
          text: AppLocalizations.of(context)!.license,
          onTap: () => context.push(
            '/topic',
            extra: {
              'name': AppLocalizations.of(context)!.license,
              'description': AppLocalizations.of(context)!.license_description,
              'file': "license",
            },
          ),
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

  Widget _buildAcknowledgements(
    BuildContext context,
    AboutViewModel viewModel,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return ExpansionTile(
      initiallyExpanded: viewModel.isAcknowledgementsExpanded,
      onExpansionChanged: (expanded) {
        aud.playSound("click");
        viewModel.toggleAcknowledgements();
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

  Widget _buildRecommended(BuildContext context, AboutViewModel viewModel) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return ExpansionTile(
      initiallyExpanded: viewModel.isRecommendedExpanded,
      onExpansionChanged: (expanded) {
        aud.playSound("click");
        viewModel.toggleRecommended();
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

  Widget _buildChangelog(BuildContext context, AboutViewModel viewModel) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return ExpansionTile(
      minTileHeight: 30,
      tilePadding: const EdgeInsets.fromLTRB(2, 0, 2, 0),
      initiallyExpanded: viewModel.isChangelogExpanded,
      onExpansionChanged: (expanded) {
        aud.playSound("click");
        viewModel.toggleChangelogExpanded();
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
        viewModel.changelog.isNotEmpty
            ? Padding(
                padding: const EdgeInsets.all(4.0),
                child: MarkdownBody(
                  data: viewModel.changelog,
                  styleSheet: getMarkdownStyleSheet(theme, colorScheme),
                  onTapLink: (text, href, title) {
                    if (href != null && href.isNotEmpty) {
                      launchLink(href);
                    }
                  },
                ),
              )
            : Center(
                child: CircularProgressIndicator(color: colorScheme.primary),
              ),
      ],
    );
  }
}
