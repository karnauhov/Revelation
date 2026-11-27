import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/bible/domain/models/bible_bookmark.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_bookmarks_cubit.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_bookmark_marker.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/bible_book_localization.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/ui/dialogs/study_text_dialog.dart';
import 'package:revelation/shared/ui/widgets/toolbar_dropdown.dart';

const _bookmarkControlHeight = 48.0;
const _bookmarkFieldDecoration = InputDecoration(
  isDense: false,
  contentPadding: EdgeInsets.symmetric(horizontal: 10),
  border: OutlineInputBorder(),
);

Future<BibleBookmarkLocation?> showBibleBookmarksDialog(
  BuildContext context, {
  required BibleVerseMap verseMap,
  required BibleBookmarkLocation defaultLocation,
  required BibleBookmarkLocation? selectedVerse,
}) {
  final cubit = context.read<BibleBookmarksCubit>();
  return showDialog<BibleBookmarkLocation>(
    context: context,
    builder: (_) => BlocProvider.value(
      value: cubit,
      child: _BibleBookmarksDialog(
        defaultLocation: defaultLocation,
        selectedVerse: selectedVerse,
        verseMap: verseMap,
      ),
    ),
  );
}

class _BibleBookmarksDialog extends StatelessWidget {
  const _BibleBookmarksDialog({
    required this.defaultLocation,
    required this.selectedVerse,
    required this.verseMap,
  });

  final BibleBookmarkLocation defaultLocation;
  final BibleBookmarkLocation? selectedVerse;
  final BibleVerseMap verseMap;

  @override
  Widget build(BuildContext context) {
    final strings = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final cubit = context.read<BibleBookmarksCubit>();
    final state = context.watch<BibleBookmarksCubit>().state;
    final selection = selectedVerse;

    return StudyTextDialog(
      title: strings.bible_bookmarks,
      moveByHeader: true,
      content: SizedBox(
        width: 420,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              strings.bible_bookmarks_local_storage,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 12),
            if (state.status == BibleBookmarksStatus.loading)
              const LinearProgressIndicator()
            else if (state.status == BibleBookmarksStatus.loadFailed) ...[
              Text(strings.bible_bookmarks_load_failed),
              TextButton(
                onPressed: cubit.load,
                child: Text(strings.startup_retry),
              ),
            ] else if (state.bookmarks.isEmpty)
              Text(strings.bible_bookmarks_empty)
            else
              Flexible(
                child: ListView.builder(
                  key: const Key('bible_bookmarks_list'),
                  primary: false,
                  shrinkWrap: true,
                  itemCount: state.bookmarks.length,
                  itemBuilder: (context, index) {
                    final bookmark = state.bookmarks[index];
                    return ListTile(
                      key: ValueKey(bookmark.id),
                      contentPadding: EdgeInsets.zero,
                      leading: Icon(
                        Icons.bookmark,
                        color: bibleBookmarkColor(context, bookmark.color),
                        semanticLabel: _colorName(strings, bookmark.color),
                      ),
                      title: Text(
                        bookmark.name,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      subtitle: Text(
                        _referenceLabel(strings, bookmark.location),
                      ),
                      enabled: state.canChange,
                      onTap: () => Navigator.of(context).pop(bookmark.location),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            tooltip: strings.bible_bookmark_delete,
                            icon: const Icon(Icons.close),
                            onPressed: state.canChange
                                ? () async {
                                    if (await _confirmRemoval(
                                          context,
                                          bookmark,
                                        ) &&
                                        !cubit.isClosed) {
                                      await cubit.remove(bookmark.id);
                                    }
                                  }
                                : null,
                          ),
                          IconButton(
                            tooltip: strings.bible_bookmark_edit,
                            icon: const Icon(Icons.edit_outlined),
                            onPressed: state.canChange
                                ? () => showBibleBookmarkEditor(
                                    context,
                                    verseMap: verseMap,
                                    location: bookmark.location,
                                    bookmark: bookmark,
                                  )
                                : null,
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            if (state.status == BibleBookmarksStatus.saveFailed)
              _SaveError(message: strings.bible_bookmarks_save_failed),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(strings.close),
        ),
        FilledButton.icon(
          onPressed: state.canChange
              ? () => showBibleBookmarkEditor(
                  context,
                  verseMap: verseMap,
                  location: selection ?? defaultLocation,
                )
              : null,
          icon: const Icon(Icons.bookmark_add_outlined),
          label: Text(
            selection == null
                ? strings.bible_bookmark_add
                : '${strings.bible_bookmark_add} (${_shortReferenceLabel(strings, selection)})',
            textAlign: TextAlign.center,
          ),
        ),
      ],
    );
  }
}

Future<void> showBibleBookmarkEditor(
  BuildContext context, {
  required BibleVerseMap verseMap,
  required BibleBookmarkLocation location,
  BibleBookmark? bookmark,
}) {
  final cubit = context.read<BibleBookmarksCubit>();
  if (!cubit.state.canChange) return Future<void>.value();
  final editor = _BibleBookmarkEditor(
    verseMap: verseMap,
    location: location,
    bookmark: bookmark,
  );
  return showDialog<void>(
    context: context,
    builder: (_) => BlocProvider.value(value: cubit, child: editor),
  );
}

class _BibleBookmarkEditor extends StatelessWidget {
  _BibleBookmarkEditor({
    required this.verseMap,
    required this.location,
    required this.bookmark,
  });

  final BibleVerseMap verseMap;
  final BibleBookmarkLocation location;
  final BibleBookmark? bookmark;
  final _form = GlobalKey<FormState>();
  final _name = GlobalKey<FormFieldState<String>>();
  final _color = GlobalKey<FormFieldState<BibleBookmarkColor>>();
  final _location = GlobalKey<FormFieldState<BibleBookmarkLocation>>();

  @override
  Widget build(BuildContext context) {
    final strings = AppLocalizations.of(context)!;
    final cubit = context.read<BibleBookmarksCubit>();
    final state = context.watch<BibleBookmarksCubit>().state;
    final saving = state.status == BibleBookmarksStatus.saving;
    final current = bookmark;
    final initialReference = verseMap.normalizedReference(
      bookId: location.bookId,
      chapter: location.chapter,
      verse: location.verse,
    );
    final initialLocation = (
      bookId: initialReference.bookId,
      chapter: initialReference.chapter,
      verse: initialReference.verse,
    );

    return PopScope(
      canPop: !saving,
      child: StudyTextDialog(
        moveByHeader: true,
        title: current == null
            ? strings.bible_bookmark_add
            : strings.bible_bookmark_edit,
        content: SizedBox(
          width: 420,
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(6, 8, 6, 10),
            child: Form(
              key: _form,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  FormField<BibleBookmarkLocation>(
                    key: _location,
                    initialValue: initialLocation,
                    builder: (field) => _BookmarkReferenceFields(
                      verseMap: verseMap,
                      location: field.value!,
                      enabled: !saving,
                      onChanged: field.didChange,
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    key: _name,
                    initialValue:
                        current?.name ??
                        _nextBookmarkName(strings, state.bookmarks),
                    readOnly: saving,
                    maxLength: 80,
                    style: Theme.of(context).textTheme.bodyMedium,
                    decoration: _bookmarkFieldDecoration.copyWith(
                      labelText: strings.bible_bookmark_name,
                    ),
                    validator: (name) => name == null || name.trim().isEmpty
                        ? strings.bible_bookmark_name_required
                        : null,
                  ),
                  const SizedBox(height: 8),
                  Text(strings.bible_bookmark_color),
                  const SizedBox(height: 4),
                  FormField<BibleBookmarkColor>(
                    key: _color,
                    initialValue: current?.color ?? BibleBookmarkColor.blue,
                    builder: (field) => Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        for (final color in BibleBookmarkColor.values)
                          _BookmarkColorButton(
                            color: color,
                            selected: field.value == color,
                            onPressed: saving
                                ? null
                                : () => field.didChange(color),
                          ),
                      ],
                    ),
                  ),
                  if (saving) ...[
                    const SizedBox(height: 8),
                    const LinearProgressIndicator(),
                  ],
                  if (state.status == BibleBookmarksStatus.saveFailed)
                    _SaveError(message: strings.bible_bookmarks_save_failed),
                ],
              ),
            ),
          ),
        ),
        actions: [
          if (current != null)
            TextButton(
              onPressed: saving
                  ? null
                  : () async {
                      final confirmed = await _confirmRemoval(context, current);
                      if (!confirmed || !context.mounted) {
                        return;
                      }
                      await cubit.remove(current.id);
                      if (context.mounted &&
                          cubit.state.status == BibleBookmarksStatus.ready) {
                        Navigator.of(context).pop();
                      }
                    },
              child: Text(strings.bible_bookmark_delete),
            ),
          TextButton(
            onPressed: saving ? null : () => Navigator.of(context).pop(),
            child: Text(strings.cancel),
          ),
          FilledButton(
            onPressed: saving
                ? null
                : () async {
                    if (!_form.currentState!.validate()) return;
                    await cubit.save(
                      id: current?.id,
                      location: _location.currentState!.value!,
                      name: _name.currentState!.value!,
                      color: _color.currentState!.value!,
                    );
                    if (context.mounted &&
                        cubit.state.status == BibleBookmarksStatus.ready) {
                      Navigator.of(context).pop();
                    }
                  },
            child: Text(strings.bible_bookmark_save),
          ),
        ],
      ),
    );
  }
}

class _BookmarkReferenceFields extends StatelessWidget {
  const _BookmarkReferenceFields({
    required this.verseMap,
    required this.location,
    required this.enabled,
    required this.onChanged,
  });

  final BibleVerseMap verseMap;
  final BibleBookmarkLocation location;
  final bool enabled;
  final ValueChanged<BibleBookmarkLocation> onChanged;

  @override
  Widget build(BuildContext context) {
    final strings = AppLocalizations.of(context)!;
    final (:bookId, :chapter, :verse) = location;
    final chapterField = ToolbarDropdown<int>(
      key: ValueKey(('bible_bookmark_chapter', bookId)),
      width: double.infinity,
      label: strings.bible_chapter,
      decoration: _bookmarkFieldDecoration,
      value: chapter,
      items: _numberOptions(verseMap.chapterCount(bookId)),
      enabled: enabled,
      onChanged: (value) {
        if (value != null && value != chapter) {
          onChanged((bookId: bookId, chapter: value, verse: 1));
        }
      },
    );
    final verseField = ToolbarDropdown<int>(
      key: ValueKey(('bible_bookmark_verse', bookId, chapter)),
      width: double.infinity,
      label: strings.bible_verse,
      decoration: _bookmarkFieldDecoration,
      value: verse,
      items: _numberOptions(
        verseMap.verseCount(bookId: bookId, chapter: chapter),
      ),
      enabled: enabled,
      onChanged: (value) {
        if (value != null) {
          onChanged((bookId: bookId, chapter: chapter, verse: value));
        }
      },
    );

    return Row(
      children: [
        Expanded(
          flex: 5,
          child: ToolbarDropdown<int>(
            key: const Key('bible_bookmark_book'),
            width: double.infinity,
            label: strings.bible_book,
            decoration: _bookmarkFieldDecoration,
            value: bookId,
            items: [
              for (final id in verseMap.bookIds)
                DropdownMenuItem(
                  value: id,
                  child: Text(
                    localizedBibleBookName(strings, id),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
            ],
            enabled: enabled,
            onChanged: (value) {
              if (value != null && value != bookId) {
                onChanged((bookId: value, chapter: 1, verse: 1));
              }
            },
          ),
        ),
        const SizedBox(width: 8),
        Expanded(flex: 3, child: chapterField),
        const SizedBox(width: 8),
        Expanded(flex: 3, child: verseField),
      ],
    );
  }

  List<DropdownMenuItem<int>> _numberOptions(int count) => [
    for (var number = 1; number <= count; number++)
      DropdownMenuItem(value: number, child: Text('$number')),
  ];
}

class _BookmarkColorButton extends StatelessWidget {
  const _BookmarkColorButton({
    required this.color,
    required this.selected,
    required this.onPressed,
  });

  final BibleBookmarkColor color;
  final bool selected;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    final strings = AppLocalizations.of(context)!;
    final scheme = Theme.of(context).colorScheme;
    return Semantics(
      selected: selected,
      child: SizedBox(
        height: _bookmarkControlHeight,
        child: OutlinedButton.icon(
          onPressed: onPressed,
          style: OutlinedButton.styleFrom(
            backgroundColor: selected ? scheme.secondaryContainer : null,
            foregroundColor: selected
                ? scheme.onSecondaryContainer
                : scheme.onSurface,
            side: BorderSide(
              color: selected
                  ? scheme.secondaryContainer
                  : scheme.outlineVariant,
            ),
            shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(8)),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 12),
            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
          icon: Icon(
            Icons.circle,
            size: 14,
            color: bibleBookmarkColor(context, color),
          ),
          label: Text(_colorName(strings, color)),
        ),
      ),
    );
  }
}

class _SaveError extends StatelessWidget {
  const _SaveError({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) => Semantics(
    liveRegion: true,
    child: Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Text(
        message,
        style: TextStyle(color: Theme.of(context).colorScheme.error),
      ),
    ),
  );
}

Future<bool> _confirmRemoval(
  BuildContext context,
  BibleBookmark bookmark,
) async {
  final strings = AppLocalizations.of(context)!;
  final confirmed = await showDialog<bool>(
    context: context,
    builder: (context) => StudyTextDialog(
      title: strings.bible_bookmark_delete_confirm,
      moveByHeader: true,
      content: SizedBox(
        width: 360,
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(6, 4, 6, 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                bookmark.name,
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 4),
              Text(_referenceLabel(strings, bookmark.location)),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(false),
          child: Text(strings.cancel),
        ),
        FilledButton(
          onPressed: () => Navigator.of(context).pop(true),
          child: Text(strings.bible_bookmark_delete),
        ),
      ],
    ),
  );
  return confirmed == true;
}

String _referenceLabel(AppLocalizations strings, BibleBookmarkLocation verse) =>
    '${localizedBibleBookName(strings, verse.bookId)} ${verse.chapter}:${verse.verse}';

String _shortReferenceLabel(
  AppLocalizations strings,
  BibleBookmarkLocation verse,
) {
  final code = localizedBibleBookCode(strings, verse.bookId);
  final book =
      code.endsWith('.') ||
          code == localizedBibleBookName(strings, verse.bookId)
      ? code
      : '$code.';
  return '$book ${verse.chapter}:${verse.verse}';
}

final _numberedBookmarkPatterns = [
  for (final locale in AppLocalizations.supportedLocales)
    RegExp(
      '^' +
          lookupAppLocalizations(locale)
              .bible_bookmark_default_name('#')
              .split('#')
              .map(RegExp.escape)
              .join(r'([0-9]+)') +
          r'$',
    ),
];

String _nextBookmarkName(
  AppLocalizations strings,
  List<BibleBookmark> bookmarks,
) {
  var largest = BigInt.zero;
  for (final bookmark in bookmarks) {
    for (final pattern in _numberedBookmarkPatterns) {
      final match = pattern.firstMatch(bookmark.name);
      if (match == null) continue;
      final number = BigInt.parse(match.group(1)!);
      if (number > largest) largest = number;
      break;
    }
  }
  return strings.bible_bookmark_default_name((largest + BigInt.one).toString());
}

String _colorName(AppLocalizations strings, BibleBookmarkColor color) =>
    switch (color) {
      BibleBookmarkColor.blue => strings.bible_bookmark_blue,
      BibleBookmarkColor.green => strings.bible_bookmark_green,
      BibleBookmarkColor.amber => strings.bible_bookmark_amber,
      BibleBookmarkColor.red => strings.bible_bookmark_red,
      BibleBookmarkColor.violet => strings.bible_bookmark_violet,
    };
