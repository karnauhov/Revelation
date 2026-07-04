import 'dart:async';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter/services.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_search_result.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_state.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_state.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_search_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/bible_book_localization.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';

const double _kParallelPaneMinWidth = 420;
const double _kParallelPaneGap = 10;
const double _kToolbarChoiceDialogMaxWidth = 420;
const double _kToolbarChoiceDialogMinWidth = 280;
const double _kToolbarChoiceDialogHorizontalMargin = 96;
const double _kToolbarChoiceRowHeight = 44;

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
    final repository = bibleRepository;

    return BlocProvider<BibleWorkspaceCubit>(
      create: (_) {
        final cubit = BibleWorkspaceCubit(
          repositoryFactory: repository == null
              ? AppDi.createBibleRepository
              : () => repository,
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
        actions: [
          BlocBuilder<BibleWorkspaceCubit, BibleWorkspaceState>(
            builder: (context, workspaceState) {
              final workspaceCubit = context.read<BibleWorkspaceCubit>();
              return Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (workspaceState.hasMultiplePanes)
                    IconButton(
                      key: const Key('bible_linked_navigation_button'),
                      icon: Icon(
                        workspaceState.linkedNavigation
                            ? Icons.link
                            : Icons.link_off,
                      ),
                      tooltip: localizations.bible_linked_navigation,
                      style: IconButton.styleFrom(
                        backgroundColor: workspaceState.linkedNavigation
                            ? colorScheme.secondaryContainer
                            : Colors.transparent,
                        shape: const CircleBorder(),
                      ),
                      onPressed: workspaceCubit.toggleLinkedNavigation,
                    ),
                  IconButton(
                    key: const Key('bible_open_parallel_reader_button'),
                    icon: const Icon(Icons.add),
                    tooltip: localizations.bible_open_parallel_reader,
                    onPressed: workspaceState.canOpenParallelReader
                        ? workspaceCubit.openParallelReader
                        : null,
                  ),
                ],
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: BlocBuilder<BibleWorkspaceCubit, BibleWorkspaceState>(
          builder: (context, workspaceState) {
            return _BibleReadersArea(workspaceState: workspaceState);
          },
        ),
      ),
    );
  }
}

class _BibleReadersArea extends StatefulWidget {
  const _BibleReadersArea({required this.workspaceState});

  final BibleWorkspaceState workspaceState;

  @override
  State<_BibleReadersArea> createState() => _BibleReadersAreaState();
}

class _BibleReadersAreaState extends State<_BibleReadersArea> {
  final _BibleLinkedScrollCoordinator _scrollCoordinator =
      _BibleLinkedScrollCoordinator();
  double? _lastLayoutWidth;
  double? _lastLayoutHeight;
  bool? _lastLinkedNavigation;

  @override
  Widget build(BuildContext context) {
    final paneIds = widget.workspaceState.paneIds;
    _scrollCoordinator.linkedNavigation =
        widget.workspaceState.hasMultiplePanes &&
        widget.workspaceState.linkedNavigation;

    if (paneIds.isEmpty) {
      return _BibleLoadingMessage(
        message: AppLocalizations.of(context)!.bible_loading,
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        _schedulePostLayoutScrollSyncIfNeeded(constraints, paneIds.length);
        if (paneIds.length == 1) {
          return _buildPane(context, paneIds.first);
        }

        final horizontal =
            constraints.maxWidth >=
            (_kParallelPaneMinWidth * paneIds.length) +
                (_kParallelPaneGap * (paneIds.length - 1));
        if (horizontal) {
          return Row(
            key: const Key('bible_parallel_layout_horizontal'),
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (var index = 0; index < paneIds.length; index++) ...[
                if (index > 0) const SizedBox(width: _kParallelPaneGap),
                _buildExpandedPane(context, paneIds[index]),
              ],
            ],
          );
        }

        return Column(
          key: const Key('bible_parallel_layout_vertical'),
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            for (var index = 0; index < paneIds.length; index++) ...[
              if (index > 0) const SizedBox(height: _kParallelPaneGap),
              _buildExpandedPane(context, paneIds[index]),
            ],
          ],
        );
      },
    );
  }

  Widget _buildExpandedPane(BuildContext context, String paneId) {
    return Expanded(
      key: Key('bible_reader_slot_$paneId'),
      child: _buildPane(context, paneId),
    );
  }

  Widget _buildPane(BuildContext context, String paneId) {
    final colorScheme = Theme.of(context).colorScheme;
    final workspaceCubit = context.read<BibleWorkspaceCubit>();
    return KeyedSubtree(
      key: Key('bible_reader_root_$paneId'),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: colorScheme.surface,
          border: Border.all(color: colorScheme.outlineVariant),
          borderRadius: BorderRadius.circular(8),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: BlocProvider<BibleReaderCubit>.value(
            value: workspaceCubit.readerCubitFor(paneId),
            child: _BibleReaderPane(
              paneId: paneId,
              workspaceState: widget.workspaceState,
              scrollCoordinator: _scrollCoordinator,
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _scrollCoordinator.dispose();
    super.dispose();
  }

  void _schedulePostLayoutScrollSyncIfNeeded(
    BoxConstraints constraints,
    int paneCount,
  ) {
    final linkedNavigation = _scrollCoordinator.linkedNavigation;
    if (!linkedNavigation || paneCount <= 1) {
      _lastLinkedNavigation = linkedNavigation;
      _lastLayoutWidth = constraints.maxWidth;
      _lastLayoutHeight = constraints.maxHeight;
      return;
    }

    final layoutChanged =
        _lastLayoutWidth != constraints.maxWidth ||
        _lastLayoutHeight != constraints.maxHeight ||
        _lastLinkedNavigation != linkedNavigation;
    _lastLinkedNavigation = linkedNavigation;
    _lastLayoutWidth = constraints.maxWidth;
    _lastLayoutHeight = constraints.maxHeight;

    if (layoutChanged) {
      _scrollCoordinator.scheduleSyncFromLastSource();
    }
  }
}

class _BibleReaderPane extends StatelessWidget {
  const _BibleReaderPane({
    required this.paneId,
    required this.workspaceState,
    required this.scrollCoordinator,
  });

  final String paneId;
  final BibleWorkspaceState workspaceState;
  final _BibleLinkedScrollCoordinator scrollCoordinator;

  @override
  Widget build(BuildContext context) {
    return KeyedSubtree(
      key: Key('bible_reader_pane_$paneId'),
      child: BlocBuilder<BibleReaderCubit, BibleReaderState>(
        builder: (context, state) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _BibleReaderToolbar(
                state: state,
                canClosePane: paneId != BibleWorkspaceCubit.primaryPaneId,
                onClosePane: () {
                  unawaited(
                    context.read<BibleWorkspaceCubit>().closeReaderPane(paneId),
                  );
                },
              ),
              _BibleProgressLine(state: state),
              Expanded(
                child: _BibleReaderBody(
                  paneId: paneId,
                  state: state,
                  scrollCoordinator: scrollCoordinator,
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _BibleReaderToolbar extends StatelessWidget {
  const _BibleReaderToolbar({
    required this.state,
    required this.canClosePane,
    required this.onClosePane,
  });

  final BibleReaderState state;
  final bool canClosePane;
  final VoidCallback onClosePane;

  @override
  Widget build(BuildContext context) {
    final map = state.verseMap;
    final reference = state.selectedReference;
    final selectedModule = state.selectedModule;
    final localizations = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;

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
    final readerCubit = context.read<BibleReaderCubit>();
    final toolbarActions = <_BibleToolbarAction>[
      _BibleToolbarAction(
        id: 'module',
        width: 124,
        inline: _ToolbarDropdown<BibleModuleInfo>(
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
              unawaited(readerCubit.selectModule(module));
            }
          },
        ),
        menuIcon: Icons.storage,
        menuLabel: localizations.bible_module,
        menuValue: selectedModule.displayTitle,
        enabled: !state.isBusy,
        onMenuSelected: (context) async {
          final module = await _showToolbarChoiceDialog<BibleModuleInfo>(
            context: context,
            title: localizations.bible_module,
            values: state.modules,
            selectedValue: selectedModule,
            labelFor: (module) => module.displayTitle,
          );
          if (module != null) {
            unawaited(readerCubit.selectModule(module));
          }
        },
      ),
      _BibleToolbarAction(
        id: 'module_info',
        width: 44,
        inline: IconButton(
          key: const Key('bible_module_info_button'),
          icon: const Icon(Icons.info_outline),
          tooltip: localizations.bible_module_info,
          color: colorScheme.primary,
          onPressed: state.isBusy
              ? null
              : () => _showBibleModuleInfoDialog(context, selectedModule),
        ),
        menuIcon: Icons.info_outline,
        menuLabel: localizations.bible_module_info,
        enabled: !state.isBusy,
        onMenuSelected: (context) {
          _showBibleModuleInfoDialog(context, selectedModule);
        },
      ),
      _BibleToolbarAction(
        id: 'search',
        width: 44,
        inline: IconButton(
          key: const Key('bible_search_button'),
          icon: const Icon(Icons.manage_search),
          tooltip: localizations.bible_search_in_module,
          color: colorScheme.primary,
          onPressed: state.isBusy
              ? null
              : () => unawaited(
                  _showBibleSearchDialog(context, selectedModule, readerCubit),
                ),
        ),
        menuIcon: Icons.manage_search,
        menuLabel: localizations.bible_search_in_module,
        enabled: !state.isBusy,
        onMenuSelected: (context) {
          unawaited(
            _showBibleSearchDialog(context, selectedModule, readerCubit),
          );
        },
      ),
      _BibleToolbarAction(
        id: 'book',
        width: 194,
        inline: _ToolbarDropdown<int>(
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
                readerCubit.selectReference(
                  bookId: bookId,
                  chapter: 1,
                  verse: 1,
                ),
              );
            }
          },
        ),
        menuIcon: Icons.menu_book,
        menuLabel: localizations.bible_book,
        menuValue: localizedBibleBookName(localizations, reference.bookId),
        enabled: !state.isBusy,
        onMenuSelected: (context) async {
          final bookId = await _showToolbarChoiceDialog<int>(
            context: context,
            title: localizations.bible_book,
            values: map.bookIds,
            selectedValue: reference.bookId,
            labelFor: (bookId) => localizedBibleBookName(localizations, bookId),
          );
          if (bookId != null) {
            unawaited(
              readerCubit.selectReference(bookId: bookId, chapter: 1, verse: 1),
            );
          }
        },
      ),
      _BibleToolbarAction(
        id: 'chapter',
        width: 104,
        inline: _ToolbarDropdown<int>(
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
                readerCubit.selectReference(
                  bookId: reference.bookId,
                  chapter: chapter,
                  verse: 1,
                ),
              );
            }
          },
        ),
        menuIcon: Icons.view_agenda_outlined,
        menuLabel: localizations.bible_chapter,
        menuValue: reference.chapter.toString(),
        enabled: !state.isBusy,
        onMenuSelected: (context) async {
          final chapter = await _showToolbarChoiceDialog<int>(
            context: context,
            title: localizations.bible_chapter,
            values: [
              for (var chapter = 1; chapter <= chapterCount; chapter++) chapter,
            ],
            selectedValue: reference.chapter,
            labelFor: (chapter) => chapter.toString(),
          );
          if (chapter != null) {
            unawaited(
              readerCubit.selectReference(
                bookId: reference.bookId,
                chapter: chapter,
                verse: 1,
              ),
            );
          }
        },
      ),
      _BibleToolbarAction(
        id: 'verse',
        width: 96,
        inline: _ToolbarDropdown<int>(
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
                readerCubit.selectReference(
                  bookId: reference.bookId,
                  chapter: reference.chapter,
                  verse: verse,
                ),
              );
            }
          },
        ),
        menuIcon: Icons.format_list_numbered,
        menuLabel: localizations.bible_verse,
        menuValue: reference.verse.toString(),
        enabled: !state.isBusy,
        onMenuSelected: (context) async {
          final verse = await _showToolbarChoiceDialog<int>(
            context: context,
            title: localizations.bible_verse,
            values: [for (var verse = 1; verse <= verseCount; verse++) verse],
            selectedValue: reference.verse,
            labelFor: (verse) => verse.toString(),
          );
          if (verse != null) {
            unawaited(
              readerCubit.selectReference(
                bookId: reference.bookId,
                chapter: reference.chapter,
                verse: verse,
              ),
            );
          }
        },
      ),
      _BibleToolbarAction(
        id: 'previous_chapter',
        width: 44,
        inline: IconButton(
          key: const Key('bible_previous_chapter_button'),
          icon: const Icon(Icons.chevron_left),
          tooltip: localizations.bible_previous_chapter,
          color: colorScheme.primary,
          onPressed: !state.isBusy && state.canNavigateBackward
              ? () {
                  unawaited(readerCubit.navigateChapter(forward: false));
                }
              : null,
        ),
        menuIcon: Icons.chevron_left,
        menuLabel: localizations.bible_previous_chapter,
        enabled: !state.isBusy && state.canNavigateBackward,
        onMenuSelected: (context) {
          unawaited(readerCubit.navigateChapter(forward: false));
        },
      ),
      _BibleToolbarAction(
        id: 'next_chapter',
        width: 44,
        inline: IconButton(
          key: const Key('bible_next_chapter_button'),
          icon: const Icon(Icons.chevron_right),
          tooltip: localizations.bible_next_chapter,
          color: colorScheme.primary,
          onPressed: !state.isBusy && state.canNavigateForward
              ? () {
                  unawaited(readerCubit.navigateChapter(forward: true));
                }
              : null,
        ),
        menuIcon: Icons.chevron_right,
        menuLabel: localizations.bible_next_chapter,
        enabled: !state.isBusy && state.canNavigateForward,
        onMenuSelected: (context) {
          unawaited(readerCubit.navigateChapter(forward: true));
        },
      ),
      _BibleToolbarAction(
        id: 'strong_numbers',
        width: 44,
        inline: IconButton(
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
          onPressed: readerCubit.toggleStrongNumbers,
        ),
        menuIcon: Icons.local_offer,
        menuLabel: localizations.toggle_show_strong_numbers,
        active: state.showStrongNumbers,
        onMenuSelected: (context) {
          readerCubit.toggleStrongNumbers();
        },
      ),
      _BibleToolbarAction(
        id: 'copy_selection',
        width: 44,
        inline: IconButton(
          key: const Key('bible_copy_selection_button'),
          icon: const Icon(Icons.content_copy),
          tooltip: localizations.bible_copy_selected_verses,
          color: colorScheme.primary,
          onPressed: state.hasSelectedVerses
              ? () => unawaited(_copySelectedVerses(context, state))
              : null,
        ),
        menuIcon: Icons.content_copy,
        menuLabel: localizations.bible_copy_selected_verses,
        enabled: state.hasSelectedVerses,
        onMenuSelected: (context) {
          unawaited(_copySelectedVerses(context, state));
        },
      ),
      if (canClosePane)
        _BibleToolbarAction(
          id: 'close_pane',
          width: 44,
          inline: IconButton(
            key: const Key('bible_close_parallel_reader_button'),
            icon: const Icon(Icons.close),
            tooltip: localizations.bible_close_parallel_reader,
            color: colorScheme.primary,
            onPressed: onClosePane,
          ),
          menuIcon: Icons.close,
          menuLabel: localizations.bible_close_parallel_reader,
          onMenuSelected: (context) {
            onClosePane();
          },
        ),
    ];

    return ColoredBox(
      color: colorScheme.surface,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final visibleActions = _visibleToolbarActions(
            toolbarActions,
            constraints.maxWidth - 16,
          );
          final hiddenActions = toolbarActions
              .where((action) => !visibleActions.contains(action))
              .toList(growable: false);

          return Padding(
            padding: const EdgeInsets.fromLTRB(8, 8, 8, 6),
            child: Row(
              children: [
                for (final action in visibleActions)
                  SizedBox(width: action.width, child: action.inline),
                if (hiddenActions.isNotEmpty)
                  _BibleToolbarOverflowMenuButton(actions: hiddenActions),
              ],
            ),
          );
        },
      ),
    );
  }
}

List<_BibleToolbarAction> _visibleToolbarActions(
  List<_BibleToolbarAction> actions,
  double maxWidth,
) {
  if (maxWidth.isInfinite) {
    return actions;
  }

  final fullWidth = actions.fold<double>(
    0,
    (sum, action) => sum + action.width,
  );
  if (fullWidth <= maxWidth) {
    return actions;
  }

  const overflowWidth = 44.0;
  final availableWidth = maxWidth - overflowWidth;
  var usedWidth = 0.0;
  final visibleActions = <_BibleToolbarAction>[];
  for (final action in actions) {
    if (usedWidth + action.width <= availableWidth) {
      visibleActions.add(action);
      usedWidth += action.width;
    }
  }
  return List<_BibleToolbarAction>.unmodifiable(visibleActions);
}

class _BibleToolbarAction {
  const _BibleToolbarAction({
    required this.id,
    required this.width,
    required this.inline,
    required this.menuIcon,
    required this.menuLabel,
    required this.onMenuSelected,
    this.menuValue,
    this.enabled = true,
    this.active = false,
  });

  final String id;
  final double width;
  final Widget inline;
  final IconData menuIcon;
  final String menuLabel;
  final String? menuValue;
  final bool enabled;
  final bool active;
  final FutureOr<void> Function(BuildContext context) onMenuSelected;
}

class _BibleToolbarOverflowMenuButton extends StatelessWidget {
  const _BibleToolbarOverflowMenuButton({required this.actions});

  final List<_BibleToolbarAction> actions;

  @override
  Widget build(BuildContext context) {
    final menuKey = GlobalKey();
    final colorScheme = Theme.of(context).colorScheme;
    return IconButton(
      key: menuKey,
      icon: const Icon(Icons.more_vert),
      tooltip: AppLocalizations.of(context)!.menu,
      color: colorScheme.primary,
      onPressed: () async {
        final button = menuKey.currentContext!.findRenderObject() as RenderBox;
        final overlay =
            Overlay.of(context).context.findRenderObject() as RenderBox;
        final selectedActionId = await showMenu<String>(
          context: context,
          position: RelativeRect.fromRect(
            Rect.fromPoints(
              button.localToGlobal(Offset.zero, ancestor: overlay),
              button.localToGlobal(
                button.size.bottomRight(Offset.zero),
                ancestor: overlay,
              ),
            ),
            Offset.zero & overlay.size,
          ),
          items: [
            for (final action in actions)
              PopupMenuItem<String>(
                key: Key('bible_toolbar_menu_${action.id}'),
                value: action.id,
                enabled: action.enabled,
                child: _ToolbarMenuRow(action: action),
              ),
          ],
        );
        if (!context.mounted || selectedActionId == null) {
          return;
        }
        final selectedAction = actions.firstWhere(
          (action) => action.id == selectedActionId,
        );
        await selectedAction.onMenuSelected(context);
      },
    );
  }
}

class _ToolbarMenuRow extends StatelessWidget {
  const _ToolbarMenuRow({required this.action});

  final _BibleToolbarAction action;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final iconColor = action.enabled
        ? colorScheme.primary
        : colorScheme.onSurface.withValues(alpha: 0.38);
    final icon = Icon(action.menuIcon, color: iconColor);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (action.active && action.enabled)
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: colorScheme.secondaryContainer,
            ),
            child: icon,
          )
        else
          icon,
        const SizedBox(width: 10),
        Flexible(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(action.menuLabel, overflow: TextOverflow.ellipsis),
              if (action.menuValue != null)
                Text(
                  action.menuValue!,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

Future<T?> _showToolbarChoiceDialog<T>({
  required BuildContext context,
  required String title,
  required List<T> values,
  required T selectedValue,
  required String Function(T value) labelFor,
}) {
  final colorScheme = Theme.of(context).colorScheme;
  return showDialog<T>(
    context: context,
    builder: (context) {
      final mediaSize = MediaQuery.sizeOf(context);
      final availableWidth =
          mediaSize.width - _kToolbarChoiceDialogHorizontalMargin;
      final contentWidth =
          (availableWidth < _kToolbarChoiceDialogMinWidth
                  ? _kToolbarChoiceDialogMinWidth
                  : availableWidth > _kToolbarChoiceDialogMaxWidth
                  ? _kToolbarChoiceDialogMaxWidth
                  : availableWidth)
              .toDouble();
      final maxHeight = mediaSize.height * 0.72;
      final valuesHeight = values.isEmpty
          ? _kToolbarChoiceRowHeight
          : values.length * _kToolbarChoiceRowHeight;
      final contentHeight =
          (valuesHeight > maxHeight ? maxHeight : valuesHeight).toDouble();
      return AlertDialog(
        title: Text(title, maxLines: 2, overflow: TextOverflow.ellipsis),
        contentPadding: const EdgeInsets.fromLTRB(0, 12, 0, 12),
        content: SizedBox(
          width: contentWidth,
          height: contentHeight,
          child: ListView.builder(
            itemExtent: _kToolbarChoiceRowHeight,
            itemCount: values.length,
            itemBuilder: (context, index) {
              final value = values[index];
              final selected = value == selectedValue;
              return InkWell(
                onTap: () => Navigator.of(context).pop(value),
                child: SizedBox(
                  height: _kToolbarChoiceRowHeight,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 8,
                    ),
                    child: Row(
                      children: [
                        Icon(
                          selected
                              ? Icons.radio_button_checked
                              : Icons.radio_button_unchecked,
                          size: 18,
                          color: selected
                              ? colorScheme.primary
                              : colorScheme.onSurfaceVariant,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            labelFor(value),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      );
    },
  );
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
  const _BibleReaderBody({
    required this.paneId,
    required this.state,
    required this.scrollCoordinator,
  });

  final String paneId;
  final BibleReaderState state;
  final _BibleLinkedScrollCoordinator scrollCoordinator;

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
      fit: StackFit.expand,
      children: [
        _BibleChapterView(
          key: Key('bible_chapter_view_$paneId'),
          paneId: paneId,
          verses: state.verses,
          selectedVerseKey: state.selectedReference?.verseKey,
          selectedVerseRangeStart: state.selectedVerseRangeStart,
          selectedVerseRangeEnd: state.selectedVerseRangeEnd,
          showStrongNumbers: state.showStrongNumbers,
          onVerseTap: context.read<BibleReaderCubit>().selectLoadedVerse,
          onVerseLongPress: context
              .read<BibleReaderCubit>()
              .extendSelectionToVerse,
          scrollCoordinator: scrollCoordinator,
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

class _BibleLinkedScrollCoordinator {
  final Map<String, _BibleScrollPaneRegistration> _panes =
      <String, _BibleScrollPaneRegistration>{};
  final Map<String, VoidCallback> _listeners = <String, VoidCallback>{};
  final Set<String> _programmaticScrollPaneIds = <String>{};
  final Set<String> _scheduledSourcePaneIds = <String>{};
  bool linkedNavigation = false;
  bool _syncing = false;
  bool _postFrameSyncScheduled = false;
  String? _lastSourcePaneId;

  void register({
    required String paneId,
    required ScrollController controller,
    required int? Function() topVisibleVerse,
    required bool Function(int verse) scrollToVerse,
  }) {
    unregister(paneId);
    void listener() => scheduleSyncFrom(paneId);
    _panes[paneId] = _BibleScrollPaneRegistration(
      controller: controller,
      topVisibleVerse: topVisibleVerse,
      scrollToVerse: scrollToVerse,
    );
    _listeners[paneId] = listener;
    controller.addListener(listener);
  }

  void unregister(String paneId, [ScrollController? controller]) {
    final pane = _panes[paneId];
    if (controller != null && pane != null && pane.controller != controller) {
      return;
    }
    final removedPane = _panes.remove(paneId);
    final listener = _listeners.remove(paneId);
    if (removedPane != null && listener != null) {
      removedPane.controller.removeListener(listener);
    }
  }

  void dispose() {
    for (final paneId in _panes.keys.toList(growable: false)) {
      unregister(paneId);
    }
  }

  void scheduleSyncFromLastSource() {
    if (_postFrameSyncScheduled) {
      return;
    }
    _postFrameSyncScheduled = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _postFrameSyncScheduled = false;
      if (!linkedNavigation) {
        return;
      }
      final sourcePaneId =
          _lastSourcePaneId != null && _panes.containsKey(_lastSourcePaneId)
          ? _lastSourcePaneId!
          : _panes.isEmpty
          ? null
          : _panes.keys.first;
      if (sourcePaneId == null) {
        return;
      }
      syncFrom(sourcePaneId);
    });
  }

  void scheduleSyncFrom(String sourcePaneId) {
    if (_scheduledSourcePaneIds.contains(sourcePaneId)) {
      return;
    }
    _scheduledSourcePaneIds.add(sourcePaneId);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scheduledSourcePaneIds.remove(sourcePaneId);
      syncFrom(sourcePaneId);
    });
  }

  void syncFrom(String sourcePaneId) {
    final sourcePane = _panes[sourcePaneId];
    if (!linkedNavigation ||
        _syncing ||
        _programmaticScrollPaneIds.contains(sourcePaneId) ||
        sourcePane == null ||
        !sourcePane.controller.hasClients) {
      return;
    }

    final sourceVerse = sourcePane.topVisibleVerse();
    if (sourceVerse == null) {
      return;
    }
    _lastSourcePaneId = sourcePaneId;

    _syncing = true;
    try {
      for (final entry in _panes.entries) {
        if (entry.key == sourcePaneId || !entry.value.controller.hasClients) {
          continue;
        }
        _programmaticScrollPaneIds.add(entry.key);
        entry.value.scrollToVerse(sourceVerse);
        _releaseProgrammaticScroll(entry.key);
      }
    } finally {
      _syncing = false;
    }
  }

  void _releaseProgrammaticScroll(String paneId) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _programmaticScrollPaneIds.remove(paneId);
    });
  }
}

class _BibleScrollPaneRegistration {
  const _BibleScrollPaneRegistration({
    required this.controller,
    required this.topVisibleVerse,
    required this.scrollToVerse,
  });

  final ScrollController controller;
  final int? Function() topVisibleVerse;
  final bool Function(int verse) scrollToVerse;
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
    super.key,
    required this.paneId,
    required this.verses,
    required this.selectedVerseKey,
    required this.selectedVerseRangeStart,
    required this.selectedVerseRangeEnd,
    required this.showStrongNumbers,
    required this.onVerseTap,
    required this.onVerseLongPress,
    required this.scrollCoordinator,
  });

  final String paneId;
  final List<BibleChapterVerse> verses;
  final String? selectedVerseKey;
  final int? selectedVerseRangeStart;
  final int? selectedVerseRangeEnd;
  final bool showStrongNumbers;
  final ValueChanged<int> onVerseTap;
  final ValueChanged<int> onVerseLongPress;
  final _BibleLinkedScrollCoordinator scrollCoordinator;

  @override
  State<_BibleChapterView> createState() => _BibleChapterViewState();
}

class _BibleChapterViewState extends State<_BibleChapterView> {
  final ScrollController _scrollController = ScrollController();
  final GlobalKey _viewportKey = GlobalKey();
  final Map<String, GlobalKey> _verseKeys = <String, GlobalKey>{};

  @override
  void initState() {
    super.initState();
    _registerScrollPane();
    _scheduleScrollToSelected();
  }

  @override
  void didUpdateWidget(covariant _BibleChapterView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.paneId != widget.paneId ||
        oldWidget.scrollCoordinator != widget.scrollCoordinator) {
      oldWidget.scrollCoordinator.unregister(
        oldWidget.paneId,
        _scrollController,
      );
      _registerScrollPane();
    }
    if (oldWidget.selectedVerseKey != widget.selectedVerseKey ||
        oldWidget.verses != widget.verses) {
      _scheduleScrollToSelected();
    }
  }

  @override
  void dispose() {
    widget.scrollCoordinator.unregister(widget.paneId, _scrollController);
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    _registerScrollPane();
    final visibleVerseKeys = {
      for (final verse in widget.verses) verse.reference.verseKey,
    };
    _verseKeys.removeWhere(
      (verseKey, _) => !visibleVerseKeys.contains(verseKey),
    );

    return SizedBox.expand(
      key: _viewportKey,
      child: NotificationListener<ScrollNotification>(
        onNotification: (notification) {
          if (notification.depth == 0 &&
              (notification is ScrollUpdateNotification ||
                  notification is ScrollEndNotification)) {
            widget.scrollCoordinator.scheduleSyncFrom(widget.paneId);
          }
          return false;
        },
        child: SingleChildScrollView(
          key: const Key('bible_chapter_verses'),
          controller: _scrollController,
          padding: const EdgeInsets.fromLTRB(14, 12, 14, 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (final verse in widget.verses)
                Builder(
                  builder: (context) {
                    final selected =
                        verse.reference.verseKey == widget.selectedVerseKey;
                    final verseKey = _verseKeys.putIfAbsent(
                      verse.reference.verseKey,
                      () => GlobalKey(),
                    );
                    return _BibleVerseRow(
                      key: verseKey,
                      verse: verse,
                      selected: selected,
                      inSelectionRange: _isVerseInSelectionRange(
                        verse.reference.verse,
                        widget.selectedVerseRangeStart,
                        widget.selectedVerseRangeEnd,
                      ),
                      showStrongNumbers: widget.showStrongNumbers,
                      onTap: () => widget.onVerseTap(verse.reference.verse),
                      onLongPress: () =>
                          widget.onVerseLongPress(verse.reference.verse),
                    );
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _registerScrollPane() {
    widget.scrollCoordinator.register(
      paneId: widget.paneId,
      controller: _scrollController,
      topVisibleVerse: _topVisibleVerse,
      scrollToVerse: _scrollToVerse,
    );
  }

  bool _isVerseInSelectionRange(int verse, int? start, int? end) {
    if (start == null || end == null) {
      return false;
    }
    return verse >= start && verse <= end;
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
      final selectedVerse = _verseForKey(selectedVerseKey);
      if (selectedVerse == null) {
        return;
      }
      _scrollToVerse(selectedVerse, alignment: 0.2);
    });
  }

  int? _topVisibleVerse() {
    final viewportBox = _viewportRenderBox();
    if (viewportBox == null) {
      return null;
    }

    final viewportTop = viewportBox.localToGlobal(Offset.zero).dy;
    final viewportBottom = viewportTop + viewportBox.size.height;
    for (final verse in widget.verses) {
      final verseBox = _verseRenderBox(verse.reference.verseKey);
      if (verseBox == null) {
        continue;
      }

      final verseTop = verseBox.localToGlobal(Offset.zero).dy;
      final verseBottom = verseTop + verseBox.size.height;
      if (verseBottom > viewportTop + 1 && verseTop < viewportBottom - 1) {
        return verse.reference.verse;
      }
    }
    return null;
  }

  bool _scrollToVerse(int verse, {double alignment = 0}) {
    if (!_scrollController.hasClients) {
      return false;
    }

    final verseKey = _verseKeyForVerse(verse);
    final viewportBox = _viewportRenderBox();
    final verseBox = verseKey == null ? null : _verseRenderBox(verseKey);
    if (viewportBox == null || verseBox == null) {
      return false;
    }

    final viewportTop = viewportBox.localToGlobal(Offset.zero).dy;
    final verseTop = verseBox.localToGlobal(Offset.zero).dy;
    final alignmentOffset = viewportBox.size.height * alignment;
    final targetOffset =
        (_scrollController.offset + verseTop - viewportTop - alignmentOffset)
            .clamp(
              _scrollController.position.minScrollExtent,
              _scrollController.position.maxScrollExtent,
            )
            .toDouble();
    if ((_scrollController.offset - targetOffset).abs() <= 1) {
      return true;
    }
    _scrollController.jumpTo(targetOffset);
    return true;
  }

  RenderBox? _viewportRenderBox() {
    final renderObject = _viewportKey.currentContext?.findRenderObject();
    if (renderObject is RenderBox && renderObject.attached) {
      return renderObject;
    }
    return null;
  }

  RenderBox? _verseRenderBox(String verseKey) {
    final renderObject = _verseKeys[verseKey]?.currentContext
        ?.findRenderObject();
    if (renderObject is RenderBox && renderObject.attached) {
      return renderObject;
    }
    return null;
  }

  String? _verseKeyForVerse(int verse) {
    for (final chapterVerse in widget.verses) {
      if (chapterVerse.reference.verse == verse) {
        return chapterVerse.reference.verseKey;
      }
    }
    return null;
  }

  int? _verseForKey(String verseKey) {
    for (final chapterVerse in widget.verses) {
      if (chapterVerse.reference.verseKey == verseKey) {
        return chapterVerse.reference.verse;
      }
    }
    return null;
  }
}

class _BibleVerseRow extends StatelessWidget {
  const _BibleVerseRow({
    required super.key,
    required this.verse,
    required this.selected,
    required this.inSelectionRange,
    required this.showStrongNumbers,
    required this.onTap,
    required this.onLongPress,
  });

  final BibleChapterVerse verse;
  final bool selected;
  final bool inSelectionRange;
  final bool showStrongNumbers;
  final VoidCallback onTap;
  final VoidCallback onLongPress;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textStyle = theme.textTheme.bodyLarge?.copyWith(
      height: 1.28,
      color: colorScheme.onSurface,
    );

    final backgroundColor = selected
        ? colorScheme.primaryContainer.withValues(alpha: 0.42)
        : inSelectionRange
        ? colorScheme.primaryContainer.withValues(alpha: 0.24)
        : Colors.transparent;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 1),
      child: Material(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(6),
        child: InkWell(
          borderRadius: BorderRadius.circular(6),
          onTap: onTap,
          onLongPress: onLongPress,
          child: DecoratedBox(
            decoration: BoxDecoration(
              border: selected
                  ? Border.all(
                      color: colorScheme.primary.withValues(alpha: 0.5),
                    )
                  : null,
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
          ),
        ),
      ),
    );
  }
}

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
    final isStrongToken = bibleStrongTokenPattern.hasMatch(token);
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
            child: MouseRegion(
              cursor: SystemMouseCursors.click,
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: () {
                  unawaited(
                    handleAppLink(context, 'strong:${token.toUpperCase()}'),
                  );
                },
                child: Text(
                  token.toUpperCase(),
                  style: baseStyle?.copyWith(
                    fontSize: (baseStyle.fontSize ?? 16) * 0.58,
                    height: 1,
                    color: colorScheme.primary,
                    fontWeight: FontWeight.w700,
                    decoration: TextDecoration.underline,
                    decorationColor: colorScheme.primary,
                  ),
                ),
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

Future<void> _copySelectedVerses(
  BuildContext context,
  BibleReaderState state,
) async {
  final selectedReference = state.selectedReference;
  final start = state.selectedVerseRangeStart;
  final end = state.selectedVerseRangeEnd;
  if (selectedReference == null || start == null || end == null) {
    return;
  }

  final localizations = AppLocalizations.of(context)!;
  final label = _selectedVerseRangeLabel(localizations, state);
  final selectedVerses = state.verses
      .where((verse) {
        final verseNumber = verse.reference.verse;
        return verseNumber >= start && verseNumber <= end;
      })
      .toList(growable: false);
  if (selectedVerses.isEmpty) {
    return;
  }

  final buffer = StringBuffer(label);
  for (final verse in selectedVerses) {
    buffer
      ..writeln()
      ..write('${verse.reference.verse}. ${plainBibleText(verse.text)}');
  }

  await Clipboard.setData(ClipboardData(text: buffer.toString()));
  if (!context.mounted) {
    return;
  }
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text(localizations.bible_selected_verses_copied)),
  );
}

Future<void> _showBibleSearchDialog(
  BuildContext context,
  BibleModuleInfo module,
  BibleReaderCubit readerCubit,
) async {
  final result = await showDialog<BibleSearchResult>(
    context: context,
    builder: (context) {
      return BibleSearchDialog(
        repository: readerCubit.repository,
        module: module,
      );
    },
  );
  if (result == null || readerCubit.isClosed) {
    return;
  }
  await readerCubit.selectReference(
    bookId: result.reference.bookId,
    chapter: result.reference.chapter,
    verse: result.reference.verse,
  );
}

String _selectedVerseRangeLabel(
  AppLocalizations localizations,
  BibleReaderState state,
) {
  final reference = state.selectedReference!;
  final start = state.selectedVerseRangeStart ?? reference.verse;
  final end = state.selectedVerseRangeEnd ?? reference.verse;
  final bookName = localizedBibleBookName(localizations, reference.bookId);
  final versePart = start == end ? '$start' : '$start-$end';
  return '$bookName ${reference.chapter}:$versePart';
}

void _showBibleModuleInfoDialog(BuildContext context, BibleModuleInfo module) {
  final localizations = AppLocalizations.of(context)!;
  final entries = <({String label, String value})>[
    (label: localizations.bible_module_info_code, value: module.code),
    (label: localizations.bible_module_info_module_id, value: module.moduleId),
    (label: localizations.bible_module_info_title, value: module.title),
    (
      label: localizations.bible_module_info_description,
      value: module.description,
    ),
    (label: localizations.bible_module_info_language, value: module.language),
    (label: localizations.bible_module_info_canon, value: module.canon),
    (
      label: localizations.bible_module_info_versification,
      value: module.versification,
    ),
    (label: localizations.bible_module_info_license, value: module.license),
    (
      label: localizations.bible_module_info_source_summary,
      value: module.sourceSummary,
    ),
  ];

  showDialog<void>(
    context: context,
    builder: (context) {
      final theme = Theme.of(context);
      return AlertDialog(
        key: const Key('bible_module_info_dialog'),
        title: Text(localizations.bible_module_info),
        content: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (final entry in entries) ...[
                  Text(
                    entry.label,
                    style: theme.textTheme.labelLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 2),
                  _ModuleInfoValueText(
                    key: Key('bible_module_info_${entry.label}'),
                    value: entry.value.isEmpty ? '-' : entry.value,
                    style: theme.textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 12),
                ],
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(localizations.close),
          ),
        ],
      );
    },
  );
}

final _httpLinkPattern = RegExp(r'https?:\/\/[^\s]+', caseSensitive: false);

class _ModuleInfoValueText extends StatefulWidget {
  const _ModuleInfoValueText({
    required this.value,
    required this.style,
    super.key,
  });

  final String value;
  final TextStyle? style;

  @override
  State<_ModuleInfoValueText> createState() => _ModuleInfoValueTextState();
}

class _ModuleInfoValueTextState extends State<_ModuleInfoValueText> {
  final List<TapGestureRecognizer> _recognizers = <TapGestureRecognizer>[];
  String? _cachedValue;
  TextStyle? _cachedStyle;
  List<InlineSpan>? _cachedSpans;

  @override
  Widget build(BuildContext context) {
    if (_cachedValue != widget.value || _cachedStyle != widget.style) {
      _disposeRecognizers();
      _cachedValue = widget.value;
      _cachedStyle = widget.style;
      _cachedSpans = _buildSpans(context, widget.value, widget.style);
    }

    return Text.rich(TextSpan(style: widget.style, children: _cachedSpans));
  }

  List<InlineSpan> _buildSpans(
    BuildContext context,
    String value,
    TextStyle? style,
  ) {
    final colorScheme = Theme.of(context).colorScheme;
    final spans = <InlineSpan>[];
    var index = 0;
    for (final match in _httpLinkPattern.allMatches(value)) {
      if (match.start > index) {
        spans.add(TextSpan(text: value.substring(index, match.start)));
      }

      final rawLink = match.group(0)!;
      final link = _trimTrailingLinkPunctuation(rawLink);
      final trailingText = rawLink.substring(link.length);
      final recognizer = TapGestureRecognizer()
        ..onTap = () {
          unawaited(handleAppLink(context, link));
        };
      _recognizers.add(recognizer);
      spans.add(
        TextSpan(
          text: link,
          recognizer: recognizer,
          style: style?.copyWith(
            color: colorScheme.primary,
            decoration: TextDecoration.underline,
            decorationColor: colorScheme.primary,
          ),
        ),
      );
      if (trailingText.isNotEmpty) {
        spans.add(TextSpan(text: trailingText));
      }
      index = match.end;
    }

    if (index < value.length) {
      spans.add(TextSpan(text: value.substring(index)));
    }
    return spans.isEmpty ? [TextSpan(text: value)] : spans;
  }

  String _trimTrailingLinkPunctuation(String link) {
    var end = link.length;
    while (end > 0 && '.,;:)]}'.contains(link[end - 1])) {
      end--;
    }
    return link.substring(0, end);
  }

  void _disposeRecognizers() {
    for (final recognizer in _recognizers) {
      recognizer.dispose();
    }
    _recognizers.clear();
  }

  @override
  void dispose() {
    _disposeRecognizers();
    super.dispose();
  }
}
