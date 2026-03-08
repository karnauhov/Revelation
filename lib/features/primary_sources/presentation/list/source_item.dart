import 'package:float_column/float_column.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/utils/common.dart';

class SourceItemWidget extends StatefulWidget {
  final PrimarySource source;

  const SourceItemWidget({super.key, required this.source});

  @override
  State<SourceItemWidget> createState() => _SourceItemWidgetState();
}

class _SourceItemWidgetState extends State<SourceItemWidget> {
  late bool _showMore;
  final aud = AudioController();

  @override
  void initState() {
    super.initState();
    _showMore = widget.source.showMore;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;
    final colorScheme = theme.colorScheme;
    final bodyTextStyle = textTheme.bodyMedium;

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
                          widget.source.title,
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
                      extra: PrimarySourceRouteArgs(
                        primarySource: widget.source,
                      ),
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
                text: TextSpan(
                  text: "✒ ${widget.source.date}",
                  style: bodyTextStyle,
                ),
              ),
              WrappableText(
                text: TextSpan(
                  text:
                      "📖 ${widget.source.content} [${AppLocalizations.of(context)!.verses}: ${widget.source.quantity}]",
                  style: bodyTextStyle,
                ),
              ),
              WrappableText(
                text: TextSpan(
                  text: !_showMore
                      ? "(${AppLocalizations.of(context)!.show_more})"
                      : "(${AppLocalizations.of(context)!.hide})",
                  style: textTheme.bodyMedium?.copyWith(
                    color: colorScheme.primary,
                  ),
                  recognizer: TapGestureRecognizer()
                    ..onTap = () {
                      aud.playSound("click");
                      setState(() {
                        _showMore = !_showMore;
                        widget.source.showMore = _showMore;
                      });
                    },
                ),
              ),
              if (_showMore)
                WrappableText(
                  text: TextSpan(
                    text: "📜 ${widget.source.material}",
                    style: bodyTextStyle,
                  ),
                ),
              if (_showMore)
                WrappableText(
                  text: TextSpan(
                    text: "🔎 ${widget.source.textStyle}",
                    style: bodyTextStyle,
                  ),
                ),
              if (_showMore)
                WrappableText(
                  text: TextSpan(
                    text: "🗂 ${widget.source.classification}",
                    style: bodyTextStyle,
                  ),
                ),
              if (_showMore)
                WrappableText(
                  text: TextSpan(
                    text: "🔓 ${widget.source.found}",
                    style: bodyTextStyle,
                  ),
                ),
              if (_showMore)
                WrappableText(
                  text: TextSpan(
                    text: "📌 ${widget.source.currentLocation}",
                    style: bodyTextStyle,
                  ),
                ),
              if (_showMore)
                Text.rich(
                  TextSpan(
                    text: "🌐 ",
                    style: bodyTextStyle,
                    children: _buildSourceLinkSpans(context),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPreviewImage(BuildContext context) {
    if (widget.source.previewBytes != null) {
      return Image.memory(widget.source.previewBytes!, fit: BoxFit.cover);
    }

    if (widget.source.preview.startsWith('assets/')) {
      return Image.asset(widget.source.preview, fit: BoxFit.cover);
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

    if (widget.source.links.isNotEmpty) {
      final spans = <InlineSpan>[];
      for (final link in widget.source.links) {
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

    return [
      if (widget.source.link1Title.isNotEmpty)
        TextSpan(
          text: "[${widget.source.link1Title}]",
          style: linkStyle,
          recognizer: TapGestureRecognizer()
            ..onTap = () {
              if (widget.source.link1Url.isNotEmpty) {
                launchLink(widget.source.link1Url);
              }
            },
        ),
      if (widget.source.link2Title.isNotEmpty)
        TextSpan(
          text: ", [${widget.source.link2Title}]",
          style: linkStyle,
          recognizer: TapGestureRecognizer()
            ..onTap = () {
              if (widget.source.link2Url.isNotEmpty) {
                launchLink(widget.source.link2Url);
              }
            },
        ),
      if (widget.source.link3Title.isNotEmpty)
        TextSpan(
          text: ", [${widget.source.link3Title}]",
          style: linkStyle,
          recognizer: TapGestureRecognizer()
            ..onTap = () {
              if (widget.source.link3Url.isNotEmpty) {
                launchLink(widget.source.link3Url);
              }
            },
        ),
    ];
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
