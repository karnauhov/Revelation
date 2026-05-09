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

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.strongs_dictionary_screen),
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
                if (constraints.maxWidth >= 840) {
                  return Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      SizedBox(width: 340, child: selector),
                      const VerticalDivider(width: 1),
                      Expanded(child: entryView),
                    ],
                  );
                }

                final selectorHeight = (constraints.maxHeight * 0.34)
                    .clamp(150.0, 240.0)
                    .toDouble();
                return Column(
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

class _StrongDictionarySelector extends StatelessWidget {
  const _StrongDictionarySelector({required this.state});

  final StrongsDictionaryState state;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final visibleEntries = state.visiblePickerEntries;

    return ColoredBox(
      color: colorScheme.surface,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
            child: TextField(
              key: const Key('strong_dictionary_search_field'),
              onChanged: context
                  .read<StrongsDictionaryCubit>()
                  .updateSearchQuery,
              onSubmitted: (value) => _submitSearch(context, value),
              textInputAction: TextInputAction.search,
              decoration: InputDecoration(
                labelText: localizations.strong_dictionary_search,
                hintText: 'G3056',
                prefixIcon: const Icon(Icons.search),
                border: const OutlineInputBorder(),
              ),
            ),
          ),
          Expanded(
            child: Builder(
              builder: (context) {
                if (state.pickerEntries.isEmpty) {
                  return _SelectorMessage(
                    text: localizations.strong_dictionary_no_entries,
                  );
                }
                if (visibleEntries.isEmpty) {
                  return _SelectorMessage(
                    text: localizations.strong_dictionary_no_results,
                  );
                }

                return ListView.separated(
                  key: const Key('strong_dictionary_entry_list'),
                  itemCount: visibleEntries.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final entry = visibleEntries[index];
                    final selected = entry.number == state.strongNumber;
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
      for (final entry in state.pickerEntries) {
        if (entry.number == parsedNumber) {
          return entry.number;
        }
      }
    }

    final visibleEntries = state.visiblePickerEntries;
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

    return ListTile(
      key: Key('strong_dictionary_entry_${entry.number}'),
      dense: true,
      selected: selected,
      selectedTileColor: colorScheme.primaryContainer.withValues(alpha: 0.42),
      title: Text(
        entry.word,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: theme.textTheme.bodyLarge?.copyWith(
          fontWeight: selected ? FontWeight.w700 : null,
        ),
      ),
      leading: Text(
        entry.code,
        style: theme.textTheme.labelLarge?.copyWith(
          color: selected ? colorScheme.primary : colorScheme.onSurfaceVariant,
          fontWeight: FontWeight.w700,
        ),
      ),
      onTap: () {
        context.read<StrongsDictionaryCubit>().showStrongNumber(
          localizations: AppLocalizations.of(context)!,
          strongNumber: entry.number,
        );
      },
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
    );
  }
}
