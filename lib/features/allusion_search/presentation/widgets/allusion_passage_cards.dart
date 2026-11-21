import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_marked_verse.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/presentation/bloc/allusion_search_cubit.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_passage_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/bible_book_localization.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';

class AllusionSourcePreview extends StatelessWidget {
  const AllusionSourcePreview({super.key, required this.state});
  final AllusionSearchState state;
  @override
  Widget build(BuildContext context) {
    final refs = state.sourceReferences;
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final title = localizedBiblePassageLabel(l10n, refs.first, refs.last);
    Map<int, double> sourceWeights(String? original) {
      final index = state.index;
      if (index == null || original == null) return const {};
      final weights = <int, double>{};
      for (final word in bibleMarkedWords(original)) {
        for (final code in word.codes.where((code) => code.startsWith('G'))) {
          final number = int.parse(code.substring(1));
          final weight = index.baseWeight(number);
          if (weight != null) weights[number] = weight;
        }
      }
      return weights;
    }

    Widget edition(
      String label,
      String? marked,
      Map<int, double> weights,
      String prefix,
      String linkPrefix, {
      required bool loading,
    }) => Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: theme.textTheme.labelSmall),
          if (marked != null)
            BibleMarkedVerse(
              text: marked,
              prefix: prefix,
              highlights: weights,
              showWeights: true,
              linkPrefix: linkPrefix,
            )
          else if (!loading)
            Text(
              l10n.bible_reference_preview_unavailable,
              style: theme.textTheme.bodySmall,
            ),
        ],
      ),
    );
    final vocabulary = state.index?.sourceVocabulary(refs, state.originals);
    final format = NumberFormat('0.##', l10n.localeName);
    final visibleRefs = state.sourceExpanded ? refs : refs.take(1);
    return Card(
      color: theme.colorScheme.surfaceContainer,
      elevation: 0,
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Align(
                    alignment: AlignmentDirectional.centerStart,
                    child: TextButton.icon(
                      key: const Key('allusion_source_reference'),
                      style: _referenceButton(theme),
                      onPressed: () => showBiblePassageDialog(
                        context,
                        references: refs,
                        title: title,
                        verseMap: state.verseMap,
                        moduleFile: state.module?.fileName,
                        matchedNumbers: vocabulary?.words.keys ?? const [],
                      ),
                      icon: const Icon(Icons.menu_book_outlined, size: 18),
                      label: Text(title),
                    ),
                  ),
                ),
              ],
            ),
            for (final ref in visibleRefs)
              Builder(
                builder: (context) {
                  final original = state.originals?[ref.verseKey];
                  final weights = sourceWeights(original);
                  final prefix = refs.length == 1
                      ? ''
                      : '${ref.chapter}:${ref.verse}  ';
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      edition(
                        'LXX_TR',
                        original,
                        weights,
                        prefix,
                        'allusion_source_greek',
                        loading: state.originals == null,
                      ),
                      edition(
                        state.module?.displayTitle ?? l10n.bible_default,
                        state.texts[ref.verseKey],
                        weights,
                        prefix,
                        'allusion_source_translation',
                        loading: state.loadingText,
                      ),
                    ],
                  );
                },
              ),
            if (state.loadingText &&
                state.texts.isEmpty &&
                state.status != AllusionStatus.searching)
              const LinearProgressIndicator(minHeight: 2),
            if (refs.length > 1)
              TextButton.icon(
                key: const Key('allusion_source_expand'),
                onPressed: context.read<AllusionSearchCubit>().toggleSource,
                icon: Icon(
                  state.sourceExpanded ? Icons.expand_less : Icons.expand_more,
                  size: 18,
                ),
                label: Text(
                  state.sourceExpanded
                      ? l10n.allusion_collapse
                      : l10n.allusion_expand_verses(refs.length - 1),
                ),
              ),
            if (vocabulary != null) ...[
              const SizedBox(height: 4),
              _AllusionWordList(
                key: const Key('allusion_source_words'),
                label: Text(
                  l10n.allusion_source_word_count(
                    vocabulary.words.length,
                    format.format(vocabulary.totalWeight),
                  ),
                  style: theme.textTheme.labelMedium,
                ),
                numbers: vocabulary.words.keys,
                fallbackForm: (n) => vocabulary.words[n]!.form,
                wordTooltip: (n) {
                  final word = vocabulary.words[n]!;
                  return l10n.allusion_source_word_details(
                    word.occurrences?.toString() ?? '?',
                    format.format(word.baseWeight),
                    format.format(word.searchWeight),
                  );
                },
                expanded: state.sourceWordsExpanded,
                onToggle: context.read<AllusionSearchCubit>().toggleSourceWords,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class AllusionResultCard extends StatelessWidget {
  const AllusionResultCard({
    super.key,
    required this.match,
    required this.state,
  });
  final AllusionMatch match;
  final AllusionSearchState state;
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final grouped = state.level != AllusionLevel.verse;
    final ref = match.reference;
    final id = ref.verseKey;
    final label = localizedBibleBookName(l10n, ref.bookId);
    final title = state.level == AllusionLevel.book
        ? label
        : '$label ${ref.chapter}';
    final cubit = context.read<AllusionSearchCubit>();
    final refs = match.references;
    final groupExpanded = state.expandedGroup == id;
    final wordsExpanded = state.expandedWords == id;
    final text = state.texts[id];
    Set<int> numbersFor(BibleVerseReference r) => grouped
        ? state.index!.matchedInVerse(r, match.numbers)
        : match.numbers.toSet();
    final score = l10n.allusion_match_score(
      NumberFormat('0.##', l10n.localeName).format(match.sharedWeight),
      NumberFormat.decimalPercentPattern(
        locale: l10n.localeName,
        decimalDigits: 2,
      ).format(match.score),
    );
    Widget verseLink(BibleVerseReference r) {
      return TextButton(
        key: ValueKey('allusion_result_${r.verseKey}'),
        style: _referenceButton(theme, underline: grouped),
        onPressed: () => showBiblePassageDialog(
          context,
          references: [r],
          verseMap: state.verseMap,
          moduleFile: state.module?.fileName,
          matchedNumbers: numbersFor(r),
        ),
        child: Text(localizedBiblePassageLabel(l10n, r, r)),
      );
    }

    return Card(
      color: theme.colorScheme.surfaceContainerHighest,
      margin: const EdgeInsets.symmetric(vertical: 4),
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Align(
                    alignment: AlignmentDirectional.centerStart,
                    child: grouped
                        ? Text(
                            title,
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          )
                        : verseLink(ref),
                  ),
                ),
                if (state.module != null)
                  Text(
                    state.module!.displayTitle,
                    style: theme.textTheme.labelSmall,
                  ),
              ],
            ),
            if (grouped) ...[
              Wrap(
                spacing: 6,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  for (final r
                      in (groupExpanded && refs.length <= 20)
                          ? refs
                          : refs.take(3))
                    verseLink(r),
                  if (refs.length > 3)
                    TextButton(
                      onPressed: () => cubit.toggleGroup(id),
                      child: Text(
                        groupExpanded
                            ? l10n.allusion_collapse
                            : '+${refs.length - 3}',
                      ),
                    ),
                ],
              ),
              if (groupExpanded && refs.length > 20)
                SizedBox(
                  height: 180,
                  child: ListView.builder(
                    primary: false,
                    itemCount: refs.length - 3,
                    itemBuilder: (_, i) => Align(
                      alignment: AlignmentDirectional.centerStart,
                      child: verseLink(refs[i + 3]),
                    ),
                  ),
                ),
            ],
            if (text != null && text.isNotEmpty)
              BibleMarkedVerse(
                text: text,
                highlights: {for (final n in numbersFor(ref)) n: 1.0},
              )
            else if (!state.loadingText)
              Text(
                l10n.bible_reference_preview_unavailable,
                style: theme.textTheme.bodySmall,
              ),
            const SizedBox(height: 4),
            _AllusionWordList(
              label: Tooltip(
                message: grouped
                    ? l10n.allusion_group_score_hint
                    : l10n.allusion_verse_score_hint,
                child: Text(
                  '${l10n.allusion_common_count(match.numbers.length)} ($score)',
                  style: theme.textTheme.labelMedium,
                ),
              ),
              numbers: match.numbers,
              expanded: wordsExpanded,
              onToggle: () => cubit.toggleWords(id),
            ),
          ],
        ),
      ),
    );
  }
}

class _AllusionWordList extends StatelessWidget {
  const _AllusionWordList({
    super.key,
    required this.label,
    required this.numbers,
    required this.expanded,
    required this.onToggle,
    this.fallbackForm,
    this.wordTooltip,
  });

  final Widget label;
  final Iterable<int> numbers;
  final bool expanded;
  final VoidCallback onToggle;
  final String? Function(int)? fallbackForm;
  final String Function(int)? wordTooltip;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;
    Widget chip(int number) {
      final form = AppDi.greekWord(number) ?? fallbackForm?.call(number) ?? '';
      final button = TextButton(
        style: TextButton.styleFrom(
          backgroundColor: theme.colorScheme.surfaceContainerLow,
          minimumSize: const Size(32, 30),
          padding: const EdgeInsets.symmetric(horizontal: 8),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
        onPressed: () => handleAppLink(context, 'strong:G$number'),
        child: Text('$form G$number'.trim()),
      );
      final tip = wordTooltip?.call(number);
      return tip == null ? button : Tooltip(message: tip, child: button);
    }

    return Wrap(
      spacing: 6,
      runSpacing: 2,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        label,
        for (final number in expanded ? numbers : numbers.take(3)) chip(number),
        if (numbers.length > 3)
          TextButton(
            onPressed: onToggle,
            child: Text(
              expanded ? l10n.allusion_collapse : '+${numbers.length - 3}',
            ),
          ),
      ],
    );
  }
}

ButtonStyle _referenceButton(ThemeData theme, {bool underline = false}) =>
    TextButton.styleFrom(
      padding: const EdgeInsets.symmetric(horizontal: 2),
      minimumSize: const Size(32, 34),
      alignment: AlignmentDirectional.centerStart,
      textStyle: theme.textTheme.titleSmall?.copyWith(
        fontWeight: underline ? FontWeight.normal : FontWeight.bold,
        decoration: underline ? TextDecoration.underline : null,
      ),
    );
