@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/topics/presentation/widgets/drawer_item.dart';

void main() {
  testWidgets('DrawerItem renders label and invokes callback on tap', (
    tester,
  ) async {
    var tapped = 0;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: DrawerItem(
            assetPath: 'assets/images/UI/settings.svg',
            text: 'Settings',
            onClick: () {
              tapped += 1;
            },
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Settings'), findsOneWidget);
    expect(find.byType(SvgPicture), findsOneWidget);

    await tester.tap(find.text('Settings'));
    await tester.pumpAndSettle();

    expect(tapped, 1);
  });
}
