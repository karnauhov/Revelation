import 'package:flutter/material.dart';

class GreekKeyboardButton extends StatelessWidget {
  const GreekKeyboardButton({
    required this.controller,
    required this.focusNode,
    required this.tooltip,
    this.onChanged,
    super.key,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final String tooltip;
  final ValueChanged<String>? onChanged;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    // InputDecorator can partially clip its suffix during a route slide.
    // Clip the anchor's semantics before Tooltip/OverlayPortal contributes it.
    return ClipRect(
      child: MenuAnchor(
        menuChildren: [GreekKeyboardPanel(onKeyPressed: _insertLetter)],
        builder: (context, menuController, child) => IconButton(
          key: const Key('greek_keyboard_button'),
          tooltip: tooltip,
          visualDensity: VisualDensity.compact,
          padding: const EdgeInsets.all(2),
          constraints: const BoxConstraints.tightFor(width: 44, height: 42),
          icon: Text(
            'ω',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: colorScheme.primary,
            ),
          ),
          onPressed: () {
            if (menuController.isOpen) {
              menuController.close();
            } else {
              menuController.open();
            }
          },
        ),
      ),
    );
  }

  void _insertLetter(String letter) {
    final value = controller.value;
    final text = value.text;
    final selection = value.selection;
    final insertionOffset =
        focusNode.hasFocus && selection.isValid && selection.isCollapsed
        ? selection.baseOffset.clamp(0, text.length).toInt()
        : text.length;
    final updatedText = text.replaceRange(
      insertionOffset,
      insertionOffset,
      letter,
    );
    final updatedSelection = TextSelection.collapsed(
      offset: insertionOffset + letter.length,
    );

    focusNode.requestFocus();
    controller.value = value.copyWith(
      text: updatedText,
      selection: updatedSelection,
      composing: TextRange.empty,
    );
    onChanged?.call(updatedText);
  }
}

class GreekKeyboardPanel extends StatelessWidget {
  const GreekKeyboardPanel({required this.onKeyPressed, super.key});

  static const letters = <String>[
    'α',
    'β',
    'γ',
    'δ',
    'ε',
    'ζ',
    'η',
    'θ',
    'ι',
    'κ',
    'λ',
    'μ',
    'ν',
    'ξ',
    'ο',
    'π',
    'ρ',
    'σ',
    'τ',
    'υ',
    'φ',
    'χ',
    'ψ',
    'ω',
  ];

  final ValueChanged<String> onKeyPressed;

  @override
  Widget build(BuildContext context) {
    final rows = <Widget>[];
    for (var row = 0; row < 4; row++) {
      rows.add(
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            for (final letter in letters.skip(row * 6).take(6))
              Padding(
                padding: const EdgeInsets.all(1.5),
                child: _GreekKeyboardKey(
                  letter: letter,
                  onPressed: () => onKeyPressed(letter),
                ),
              ),
          ],
        ),
      );
    }

    return Material(
      key: const Key('greek_keyboard_panel'),
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      borderRadius: BorderRadius.circular(6),
      child: Padding(
        padding: const EdgeInsets.all(4),
        child: Column(mainAxisSize: MainAxisSize.min, children: rows),
      ),
    );
  }
}

class _GreekKeyboardKey extends StatelessWidget {
  const _GreekKeyboardKey({required this.letter, required this.onPressed});

  final String letter;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return SizedBox.square(
      dimension: 42,
      child: TextButton(
        key: Key('greek_keyboard_key_$letter'),
        style: TextButton.styleFrom(
          padding: EdgeInsets.zero,
          minimumSize: Size.zero,
          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          visualDensity: VisualDensity.compact,
          foregroundColor: colorScheme.onSurface,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
        ),
        onPressed: onPressed,
        child: Text(letter, style: const TextStyle(fontSize: 22)),
      ),
    );
  }
}
