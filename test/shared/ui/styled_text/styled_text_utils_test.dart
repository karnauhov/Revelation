@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/styled_text/styled_text_utils.dart';
import 'package:styled_text/tags/styled_text_tag_widget_builder.dart';

void main() {
  testWidgets('getStyledText builds StyledText with expected tag handlers', (
    tester,
  ) async {
    final styled = getStyledText(
      '<sup>1</sup> <b>bold</b>',
      const TextStyle(fontSize: 20, letterSpacing: 1),
    );

    expect(styled.text, '<sup>1</sup> <b>bold</b>');
    expect(styled.style?.fontSize, 20);
    expect(styled.tags.keys, containsAll(<String>['sup', 'b']));
    expect(styled.tags['sup'], isA<StyledTextWidgetBuilderTag>());
    expect(styled.tags['b'], isA<StyledTextWidgetBuilderTag>());
  });

  testWidgets('sup tag shifts baseline and shrinks font size', (tester) async {
    final styled = getStyledText('x', const TextStyle(fontSize: 22));
    final supTag = styled.tags['sup']! as StyledTextWidgetBuilderTag;
    late Widget supWidget;

    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) {
            supWidget = supTag.builder(
              context,
              const <String?, String?>{},
              '7',
            );
            return const SizedBox.shrink();
          },
        ),
      ),
    );

    final transform = supWidget as Transform;
    final transformValues = transform.transform.storage;
    final childText = transform.child as Text;

    expect(transformValues[12], 0.5);
    expect(transformValues[13], -4);
    expect(childText.data, '7');
    expect(childText.style?.fontSize, 16);
  });

  testWidgets('default style contract keeps sup and bold formatting stable', (
    tester,
  ) async {
    final styled = getStyledText('x', null);
    final supTag = styled.tags['sup']! as StyledTextWidgetBuilderTag;
    final boldTag = styled.tags['b']! as StyledTextWidgetBuilderTag;
    late Widget supWidget;
    late Widget boldWidget;

    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) {
            supWidget = supTag.builder(
              context,
              const <String?, String?>{},
              '2',
            );
            boldWidget = boldTag.builder(
              context,
              const <String?, String?>{},
              'Word',
            );
            return const SizedBox.shrink();
          },
        ),
      ),
    );

    final supText = (supWidget as Transform).child as Text;
    final boldText = boldWidget as Text;

    expect(supText.style?.fontSize, 12);
    expect(boldText.style?.fontWeight, FontWeight.w700);
  });
}
