import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_svg/svg.dart';
import 'package:revelation/app_router.dart';
import 'package:logger/logger.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:xml/xml.dart';
import '../models/library_info.dart';

final log = Logger();

bool isDesktop() {
  return [TargetPlatform.windows, TargetPlatform.linux, TargetPlatform.macOS]
          .contains(defaultTargetPlatform) &&
      !kIsWeb;
}

bool isWeb() {
  return kIsWeb;
}

TargetPlatform getPlatform() {
  return defaultTargetPlatform;
}

Future<List<LibraryInfo>> parseLibraries(
    AssetBundle bundle, String xmlPath) async {
  try {
    final xmlString = await bundle.loadString(xmlPath);
    final document = XmlDocument.parse(xmlString);
    final libraries = <LibraryInfo>[];

    for (var element in document.findAllElements('library')) {
      final name = element.getElement('name')?.innerText;
      final idIcon = element.getElement('idIcon')?.innerText;
      final license = element.getElement('license')?.innerText;
      final officialSite = element.getElement('officialSite')?.innerText;
      final licenseLink = element.getElement('licenseLink')?.innerText;

      if (name == null ||
          idIcon == null ||
          license == null ||
          officialSite == null ||
          licenseLink == null) {
        throw Exception('Missing required tags in library element');
      }

      libraries.add(LibraryInfo(
        name: name,
        idIcon: idIcon,
        license: license,
        officialSite: officialSite,
        licenseLink: licenseLink,
      ));
    }

    return libraries;
  } on XmlException {
    rethrow;
  } on PlatformException {
    rethrow;
  } catch (e) {
    throw Exception('Unknown error: $e');
  }
}

launchLink(String url) async {
  try {
    final Uri uri = Uri.parse(url);
    final bool launched =
        await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!launched) {
      showCustomDialog(MessageType.errorBrokenLink, param: url);
    }
    return launched;
  } catch (e) {
    showCustomDialog(MessageType.errorBrokenLink,
        param: url, markdownExtension: e.toString());
  }
}

enum MessageType {
  errorCommon,
  errorBrokenLink,
  warningCommon,
  infoCommon,
}

void showCustomDialog(MessageType type,
    {String param = "", String markdownExtension = ""}) {
  BuildContext? context =
      AppRouter().navigatorKey.currentState?.overlay?.context;
  log.d("${type.name}: $param [$markdownExtension]");
  if (context == null) {
    log.e("The context is not available to display dialog.");
    return;
  }

  String title = "";
  String icon = "";
  String message = "";
  String additional = markdownExtension;
  switch (type) {
    case MessageType.errorCommon:
      title = AppLocalizations.of(context)!.error;
      icon = "assets/images/UI/error.svg";
      message = param;
      break;
    case MessageType.errorBrokenLink:
      title = AppLocalizations.of(context)!.error;
      icon = "assets/images/UI/error.svg";
      message =
          "${AppLocalizations.of(context)!.unable_to_follow_the_link}: $param";
      break;
    case MessageType.warningCommon:
      title = AppLocalizations.of(context)!.attention;
      icon = "assets/images/UI/attention.svg";
      message = param;
      break;
    case MessageType.infoCommon:
      title = AppLocalizations.of(context)!.info;
      icon = "assets/images/UI/info.svg";
      message = param;
      break;
  }

  showDialog(
    context: context,
    builder: (BuildContext dialogContext) {
      return AlertDialog(
        title: Center(
          child: Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontSize: 24.0,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              mainAxisSize: MainAxisSize.max,
              children: [
                SvgPicture.asset(
                  icon,
                  width: 48,
                  height: 48,
                ),
                SizedBox(width: 10.0),
                Expanded(
                  child: Text(
                    message,
                    style: const TextStyle(
                      fontSize: 18.0,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 10),
            if (additional != "")
              ExpansionTile(
                title: ConstrainedBox(
                  constraints: const BoxConstraints(
                    minWidth: 300.0,
                  ),
                  child: Row(
                    children: [
                      SvgPicture.asset(
                        "assets/images/UI/additional.svg",
                        width: 24,
                        height: 24,
                      ),
                      SizedBox(width: 16),
                      Text(
                        AppLocalizations.of(context)!.more_information,
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                children: [MarkdownBody(data: additional)],
              )
          ],
        ),
        actions: <Widget>[
          TextButton(
            child: Text(AppLocalizations.of(context)!.close),
            onPressed: () {
              Navigator.of(dialogContext).pop();
            },
          ),
        ],
      );
    },
  );
}