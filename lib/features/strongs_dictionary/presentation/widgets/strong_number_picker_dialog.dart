import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:revelation/shared/ui/dialogs/revelation_dialog.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/features/strongs_dictionary/domain/services/strong_number_policy.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strong_number_picker_cubit.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strong_number_picker_state.dart';
import 'package:revelation/l10n/app_localizations.dart';

class StrongNumberPickerDialog extends StatelessWidget {
  const StrongNumberPickerDialog({
    required this.entries,
    required this.initialStrongNumber,
    super.key,
  });

  final List<StrongPickerEntry> entries;
  final int initialStrongNumber;

  @override
  Widget build(BuildContext context) {
    return BlocProvider<StrongNumberPickerCubit>(
      create: (_) => StrongNumberPickerCubit(
        entries: entries,
        initialStrongNumber: initialStrongNumber,
      ),
      child: const _StrongNumberPickerDialogContent(),
    );
  }
}

class _StrongNumberPickerDialogContent extends StatefulWidget {
  const _StrongNumberPickerDialogContent();

  @override
  State<_StrongNumberPickerDialogContent> createState() =>
      _StrongNumberPickerDialogContentState();
}

class _StrongNumberPickerDialogContentState
    extends State<_StrongNumberPickerDialogContent> {
  late final TextEditingController _numberController;
  late final FocusNode _numberFocusNode;

  bool _isProgrammaticEdit = false;

  @override
  void initState() {
    super.initState();

    final initialState = context.read<StrongNumberPickerCubit>().state;
    _numberController = TextEditingController(text: initialState.inputText);
    _numberFocusNode = FocusNode();
    _numberController.addListener(_handleNumberChanged);
    _numberFocusNode.addListener(_handleInputFocusChanged);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        return;
      }
      _numberFocusNode.requestFocus();
      _selectAllInputText();
    });
  }

  @override
  void dispose() {
    _numberController.removeListener(_handleNumberChanged);
    _numberFocusNode.removeListener(_handleInputFocusChanged);
    _numberController.dispose();
    _numberFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<StrongNumberPickerCubit, StrongNumberPickerState>(
      listenWhen: (previous, current) =>
          previous.inputText != current.inputText,
      listener: (context, state) {
        if (_numberController.text != state.inputText) {
          _replaceInputText(state.inputText);
        }
      },
      builder: (context, state) {
        return _buildDialog(context, state);
      },
    );
  }

  Widget _buildDialog(BuildContext context, StrongNumberPickerState state) {
    final theme = Theme.of(context);
    final mediaSize = MediaQuery.sizeOf(context);
    final keyboardInset = MediaQuery.viewInsetsOf(context).bottom;
    final availableHeight = mediaSize.height - keyboardInset;
    final keyboardVisible = keyboardInset > 0;
    final isPortrait = mediaSize.height >= mediaSize.width;
    final isMobileLike = mediaSize.shortestSide < 600;
    final localizations = AppLocalizations.of(context)!;
    final selectedEntry = state.selectedEntry;
    final helperText = localizations.strong_picker_unavailable_numbers;
    final helperStyle =
        theme.inputDecorationTheme.helperStyle ?? theme.textTheme.bodySmall;
    final helperPainter = TextPainter(
      text: TextSpan(text: helperText, style: helperStyle),
      textDirection: Directionality.of(context),
      textScaler: MediaQuery.textScalerOf(context),
      maxLines: 1,
    )..layout(maxWidth: mediaSize.width);

    final maxDialogWidth = math.min(mediaSize.width - 16, 980.0);
    final minDialogWidth = math.min(maxDialogWidth, 340.0);
    final desiredDialogWidth = helperPainter.width + 150.0;
    final dialogWidth = desiredDialogWidth
        .clamp(minDialogWidth, maxDialogWidth)
        .toDouble();
    final inputMaxWidth = math.max(220.0, dialogWidth - 56.0);
    final maxContentHeight = math.max(120.0, availableHeight - 180.0);
    double preferredContentHeight;
    if (isMobileLike) {
      if (isPortrait) {
        preferredContentHeight = keyboardVisible ? 250.0 : 320.0;
      } else {
        preferredContentHeight = keyboardVisible ? 170.0 : 240.0;
      }
    } else {
      preferredContentHeight = keyboardVisible ? 260.0 : 340.0;
    }
    final contentHeight = preferredContentHeight
        .clamp(120.0, maxContentHeight)
        .toDouble();
    final showHelperText = contentHeight >= 170.0;
    final showWord = contentHeight >= (isPortrait ? 190.0 : 160.0);

    if (!state.hasEntries) {
      return RevelationDialog(
        constraints: BoxConstraints(
          minWidth: minDialogWidth,
          maxWidth: dialogWidth,
        ),
        title: Text(localizations.strong_number),
        scrollContent: true,
        content: const Text('-'),
        secondaryActions: [
          RevelationDialogAction(
            label: localizations.close,
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      );
    }

    return RevelationDialog(
      constraints: BoxConstraints(
        minWidth: minDialogWidth,
        maxWidth: dialogWidth,
      ),
      title: Text(localizations.strong_number),
      scrollContent: true,
      content: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: dialogWidth),
        child: SizedBox(
          height: contentHeight,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: ConstrainedBox(
                  constraints: BoxConstraints(maxWidth: inputMaxWidth),
                  child: TextField(
                    controller: _numberController,
                    focusNode: _numberFocusNode,
                    autofocus: true,
                    onTap: _selectAllInputText,
                    keyboardType: const TextInputType.numberWithOptions(
                      decimal: false,
                      signed: false,
                    ),
                    textInputAction: TextInputAction.done,
                    inputFormatters: <TextInputFormatter>[
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(
                        StrongNumberPolicy.maxNumber.toString().length,
                      ),
                    ],
                    onSubmitted: (_) => _submitSelection(context),
                    decoration: InputDecoration(
                      labelText: localizations.strong_number,
                      hintText:
                          '${StrongNumberPolicy.minNumber} - ${StrongNumberPolicy.maxNumber}',
                      helperText: showHelperText ? helperText : null,
                      helperMaxLines: 1,
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ),
              ),
              if (showWord) ...[
                const SizedBox(height: 8),
                Expanded(
                  child: ClipRect(
                    child: Center(
                      child: Text(
                        selectedEntry?.word ?? '-',
                        textAlign: TextAlign.center,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
      secondaryActions: [
        RevelationDialogAction(
          label: localizations.cancel,
          onPressed: () => Navigator.of(context).pop(),
        ),
      ],
      primaryAction: RevelationDialogAction(
        label: localizations.dialog_select,
        onPressed: selectedEntry == null
            ? null
            : () => Navigator.of(context).pop(selectedEntry.number),
      ),
    );
  }

  void _handleInputFocusChanged() {
    if (_numberFocusNode.hasFocus) {
      _selectAllInputText();
    }
  }

  void _selectAllInputText() {
    final text = _numberController.text;
    _numberController.selection = TextSelection(
      baseOffset: 0,
      extentOffset: text.length,
    );
  }

  void _handleNumberChanged() {
    if (_isProgrammaticEdit) {
      return;
    }

    final cubit = context.read<StrongNumberPickerCubit>()
      ..updateInputText(_numberController.text);
    if (_numberController.text != cubit.state.inputText) {
      _replaceInputText(cubit.state.inputText);
    }
  }

  void _replaceInputText(String text) {
    _isProgrammaticEdit = true;
    _numberController.value = TextEditingValue(
      text: text,
      selection: TextSelection.collapsed(offset: text.length),
    );
    _isProgrammaticEdit = false;
  }

  void _submitSelection(BuildContext context) {
    final selectedEntry = context
        .read<StrongNumberPickerCubit>()
        .state
        .selectedEntry;
    if (selectedEntry == null) {
      return;
    }
    Navigator.of(context).pop(selectedEntry.number);
  }
}
