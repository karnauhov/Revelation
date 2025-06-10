import 'package:float_column/float_column.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/utils/common.dart';

class SourceItemWidget extends StatefulWidget {
  final PrimarySource source;
  const SourceItemWidget({super.key, required this.source});

  @override
  State<SourceItemWidget> createState() => _SourceItemWidgetState();
}

class _SourceItemWidgetState extends State<SourceItemWidget> {
  late bool _showMore;

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
                TextSpan(children: [
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
                ]),
              ),
              Floatable(
                float: FCFloat.start,
                padding: const EdgeInsets.only(right: 8, bottom: 8),
                child: ElevatedButton(
                  onPressed: () {
                    context.push('/primary_source', extra: widget.source);
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
                      child: Image.asset(
                        widget.source.preview,
                        fit: BoxFit.cover,
                      ),
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
                  style: textTheme.bodyMedium
                      ?.copyWith(color: colorScheme.primary),
                  recognizer: TapGestureRecognizer()
                    ..onTap = () {
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
                    children: [
                      if (widget.source.link1Title.isNotEmpty)
                        TextSpan(
                          text: "[${widget.source.link1Title}]",
                          style: textTheme.bodyMedium
                              ?.copyWith(color: colorScheme.primary),
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
                          style: textTheme.bodyMedium
                              ?.copyWith(color: colorScheme.primary),
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
                          style: textTheme.bodyMedium
                              ?.copyWith(color: colorScheme.primary),
                          recognizer: TapGestureRecognizer()
                            ..onTap = () {
                              if (widget.source.link3Url.isNotEmpty) {
                                launchLink(widget.source.link3Url);
                              }
                            },
                        ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
