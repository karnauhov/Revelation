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
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;
    final colorScheme = theme.colorScheme;
    final bodyTextStyle = textTheme.bodyMedium;

    void openSource() {
      context.push(
        '/primary_source',
        extra: PrimarySourceRouteArgs(primarySource: source),
      );
    }

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
                        child: _buildPageLink(
                          onTap: openSource,
                          child: getStyledText(
                            source.title,
                            textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: colorScheme.primary,
                              decoration: TextDecoration.underline,
                              decorationColor: colorScheme.primary,
                            ),
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
                  onPressed: openSource,
                  style: ElevatedButton.styleFrom(
                    enabledMouseCursor: SystemMouseCursors.click,
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
                      "📖 ${source.content} [${l10n.verses}: ${source.quantity}]",
                  style: bodyTextStyle,
                ),
              ),
              WrappableText(
                text: TextSpan(
                  text: !showMore ? "(${l10n.show_more})" : "(${l10n.hide})",
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
              if (showMore)
                Text.rich(
                  TextSpan(
                    text: '${l10n.primary_source_links}: ',
                    style: bodyTextStyle,
                    children: _buildSourceLinkSpans(context, openSource),
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

  Widget _buildPageLink({required Widget child, required VoidCallback onTap}) {
    return Semantics(
      link: true,
      child: InkWell(
        mouseCursor: SystemMouseCursors.click,
        onTap: onTap,
        child: child,
      ),
    );
  }

  List<InlineSpan> _buildSourceLinkSpans(
    BuildContext context,
    VoidCallback openSource,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final linkStyle = Theme.of(context).textTheme.bodyMedium?.copyWith(
      color: Theme.of(context).colorScheme.primary,
    );

    final spans = <InlineSpan>[
      WidgetSpan(
        alignment: PlaceholderAlignment.baseline,
        baseline: TextBaseline.alphabetic,
        child: _buildPageLink(
          onTap: openSource,
          child: Text(
            '[${l10n.open_primary_source}]',
            style: linkStyle?.copyWith(decoration: TextDecoration.underline),
          ),
        ),
      ),
    ];
    for (final link in source.links) {
      final title = _resolveLinkTitle(l10n, link.role, link.titleOverride);
      if (title.isEmpty || link.url.isEmpty) {
        continue;
      }
      spans.add(
        TextSpan(
          text: ', [$title]',
          style: linkStyle,
          recognizer: TapGestureRecognizer()
            ..onTap = () => launchLink(link.url),
        ),
      );
    }

    return spans;
  }

  String _resolveLinkTitle(
    AppLocalizations localizations,
    String role,
    String titleOverride,
  ) {
    if (titleOverride.trim().isNotEmpty) {
      return titleOverride;
    }

    return switch (role) {
      'wikipedia' => localizations.wikipedia,
      'intf' => localizations.intf,
      'image_source' => localizations.image_source,
      _ => role,
    };
  }
}
