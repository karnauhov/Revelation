import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:revelation/l10n/app_localizations.dart';
import '../../common_widgets/icon_link_item.dart';
import '../../utils/app_constants.dart';
import '../../utils/common.dart';

class DownloadScreen extends StatelessWidget {
  const DownloadScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final sections = [
      _DownloadSection(
        iconPath: "assets/images/UI/android.svg",
        title: l10n.download_android,
        linkIconPath: "assets/images/UI/google_play.svg",
        linkText: l10n.download_google_play,
        url: AppConstants.googlePlayUrl,
      ),
      _DownloadSection(
        iconPath: "assets/images/UI/windows.svg",
        title: l10n.download_windows,
        linkIconPath: "assets/images/UI/microsoft_store.svg",
        linkText: l10n.download_microsoft_store,
        url: AppConstants.microsoftStoreUrl,
      ),
      _DownloadSection(
        iconPath: "assets/images/UI/linux.svg",
        title: l10n.download_linux,
        linkIconPath: "assets/images/UI/snapcraft.svg",
        linkText: l10n.download_snapcraft,
        url: AppConstants.snapcraftUrl,
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.download,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                height: 0.9,
              ),
            ),
            Text(
              l10n.download_header,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
        foregroundColor: colorScheme.primary,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: ListView.separated(
            itemCount: sections.length,
            itemBuilder: (context, index) {
              return _buildPlatformSection(
                context,
                sections[index],
              );
            },
            separatorBuilder: (context, index) => Column(
              children: [
                Divider(height: 1, color: colorScheme.outlineVariant),
                const SizedBox(height: 4),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPlatformSection(
    BuildContext context,
    _DownloadSection section,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            SvgPicture.asset(
              section.iconPath,
              width: 24,
              height: 24,
              colorFilter: ColorFilter.mode(
                colorScheme.primary,
                BlendMode.srcIn,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              section.title,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.onSurface,
              ),
            ),
          ],
        ),
        IconLinkItem(
          iconPath: section.linkIconPath,
          text: section.linkText,
          onTap: () => launchLink(section.url),
          leftMargin: 30,
        ),
      ],
    );
  }
}

class _DownloadSection {
  const _DownloadSection({
    required this.iconPath,
    required this.title,
    required this.linkIconPath,
    required this.linkText,
    required this.url,
  });

  final String iconPath;
  final String title;
  final String linkIconPath;
  final String linkText;
  final String url;
}
