import 'package:flutter/material.dart';

class ToolbarDropdown<T> extends StatelessWidget {
  const ToolbarDropdown({
    required super.key,
    required this.width,
    required this.label,
    required this.value,
    required this.items,
    required this.onChanged,
    this.enabled = true,
    this.decoration,
  });

  final double width;
  final String label;
  final T value;
  final List<DropdownMenuItem<T>> items;
  final ValueChanged<T?> onChanged;
  final bool enabled;
  final InputDecoration? decoration;

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
        decoration:
            decoration?.copyWith(labelText: label) ??
            InputDecoration(
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
