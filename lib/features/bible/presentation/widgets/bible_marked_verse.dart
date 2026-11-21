import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/dialogs/study_text_dialog.dart';

/// Strong links follow the module's own annotations. Only Greek identifiers
/// from the current allusion query can contribute a highlight.
class BibleMarkedVerse extends StatelessWidget {
  const BibleMarkedVerse({
    super.key,
    required this.text,
    this.prefix = '',
    this.highlights = const {},
    this.showWeights = false,
    this.linkPrefix,
  });

  final String text;
  final String prefix;
  final Map<int, double> highlights;
  final bool showWeights;
  final String? linkPrefix;

  @override
  Widget build(BuildContext context) {
    final words = bibleMarkedWords(text).toList();
    if (words.every((word) => word.codes.isEmpty)) return Text('$prefix$text');
    final l10n = AppLocalizations.of(context)!;
    final format = NumberFormat('0.##', l10n.localeName);
    final style = DefaultTextStyle.of(context).style;
    final dark = Theme.of(context).brightness == Brightness.dark;
    final spans = <InlineSpan>[TextSpan(text: prefix)];
    for (var i = 0; i < words.length; i++) {
      final word = words[i];
      if (i > 0) spans.add(const TextSpan(text: ' '));
      final tips = <String>[];
      var strength = 0.0;
      for (final code in word.codes) {
        final weight = code.startsWith('G')
            ? highlights[int.parse(code.substring(1))]
            : null;
        if (weight != null && weight > strength) strength = weight;
        tips.add(
          showWeights && weight != null
              ? l10n.allusion_word_weight(code, format.format(weight))
              : code,
        );
      }
      final color = strength == 0
          ? null
          : Color.lerp(
              dark ? const Color(0xffffcdcd) : const Color(0xffa45e62),
              dark ? const Color(0xffff7575) : const Color(0xffad1825),
              strength,
            );
      if (linkPrefix == null || word.codes.isEmpty) {
        spans.add(
          TextSpan(
            text: word.text,
            style: color == null ? null : TextStyle(color: color),
          ),
        );
        continue;
      }
      spans.add(
        WidgetSpan(
          alignment: PlaceholderAlignment.baseline,
          baseline: TextBaseline.alphabetic,
          child: Tooltip(
            message: tips.join('\n'),
            child: Semantics(
              link: true,
              child: InkWell(
                key: ValueKey('${linkPrefix}_${word.codes.join("_")}'),
                onTap: () => _openWord(context, word),
                child: Text(
                  word.text,
                  style: style.copyWith(
                    color: color,
                    decoration: TextDecoration.underline,
                    decorationStyle: TextDecorationStyle.dotted,
                  ),
                ),
              ),
            ),
          ),
        ),
      );
    }
    return Text.rich(TextSpan(children: spans));
  }

  Future<void> _openWord(BuildContext context, BibleMarkedWord word) async {
    final l10n = AppLocalizations.of(context)!;
    var code = word.codes.first;
    if (word.codes.length > 1) {
      final selected = await showDialog<String>(
        context: context,
        builder: (dialog) => SimpleDialog(
          title: Text(word.text),
          children: [
            for (final candidate in word.codes)
              SimpleDialogOption(
                onPressed: () => Navigator.pop(dialog, candidate),
                child: Text(candidate),
              ),
          ],
        ),
      );
      if (selected == null || !context.mounted) return;
      code = selected;
    }
    if (code.startsWith('G')) {
      await handleAppLink(context, 'strong:$code');
      return;
    }
    // The app's Hebrew dictionary is external. Keep passage context on tap
    // and open that exact entry only on an explicit dictionary action.
    await showDialog<void>(
      context: context,
      builder: (dialog) => StudyTextDialog(
        title: code,
        subtitle: l10n.bible_module_info_hebrew,
        content: Padding(
          padding: const EdgeInsets.all(12),
          child: Text(word.text),
        ),
        actions: [
          TextButton.icon(
            onPressed: () => handleAppLink(dialog, 'strong:$code'),
            icon: const Icon(Icons.open_in_new),
            label: Text(l10n.strong_open_dictionary),
          ),
          TextButton(
            onPressed: () => Navigator.pop(dialog),
            child: Text(l10n.close),
          ),
        ],
      ),
    );
  }
}
