import 'package:float_column/float_column.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/utils/links_utils.dart';
import 'package:revelation/shared/ui/styled_text/styled_text_utils.dart';

class SourceItemWidget extends StatelessWidget {
  final PrimarySource source;
  final bool showMore;
  final VoidCallback onToggleShowMore;
  static final AudioController _audioController = AudioController();

  const SourceItemWidget({
    super.key,
    required this.source,
    required this.showMore,
    required this.onToggleShowMore,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;
    final colorScheme = theme.colorScheme;
    final bodyTextStyle = textTheme.bodyMedium;
    final sourceLinkSpans = _buildSourceLinkSpans(context);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: colorScheme.surfaceContainerHigh,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
        child: SizedBox(
          width: double.infinity,
          child: FloatColumn(
            children: [
              Text.rich(
                textAlign: TextAlign.center,
                TextSpan(
                  children: [
                    WidgetSpan(
                      child: Floatable(
                        float: FCFloat.none,
                        padding: const EdgeInsets.only(right: 0),
                        child: getStyledText(
                          source.title,
                          textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: colorScheme.onSurface,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              Floatable(
                float: FCFloat.start,
                padding: const EdgeInsets.only(right: 8, bottom: 8),
                child: ElevatedButton(
                  onPressed: () {
                    context.push(
                      '/primary_source',
                      extra: PrimarySourceRouteArgs(primarySource: source),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: colorScheme.surface,
                    elevation: 8,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    padding: EdgeInsets.zero,
                  ),
                  child: Ink(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: colorScheme.primary, width: 1),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: _buildPreviewImage(context),
                    ),
                  ),
                ),
              ),
              WrappableText(
                text: TextSpan(text: "✒ ${source.date}", style: bodyTextStyle),
              ),
              WrappableText(
                text: TextSpan(
                  text:
                      "📖 ${source.content} [${AppLocalizations.of(context)!.verses}: ${source.quantity}]",
                  style: bodyTextStyle,
                ),
              ),
              WrappableText(
                text: TextSpan(
                  text: !showMore
                      ? "(${AppLocalizations.of(context)!.show_more})"
                      : "(${AppLocalizations.of(context)!.hide})",
                  style: textTheme.bodyMedium?.copyWith(
                    color: colorScheme.primary,
                  ),
                  recognizer: TapGestureRecognizer()
                    ..onTap = () {
                      _audioController.playSound("click");
                      onToggleShowMore();
                    },
                ),
              ),
              if (showMore)
                WrappableText(
                  text: TextSpan(
                    text: "📜 ${source.material}",
                    style: bodyTextStyle,
                  ),
                ),
              if (showMore)
                WrappableText(
                  text: TextSpan(
                    text: "🔎 ${source.textStyle}",
                    style: bodyTextStyle,
                  ),
                ),
              if (showMore)
                WrappableText(
                  text: TextSpan(
                    text: "🗂 ${source.classification}",
                    style: bodyTextStyle,
                  ),
                ),
              if (showMore)
                WrappableText(
                  text: TextSpan(
                    text: "🔓 ${source.found}",
                    style: bodyTextStyle,
                  ),
                ),
              if (showMore)
                WrappableText(
                  text: TextSpan(
                    text: "📌 ${source.currentLocation}",
                    style: bodyTextStyle,
                  ),
                ),
              if (showMore && sourceLinkSpans.isNotEmpty)
                Text.rich(
                  TextSpan(
                    text: "🌐 ",
                    style: bodyTextStyle,
                    children: sourceLinkSpans,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPreviewImage(BuildContext context) {
    if (source.previewBytes != null) {
      return Image.memory(source.previewBytes!, fit: BoxFit.cover);
    }

    if (source.preview.startsWith('assets/')) {
      return Image.asset(source.preview, fit: BoxFit.cover);
    }

    return Container(
      width: 168,
      height: 230,
      color: Theme.of(context).colorScheme.surfaceContainer,
      alignment: Alignment.center,
      child: Icon(
        Icons.image_not_supported_outlined,
        color: Theme.of(context).colorScheme.onSurfaceVariant,
      ),
    );
  }

  List<InlineSpan> _buildSourceLinkSpans(BuildContext context) {
    final linkStyle = Theme.of(context).textTheme.bodyMedium?.copyWith(
      color: Theme.of(context).colorScheme.primary,
    );

    final spans = <InlineSpan>[];
    for (final link in source.links) {
      final title = _resolveLinkTitle(context, link.role, link.titleOverride);
      if (title.isEmpty || link.url.isEmpty) {
        continue;
      }
      spans.add(
        TextSpan(
          text: '${spans.isEmpty ? '' : ', '}[$title]',
          style: linkStyle,
          recognizer: TapGestureRecognizer()
            ..onTap = () => launchLink(link.url),
        ),
      );
    }

    return spans;
  }

  String _resolveLinkTitle(
    BuildContext context,
    String role,
    String titleOverride,
  ) {
    if (titleOverride.trim().isNotEmpty) {
      return titleOverride;
    }

    final localizations = AppLocalizations.of(context)!;
    return switch (role) {
      'wikipedia' => localizations.wikipedia,
      'intf' => localizations.intf,
      'image_source' => localizations.image_source,
      _ => role,
    };
  }
}
