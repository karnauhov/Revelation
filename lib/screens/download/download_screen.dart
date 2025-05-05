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
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppLocalizations.of(context)!.download,
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(
              AppLocalizations.of(context)!.download_header,
              style: Theme.of(context)
                  .textTheme
                  .labelSmall
                  ?.copyWith(fontWeight: FontWeight.normal),
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildAndroidLinks(context),
              const Divider(height: 1),
              const SizedBox(height: 4),
              _buildWindowsLinks(context),
              const Divider(height: 1),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAndroidLinks(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            SvgPicture.asset(
              "assets/images/UI/android.svg",
              width: 24,
              height: 24,
            ),
            const SizedBox(width: 12),
            Text(
              "Android",
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
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
    return Column(
      children: [
        Row(
          children: [
            SvgPicture.asset(
              "assets/images/UI/windows.svg",
              width: 24,
              height: 24,
            ),
            const SizedBox(width: 12),
            Text(
              "Windows",
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
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
