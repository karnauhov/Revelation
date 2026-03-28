@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';

import '../../../test_harness/widget_test_harness.dart';

void main() {
  testWidgets('ErrorMessage shows icon and text', (tester) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const ErrorMessage(errorMessage: 'Something went wrong'),
      ),
    );

    expect(find.byIcon(Icons.error_outline), findsOneWidget);
    expect(find.text('Something went wrong'), findsOneWidget);
  });
}
