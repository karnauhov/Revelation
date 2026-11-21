import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_content_service.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strongs_dictionary_cubit.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strongs_dictionary_state.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_dictionary_entry_view.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_number_picker_dialog.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_reference_info_icon.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/ui/dialogs/study_text_dialog.dart';

Future<BibleVerseMap>? _strongDictionaryDialogVerseMapFuture;

Future<BibleVerseMap> _loadStrongDictionaryDialogVerseMap() {
  return _strongDictionaryDialogVerseMapFuture ??=
      BibleVerseMap.loadFromAssets();
}

Future<void> showStrongDictionaryDialog(
  BuildContext context,
  int initialStrongNumber, {
  StrongsDictionaryContentService? contentService,
}) {
  return showDialog<void>(
    context: context,
    routeSettings: const RouteSettings(name: 'strong_dictionary_dialog'),
    builder: (_) => StrongDictionaryDialog(
      initialStrongNumber: initialStrongNumber,
      contentService: contentService,
    ),
  );
}

class StrongDictionaryDialog extends StatelessWidget {
  const StrongDictionaryDialog({
    required this.initialStrongNumber,
    this.contentService,
    super.key,
  });

  final int initialStrongNumber;
  final StrongsDictionaryContentService? contentService;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final explicitContentService = contentService;
    if (explicitContentService != null) {
      return _StrongDictionaryDialogProvider(
        initialStrongNumber: initialStrongNumber,
        localizations: localizations,
        contentService: explicitContentService,
      );
    }

    return FutureBuilder<BibleVerseMap>(
      future: _loadStrongDictionaryDialogVerseMap(),
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          return _StrongDictionaryDialogProvider(
            initialStrongNumber: initialStrongNumber,
            localizations: localizations,
            contentService: StrongsDictionaryContentService(
              verseMap: snapshot.requireData,
            ),
          );
        }
        if (snapshot.hasError) {
          return _StrongDictionaryDialogProvider(
            initialStrongNumber: initialStrongNumber,
            localizations: localizations,
            contentService: StrongsDictionaryContentService(),
          );
        }
        return const AlertDialog(
          content: SizedBox(
            width: 96,
            height: 96,
            child: Center(child: CircularProgressIndicator()),
          ),
        );
      },
    );
  }
}

class _StrongDictionaryDialogProvider extends StatelessWidget {
  const _StrongDictionaryDialogProvider({
    required this.initialStrongNumber,
    required this.localizations,
    required this.contentService,
  });

  final int initialStrongNumber;
  final AppLocalizations localizations;
  final StrongsDictionaryContentService contentService;

  @override
  Widget build(BuildContext context) {
    return BlocProvider<StrongsDictionaryCubit>(
      create: (_) => StrongsDictionaryCubit(
        initialStrongNumber: initialStrongNumber,
        localizations: localizations,
        contentService: contentService,
      ),
      child: const _StrongDictionaryDialogContent(),
    );
  }
}

class _StrongDictionaryDialogContent extends StatefulWidget {
  const _StrongDictionaryDialogContent();

  @override
  State<_StrongDictionaryDialogContent> createState() =>
      _StrongDictionaryDialogContentState();
}

class _StrongDictionaryDialogContentState
    extends State<_StrongDictionaryDialogContent> {
  final GlobalKey<TooltipState> _referenceTooltipKey =
      GlobalKey<TooltipState>();

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final mediaSize = MediaQuery.sizeOf(context);
    final dialogHeight = (mediaSize.height - 36).clamp(220.0, 600.0).toDouble();

    return BlocBuilder<StrongsDictionaryCubit, StrongsDictionaryState>(
      builder: (context, state) {
        final word = state.pickerEntries
            .where((entry) => entry.number == state.strongNumber)
            .firstOrNull
            ?.word;
        return StudyTextDialog(
          title: localizations.strongs_dictionary_screen,
          subtitle: word == null || word.isEmpty
              ? 'G${state.strongNumber}'
              : 'G${state.strongNumber} · $word',
          titleInfo: StrongReferenceInfoIcon(tooltipKey: _referenceTooltipKey),
          maxWidth: 800,
          content: SizedBox(
            width: 800,
            height: dialogHeight,
            child: StrongDictionaryEntryView(
              strongNumber: state.strongNumber,
              markdown: state.displayMarkdown,
              onStrongNumberSelected: (strongNumber) {
                context.read<StrongsDictionaryCubit>().showStrongNumber(
                  localizations: localizations,
                  strongNumber: strongNumber,
                  clearSearch: true,
                );
              },
              onStrongNumberPickerRequested: _openStrongNumberPicker,
              popBeforeBibleNavigation: true,
              onNavigateBackward: () {
                context.read<StrongsDictionaryCubit>().navigate(
                  localizations: localizations,
                  forward: false,
                );
              },
              onNavigateForward: () {
                context.read<StrongsDictionaryCubit>().navigate(
                  localizations: localizations,
                  forward: true,
                );
              },
            ),
          ),
          actions: [
            TextButton.icon(
              key: const Key('strong_dialog_open_page'),
              icon: const Icon(Icons.open_in_new),
              onPressed: () {
                final router = GoRouter.of(context);
                Navigator.of(context).pop();
                router.push(
                  '/strongs_dictionary?number=G${state.strongNumber}',
                );
              },
              label: Text(localizations.strong_open_dictionary),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text(localizations.close),
            ),
          ],
        );
      },
    );
  }

  Future<void> _openStrongNumberPicker(
    BuildContext dialogContext,
    int initialStrongNumber,
  ) async {
    final localizations = AppLocalizations.of(context)!;
    final cubit = context.read<StrongsDictionaryCubit>();
    final pickedStrongNumber = await showDialog<int>(
      context: dialogContext,
      routeSettings: const RouteSettings(name: 'strong_number_picker_dialog'),
      builder: (_) => StrongNumberPickerDialog(
        entries: cubit.getPickerEntries(),
        initialStrongNumber: initialStrongNumber,
      ),
    );

    if (!mounted || pickedStrongNumber == null) {
      return;
    }

    cubit.showStrongNumber(
      localizations: localizations,
      strongNumber: pickedStrongNumber,
      clearSearch: true,
    );
  }
}
