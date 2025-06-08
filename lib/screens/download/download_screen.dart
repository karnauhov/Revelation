import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:revelation/l10n/app_localizations.dart';
import '../../common_widgets/icon_link_item.dart';
import '../../utils/app_constants.dart';
import '../../utils/common.dart';

class DownloadScreen extends StatefulWidget {
  const DownloadScreen({super.key});

  @override
  State<DownloadScreen> createState() => _DownloadScreenState();
}

class _DownloadScreenState extends State<DownloadScreen> {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppLocalizations.of(context)!.download,
              style: theme.textTheme.headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(
              AppLocalizations.of(context)!.download_header,
              style: theme.textTheme.labelSmall
                  ?.copyWith(fontWeight: FontWeight.normal),
            ),
          ],
        ),
        foregroundColor: colorScheme.primary,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildAndroidLinks(context),
              Divider(
                height: 1,
                color: colorScheme.outlineVariant,
              ),
              const SizedBox(height: 4),
              _buildWindowsLinks(context),
              Divider(
                height: 1,
                color: colorScheme.outlineVariant,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAndroidLinks(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            SvgPicture.asset(
              "assets/images/UI/android.svg",
              width: 24,
              height: 24,
              colorFilter:
                  ColorFilter.mode(colorScheme.primary, BlendMode.srcIn),
            ),
            const SizedBox(width: 12),
            Text(
              "Android",
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.onSurface,
              ),
            ),
          ],
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/google_play.svg",
          text: "Google Play",
          onTap: () => launchLink(AppConstants.googlePlayUrl),
          leftMargin: 30,
        ),
      ],
    );
  }

  Widget _buildWindowsLinks(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            SvgPicture.asset(
              "assets/images/UI/windows.svg",
              width: 24,
              height: 24,
              colorFilter:
                  ColorFilter.mode(colorScheme.primary, BlendMode.srcIn),
            ),
            const SizedBox(width: 12),
            Text(
              "Windows",
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.onSurface,
              ),
            ),
          ],
        ),
        IconLinkItem(
          iconPath: "assets/images/UI/microsoft_store.svg",
          text: "Microsoft Store",
          onTap: () => launchLink(AppConstants.microsoftStoreUrl),
          leftMargin: 30,
        ),
      ],
    );
  }
}
