import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_index.dart';
import 'package:revelation/features/allusion_search/presentation/bloc/allusion_search_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/bible_book_localization.dart';
import 'package:revelation/shared/ui/widgets/toolbar_dropdown.dart';

String allusionScopeLabel(AppLocalizations l10n, AllusionScope scope) =>
    switch (scope) {
      AllusionScope.wholeBible => l10n.allusion_scope_all,
      AllusionScope.oldTestament => l10n.allusion_scope_ot,
      AllusionScope.newTestament => l10n.allusion_scope_nt,
    };

class AllusionQueryToolbar extends StatelessWidget {
  const AllusionQueryToolbar({
    super.key,
    required this.state,
    this.inSidePanel = false,
  });
  final AllusionSearchState state;
  final bool inSidePanel;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final map = state.verseMap!;
    final cubit = context.read<AllusionSearchCubit>();
    final query = state.query;
    final theme = Theme.of(context);
    final heading = Text(
      l10n.allusion_source,
      style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
    );
    final search = IconButton(
      key: const Key('allusion_search'),
      tooltip: l10n.allusion_search_screen,
      onPressed: state.status == AllusionStatus.searching ? null : cubit.search,
      icon: const Icon(Icons.search),
    );
    final scale = MediaQuery.textScalerOf(context).scale(14) / 14;
    return LayoutBuilder(
      builder: (context, box) {
        const gap = 4.0;
        // Leave room for the dropdown arrow and three-digit references
        // (for example Psalm 119:176), including at larger text scales.
        final chapterWidth = 88.0 * scale;
        final verseWidth = 88.0 * scale;
        final lengthWidth = 156.0 * scale;
        final scopeWidth = 216.0 * scale;
        final bookMin = 140.0 * scale;
        final hideScope =
            box.maxWidth <
            bookMin +
                chapterWidth +
                verseWidth +
                lengthWidth +
                scopeWidth +
                48 +
                gap * 5;
        final compact =
            box.maxWidth <
            bookMin + chapterWidth + verseWidth + lengthWidth + 96 + gap * 5;
        // On small screens keep the reference in one row as long as labels fit.
        final wrap =
            box.maxWidth < 100 * scale + chapterWidth + verseWidth + 2 * gap;
        final separateOptions = compact || inSidePanel;
        final optionWidth = separateOptions
            ? 2 * gap
            : lengthWidth + (hideScope ? 48 : scopeWidth) + 48 + 5 * gap;
        final bookWidth = wrap
            ? box.maxWidth
            : box.maxWidth - chapterWidth - verseWidth - optionWidth;
        final options = IconButton(
          key: const Key('allusion_overflow'),
          tooltip: l10n.allusion_options,
          onPressed: () => showDialog<void>(
            context: context,
            builder: (_) => BlocProvider.value(
              value: cubit,
              child: _QueryOptions(showLength: compact),
            ),
          ),
          icon: const Icon(Icons.more_vert),
        );
        final fields = [
          ToolbarDropdown<int>(
            key: const Key('allusion_book'),
            width: bookWidth,
            label: l10n.bible_book,
            value: query.bookId,
            items: [
              for (final id in map.bookIds)
                DropdownMenuItem(
                  value: id,
                  child: Text(
                    localizedBibleBookName(l10n, id),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
            ],
            onChanged: (book) {
              if (book != null)
                cubit.updateQuery(bookId: book, chapter: 1, verse: 1);
            },
          ),
          _numericField(
            'allusion_chapter',
            chapterWidth,
            l10n.bible_chapter,
            query.chapter,
            map.chapterCount(query.bookId),
            (n) => cubit.updateQuery(chapter: n, verse: 1),
          ),
          _numericField(
            'allusion_verse',
            verseWidth,
            l10n.bible_verse,
            query.verse,
            map.verseCount(bookId: query.bookId, chapter: query.chapter),
            (n) => cubit.updateQuery(verse: n),
          ),
          if (inSidePanel) ...[
            _lengthField(context, state, lengthWidth),
            _scopeField(context, state, box.maxWidth - lengthWidth - gap),
          ] else if (!compact) ...[
            _lengthField(context, state, lengthWidth),
            if (!hideScope) _scopeField(context, state, scopeWidth),
            SizedBox(width: 48, child: search),
            if (hideScope) SizedBox(width: 48, child: options),
          ],
        ];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (separateOptions)
              Row(
                children: [
                  Expanded(child: heading),
                  search,
                  if (!inSidePanel) options,
                ],
              )
            else
              heading,
            const SizedBox(height: 8),
            IconTheme(
              data: IconThemeData(color: theme.colorScheme.primary),
              child: Wrap(
                spacing: gap,
                runSpacing: 8,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: fields,
              ),
            ),
          ],
        );
      },
    );
  }
}

ToolbarDropdown<int> _numericField(
  String key,
  double width,
  String label,
  int value,
  int count,
  ValueChanged<int> changed,
) => ToolbarDropdown<int>(
  key: Key(key),
  width: width,
  label: label,
  value: value,
  items: [
    for (var n = 1; n <= count; n++)
      DropdownMenuItem(value: n, child: Text('$n', maxLines: 1)),
  ],
  onChanged: (n) {
    if (n != null) changed(n);
  },
);

ToolbarDropdown<int> _lengthField(
  BuildContext context,
  AllusionSearchState state,
  double width,
) {
  final l10n = AppLocalizations.of(context)!;
  final first = state.verseMap!.referenceFor(
    bookId: state.query.bookId,
    chapter: state.query.chapter,
    verse: state.query.verse,
  );
  final available =
      (state.verseMap!.totalVerses - int.parse(first.verseKey, radix: 36) + 1)
          .clamp(1, AllusionIndex.maxLength);
  return ToolbarDropdown<int>(
    key: const Key('allusion_length'),
    width: width,
    label: l10n.allusion_length,
    value: state.query.length,
    items: [
      for (var n = 1; n <= available; n++)
        DropdownMenuItem(
          value: n,
          child: Text(
            l10n.allusion_verse_count(n),
            overflow: TextOverflow.ellipsis,
          ),
        ),
    ],
    onChanged: (n) {
      if (n != null) context.read<AllusionSearchCubit>().updateQuery(length: n);
    },
  );
}

ToolbarDropdown<AllusionScope> _scopeField(
  BuildContext context,
  AllusionSearchState state,
  double width,
) {
  final l10n = AppLocalizations.of(context)!;
  return ToolbarDropdown<AllusionScope>(
    key: const Key('allusion_scope'),
    width: width,
    label: l10n.allusion_scope,
    value: state.query.scope,
    items: [
      for (final scope in AllusionScope.values)
        DropdownMenuItem(
          value: scope,
          child: Text(
            allusionScopeLabel(l10n, scope),
            overflow: TextOverflow.ellipsis,
          ),
        ),
    ],
    onChanged: (scope) {
      if (scope != null)
        context.read<AllusionSearchCubit>().updateQuery(scope: scope);
    },
  );
}

class _QueryOptions extends StatelessWidget {
  const _QueryOptions({required this.showLength});
  final bool showLength;
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    return AlertDialog(
      backgroundColor: theme.colorScheme.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: theme.colorScheme.primary),
        borderRadius: BorderRadius.circular(8),
      ),
      title: Text(l10n.allusion_options, textAlign: TextAlign.center),
      content: SizedBox(
        width: 320,
        child: SingleChildScrollView(
          child: BlocBuilder<AllusionSearchCubit, AllusionSearchState>(
            builder: (context, state) => Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (showLength) ...[
                  _lengthField(context, state, double.infinity),
                  const SizedBox(height: 12),
                ],
                _scopeField(context, state, double.infinity),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(l10n.close),
        ),
      ],
    );
  }
}
