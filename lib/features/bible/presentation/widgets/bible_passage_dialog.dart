import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_passage_preview_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/bible_book_localization.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_marked_verse.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/ui/dialogs/revelation_dialog.dart';
import 'package:revelation/shared/ui/dialogs/study_text_dialog.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

Future<bool> previewBibleReference(
  BuildContext context,
  int book,
  int chapter,
  int first,
  int last,
) async {
  final map = AppDi.bibleVerseMapOrNull ?? await BibleVerseMap.loadFromAssets();
  if (!context.mounted ||
      !map.containsReference(bookId: book, chapter: chapter, verse: last)) {
    return false;
  }
  unawaited(
    showBiblePassageDialog(
      context,
      verseMap: map,
      references: [
        for (var verse = first; verse <= last; verse++)
          map.referenceFor(bookId: book, chapter: chapter, verse: verse),
      ],
    ),
  );
  return true;
}

Future<void> showBiblePassageDialog(
  BuildContext context, {
  required List<BibleVerseReference> references,
  String? title,
  String? moduleFile,
  Iterable<int> matchedNumbers = const [],
  BibleVerseMap? verseMap,
  BiblePassagePreviewCubit? previewCubit,
  DescriptionMarkdownCopyHandler? onCopyRequested,
  DescriptionMarkdownExportPdfHandler? onExportPdfRequested,
}) {
  if (references.isEmpty) throw ArgumentError.value(references, 'references');
  final router = GoRouter.of(context);
  final matches = matchedNumbers.toSet();
  return showDialog<void>(
    context: context,
    routeSettings: const RouteSettings(name: 'bible_passage_dialog'),
    builder: (_) => BlocProvider(
      create: (_) {
        final cubit = previewCubit ?? AppDi.createBiblePassagePreviewCubit();
        unawaited(
          cubit.open(
            references,
            moduleFile: moduleFile,
            verseMap: verseMap ?? AppDi.bibleVerseMapOrNull,
          ),
        );
        return cubit;
      },
      child: BlocBuilder<BiblePassagePreviewCubit, BiblePassagePreviewState>(
        builder: (context, state) {
          final l10n = AppLocalizations.of(context)!;
          final cubit = context.read<BiblePassagePreviewCubit>();
          final first = state.lines.first.reference;
          final last = state.lines.last.reference;
          final label =
              title != null &&
                  first == references.first &&
                  last == references.last
              ? title
              : localizedBiblePassageLabel(l10n, first, last);
          final translation = state.module;
          final translationLabel = translation == null
              ? l10n.bible_default
              : '${translation.displayTitle} · ${localizedBibleModuleLanguage(l10n, translation.language)}';
          final greekLabel =
              '${state.original?.displayTitle ?? 'LXX_TR'} · ${l10n.bible_module_info_greek}';
          final unavailable = l10n.bible_reference_preview_unavailable;
          final translationLines = <String>[];
          final greekLines = <String>[];
          for (final line in state.lines) {
            final verse = _lineLabel(l10n, line.reference, first, last);
            translationLines.add(
              '$verse  ${_plain(line.translation, unavailable)}',
            );
            greekLines.add('$verse  ${_plain(line.original, unavailable)}');
          }
          final copyText = [
            label,
            '',
            translationLabel,
            ...translationLines,
            '',
            greekLabel,
            ...greekLines,
          ].join('\n');
          final markdown = [
            '# ${_escapeMarkdown(label)}',
            '## ${_escapeMarkdown(translationLabel)}',
            ...translationLines.map(_escapeMarkdown),
            '## ${_escapeMarkdown(greekLabel)}',
            ...greekLines.map(_escapeMarkdown),
          ].join('\n\n');
          final exportEnabled =
              !state.loading && (translation != null || state.original != null);
          return StudyTextDialog(
            key: const Key('bible_passage_dialog'),
            title: label,
            subtitle: l10n.bible_passage_subtitle,
            content: SizedBox(
              width: 640,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      DescriptionMarkdownExportActions(
                        documentTitle: label,
                        markdown: markdown,
                        copyText: copyText,
                        pdfEnabled: exportEnabled,
                        copyEnabled: exportEnabled,
                        onCopyRequested: onCopyRequested,
                        onExportPdfRequested: onExportPdfRequested,
                      ),
                      const Spacer(),
                      for (final direction in [-1, 1])
                        DescriptionMarkdownToolbarButton(
                          buttonKey: Key(
                            direction < 0
                                ? 'bible_passage_previous'
                                : 'bible_passage_next',
                          ),
                          tooltip: direction < 0
                              ? l10n.bible_previous_verse
                              : l10n.bible_next_verse,
                          icon: direction < 0
                              ? Icons.arrow_back_ios_new_rounded
                              : Icons.arrow_forward_ios_rounded,
                          iconSize: 18,
                          buttonExtent: 36,
                          enabled: state.canStep(direction),
                          onPressed: () => unawaited(cubit.step(direction)),
                        ),
                    ],
                  ),
                  const Divider(height: 12),
                  if (state.loading)
                    const Padding(
                      padding: EdgeInsets.all(18),
                      child: CircularProgressIndicator(),
                    )
                  else
                    Flexible(
                      child: SingleChildScrollView(
                        key: ValueKey(first.verseKey),
                        child: LayoutBuilder(
                          builder: (context, box) {
                            final wide =
                                box.maxWidth >=
                                500 * MediaQuery.textScalerOf(context).scale(1);
                            return Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                for (
                                  var i = 0;
                                  i < state.lines.length;
                                  i++
                                ) ...[
                                  if (i > 0) const Divider(height: 16),
                                  _PassageRow(
                                    verse: _lineLabel(
                                      l10n,
                                      state.lines[i].reference,
                                      first,
                                      last,
                                    ),
                                    line: state.lines[i],
                                    translationLabel: translationLabel,
                                    greekLabel: greekLabel,
                                    wide: wide,
                                    showHeaders: i == 0 || !wide,
                                    matchedNumbers: matches,
                                  ),
                                ],
                              ],
                            );
                          },
                        ),
                      ),
                    ),
                  const Divider(height: 12),
                ],
              ),
            ),
            secondaryActions: [
              if (!state.loading &&
                  (translation == null || state.original == null))
                RevelationDialogAction(
                  label: l10n.startup_retry,
                  onPressed: cubit.retry,
                ),
              RevelationDialogAction(
                label: l10n.close,
                onPressed: () => Navigator.pop(context),
              ),
            ],
            primaryAction: RevelationDialogAction(
              key: const Key('bible_passage_open_reader'),
              icon: Icons.open_in_new,
              label: l10n.bible_open_reader,
              onPressed: translation == null && state.original == null
                  ? null
                  : () {
                      Navigator.of(
                        context,
                      ).popUntil((route) => route is! PopupRoute);
                      router.push(
                        Uri(
                          path: '/bible',
                          queryParameters: {
                            'book': '${first.bookId}',
                            'chapter': '${first.chapter}',
                            'verse': '${first.verse}',
                            if (moduleFile != null) 'module': moduleFile,
                            'length': '${state.lines.length}',
                          },
                        ).toString(),
                      );
                    },
            ),
          );
        },
      ),
    ),
  );
}

String _plain(String? markedText, String unavailable) {
  final text = plainBibleText(markedText ?? '');
  return text.isEmpty ? unavailable : text;
}

String _escapeMarkdown(String text) => text.replaceAllMapped(
  RegExp(r'[\\`*_{}\[\]()<>#+!|~]'),
  (match) => '\\${match[0]}',
);

String _lineLabel(
  AppLocalizations l10n,
  BibleVerseReference ref,
  BibleVerseReference first,
  BibleVerseReference last,
) {
  if (first.bookId != last.bookId)
    return '${localizedBibleBookCode(l10n, ref.bookId)} ${ref.chapter}:${ref.verse}';
  if (first.chapter != last.chapter) return '${ref.chapter}:${ref.verse}';
  return '${ref.verse}';
}

class _PassageRow extends StatelessWidget {
  const _PassageRow({
    required this.verse,
    required this.line,
    required this.translationLabel,
    required this.greekLabel,
    required this.wide,
    required this.showHeaders,
    required this.matchedNumbers,
  });
  final String verse;
  final BiblePassageLine line;
  final String translationLabel, greekLabel;
  final bool wide, showHeaders;
  final Set<int> matchedNumbers;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final unavailable = AppLocalizations.of(
      context,
    )!.bible_reference_preview_unavailable;
    Widget column(String label, Widget body) => Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (showHeaders)
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(
              label,
              style: theme.textTheme.labelMedium?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        body,
      ],
    );
    final highlights = {for (final n in matchedNumbers) n: 1.0};
    Widget text(String? marked, String linkPrefix) => BibleMarkedVerse(
      text: marked == null || marked.trim().isEmpty ? unavailable : marked,
      prefix: '$verse  ',
      highlights: highlights,
      linkPrefix: linkPrefix,
    );
    final translation = column(
      translationLabel,
      text(line.translation, 'bible_passage_translation_word'),
    );
    final greek = column(greekLabel, text(line.original, 'bible_passage_word'));
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
      child: wide
          ? Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(child: translation),
                const SizedBox(width: 16),
                Expanded(child: greek),
              ],
            )
          : Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [translation, const SizedBox(height: 12), greek],
            ),
    );
  }
}
