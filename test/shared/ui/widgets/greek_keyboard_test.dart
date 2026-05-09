@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/widgets/greek_keyboard.dart';

void main() {
  testWidgets('GreekKeyboardButton inserts letters at the text selection', (
    tester,
  ) async {
    final controller = TextEditingController(text: 'ab');
    final focusNode = FocusNode();
    addTearDown(controller.dispose);
    addTearDown(focusNode.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Center(
            child: TextField(
              controller: controller,
              focusNode: focusNode,
              decoration: InputDecoration(
                suffixIcon: GreekKeyboardButton(
                  controller: controller,
                  focusNode: focusNode,
                  tooltip: 'Greek keyboard',
                ),
              ),
            ),
          ),
        ),
      ),
    );

    focusNode.requestFocus();
    await tester.pump();
    controller.selection = const TextSelection.collapsed(offset: 1);
    await tester.tap(find.byTooltip('Greek keyboard'));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('greek_keyboard_key_α')));
    await tester.pump();

    expect(controller.text, 'aαb');
    expect(controller.selection.baseOffset, 2);
    expect(focusNode.hasFocus, isTrue);
  });
  testWidgets(
    'GreekKeyboardButton appends when the field selection is not collapsed',
    (tester) async {
      final controller = TextEditingController(text: 'seed');
      final focusNode = FocusNode();
      addTearDown(controller.dispose);
      addTearDown(focusNode.dispose);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: TextField(
                controller: controller,
                focusNode: focusNode,
                decoration: InputDecoration(
                  suffixIcon: GreekKeyboardButton(
                    controller: controller,
                    focusNode: focusNode,
                    tooltip: 'Greek keyboard',
                  ),
                ),
              ),
            ),
          ),
        ),
      );

      controller.selection = TextSelection(
        baseOffset: 0,
        extentOffset: controller.text.length,
      );
      await tester.tap(find.byTooltip('Greek keyboard'));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(TextButton).first);
      await tester.pump();
      final textAfterFirstKey = controller.text;

      await tester.tap(find.byType(TextButton).at(1));
      await tester.pump();

      expect(textAfterFirstKey.length, 5);
      expect(controller.text.length, 6);
      expect(controller.text.startsWith('seed'), isTrue);
      expect(controller.selection.baseOffset, controller.text.length);
      expect(focusNode.hasFocus, isTrue);
    },
  );
}
