import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/bible_book_localization.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';

class BibleScreen extends StatelessWidget {
  const BibleScreen({
    this.initialBookId = 66,
    this.initialChapter = 1,
    this.initialVerse = 1,
    this.initialModuleFile,
    this.bibleRepository,
    super.key,
  });

  static const iconAssetPath = 'assets/images/UI/bible.svg';

  final int initialBookId;
  final int initialChapter;
  final int initialVerse;
  final String? initialModuleFile;
  final BibleRepository? bibleRepository;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final locale = Localizations.localeOf(context);

    return BlocProvider<BibleReaderCubit>(
      create: (_) {
        final cubit = BibleReaderCubit(
          repository: bibleRepository ?? AppDi.createBibleRepository(),
          languageCode: locale.languageCode,
          initialBookId: initialBookId,
          initialChapter: initialChapter,
          initialVerse: initialVerse,
          initialModuleFile: initialModuleFile,
          loadingBibleMessage: localizations.bible_loading,
          loadingChapterMessage: localizations.bible_loading_chapter,
          loadingModuleMessage: localizations.bible_loading_module,
          modulesUnavailableMessage: localizations.bible_no_modules,
        );
        unawaited(cubit.loadInitial());
        return cubit;
      },
      child: const _BibleScreenContent(),
    );
  }
}

class _BibleScreenContent extends StatelessWidget {
  const _BibleScreenContent();

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              localizations.bible_screen,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                height: 0.9,
              ),
            ),
            Text(
              localizations.bible_header,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
        foregroundColor: colorScheme.primary,
      ),
      body: SafeArea(
        child: BlocBuilder<BibleReaderCubit, BibleReaderState>(
          builder: (context, state) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _BibleReaderToolbar(state: state),
                _BibleProgressLine(state: state),
                Expanded(child: _BibleReaderBody(state: state)),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _BibleReaderToolbar extends StatelessWidget {
  const _BibleReaderToolbar({required this.state});

  final BibleReaderState state;

  @override
  Widget build(BuildContext context) {
    final map = state.verseMap;
    final reference = state.selectedReference;
    final selectedModule = state.selectedModule;
    final localizations = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    if (map == null || reference == null || selectedModule == null) {
      return ColoredBox(
        color: colorScheme.surface,
        child: const SizedBox(height: 8),
      );
    }

    final chapterCount = map.chapterCount(reference.bookId);
    final verseCount = map.verseCount(
      bookId: reference.bookId,
      chapter: reference.chapter,
    );

    return ColoredBox(
      color: colorScheme.surface,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.fromLTRB(8, 8, 8, 6),
        child: Row(
          children: [
            _ToolbarDropdown<BibleModuleInfo>(
              key: const Key('bible_module_dropdown'),
              width: 116,
              label: localizations.bible_module,
              value: selectedModule,
              enabled: !state.isBusy,
              items: [
                for (final module in state.modules)
                  DropdownMenuItem<BibleModuleInfo>(
                    value: module,
                    child: Tooltip(
                      message: module.title,
                      child: Text(
                        module.displayTitle,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ),
              ],
              onChanged: (module) {
                if (module != null) {
                  unawaited(
                    context.read<BibleReaderCubit>().selectModule(module),
                  );
                }
              },
            ),
            const SizedBox(width: 8),
            _ToolbarDropdown<int>(
              key: const Key('bible_book_dropdown'),
              width: 186,
              label: localizations.bible_book,
              value: reference.bookId,
              enabled: !state.isBusy,
              items: [
                for (final bookId in map.bookIds)
                  DropdownMenuItem<int>(
                    value: bookId,
                    child: Text(
                      localizedBibleBookName(localizations, bookId),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
              ],
              onChanged: (bookId) {
                if (bookId != null) {
                  unawaited(
                    context.read<BibleReaderCubit>().selectReference(
                      bookId: bookId,
                      chapter: 1,
                      verse: 1,
                    ),
                  );
                }
              },
            ),
            const SizedBox(width: 8),
            _ToolbarDropdown<int>(
              key: const Key('bible_chapter_dropdown'),
              width: 96,
              label: localizations.bible_chapter,
              value: reference.chapter,
              enabled: !state.isBusy,
              items: [
                for (var chapter = 1; chapter <= chapterCount; chapter++)
                  DropdownMenuItem<int>(
                    value: chapter,
                    child: Text(chapter.toString()),
                  ),
              ],
              onChanged: (chapter) {
                if (chapter != null) {
                  unawaited(
                    context.read<BibleReaderCubit>().selectReference(
                      bookId: reference.bookId,
                      chapter: chapter,
                      verse: 1,
                    ),
                  );
                }
              },
            ),
            const SizedBox(width: 8),
            _ToolbarDropdown<int>(
              key: const Key('bible_verse_dropdown'),
              width: 88,
              label: localizations.bible_verse,
              value: reference.verse,
              enabled: !state.isBusy,
              items: [
                for (var verse = 1; verse <= verseCount; verse++)
                  DropdownMenuItem<int>(
                    value: verse,
                    child: Text(verse.toString()),
                  ),
              ],
              onChanged: (verse) {
                if (verse != null) {
                  unawaited(
                    context.read<BibleReaderCubit>().selectReference(
                      bookId: reference.bookId,
                      chapter: reference.chapter,
                      verse: verse,
                    ),
                  );
                }
              },
            ),
            const SizedBox(width: 6),
            IconButton(
              key: const Key('bible_previous_chapter_button'),
              icon: const Icon(Icons.chevron_left),
              tooltip: localizations.bible_previous_chapter,
              color: colorScheme.primary,
              onPressed: !state.isBusy && state.canNavigateBackward
                  ? () {
                      unawaited(
                        context.read<BibleReaderCubit>().navigateChapter(
                          forward: false,
                        ),
                      );
                    }
                  : null,
            ),
            IconButton(
              key: const Key('bible_next_chapter_button'),
              icon: const Icon(Icons.chevron_right),
              tooltip: localizations.bible_next_chapter,
              color: colorScheme.primary,
              onPressed: !state.isBusy && state.canNavigateForward
                  ? () {
                      unawaited(
                        context.read<BibleReaderCubit>().navigateChapter(
                          forward: true,
                        ),
                      );
                    }
                  : null,
            ),
            const SizedBox(width: 12),
            IconButton(
              key: const Key('bible_strong_toggle_button'),
              icon: const Icon(Icons.local_offer),
              tooltip: localizations.toggle_show_strong_numbers,
              color: colorScheme.primary,
              style: IconButton.styleFrom(
                backgroundColor: state.showStrongNumbers
                    ? colorScheme.secondaryContainer
                    : Colors.transparent,
                shape: const CircleBorder(),
              ),
              onPressed: () {
                context.read<BibleReaderCubit>().toggleStrongNumbers();
              },
            ),
            if (state.showStrongNumbers) ...[
              const SizedBox(width: 2),
              Text(
                localizations.bible_strong_toggle_label,
                style: theme.textTheme.labelMedium?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ToolbarDropdown<T> extends StatelessWidget {
  const _ToolbarDropdown({
    required super.key,
    required this.width,
    required this.label,
    required this.value,
    required this.items,
    required this.onChanged,
    this.enabled = true,
  });

  final double width;
  final String label;
  final T value;
  final List<DropdownMenuItem<T>> items;
  final ValueChanged<T?> onChanged;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SizedBox(
      width: width,
      child: DropdownButtonFormField<T>(
        initialValue: value,
        isExpanded: true,
        items: items,
        onChanged: enabled ? onChanged : null,
        style: theme.textTheme.bodyMedium,
        decoration: InputDecoration(
          isDense: true,
          labelText: label,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 10,
            vertical: 8,
          ),
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }
}

class _BibleProgressLine extends StatelessWidget {
  const _BibleProgressLine({required this.state});

  final BibleReaderState state;

  @override
  Widget build(BuildContext context) {
    if (!state.isBusy) {
      return const SizedBox(height: 1);
    }

    return const LinearProgressIndicator(minHeight: 2);
  }
}

class _BibleReaderBody extends StatelessWidget {
  const _BibleReaderBody({required this.state});

  final BibleReaderState state;

  @override
  Widget build(BuildContext context) {
    if (state.status == BibleReaderStatus.failure) {
      return ErrorMessage(errorMessage: state.errorMessage ?? '');
    }

    if (state.verses.isEmpty) {
      return _BibleLoadingMessage(
        message:
            state.loadingMessage ?? AppLocalizations.of(context)!.bible_loading,
      );
    }

    return Stack(
      children: [
        _BibleChapterView(
          verses: state.verses,
          selectedVerseKey: state.selectedReference?.verseKey,
          showStrongNumbers: state.showStrongNumbers,
        ),
        if (state.isBusy)
          Align(
            alignment: Alignment.topCenter,
            child: _BibleBusyBanner(message: state.loadingMessage),
          ),
      ],
    );
  }
}

class _BibleLoadingMessage extends StatelessWidget {
  const _BibleLoadingMessage({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(
              message,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }
}

class _BibleBusyBanner extends StatelessWidget {
  const _BibleBusyBanner({required this.message});

  final String? message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final text = message;
    if (text == null || text.isEmpty) {
      return const SizedBox.shrink();
    }

    return DecoratedBox(
      decoration: BoxDecoration(
        color: colorScheme.surface.withValues(alpha: 0.92),
        border: Border(bottom: BorderSide(color: colorScheme.outlineVariant)),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: colorScheme.primary,
              ),
            ),
            const SizedBox(width: 10),
            Text(text, style: theme.textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}

class _BibleChapterView extends StatefulWidget {
  const _BibleChapterView({
    required this.verses,
    required this.selectedVerseKey,
    required this.showStrongNumbers,
  });

  final List<BibleChapterVerse> verses;
  final String? selectedVerseKey;
  final bool showStrongNumbers;

  @override
  State<_BibleChapterView> createState() => _BibleChapterViewState();
}

class _BibleChapterViewState extends State<_BibleChapterView> {
  final ScrollController _scrollController = ScrollController();
  final Map<String, GlobalKey> _verseKeys = <String, GlobalKey>{};

  @override
  void initState() {
    super.initState();
    _scheduleScrollToSelected();
  }

  @override
  void didUpdateWidget(covariant _BibleChapterView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.selectedVerseKey != widget.selectedVerseKey ||
        oldWidget.verses != widget.verses) {
      _scheduleScrollToSelected();
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      key: const Key('bible_chapter_verses'),
      controller: _scrollController,
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 20),
      itemCount: widget.verses.length,
      itemBuilder: (context, index) {
        final verse = widget.verses[index];
        final selected = verse.reference.verseKey == widget.selectedVerseKey;
        final verseKey = _verseKeys.putIfAbsent(
          verse.reference.verseKey,
          () => GlobalKey(),
        );
        return _BibleVerseRow(
          key: verseKey,
          verse: verse,
          selected: selected,
          showStrongNumbers: widget.showStrongNumbers,
        );
      },
    );
  }

  void _scheduleScrollToSelected() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        return;
      }
      final selectedVerseKey = widget.selectedVerseKey;
      if (selectedVerseKey == null) {
        return;
      }
      final keyContext = _verseKeys[selectedVerseKey]?.currentContext;
      if (keyContext == null) {
        return;
      }
      Scrollable.ensureVisible(
        keyContext,
        duration: const Duration(milliseconds: 180),
        curve: Curves.easeOutCubic,
        alignment: 0.2,
      );
    });
  }
}

class _BibleVerseRow extends StatelessWidget {
  const _BibleVerseRow({
    required super.key,
    required this.verse,
    required this.selected,
    required this.showStrongNumbers,
  });

  final BibleChapterVerse verse;
  final bool selected;
  final bool showStrongNumbers;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textStyle = theme.textTheme.bodyLarge?.copyWith(
      height: 1.28,
      color: colorScheme.onSurface,
    );

    return DecoratedBox(
      decoration: BoxDecoration(
        color: selected
            ? colorScheme.primaryContainer.withValues(alpha: 0.28)
            : Colors.transparent,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        child: Text.rich(
          TextSpan(
            style: textStyle,
            children: [
              TextSpan(
                text: '${verse.reference.verse}. ',
                style: textStyle?.copyWith(
                  color: colorScheme.primary,
                  fontWeight: FontWeight.w700,
                ),
              ),
              ..._buildBibleTextSpans(
                context,
                verse.text,
                showStrongNumbers: showStrongNumbers,
                baseStyle: textStyle,
              ),
            ],
          ),
          key: Key('bible_verse_${verse.reference.verse}'),
        ),
      ),
    );
  }
}

final _strongTokenPattern = RegExp(r'^[GH]\d+$', caseSensitive: false);

List<InlineSpan> _buildBibleTextSpans(
  BuildContext context,
  String text, {
  required bool showStrongNumbers,
  required TextStyle? baseStyle,
}) {
  final tokens = text.trim().split(RegExp(r'\s+'));
  if (tokens.length == 1 && tokens.first.isEmpty) {
    return const <InlineSpan>[];
  }

  final colorScheme = Theme.of(context).colorScheme;
  final spans = <InlineSpan>[];
  var hasVisibleWord = false;
  for (final token in tokens) {
    final isStrongToken = _strongTokenPattern.hasMatch(token);
    if (isStrongToken) {
      if (!showStrongNumbers || !hasVisibleWord) {
        continue;
      }
      spans.add(
        WidgetSpan(
          alignment: PlaceholderAlignment.aboveBaseline,
          baseline: TextBaseline.alphabetic,
          child: Padding(
            padding: const EdgeInsets.only(left: 1),
            child: Text(
              token.toUpperCase(),
              style: baseStyle?.copyWith(
                fontSize: (baseStyle.fontSize ?? 16) * 0.58,
                height: 1,
                color: colorScheme.primary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ),
      );
      continue;
    }

    spans.add(TextSpan(text: hasVisibleWord ? ' $token' : token));
    hasVisibleWord = true;
  }
  return spans;
}
