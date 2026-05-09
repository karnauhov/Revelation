import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_content_service.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strongs_dictionary_cubit.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strongs_dictionary_state.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_dictionary_entry_view.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_number_picker_dialog.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_reference_info_icon.dart';
import 'package:revelation/l10n/app_localizations.dart';

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
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final localizations = AppLocalizations.of(context)!;
    final mediaSize = MediaQuery.sizeOf(context);
    final dialogWidth = (mediaSize.width - 20).clamp(320.0, 800.0).toDouble();
    final dialogHeight = (mediaSize.height - 36).clamp(220.0, 600.0).toDouble();

    return BlocBuilder<StrongsDictionaryCubit, StrongsDictionaryState>(
      builder: (context, state) {
        return AlertDialog(
          insetPadding: const EdgeInsets.symmetric(
            horizontal: 10,
            vertical: 10,
          ),
          backgroundColor: colorScheme.surface,
          shape: RoundedRectangleBorder(
            side: BorderSide(color: colorScheme.primary),
            borderRadius: BorderRadius.circular(8),
          ),
          titlePadding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
          contentPadding: const EdgeInsets.fromLTRB(10, 0, 10, 0),
          actionsPadding: const EdgeInsets.fromLTRB(8, 0, 8, 6),
          title: Center(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ConstrainedBox(
                  constraints: BoxConstraints(maxWidth: dialogWidth - 80),
                  child: Text(
                    localizations.strongsConcordance,
                    textAlign: TextAlign.center,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Transform.translate(
                  offset: const Offset(4, -5),
                  child: StrongReferenceInfoIcon(
                    tooltipKey: _referenceTooltipKey,
                  ),
                ),
              ],
            ),
          ),
          content: SizedBox(
            width: dialogWidth,
            height: dialogHeight,
            child: StrongDictionaryEntryView(
              strongNumber: state.strongNumber,
              markdown: state.displayMarkdown,
              onStrongNumberSelected: (strongNumber) {
                context.read<StrongsDictionaryCubit>().showStrongNumber(
                  localizations: localizations,
                  strongNumber: strongNumber,
                );
              },
              onStrongNumberPickerRequested: _openStrongNumberPicker,
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
    );
  }
}
