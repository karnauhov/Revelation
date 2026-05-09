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

    controller.selection = const TextSelection.collapsed(offset: 1);
    await tester.tap(find.byTooltip('Greek keyboard'));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('greek_keyboard_key_α')));
    await tester.pump();

    expect(controller.text, 'aαb');
    expect(controller.selection.baseOffset, 2);
    expect(focusNode.hasFocus, isTrue);
  });
}
