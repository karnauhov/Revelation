import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:provider/provider.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import '../viewmodels/about_view_model.dart';
import '../widgets/about_link_item.dart';
import '../widgets/library_list.dart';
import '../utils/common.dart';
import '../utils/app_constants.dart';

class AboutScreen extends StatefulWidget {
  const AboutScreen({super.key});

  @override
  State<AboutScreen> createState() => _AboutScreenState();
}

class _AboutScreenState extends State<AboutScreen> {
  final ScrollController _scrollController = ScrollController();
  bool _isDragging = false;
  Offset _lastOffset = Offset.zero;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AboutViewModel(),
      child: Consumer<AboutViewModel>(
        builder: (context, viewModel, child) {
          if (viewModel.isLoading) {
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
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
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 4),
                  const Divider(),
                  // Contacts Links
                  _buildContactsLinks(context),
                  const Divider(),
                  // Acknowledgments
                  _buildAcknowledgements(context),
                  SizedBox(height: 4),
                  if (!viewModel.isChangelogExpanded) const Divider(height: 1),
                  // Changelog
                  _buildChangelog(context, viewModel),
                  if (!viewModel.isChangelogExpanded) const Divider(height: 1),
                  const Divider(),
                  // Copyright
                  Center(
                    child: Text(
                      "© ${DateTime.now().year} ${AppConstants.author}. ${AppLocalizations.of(context)!.all_rights_reserved}.",
                      style: Theme.of(context)
                          .textTheme
                          .bodySmall
                          ?.copyWith(color: Colors.grey),
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
              title: Text(AppLocalizations.of(context)!.about_screen),
            ),
            body: content,
          );
        },
      ),
    );
  }

  Widget _buildAppInfo(BuildContext context, AboutViewModel viewModel) {
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
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(
              "${AppLocalizations.of(context)!.version} ${viewModel.appVersion} (${viewModel.buildNumber})",
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.normal),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildContactsLinks(BuildContext context) {
    return Column(
      children: [
        AboutLinkItem(
          iconPath: "assets/images/UI/email.svg",
          text: AppConstants.supportEmail,
          onTap: () => launchLink("mailto:${AppConstants.supportEmail}"),
        ),
      ],
    );
  }

  Widget _buildAcknowledgements(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 4),
        Row(
          children: [
            SvgPicture.asset(
              "assets/images/UI/thank-you.svg",
              width: 24,
              height: 24,
            ),
            const SizedBox(width: 16),
            Text(
              AppLocalizations.of(context)!.acknowledgements_title,
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 8),
        if (AppLocalizations.of(context)!.acknowledgements_description_1 != "")
          Text(
            AppLocalizations.of(context)!.acknowledgements_description_1,
            style: Theme.of(context).textTheme.bodyLarge,
          ),
        const LibraryList(),
        if (AppLocalizations.of(context)!.acknowledgements_description_2 != "")
          Text(
            AppLocalizations.of(context)!.acknowledgements_description_2,
            style: Theme.of(context).textTheme.bodyLarge,
          ),
      ],
    );
  }

  Widget _buildChangelog(BuildContext context, AboutViewModel viewModel) {
    return ExpansionTile(
      minTileHeight: 30,
      tilePadding: const EdgeInsets.fromLTRB(2, 0, 2, 0),
      initiallyExpanded: viewModel.isChangelogExpanded,
      onExpansionChanged: (expanded) {
        viewModel.toggleChangelogExpanded();
      },
      title: Row(
        children: [
          SvgPicture.asset(
            "assets/images/UI/changelog.svg",
            width: 24,
            height: 24,
          ),
          const SizedBox(width: 16),
          Text(
            AppLocalizations.of(context)!.changelog,
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
        ],
      ),
      children: [
        viewModel.changelog.isNotEmpty
            ? Padding(
                padding: const EdgeInsets.all(4.0),
                child: MarkdownBody(
                  data: viewModel.changelog,
                ),
              )
            : const Center(child: CircularProgressIndicator()),
      ],
    );
  }
}
