import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_content_service.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strongs_dictionary_cubit.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strongs_dictionary_state.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_dictionary_entry_view.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_number_picker_dialog.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_reference_info_icon.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/greek_keyboard.dart';

const _strongDictionaryEntryExtent = 36.0;

class StrongsDictionaryScreen extends StatelessWidget {
  const StrongsDictionaryScreen({
    this.initialStrongNumber = 1,
    this.contentService,
    super.key,
  });

  static const iconAssetPath = 'assets/images/UI/dictionary.svg';

  final int initialStrongNumber;
  final StrongsDictionaryContentService? contentService;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;

    return BlocProvider<StrongsDictionaryCubit>(
      create: (_) => StrongsDictionaryCubit(
        initialStrongNumber: initialStrongNumber,
        localizations: localizations,
        contentService: contentService,
      ),
      child: const _StrongsDictionaryScreenContent(),
    );
  }
}

class _StrongsDictionaryScreenContent extends StatefulWidget {
  const _StrongsDictionaryScreenContent();

  @override
  State<_StrongsDictionaryScreenContent> createState() =>
      _StrongsDictionaryScreenContentState();
}

class _StrongsDictionaryScreenContentState
    extends State<_StrongsDictionaryScreenContent> {
  final GlobalKey<TooltipState> _referenceTooltipKey =
      GlobalKey<TooltipState>();

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
              localizations.strongs_dictionary_screen,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                height: 0.9,
              ),
            ),
            Text(
              localizations.strongs_dictionary_header,
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
          StrongReferenceInfoIcon(tooltipKey: _referenceTooltipKey),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: BlocBuilder<StrongsDictionaryCubit, StrongsDictionaryState>(
          builder: (context, state) {
            return LayoutBuilder(
              builder: (context, constraints) {
                final selector = _StrongDictionarySelector(state: state);
                final entryView = _StrongDictionaryPageEntryView(state: state);
                final isLandscape =
                    MediaQuery.of(context).orientation == Orientation.landscape;
                final useSideBySideLayout =
                    isLandscape || constraints.maxWidth >= 840;
                if (useSideBySideLayout) {
                  final selectorWidth = (constraints.maxWidth * 0.38)
                      .clamp(280.0, 380.0)
                      .toDouble();
                  return Row(
                    key: const Key('strong_dictionary_split_view_row'),
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      SizedBox(width: selectorWidth, child: selector),
                      const VerticalDivider(width: 1),
                      Expanded(child: entryView),
                    ],
                  );
                }

                final selectorHeight = (constraints.maxHeight * 0.34)
                    .clamp(150.0, 240.0)
                    .toDouble();
                return Column(
                  key: const Key('strong_dictionary_split_view_column'),
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    SizedBox(height: selectorHeight, child: selector),
                    const Divider(height: 1),
                    Expanded(child: entryView),
                  ],
                );
              },
            );
          },
        ),
      ),
    );
  }
}

class _StrongDictionarySelector extends StatefulWidget {
  const _StrongDictionarySelector({required this.state});

  final StrongsDictionaryState state;

  @override
  State<_StrongDictionarySelector> createState() =>
      _StrongDictionarySelectorState();
}

class _StrongDictionarySelectorState extends State<_StrongDictionarySelector> {
  late final TextEditingController _searchController;
  late final FocusNode _searchFocusNode;
  late final ScrollController _scrollController;

  bool _isProgrammaticSearchEdit = false;

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController(text: widget.state.searchQuery);
    _searchFocusNode = FocusNode();
    _scrollController = ScrollController();
    _searchController.addListener(_handleSearchChanged);
    _scheduleScrollToSelected();
  }

  @override
  void didUpdateWidget(covariant _StrongDictionarySelector oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (_searchController.text != widget.state.searchQuery) {
      _replaceSearchText(widget.state.searchQuery);
    }
    if (oldWidget.state.strongNumber != widget.state.strongNumber ||
        oldWidget.state.searchQuery != widget.state.searchQuery ||
        oldWidget.state.pickerEntries != widget.state.pickerEntries) {
      _scheduleScrollToSelected();
    }
  }

  @override
  void dispose() {
    _searchController.removeListener(_handleSearchChanged);
    _searchController.dispose();
    _searchFocusNode.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final visibleEntries = widget.state.visiblePickerEntries;
    final searchLabelStyle = theme.textTheme.labelSmall?.copyWith(
      fontSize: 13,
      height: 0.95,
      color: colorScheme.onSurfaceVariant,
    );

    return ColoredBox(
      color: colorScheme.surface,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(8, 8, 8, 6),
            child: TextField(
              key: const Key('strong_dictionary_search_field'),
              controller: _searchController,
              focusNode: _searchFocusNode,
              onSubmitted: (value) => _submitSearch(context, value),
              style: theme.textTheme.bodyMedium,
              textInputAction: TextInputAction.search,
              decoration: InputDecoration(
                isDense: true,
                labelText: localizations.strong_dictionary_search,
                labelStyle: searchLabelStyle?.copyWith(fontSize: 14),
                floatingLabelStyle: searchLabelStyle?.copyWith(
                  fontSize: 16,
                  color: colorScheme.primary,
                  fontWeight: FontWeight.w500,
                ),
                hintText: localizations.strong_dictionary_search_hint,
                prefixIcon: const Icon(Icons.search, size: 20),
                prefixIconConstraints: const BoxConstraints.tightFor(
                  width: 40,
                  height: 40,
                ),
                suffixIcon: GreekKeyboardButton(
                  controller: _searchController,
                  focusNode: _searchFocusNode,
                  tooltip: localizations.greek_keyboard_tooltip,
                ),
                suffixIconConstraints: const BoxConstraints.tightFor(
                  width: 48,
                  height: 42,
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 10,
                ),
                border: const OutlineInputBorder(),
              ),
            ),
          ),
          Expanded(
            child: Builder(
              builder: (context) {
                if (widget.state.pickerEntries.isEmpty) {
                  return _SelectorMessage(
                    text: localizations.strong_dictionary_no_entries,
                  );
                }
                if (visibleEntries.isEmpty) {
                  return _SelectorMessage(
                    text: localizations.strong_dictionary_no_results,
                  );
                }

                return ListView.builder(
                  key: const Key('strong_dictionary_entry_list'),
                  controller: _scrollController,
                  itemExtent: _strongDictionaryEntryExtent,
                  itemCount: visibleEntries.length,
                  itemBuilder: (context, index) {
                    final entry = visibleEntries[index];
                    final selected = entry.number == widget.state.strongNumber;
                    return _StrongDictionaryEntryTile(
                      entry: entry,
                      selected: selected,
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _handleSearchChanged() {
    if (_isProgrammaticSearchEdit) {
      return;
    }

    context.read<StrongsDictionaryCubit>().updateSearchQuery(
      _searchController.text,
    );
  }

  void _replaceSearchText(String text) {
    _isProgrammaticSearchEdit = true;
    _searchController.value = TextEditingValue(
      text: text,
      selection: TextSelection.collapsed(offset: text.length),
    );
    _isProgrammaticSearchEdit = false;
  }

  void _scheduleScrollToSelected() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        return;
      }
      _scrollToSelected();
    });
  }

  void _scrollToSelected() {
    if (!_scrollController.hasClients) {
      return;
    }

    final visibleEntries = widget.state.visiblePickerEntries;
    final selectedIndex = visibleEntries.indexWhere(
      (entry) => entry.number == widget.state.strongNumber,
    );
    if (selectedIndex == -1) {
      return;
    }

    final position = _scrollController.position;
    final viewport = position.viewportDimension;
    final target =
        selectedIndex * _strongDictionaryEntryExtent -
        ((viewport - _strongDictionaryEntryExtent) / 2);
    _scrollController.animateTo(
      target
          .clamp(position.minScrollExtent, position.maxScrollExtent)
          .toDouble(),
      duration: const Duration(milliseconds: 160),
      curve: Curves.easeOutCubic,
    );
  }

  void _submitSearch(BuildContext context, String value) {
    final strongNumber = _resolveSubmittedStrongNumber(value);
    if (strongNumber == null) {
      return;
    }

    context.read<StrongsDictionaryCubit>().showStrongNumber(
      localizations: AppLocalizations.of(context)!,
      strongNumber: strongNumber,
    );
  }

  int? _resolveSubmittedStrongNumber(String value) {
    final rawQuery = value.trim().toLowerCase();
    final numberQuery = rawQuery.startsWith('g')
        ? rawQuery.substring(1)
        : rawQuery;
    final parsedNumber = int.tryParse(numberQuery);
    if (parsedNumber != null) {
      for (final entry in widget.state.pickerEntries) {
        if (entry.number == parsedNumber) {
          return entry.number;
        }
      }
    }

    final visibleEntries = widget.state.visiblePickerEntries;
    if (visibleEntries.isEmpty) {
      return null;
    }
    return visibleEntries.first.number;
  }
}

class _StrongDictionaryEntryTile extends StatelessWidget {
  const _StrongDictionaryEntryTile({
    required this.entry,
    required this.selected,
  });

  final StrongPickerEntry entry;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Material(
      key: Key('strong_dictionary_entry_${entry.number}'),
      color: selected
          ? colorScheme.primaryContainer.withValues(alpha: 0.42)
          : colorScheme.surface,
      child: InkWell(
        onTap: () {
          context.read<StrongsDictionaryCubit>().showStrongNumber(
            localizations: AppLocalizations.of(context)!,
            strongNumber: entry.number,
          );
        },
        child: DecoratedBox(
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(color: colorScheme.outlineVariant, width: 1),
            ),
          ),
          child: SizedBox(
            height: _strongDictionaryEntryExtent,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Row(
                children: [
                  SizedBox(
                    width: 42,
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: FittedBox(
                        fit: BoxFit.scaleDown,
                        alignment: Alignment.centerLeft,
                        child: Text(
                          entry.code,
                          maxLines: 1,
                          style: theme.textTheme.labelSmall?.copyWith(
                            fontSize: 12,
                            color: selected
                                ? colorScheme.primary
                                : colorScheme.onSurfaceVariant,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      entry.word,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: selected ? FontWeight.w700 : null,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SelectorMessage extends StatelessWidget {
  const _SelectorMessage({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final colorScheme = Theme.of(context).colorScheme;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Text(
          text,
          textAlign: TextAlign.center,
          style: textTheme.bodyMedium?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
        ),
      ),
    );
  }
}

class _StrongDictionaryPageEntryView extends StatelessWidget {
  const _StrongDictionaryPageEntryView({required this.state});

  final StrongsDictionaryState state;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return DecoratedBox(
      decoration: BoxDecoration(color: colorScheme.surface),
      child: StrongDictionaryEntryView(
        strongNumber: state.strongNumber,
        markdown: state.displayMarkdown,
        padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
        navigationEnabled: state.pickerEntries.isNotEmpty,
        onStrongNumberSelected: (strongNumber) {
          context.read<StrongsDictionaryCubit>().showStrongNumber(
            localizations: AppLocalizations.of(context)!,
            strongNumber: strongNumber,
            clearSearch: true,
          );
        },
        onStrongNumberPickerRequested: (linkContext, strongNumber) {
          _openStrongNumberPicker(context, strongNumber);
        },
        onNavigateBackward: () {
          context.read<StrongsDictionaryCubit>().navigate(
            localizations: AppLocalizations.of(context)!,
            forward: false,
          );
        },
        onNavigateForward: () {
          context.read<StrongsDictionaryCubit>().navigate(
            localizations: AppLocalizations.of(context)!,
            forward: true,
          );
        },
      ),
    );
  }

  Future<void> _openStrongNumberPicker(
    BuildContext context,
    int initialStrongNumber,
  ) async {
    final cubit = context.read<StrongsDictionaryCubit>();
    final pickedStrongNumber = await showDialog<int>(
      context: context,
      routeSettings: const RouteSettings(name: 'strong_number_picker_dialog'),
      builder: (_) => StrongNumberPickerDialog(
        entries: cubit.getPickerEntries(),
        initialStrongNumber: initialStrongNumber,
      ),
    );

    if (!context.mounted || pickedStrongNumber == null) {
      return;
    }

    cubit.showStrongNumber(
      localizations: AppLocalizations.of(context)!,
      strongNumber: pickedStrongNumber,
      clearSearch: true,
    );
  }
}
