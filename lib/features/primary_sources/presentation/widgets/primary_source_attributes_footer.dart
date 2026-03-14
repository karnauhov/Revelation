import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/dialogs/dialogs_utils.dart';

class PrimarySourceAttributesFooter extends StatelessWidget {
  final List<Map<String, String>>? attributes;
  final bool permissionsReceived;
  final bool selectAreaMode;
  final bool pipetteMode;
  final bool isMobileWeb;

  const PrimarySourceAttributesFooter({
    required this.attributes,
    required this.permissionsReceived,
    required this.selectAreaMode,
    required this.pipetteMode,
    required this.isMobileWeb,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final items = attributes;
    if (items == null || items.isEmpty || !permissionsReceived) {
      return const SizedBox.shrink();
    }

    final theme = Theme.of(context);
    final textTheme = theme.textTheme;
    final colorScheme = theme.colorScheme;
    final localizations = AppLocalizations.of(context)!;
    final commonStyle = textTheme.bodySmall?.copyWith(
      fontSize: 10,
      color: colorScheme.onSurfaceVariant,
    );

    return Align(
      alignment: Alignment.centerRight,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(10.0, 0, 10.0, 2.0),
        child: selectAreaMode
            ? Text(localizations.select_area_description, style: commonStyle)
            : pipetteMode
            ? Text(localizations.pick_color_description, style: commonStyle)
            : Text.rich(
                TextSpan(
                  style: commonStyle,
                  children: [
                    if (isMobileWeb)
                      TextSpan(
                        text: '⚠️ ${localizations.low_quality}; ',
                        style: commonStyle?.copyWith(
                          color: colorScheme.primary,
                        ),
                        recognizer: TapGestureRecognizer()
                          ..onTap = () {
                            showCustomDialog(
                              MessageType.warningCommon,
                              param: localizations.low_quality_message,
                            );
                          },
                      ),
                    ..._buildLinkSpans(context, items),
                  ],
                ),
                maxLines: 5,
                softWrap: true,
                overflow: TextOverflow.ellipsis,
              ),
      ),
    );
  }

  List<InlineSpan> _buildLinkSpans(
    BuildContext context,
    List<Map<String, String>> links,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final defaultStyle = theme.textTheme.bodySmall?.copyWith(
      fontSize: 10,
      color: colorScheme.onSurfaceVariant,
    );
    final spans = <InlineSpan>[];
    for (int i = 0; i < links.length; i++) {
      final link = links[i];
      final url = link['url'];
      if (url != null && url.isNotEmpty) {
        spans.add(
          TextSpan(
            text: link['text'],
            style: defaultStyle?.copyWith(color: colorScheme.primary),
            recognizer: TapGestureRecognizer()
              ..onTap = () {
                handleAppLink(context, url);
              },
          ),
        );
      } else {
        spans.add(TextSpan(text: link['text'], style: defaultStyle));
      }
      if (i < links.length - 1) {
        spans.add(TextSpan(text: '; ', style: defaultStyle));
      }
    }
    return spans;
  }
}
