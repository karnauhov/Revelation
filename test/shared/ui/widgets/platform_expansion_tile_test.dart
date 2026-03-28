@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/widgets/platform_expansion_tile.dart';

void main() {
  testWidgets(
    'PlatformExpansionTile uses Windows replacement and toggles children',
    (tester) async {
      await tester.pumpWidget(
        _buildHost(
          child: const PlatformExpansionTile(
            title: Text('Section'),
            children: [Text('Details')],
          ),
        ),
      );

      expect(find.byType(ExpansionTile), findsNothing);
      expect(find.text('Details'), findsNothing);

      await tester.tap(find.text('Section'));
      await tester.pumpAndSettle();

      expect(find.text('Details'), findsOneWidget);

      await tester.tap(find.text('Section'));
      await tester.pumpAndSettle();

      expect(find.text('Details'), findsNothing);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.windows),
  );

  testWidgets(
    'PlatformExpansionTile uses native ExpansionTile outside Windows',
    (tester) async {
      await tester.pumpWidget(
        _buildHost(
          child: const PlatformExpansionTile(
            title: Text('Section'),
            children: [Text('Details')],
          ),
        ),
      );

      expect(find.byType(ExpansionTile), findsOneWidget);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.android),
  );
}

Widget _buildHost({required Widget child}) {
  return MaterialApp(home: Scaffold(body: child));
}
