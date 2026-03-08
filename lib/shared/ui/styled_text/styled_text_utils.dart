import 'package:flutter/material.dart';
import 'package:styled_text/tags/styled_text_tag_widget_builder.dart';
import 'package:styled_text/widgets/styled_text.dart';

StyledText getStyledText(String text, TextStyle? style) {
  style ??= const TextStyle();
  return StyledText(
    text: text,
    style: style,
    tags: {
      'sup': StyledTextWidgetBuilderTag((_, attributes, textContent) {
        return Transform.translate(
          offset: const Offset(0.5, -4),
          child: Text(
            textContent ?? "",
            style: style?.copyWith(fontSize: (style.fontSize ?? 18) - 6),
          ),
        );
      }),
      'b': StyledTextWidgetBuilderTag((_, attributes, textContent) {
        return Text(
          textContent ?? "",
          style: style?.copyWith(fontWeight: FontWeight.w700),
        );
      }),
    },
  );
}
