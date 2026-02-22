import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';

class StrongNumberPickerDialog extends StatefulWidget {
  final List<GreekStrongPickerEntry> entries;
  final int initialStrongNumber;

  const StrongNumberPickerDialog({
    required this.entries,
    required this.initialStrongNumber,
    super.key,
  });

  @override
  State<StrongNumberPickerDialog> createState() =>
      _StrongNumberPickerDialogState();
}

class _StrongNumberPickerDialogState extends State<StrongNumberPickerDialog> {
  static const int _minStrongNumber = 1;
  static const int _maxStrongNumber = 5624;
  static const int _blockedSingleNumber = 2717;
  static const int _blockedRangeStart = 3203;
  static const int _blockedRangeEnd = 3302;

  late final Map<int, GreekStrongPickerEntry> _entryByNumber;
  late final TextEditingController _numberController;
  late final FocusNode _numberFocusNode;

  int? _currentStrongNumber;
  bool _isProgrammaticEdit = false;

  @override
  void initState() {
    super.initState();

    _entryByNumber = <int, GreekStrongPickerEntry>{
      for (final entry in widget.entries) entry.number: entry,
    };

    final initial = _normalizeToAllowedStrongNumber(widget.initialStrongNumber);
    _currentStrongNumber = _entryByNumber.isEmpty ? null : initial;

    _numberController = TextEditingController(
      text: _currentStrongNumber?.toString() ?? '',
    );
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

  GreekStrongPickerEntry? get _selectedEntry {
    final strongNumber = _currentStrongNumber;
    if (strongNumber == null) {
      return null;
    }
    return _entryByNumber[strongNumber];
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final mediaSize = MediaQuery.sizeOf(context);
    final keyboardInset = MediaQuery.viewInsetsOf(context).bottom;
    final availableHeight = mediaSize.height - keyboardInset;
    final keyboardVisible = keyboardInset > 0;
    final isPortrait = mediaSize.height >= mediaSize.width;
    final isMobileLike = mediaSize.shortestSide < 600;
    final localizations = AppLocalizations.of(context)!;
    final selectedEntry = _selectedEntry;
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

    if (widget.entries.isEmpty) {
      return AlertDialog(
        insetPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        constraints: BoxConstraints(
          minWidth: minDialogWidth,
          maxWidth: dialogWidth,
        ),
        scrollable: true,
        backgroundColor: colorScheme.surface,
        shape: RoundedRectangleBorder(
          side: BorderSide(color: colorScheme.primary),
          borderRadius: BorderRadius.circular(8),
        ),
        title: Text(localizations.strong_number),
        content: const Text('-'),
        actions: [
          TextButton(
            style: TextButton.styleFrom(foregroundColor: colorScheme.primary),
            onPressed: () => Navigator.of(context).pop(),
            child: Text(localizations.close),
          ),
        ],
      );
    }

    return AlertDialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      constraints: BoxConstraints(
        minWidth: minDialogWidth,
        maxWidth: dialogWidth,
      ),
      scrollable: true,
      contentPadding: const EdgeInsets.fromLTRB(12, 10, 12, 4),
      actionsPadding: const EdgeInsets.fromLTRB(8, 0, 8, 4),
      backgroundColor: colorScheme.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: colorScheme.primary),
        borderRadius: BorderRadius.circular(8),
      ),
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
                      LengthLimitingTextInputFormatter(4),
                    ],
                    onSubmitted: (_) => _submitSelection(context),
                    decoration: InputDecoration(
                      labelText: localizations.strong_number,
                      hintText: '1 - 5624',
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
      actions: [
        TextButton(
          style: TextButton.styleFrom(foregroundColor: colorScheme.primary),
          onPressed: () => Navigator.of(context).pop(),
          child: Text(localizations.cancel),
        ),
        TextButton(
          style: TextButton.styleFrom(foregroundColor: colorScheme.primary),
          onPressed: selectedEntry == null
              ? null
              : () => Navigator.of(context).pop(selectedEntry.number),
          child: Text(localizations.ok),
        ),
      ],
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

    final rawText = _numberController.text.trim();
    if (rawText.isEmpty) {
      setState(() {
        _currentStrongNumber = null;
      });
      return;
    }

    final parsed = int.tryParse(rawText);
    if (parsed == null) {
      return;
    }

    final normalized = _normalizeToAllowedStrongNumber(parsed);
    if (normalized.toString() != rawText) {
      _replaceInputText(normalized.toString());
    }

    if (_currentStrongNumber != normalized) {
      setState(() {
        _currentStrongNumber = normalized;
      });
    }
  }

  int _normalizeToAllowedStrongNumber(int value) {
    var normalized = value.clamp(_minStrongNumber, _maxStrongNumber);

    if (normalized == _blockedSingleNumber) {
      normalized = _blockedSingleNumber + 1;
    } else if (normalized >= _blockedRangeStart &&
        normalized <= _blockedRangeEnd) {
      normalized = _blockedRangeEnd + 1;
    }

    normalized = normalized.clamp(_minStrongNumber, _maxStrongNumber);
    return _closestExistingStrongNumber(normalized);
  }

  int _closestExistingStrongNumber(int value) {
    if (_entryByNumber.containsKey(value)) {
      return value;
    }

    for (int offset = 1; offset <= _maxStrongNumber; offset++) {
      final up = value + offset;
      if (up <= _maxStrongNumber && _entryByNumber.containsKey(up)) {
        return up;
      }
      final down = value - offset;
      if (down >= _minStrongNumber && _entryByNumber.containsKey(down)) {
        return down;
      }
    }

    return widget.entries.first.number;
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
    final selectedEntry = _selectedEntry;
    if (selectedEntry == null) {
      return;
    }
    Navigator.of(context).pop(selectedEntry.number);
  }
}
