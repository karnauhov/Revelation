import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart' show RenderTable;
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';

const String _markdownStrongTextFontFamily = 'NotoSans';
const List<String> _markdownStrongTextFontFallback = <String>[
  'NotoSansCoptic',
  'Arimo',
];

// Keep the table within the article viewport. A bare IntrinsicColumnWidth
// makes flutter_markdown_plus put the table in a horizontal scroll view.
class _MarkdownColumnWidth extends TableColumnWidth {
  const _MarkdownColumnWidth();

  static const _content = IntrinsicColumnWidth();

  @override
  double minIntrinsicWidth(Iterable<RenderBox> cells, double containerWidth) {
    final minimum = _content.minIntrinsicWidth(cells, containerWidth);
    final table = cells.firstOrNull?.parent;
    if (table is! RenderTable || !containerWidth.isFinite) return minimum;
    // Let even a long unbroken word wrap on a small screen.
    return math.min(minimum, containerWidth / table.columns);
  }

  @override
  double maxIntrinsicWidth(Iterable<RenderBox> cells, double containerWidth) =>
      math.min(
        _content.maxIntrinsicWidth(cells, containerWidth),
        containerWidth,
      );

  @override
  double? flex(Iterable<RenderBox> cells) {
    final preferred = _content.maxIntrinsicWidth(cells, double.infinity);
    final minimum = _content.minIntrinsicWidth(cells, double.infinity);
    // Only columns with wrappable content need extra space for reading.
    return preferred > minimum ? preferred - minimum : null;
  }
}

MarkdownStyleSheet getMarkdownStyleSheet(
  ThemeData theme,
  ColorScheme colorScheme, {
  FontWeight? h2FontWeight,
}) {
  return MarkdownStyleSheet.fromTheme(theme).copyWith(
    tableColumnWidth: const _MarkdownColumnWidth(),
    p: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurface),
    h1: theme.textTheme.headlineSmall?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h2: theme.textTheme.titleLarge?.copyWith(
      fontWeight: h2FontWeight ?? FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h3: theme.textTheme.titleMedium?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h4: theme.textTheme.titleSmall?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h5: theme.textTheme.bodyLarge?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h6: theme.textTheme.bodyMedium?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    a: TextStyle(
      decoration: TextDecoration.underline,
      decorationColor: colorScheme.primary,
    ).copyWith(color: colorScheme.primary, inherit: true),
    strong: theme.textTheme.bodyMedium?.copyWith(
      fontFamily: _markdownStrongTextFontFamily,
      fontFamilyFallback: _markdownStrongTextFontFallback,
      fontWeight: FontWeight.w600,
      color: colorScheme.onSurface,
    ),
    em: theme.textTheme.bodyMedium?.copyWith(
      fontStyle: FontStyle.italic,
      color: colorScheme.onSurface,
    ),
    listBullet: theme.textTheme.bodyMedium?.copyWith(
      color: colorScheme.onSurface,
    ),
    blockquote: theme.textTheme.bodyMedium?.copyWith(
      fontStyle: FontStyle.italic,
      color: colorScheme.onSurfaceVariant,
    ),
    blockquoteDecoration: BoxDecoration(
      color: colorScheme.surfaceContainer,
      border: Border(left: BorderSide(color: colorScheme.primary, width: 4)),
    ),
    blockquotePadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    code: theme.textTheme.bodySmall?.copyWith(
      fontFamily: 'monospace',
      backgroundColor: colorScheme.surfaceContainerHighest,
      color: colorScheme.onSurface,
    ),
    codeblockDecoration: BoxDecoration(
      color: colorScheme.surfaceContainerHighest,
      borderRadius: BorderRadius.circular(4),
    ),
  );
}
