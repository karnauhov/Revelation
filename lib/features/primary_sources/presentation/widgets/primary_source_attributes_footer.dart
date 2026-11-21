import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/dialogs/dialogs_utils.dart';

/// The bottom edge of a manuscript image, outside its pan and zoom transform.
class PrimarySourceAttributesFooter extends StatefulWidget {
  const PrimarySourceAttributesFooter({
    required this.credits,
    this.onGreekStrongTap,
    this.selectAreaMode = false,
    this.pipetteMode = false,
    this.isMobileWeb = false,
    super.key,
  });

  final List<SourceCredit> credits;
  final GreekStrongTapHandler? onGreekStrongTap;
  final bool selectAreaMode;
  final bool pipetteMode;
  final bool isMobileWeb;

  @override
  State<PrimarySourceAttributesFooter> createState() => _FooterState();
}

class _FooterState extends State<PrimarySourceAttributesFooter> {
  final _links = <String, TapGestureRecognizer>{};
  final _quality = TapGestureRecognizer();

  @override
  void didUpdateWidget(PrimarySourceAttributesFooter oldWidget) {
    super.didUpdateWidget(oldWidget);
    final active = widget.credits.map((credit) => credit.url).toSet();
    for (final url
        in _links.keys.where((url) => !active.contains(url)).toList()) {
      _links.remove(url)!.dispose();
    }
  }

  @override
  void dispose() {
    for (final recognizer in _links.values) {
      recognizer.dispose();
    }
    _quality.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.credits.isEmpty) return const SizedBox.shrink();
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final style = theme.textTheme.bodySmall?.copyWith(
      color: colors.onSurfaceVariant,
    );
    final linkStyle = style?.copyWith(
      color: colors.primary,
      decoration: TextDecoration.underline,
    );
    final l10n = AppLocalizations.of(context)!;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
      color: colors.surfaceContainerLow,
      child: widget.selectAreaMode || widget.pipetteMode
          ? Text(
              widget.selectAreaMode
                  ? l10n.select_area_description
                  : l10n.pick_color_description,
              style: style,
              textAlign: TextAlign.end,
            )
          : Text.rich(
              TextSpan(
                children: [
                  if (widget.isMobileWeb)
                    TextSpan(
                      text: '${l10n.low_quality} · ',
                      style: linkStyle,
                      recognizer: _quality
                        ..onTap = () {
                          showCustomDialog(
                            MessageType.warningCommon,
                            param: l10n.low_quality_message,
                          );
                        },
                    ),
                  for (final (index, credit) in widget.credits.indexed) ...[
                    if (index > 0) const TextSpan(text: ' · '),
                    TextSpan(
                      text: credit.text,
                      style: credit.url.isEmpty ? style : linkStyle,
                      recognizer: credit.url.isEmpty
                          ? null
                          : (_links.putIfAbsent(
                                credit.url,
                                TapGestureRecognizer.new,
                              )
                              ..onTap = () => handleAppLink(
                                context,
                                credit.url,
                                onGreekStrongTap: widget.onGreekStrongTap,
                              )),
                    ),
                  ],
                ],
              ),
              style: style,
              textAlign: TextAlign.end,
            ),
    );
  }
}
