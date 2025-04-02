import 'package:float_column/float_column.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
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
    TextTheme theme = Theme.of(context).textTheme;
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
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
                      theme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ]),
            ),
            Floatable(
              float: FCFloat.start,
              padding: const EdgeInsets.only(right: 8),
              child: ElevatedButton(
                onPressed: () {
                  // context.push('/primary');
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  elevation: 8,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  padding: EdgeInsets.zero,
                ),
                child: Ink(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.blueAccent, width: 1),
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
                style: theme.bodyMedium,
              ),
            ),
            WrappableText(
              text: TextSpan(
                text:
                    "📖 ${widget.source.content} [${AppLocalizations.of(context)!.verses}: ${widget.source.quantity}]",
                style: theme.bodyMedium,
              ),
            ),
            WrappableText(
              text: TextSpan(
                text: !_showMore
                    ? "(${AppLocalizations.of(context)!.show_more})"
                    : "(${AppLocalizations.of(context)!.hide})",
                style: const TextStyle(color: Colors.blue),
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
                  style: theme.bodyMedium,
                ),
              ),
            if (_showMore)
              WrappableText(
                text: TextSpan(
                  text: "🔎 ${widget.source.textStyle}",
                  style: theme.bodyMedium,
                ),
              ),
            if (_showMore)
              WrappableText(
                text: TextSpan(
                  text: "🗂 ${widget.source.classification}",
                  style: theme.bodyMedium,
                ),
              ),
            if (_showMore)
              WrappableText(
                text: TextSpan(
                  text: "🔓 ${widget.source.found}",
                  style: theme.bodyMedium,
                ),
              ),
            if (_showMore)
              WrappableText(
                text: TextSpan(
                  text: "📌 ${widget.source.currentLocation}",
                  style: theme.bodyMedium,
                ),
              ),
            if (_showMore)
              Text.rich(
                TextSpan(
                  text: "🌐 ",
                  style: theme.bodyMedium,
                  children: [
                    TextSpan(
                      text: "[${widget.source.link1Title}], ",
                      style: const TextStyle(color: Colors.blue),
                      recognizer: TapGestureRecognizer()
                        ..onTap = () {
                          launchLink(widget.source.link1Url);
                        },
                    ),
                    TextSpan(
                      text: "[${widget.source.link2Title}]",
                      style: const TextStyle(color: Colors.blue),
                      recognizer: TapGestureRecognizer()
                        ..onTap = () {
                          launchLink(widget.source.link2Url);
                        },
                    )
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
