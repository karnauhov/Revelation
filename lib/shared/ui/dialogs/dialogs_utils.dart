import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_svg/svg.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/platform_expansion_tile.dart';

import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/core/logging/common_logger.dart';

enum MessageType { errorCommon, errorBrokenLink, warningCommon, infoCommon }

void showCustomDialog(
  MessageType type, {
  String param = "",
  String markdownExtension = "",
}) {
  final context = AppRouter().navigatorKey.currentState?.overlay?.context;
  log.debug("${type.name}: $param [$markdownExtension]");
  if (context == null) {
    log.error("The context is not available to display dialog.");
    return;
  }

  var title = "";
  var icon = "";
  var message = "";
  var name = "";
  final additional = markdownExtension;
  switch (type) {
    case MessageType.errorCommon:
      title = AppLocalizations.of(context)!.error;
      icon = "assets/images/UI/error.svg";
      message = param;
      name = "error_dialog";
      break;
    case MessageType.errorBrokenLink:
      title = AppLocalizations.of(context)!.error;
      icon = "assets/images/UI/error.svg";
      message =
          "${AppLocalizations.of(context)!.unable_to_follow_the_link}: $param";
      name = "error_dialog";
      break;
    case MessageType.warningCommon:
      title = AppLocalizations.of(context)!.attention;
      icon = "assets/images/UI/attention.svg";
      message = param;
      name = "warning_dialog";
      break;
    case MessageType.infoCommon:
      title = AppLocalizations.of(context)!.info;
      icon = "assets/images/UI/info.svg";
      message = param;
      name = "info_dialog";
      break;
  }

  showDialog(
    context: context,
    routeSettings: RouteSettings(name: name),
    builder: (BuildContext dialogContext) {
      final theme = Theme.of(context);
      final colorScheme = theme.colorScheme;

      return AlertDialog(
        title: Center(
          child: Text(
            title,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 24.0, fontWeight: FontWeight.bold),
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                SvgPicture.asset(
                  icon,
                  width: 48,
                  height: 48,
                  colorFilter: ColorFilter.mode(
                    colorScheme.primary,
                    BlendMode.srcIn,
                  ),
                ),
                const SizedBox(width: 10.0),
                Expanded(
                  child: Text(message, style: const TextStyle(fontSize: 18.0)),
                ),
              ],
            ),
            const SizedBox(height: 10),
            if (additional.isNotEmpty)
              PlatformExpansionTile(
                title: ConstrainedBox(
                  constraints: const BoxConstraints(minWidth: 300.0),
                  child: Row(
                    children: [
                      SvgPicture.asset(
                        "assets/images/UI/additional.svg",
                        width: 24,
                        height: 24,
                        colorFilter: ColorFilter.mode(
                          colorScheme.primary,
                          BlendMode.srcIn,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Text(
                        AppLocalizations.of(context)!.more_information,
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                children: [MarkdownBody(data: additional)],
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              AudioController().playSound("click");
              Navigator.of(dialogContext).pop();
            },
            child: Text(AppLocalizations.of(context)!.close),
          ),
        ],
      );
    },
  );
}
