import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_search_result.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_search_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_search_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/bible_book_localization.dart';
import 'package:revelation/shared/ui/widgets/greek_keyboard.dart';

class BibleSearchDialog extends StatelessWidget {
  const BibleSearchDialog({
    required this.repository,
    required this.module,
    super.key,
  });

  final BibleRepository repository;
  final BibleModuleInfo module;

  @override
  Widget build(BuildContext context) {
    return BlocProvider<BibleSearchCubit>(
      create: (_) {
        final cubit = BibleSearchCubit(
          repository: repository,
          moduleFile: module.fileName,
        );
        unawaited(cubit.loadInitial());
        return cubit;
      },
      child: _BibleSearchDialogContent(module: module),
    );
  }
}

class _BibleSearchDialogContent extends StatefulWidget {
  const _BibleSearchDialogContent({required this.module});

  final BibleModuleInfo module;

  @override
  State<_BibleSearchDialogContent> createState() =>
      _BibleSearchDialogContentState();
}

class _BibleSearchDialogContentState extends State<_BibleSearchDialogContent> {
  late final TextEditingController _queryController;
  late final FocusNode _queryFocusNode;
  final MenuController _historyMenuController = MenuController();
  bool _isProgrammaticQueryEdit = false;

  @override
  void initState() {
    super.initState();
    _queryController = TextEditingController();
    _queryFocusNode = FocusNode();
    _queryController.addListener(_handleQueryChanged);
    _queryFocusNode.addListener(_handleQueryFocusChanged);
  }

  @override
  void dispose() {
    _queryController.removeListener(_handleQueryChanged);
    _queryFocusNode.removeListener(_handleQueryFocusChanged);
    _queryController.dispose();
    _queryFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<BibleSearchCubit, BibleSearchState>(
      listenWhen: (previous, current) => previous.query != current.query,
      listener: (context, state) {
        if (_queryController.text != state.query) {
          _replaceQueryText(state.query);
        }
      },
      builder: (context, state) => _buildDialog(context, state),
    );
  }

  Widget _buildDialog(BuildContext context, BibleSearchState state) {
    final localizations = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;
    final mediaSize = MediaQuery.sizeOf(context);
    final keyboardInset = MediaQuery.viewInsetsOf(context).bottom;
    final dialogMaxWidth = math.max(
      280.0,
      math.min(mediaSize.width - 24.0, 760.0),
    );
    final dialogMinWidth = math.min(dialogMaxWidth, 360.0);
    final availableContentHeight = math.max(
      260.0,
      mediaSize.height - keyboardInset - 180.0,
    );
    final contentHeight = math.min(620.0, availableContentHeight);

    return AlertDialog(
      key: const Key('bible_search_dialog'),
      insetPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      constraints: BoxConstraints(
        minWidth: dialogMinWidth,
        maxWidth: dialogMaxWidth,
      ),
      backgroundColor: colorScheme.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: colorScheme.primary),
        borderRadius: BorderRadius.circular(8),
      ),
      title: Text(
        '${localizations.bible_search_dialog_title} '
        '(${widget.module.displayTitle})',
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      contentPadding: const EdgeInsets.fromLTRB(20, 12, 20, 6),
      content: SizedBox(
        width: dialogMaxWidth,
        height: contentHeight,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _BibleSearchToolbar(
              state: state,
              searchField: _buildSearchField(context, state),
              onSearch: () => _submitSearch(context),
              onCopy: state.results.isEmpty
                  ? null
                  : () => _copySelectedOrAll(context, state),
            ),
            const SizedBox(height: 8),
            _BibleSearchSummary(state: state),
            const SizedBox(height: 8),
            Expanded(
              child: _BibleSearchResultsList(
                state: state,
                onToggleSelected: (result) {
                  context.read<BibleSearchCubit>().toggleResultSelection(
                    result.reference.verseKey,
                  );
                },
                onTapResult: (result) =>
                    _handleResultTap(context, state, result),
              ),
            ),
            _BibleSearchPager(state: state),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(localizations.close),
        ),
      ],
    );
  }

  Widget _buildSearchField(BuildContext context, BibleSearchState state) {
    final localizations = AppLocalizations.of(context)!;

    return MenuAnchor(
      controller: _historyMenuController,
      menuChildren: [
        if (state.history.isNotEmpty)
          _BibleSearchHistoryMenu(
            history: state.history,
            onSelected: (query) {
              _historyMenuController.close();
              _replaceQueryText(query);
              context.read<BibleSearchCubit>().updateQuery(query);
              _queryFocusNode.requestFocus();
            },
          ),
      ],
      child: TextField(
        key: const Key('bible_search_query_field'),
        controller: _queryController,
        focusNode: _queryFocusNode,
        autofocus: true,
        maxLines: 1,
        textInputAction: TextInputAction.search,
        onTap: () => _openHistoryMenu(state),
        onSubmitted: (_) => _submitSearch(context),
        decoration: InputDecoration(
          isDense: true,
          labelText: localizations.bible_search_query_label,
          hintText: localizations.bible_search_query_hint,
          prefixIcon: const Icon(Icons.search, size: 20),
          prefixIconConstraints: const BoxConstraints.tightFor(
            width: 40,
            height: 40,
          ),
          suffixIcon: GreekKeyboardButton(
            controller: _queryController,
            focusNode: _queryFocusNode,
            tooltip: localizations.greek_keyboard_tooltip,
          ),
          suffixIconConstraints: const BoxConstraints.tightFor(
            width: 48,
            height: 42,
          ),
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }

  void _handleQueryChanged() {
    if (_isProgrammaticQueryEdit || !mounted) {
      return;
    }
    context.read<BibleSearchCubit>().updateQuery(_queryController.text);
  }

  void _handleQueryFocusChanged() {
    if (!_queryFocusNode.hasFocus || !mounted) {
      return;
    }
    _openHistoryMenu(context.read<BibleSearchCubit>().state);
  }

  void _replaceQueryText(String query) {
    _isProgrammaticQueryEdit = true;
    _queryController.value = TextEditingValue(
      text: query,
      selection: TextSelection.collapsed(offset: query.length),
    );
    _isProgrammaticQueryEdit = false;
  }

  void _openHistoryMenu(BibleSearchState state) {
    if (state.history.isEmpty || _historyMenuController.isOpen) {
      return;
    }
    _historyMenuController.open();
  }

  void _submitSearch(BuildContext context) {
    _historyMenuController.close();
    unawaited(context.read<BibleSearchCubit>().search());
  }

  Future<void> _handleResultTap(
    BuildContext context,
    BibleSearchState state,
    BibleSearchResult result,
  ) async {
    switch (state.resultTapAction) {
      case BibleSearchResultTapAction.copy:
        await _copySingleResult(context, result);
      case BibleSearchResultTapAction.open:
        Navigator.of(context).pop(result);
    }
  }

  Future<void> _copySingleResult(
    BuildContext context,
    BibleSearchResult result,
  ) async {
    final localizations = AppLocalizations.of(context)!;
    final text = '${_referenceLabel(localizations, result)}\n${result.text}';
    await Clipboard.setData(ClipboardData(text: text));
    if (!context.mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(localizations.bible_search_verse_copied)),
    );
  }

  Future<void> _copySelectedOrAll(
    BuildContext context,
    BibleSearchState state,
  ) async {
    final localizations = AppLocalizations.of(context)!;
    final selectedResults = state.selectedResults;
    final text = selectedResults.isEmpty
        ? state.results
              .map((result) => _referenceLabel(localizations, result))
              .join('; ')
        : selectedResults
              .map(
                (result) =>
                    '${_referenceLabel(localizations, result)}\n${result.text}',
              )
              .join('\n\n');
    await Clipboard.setData(ClipboardData(text: text));
    if (!context.mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          selectedResults.isEmpty
              ? localizations.bible_search_references_copied
              : localizations.bible_search_verses_copied,
        ),
      ),
    );
  }
}

class _BibleSearchHistoryMenu extends StatelessWidget {
  const _BibleSearchHistoryMenu({
    required this.history,
    required this.onSelected,
  });

  final List<String> history;
  final ValueChanged<String> onSelected;

  @override
  Widget build(BuildContext context) {
    final height = math.min(240.0, history.length * 42.0);
    return SizedBox(
      width: 360,
      height: height,
      child: ListView.builder(
        key: const Key('bible_search_history_menu'),
        primary: false,
        itemExtent: 42,
        itemCount: history.length,
        itemBuilder: (context, index) {
          final query = history[index];
          return MenuItemButton(
            onPressed: () => onSelected(query),
            child: Text(query, maxLines: 1, overflow: TextOverflow.ellipsis),
          );
        },
      ),
    );
  }
}

const double _kBibleSearchToolbarGap = 8;
const double _kBibleSearchMinFieldWidth = 96;
const double _kBibleSearchFieldMaxWidth = 220;
const double _kBibleSearchButtonWidth = 116;
const double _kBibleSearchActionWidth = 230;
const double _kBibleSearchIconButtonWidth = 44;

enum _BibleSearchToolbarAction { search, resultAction, copyResults }

enum _BibleSearchOverflowAction { search, copyOnTap, openOnTap, copyResults }

class _BibleSearchToolbar extends StatelessWidget {
  const _BibleSearchToolbar({
    required this.state,
    required this.searchField,
    required this.onSearch,
    required this.onCopy,
  });

  final BibleSearchState state;
  final Widget searchField;
  final VoidCallback onSearch;
  final VoidCallback? onCopy;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final maxWidth = constraints.maxWidth.isFinite
            ? constraints.maxWidth
            : 760.0;
        final fieldWidth = _fieldWidthFor(maxWidth);
        final actions = _inlineActions(context);
        final allActionsWidth = _actionsWidth(actions);
        final allInlineWidth =
            fieldWidth + _kBibleSearchToolbarGap + allActionsWidth;
        final hasOverflow = allInlineWidth > maxWidth;
        final availableActionWidth = hasOverflow
            ? math.max(
                0.0,
                maxWidth -
                    fieldWidth -
                    _kBibleSearchToolbarGap -
                    _kBibleSearchIconButtonWidth,
              )
            : allActionsWidth;

        var usedActionWidth = 0.0;
        final visibleActions = <_BibleSearchInlineAction>[];
        final hiddenActions = <_BibleSearchToolbarAction>[];
        for (final action in actions) {
          final nextWidth = visibleActions.isEmpty
              ? action.width
              : usedActionWidth + _kBibleSearchToolbarGap + action.width;
          if (!hasOverflow || nextWidth <= availableActionWidth) {
            visibleActions.add(action);
            usedActionWidth = nextWidth;
          } else {
            hiddenActions.add(action.action);
          }
        }

        final children = <Widget>[
          SizedBox(width: fieldWidth, child: searchField),
        ];
        if (visibleActions.isNotEmpty || hiddenActions.isNotEmpty) {
          children.add(const SizedBox(width: _kBibleSearchToolbarGap));
        }
        for (var index = 0; index < visibleActions.length; index++) {
          if (index > 0) {
            children.add(const SizedBox(width: _kBibleSearchToolbarGap));
          }
          children.add(visibleActions[index].builder(context));
        }
        if (hiddenActions.isNotEmpty) {
          if (visibleActions.isNotEmpty) {
            children.add(const SizedBox(width: _kBibleSearchToolbarGap));
          }
          children.add(
            _BibleSearchOverflowMenu(
              state: state,
              hiddenActions: hiddenActions,
              onSearch: onSearch,
              onCopy: onCopy,
            ),
          );
        }

        return Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: children,
        );
      },
    );
  }

  double _fieldWidthFor(double maxWidth) {
    if (maxWidth <=
        _kBibleSearchMinFieldWidth +
            _kBibleSearchToolbarGap +
            _kBibleSearchIconButtonWidth) {
      return math.max(
        0.0,
        maxWidth - _kBibleSearchToolbarGap - _kBibleSearchIconButtonWidth,
      );
    }
    final preferredWidth = maxWidth >= 680 ? 280.0 : _kBibleSearchFieldMaxWidth;
    final maxWithOverflow =
        maxWidth - _kBibleSearchToolbarGap - _kBibleSearchIconButtonWidth;
    return math
        .max(
          _kBibleSearchMinFieldWidth,
          math.min(preferredWidth, maxWithOverflow),
        )
        .toDouble();
  }

  double _actionsWidth(List<_BibleSearchInlineAction> actions) {
    if (actions.isEmpty) {
      return 0;
    }
    return actions.fold<double>(
      -_kBibleSearchToolbarGap,
      (width, action) => width + _kBibleSearchToolbarGap + action.width,
    );
  }

  List<_BibleSearchInlineAction> _inlineActions(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;

    return [
      _BibleSearchInlineAction(
        action: _BibleSearchToolbarAction.search,
        width: _kBibleSearchButtonWidth,
        builder: (context) => SizedBox(
          width: _kBibleSearchButtonWidth,
          child: FilledButton.icon(
            key: const Key('bible_search_submit_button'),
            onPressed: state.isLoading ? null : onSearch,
            icon: const Icon(Icons.search, size: 18),
            label: Text(
              localizations.bible_search_button,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ),
      ),
      _BibleSearchInlineAction(
        action: _BibleSearchToolbarAction.resultAction,
        width: _kBibleSearchActionWidth,
        builder: (context) => SizedBox(
          width: _kBibleSearchActionWidth,
          child: DropdownButtonFormField<BibleSearchResultTapAction>(
            key: const Key('bible_search_action_dropdown'),
            initialValue: state.resultTapAction,
            isExpanded: true,
            decoration: InputDecoration(
              isDense: true,
              labelText: localizations.bible_search_result_action,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 10,
                vertical: 8,
              ),
              border: const OutlineInputBorder(),
            ),
            items: [
              DropdownMenuItem<BibleSearchResultTapAction>(
                value: BibleSearchResultTapAction.copy,
                child: Text(
                  localizations.bible_search_action_copy,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              DropdownMenuItem<BibleSearchResultTapAction>(
                value: BibleSearchResultTapAction.open,
                child: Text(
                  localizations.bible_search_action_open,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
            onChanged: state.isLoading
                ? null
                : (action) {
                    if (action != null) {
                      context.read<BibleSearchCubit>().setResultTapAction(
                        action,
                      );
                    }
                  },
          ),
        ),
      ),
      _BibleSearchInlineAction(
        action: _BibleSearchToolbarAction.copyResults,
        width: _kBibleSearchIconButtonWidth,
        builder: (context) => SizedBox(
          width: _kBibleSearchIconButtonWidth,
          height: _kBibleSearchIconButtonWidth,
          child: IconButton(
            key: const Key('bible_search_copy_results_button'),
            icon: const Icon(Icons.content_copy),
            tooltip: localizations.bible_search_copy_results,
            color: colorScheme.primary,
            onPressed: state.isLoading ? null : onCopy,
          ),
        ),
      ),
    ];
  }
}

class _BibleSearchInlineAction {
  const _BibleSearchInlineAction({
    required this.action,
    required this.width,
    required this.builder,
  });

  final _BibleSearchToolbarAction action;
  final double width;
  final WidgetBuilder builder;
}

class _BibleSearchOverflowMenu extends StatelessWidget {
  const _BibleSearchOverflowMenu({
    required this.state,
    required this.hiddenActions,
    required this.onSearch,
    required this.onCopy,
  });

  final BibleSearchState state;
  final List<_BibleSearchToolbarAction> hiddenActions;
  final VoidCallback onSearch;
  final VoidCallback? onCopy;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;

    return SizedBox(
      width: _kBibleSearchIconButtonWidth,
      height: _kBibleSearchIconButtonWidth,
      child: PopupMenuButton<_BibleSearchOverflowAction>(
        key: const Key('bible_search_overflow_button'),
        tooltip: localizations.menu,
        icon: Icon(Icons.more_vert, color: colorScheme.primary),
        itemBuilder: (context) => _menuItems(context),
        onSelected: (action) => _handleSelected(context, action),
      ),
    );
  }

  List<PopupMenuEntry<_BibleSearchOverflowAction>> _menuItems(
    BuildContext context,
  ) {
    final localizations = AppLocalizations.of(context)!;
    final items = <PopupMenuEntry<_BibleSearchOverflowAction>>[];
    for (final hiddenAction in hiddenActions) {
      switch (hiddenAction) {
        case _BibleSearchToolbarAction.search:
          items.add(
            PopupMenuItem<_BibleSearchOverflowAction>(
              value: _BibleSearchOverflowAction.search,
              enabled: !state.isLoading,
              child: _BibleSearchOverflowMenuRow(
                icon: Icons.search,
                label: localizations.bible_search_button,
              ),
            ),
          );
        case _BibleSearchToolbarAction.resultAction:
          items
            ..add(
              PopupMenuItem<_BibleSearchOverflowAction>(
                value: _BibleSearchOverflowAction.copyOnTap,
                enabled: !state.isLoading,
                child: _BibleSearchOverflowMenuRow(
                  icon: state.resultTapAction == BibleSearchResultTapAction.copy
                      ? Icons.check
                      : Icons.content_copy,
                  label: localizations.bible_search_action_copy,
                ),
              ),
            )
            ..add(
              PopupMenuItem<_BibleSearchOverflowAction>(
                value: _BibleSearchOverflowAction.openOnTap,
                enabled: !state.isLoading,
                child: _BibleSearchOverflowMenuRow(
                  icon: state.resultTapAction == BibleSearchResultTapAction.open
                      ? Icons.check
                      : Icons.open_in_new,
                  label: localizations.bible_search_action_open,
                ),
              ),
            );
        case _BibleSearchToolbarAction.copyResults:
          items.add(
            PopupMenuItem<_BibleSearchOverflowAction>(
              value: _BibleSearchOverflowAction.copyResults,
              enabled: !state.isLoading && onCopy != null,
              child: _BibleSearchOverflowMenuRow(
                icon: Icons.content_copy,
                label: localizations.bible_search_copy_results,
              ),
            ),
          );
      }
    }
    return items;
  }

  void _handleSelected(
    BuildContext context,
    _BibleSearchOverflowAction action,
  ) {
    switch (action) {
      case _BibleSearchOverflowAction.search:
        if (!state.isLoading) {
          onSearch();
        }
      case _BibleSearchOverflowAction.copyOnTap:
        if (!state.isLoading) {
          context.read<BibleSearchCubit>().setResultTapAction(
            BibleSearchResultTapAction.copy,
          );
        }
      case _BibleSearchOverflowAction.openOnTap:
        if (!state.isLoading) {
          context.read<BibleSearchCubit>().setResultTapAction(
            BibleSearchResultTapAction.open,
          );
        }
      case _BibleSearchOverflowAction.copyResults:
        if (!state.isLoading) {
          onCopy?.call();
        }
    }
  }
}

class _BibleSearchOverflowMenuRow extends StatelessWidget {
  const _BibleSearchOverflowMenuRow({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
      child: Row(
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(label, maxLines: 1, overflow: TextOverflow.ellipsis),
          ),
        ],
      ),
    );
  }
}

class _BibleSearchSummary extends StatelessWidget {
  const _BibleSearchSummary({required this.state});

  final BibleSearchState state;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    if (state.status == BibleSearchStatus.loading) {
      return Row(
        children: [
          const SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              localizations.bible_search_loading,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.bodySmall,
            ),
          ),
        ],
      );
    }

    if (state.status == BibleSearchStatus.failure) {
      return Text(
        state.errorMessage ?? localizations.bible_search_failed,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
        style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.error),
      );
    }

    if (!state.hasSearched) {
      return const SizedBox(height: 18);
    }

    if (state.results.isEmpty) {
      return Text(
        localizations.bible_search_no_results,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: theme.textTheme.bodySmall,
      );
    }

    return Text(
      localizations.bible_search_match_count(
        state.totalMatches,
        state.results.length,
      ),
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      style: theme.textTheme.bodySmall?.copyWith(
        color: colorScheme.onSurfaceVariant,
      ),
    );
  }
}

class _BibleSearchResultsList extends StatelessWidget {
  const _BibleSearchResultsList({
    required this.state,
    required this.onToggleSelected,
    required this.onTapResult,
  });

  final BibleSearchState state;
  final ValueChanged<BibleSearchResult> onToggleSelected;
  final ValueChanged<BibleSearchResult> onTapResult;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    if (state.status == BibleSearchStatus.loading && state.results.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }
    if (!state.hasSearched) {
      return const SizedBox.shrink();
    }
    if (state.results.isEmpty) {
      return Center(child: Text(localizations.bible_search_no_results));
    }

    final pageResults = state.pageResults;
    return ListView.separated(
      key: const Key('bible_search_results_list'),
      primary: false,
      itemCount: pageResults.length,
      separatorBuilder: (_, __) => const SizedBox(height: 4),
      itemBuilder: (context, index) {
        final result = pageResults[index];
        final selected = state.selectedVerseKeys.contains(
          result.reference.verseKey,
        );
        return _BibleSearchResultTile(
          key: Key('bible_search_result_${result.reference.verseKey}'),
          result: result,
          selected: selected,
          onToggleSelected: () => onToggleSelected(result),
          onTap: () => onTapResult(result),
        );
      },
    );
  }
}

class _BibleSearchResultTile extends StatelessWidget {
  const _BibleSearchResultTile({
    required super.key,
    required this.result,
    required this.selected,
    required this.onToggleSelected,
    required this.onTap,
  });

  final BibleSearchResult result;
  final bool selected;
  final VoidCallback onToggleSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final reference = _referenceLabel(AppLocalizations.of(context)!, result);
    final textStyle = theme.textTheme.bodyMedium?.copyWith(
      height: 1.25,
      color: colorScheme.onSurface,
    );

    return Material(
      color: selected
          ? colorScheme.primaryContainer.withValues(alpha: 0.34)
          : colorScheme.surfaceContainerHighest.withValues(alpha: 0.38),
      borderRadius: BorderRadius.circular(6),
      child: InkWell(
        borderRadius: BorderRadius.circular(6),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Checkbox(
                key: Key('bible_search_select_${result.reference.verseKey}'),
                value: selected,
                onChanged: (_) => onToggleSelected(),
                visualDensity: VisualDensity.compact,
              ),
              const SizedBox(width: 4),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      reference,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: colorScheme.primary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text.rich(
                      TextSpan(
                        style: textStyle,
                        children: _highlightedTextSpans(context, result),
                      ),
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
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

class _BibleSearchPager extends StatelessWidget {
  const _BibleSearchPager({required this.state});

  final BibleSearchState state;

  @override
  Widget build(BuildContext context) {
    if (state.pageCount <= 1) {
      return const SizedBox(height: 8);
    }

    final localizations = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          IconButton(
            key: const Key('bible_search_previous_page_button'),
            icon: const Icon(Icons.chevron_left),
            tooltip: localizations.bible_search_previous_page,
            color: colorScheme.primary,
            onPressed: state.canGoPrevious
                ? () => context.read<BibleSearchCubit>().goToPage(
                    state.visiblePageIndex - 1,
                  )
                : null,
          ),
          Flexible(
            child: Text(
              localizations.bible_search_page_label(
                state.pageNumber,
                state.pageCount,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          IconButton(
            key: const Key('bible_search_next_page_button'),
            icon: const Icon(Icons.chevron_right),
            tooltip: localizations.bible_search_next_page,
            color: colorScheme.primary,
            onPressed: state.canGoNext
                ? () => context.read<BibleSearchCubit>().goToPage(
                    state.visiblePageIndex + 1,
                  )
                : null,
          ),
        ],
      ),
    );
  }
}

List<InlineSpan> _highlightedTextSpans(
  BuildContext context,
  BibleSearchResult result,
) {
  final colorScheme = Theme.of(context).colorScheme;
  final spans = <InlineSpan>[];
  var offset = 0;
  for (final match in result.matches) {
    final start = match.start.clamp(0, result.text.length).toInt();
    final end = match.end.clamp(start, result.text.length).toInt();
    if (start > offset) {
      spans.add(TextSpan(text: result.text.substring(offset, start)));
    }
    if (end > start) {
      spans.add(
        TextSpan(
          text: result.text.substring(start, end),
          style: TextStyle(
            color: colorScheme.onTertiaryContainer,
            backgroundColor: colorScheme.tertiaryContainer,
            fontWeight: FontWeight.w700,
          ),
        ),
      );
    }
    offset = end;
  }
  if (offset < result.text.length) {
    spans.add(TextSpan(text: result.text.substring(offset)));
  }
  return spans.isEmpty ? [TextSpan(text: result.text)] : spans;
}

String _referenceLabel(
  AppLocalizations localizations,
  BibleSearchResult result,
) {
  final reference = result.reference;
  return '${localizedBibleBookCode(localizations, reference.bookId)} '
      '${reference.chapter}:${reference.verse}';
}
