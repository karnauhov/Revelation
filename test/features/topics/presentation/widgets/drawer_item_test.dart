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

  testWidgets('DrawerItem constrains long labels inside narrow drawers', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 304,
            child: DrawerItem(
              assetPath: 'assets/images/UI/menu.svg',
              text: 'Very long planned feature title that should fit',
              onClick: () {},
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.text('Very long planned feature title that should fit'),
      findsOneWidget,
    );
  });
}
