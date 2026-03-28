@Tags(['widget'])
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/localization_utils.dart';

import '../../test_harness/widget_test_harness.dart';

void main() {
  testWidgets(
    'locLinks resolves known keys and keeps unknown key as fallback',
    (tester) async {
      final context = await pumpLocalizedContext(
        tester,
        locale: const Locale('en'),
      );
      final localizations = AppLocalizations.of(context)!;

      expect(locLinks(context, '@noun'), localizations.strong_noun);
      expect(
        locLinksByLocalizations(localizations, '@particleNeg'),
        localizations.strong_particleNeg,
      );
      expect(locLinks(context, '@missing_key'), '@missing_key');
    },
  );

  testWidgets('locColorThemes maps all supported keys', (tester) async {
    final context = await pumpLocalizedContext(
      tester,
      locale: const Locale('es'),
    );
    final localizations = AppLocalizations.of(context)!;

    expect(
      locColorThemes(context, 'manuscript'),
      localizations.manuscript_color_theme,
    );
    expect(locColorThemes(context, 'forest'), localizations.forest_color_theme);
    expect(locColorThemes(context, 'sky'), localizations.sky_color_theme);
    expect(locColorThemes(context, 'grape'), localizations.grape_color_theme);
    expect(locColorThemes(context, 'custom-theme'), 'custom-theme');
  });

  testWidgets('locFontSizes maps all supported keys', (tester) async {
    final context = await pumpLocalizedContext(
      tester,
      locale: const Locale('ru'),
    );
    final localizations = AppLocalizations.of(context)!;

    expect(locFontSizes(context, 'small'), localizations.small_font_size);
    expect(locFontSizes(context, 'medium'), localizations.medium_font_size);
    expect(locFontSizes(context, 'large'), localizations.large_font_size);
    expect(locFontSizes(context, 'x-large'), 'x-large');
  });
}
