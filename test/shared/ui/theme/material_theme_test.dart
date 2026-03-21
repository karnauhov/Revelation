@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/theme/material_theme.dart';

void main() {
  test('getColorTheme selects supported themes and defaults to manuscript', () {
    expect(
      MaterialTheme.getColorTheme('manuscript').primary,
      MaterialTheme.manuscript().primary,
    );
    expect(
      MaterialTheme.getColorTheme('forest').primary,
      MaterialTheme.forest().primary,
    );
    expect(
      MaterialTheme.getColorTheme('sky').primary,
      MaterialTheme.sky().primary,
    );
    expect(
      MaterialTheme.getColorTheme('grape').primary,
      MaterialTheme.grape().primary,
    );
    expect(
      MaterialTheme.getColorTheme('unknown').primary,
      MaterialTheme.manuscript().primary,
    );
  });

  testWidgets('getTextTheme scales body text by selected preset', (
    tester,
  ) async {
    final baseTheme = ThemeData(
      textTheme: const TextTheme(
        bodyMedium: TextStyle(fontSize: 10, letterSpacing: 2),
      ),
    );
    late BuildContext context;

    await tester.pumpWidget(
      MaterialApp(
        theme: baseTheme,
        home: Builder(
          builder: (buildContext) {
            context = buildContext;
            return const SizedBox.shrink();
          },
        ),
      ),
    );

    final small = MaterialTheme.getTextTheme(context, 'small').bodyMedium!;
    final medium = MaterialTheme.getTextTheme(context, 'medium').bodyMedium!;
    final large = MaterialTheme.getTextTheme(context, 'large').bodyMedium!;
    final fallback = MaterialTheme.getTextTheme(context, 'missing').bodyMedium!;

    expect(small.fontSize, 10);
    expect(small.letterSpacing, 2);
    expect(medium.fontSize, 11.5);
    expect(medium.letterSpacing, 2.3);
    expect(large.fontSize, 13);
    expect(large.letterSpacing, 2.6);
    expect(fallback.fontSize, 11.5);
    expect(fallback.letterSpacing, 2.3);
  });

  testWidgets(
    'getScaledTextTheme scales explicit styles and keeps theme defaults',
    (tester) async {
      final baseTheme = ThemeData(
        textTheme: const TextTheme(
          titleMedium: TextStyle(),
          labelSmall: TextStyle(fontSize: 8),
        ),
      );
      late BuildContext context;

      await tester.pumpWidget(
        MaterialApp(
          theme: baseTheme,
          home: Builder(
            builder: (buildContext) {
              context = buildContext;
              return const SizedBox.shrink();
            },
          ),
        ),
      );

      final scaled = MaterialTheme.getScaledTextTheme(context, 1.5);

      expect(scaled.titleMedium?.fontSize, isNotNull);
      expect(scaled.labelSmall?.fontSize, 12);
      expect(scaled.bodyLarge?.fontSize, greaterThan(0));
    },
  );
}
