import 'package:flutter/material.dart';

class GreekKeyboardButton extends StatefulWidget {
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
  State<GreekKeyboardButton> createState() => _GreekKeyboardButtonState();
}

class _GreekKeyboardButtonState extends State<GreekKeyboardButton> {
  final MenuController _menuController = MenuController();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return MenuAnchor(
      controller: _menuController,
      menuChildren: [GreekKeyboardPanel(onKeyPressed: _insertLetter)],
      child: IconButton(
        key: const Key('greek_keyboard_button'),
        tooltip: widget.tooltip,
        visualDensity: VisualDensity.compact,
        padding: EdgeInsets.zero,
        constraints: const BoxConstraints.tightFor(width: 40, height: 40),
        color: colorScheme.primary,
        icon: const Text(
          'Ω',
          style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700),
        ),
        onPressed: () {
          if (_menuController.isOpen) {
            _menuController.close();
          } else {
            _menuController.open();
          }
        },
      ),
    );
  }

  void _insertLetter(String letter) {
    final value = widget.controller.value;
    final text = value.text;
    final selection = value.selection;
    final insertionOffset =
        widget.focusNode.hasFocus && selection.isValid && selection.isCollapsed
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

    widget.focusNode.requestFocus();
    widget.controller.value = value.copyWith(
      text: updatedText,
      selection: updatedSelection,
      composing: TextRange.empty,
    );
    widget.onChanged?.call(updatedText);
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
                padding: const EdgeInsets.all(1),
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
        padding: const EdgeInsets.all(3),
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
      dimension: 28,
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
        child: Text(letter, style: const TextStyle(fontSize: 15)),
      ),
    );
  }
}
