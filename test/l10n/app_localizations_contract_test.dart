@Tags(['widget'])
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/l10n/app_localizations_en.dart';
import 'package:revelation/l10n/app_localizations_es.dart';
import 'package:revelation/l10n/app_localizations_ru.dart';
import 'package:revelation/l10n/app_localizations_uk.dart';

import '../test_harness/widget_test_harness.dart';

void main() {
  group('AppLocalizations Locale Contracts', () {
    final localeFactories = <String, AppLocalizations Function()>{
      'en': () => AppLocalizationsEn(),
      'es': () => AppLocalizationsEs(),
      'ru': () => AppLocalizationsRu(),
      'uk': () => AppLocalizationsUk(),
    };

    localeFactories.forEach((code, factory) {
      test(
        '$code exposes non-empty strings and interpolates parameterized messages',
        () {
          final l10n = factory();
          _assertLocalizationContract(l10n);
        },
      );
    });

    test('locale implementations remain distinct for key identity strings', () {
      final appNames = <String>{
        AppLocalizationsEn().app_name,
        AppLocalizationsEs().app_name,
        AppLocalizationsRu().app_name,
        AppLocalizationsUk().app_name,
      };
      expect(
        appNames.length,
        4,
        reason: 'Each locale should keep a distinct app name translation.',
      );
    });

    test('constructors keep canonicalized localeName values', () {
      expect(AppLocalizationsEn('en_US').localeName, 'en_US');
      expect(AppLocalizationsEs('es_ES').localeName, 'es_ES');
      expect(AppLocalizationsRu('ru_RU').localeName, 'ru_RU');
      expect(AppLocalizationsUk('uk_UA').localeName, 'uk_UA');
    });
  });

  group('AppLocalizations Delegate Contracts', () {
    test('supportedLocales expose expected language codes', () {
      expect(
        AppLocalizations.supportedLocales.map((locale) => locale.languageCode),
        <String>['en', 'es', 'ru', 'uk'],
      );
    });

    test('lookupAppLocalizations resolves by languageCode', () {
      expect(
        lookupAppLocalizations(const Locale('en')),
        isA<AppLocalizationsEn>(),
      );
      expect(
        lookupAppLocalizations(const Locale('es')),
        isA<AppLocalizationsEs>(),
      );
      expect(
        lookupAppLocalizations(const Locale('ru')),
        isA<AppLocalizationsRu>(),
      );
      expect(
        lookupAppLocalizations(const Locale('uk')),
        isA<AppLocalizationsUk>(),
      );
    });

    test(
      'lookupAppLocalizations ignores country code for supported languages',
      () {
        expect(
          lookupAppLocalizations(const Locale('en', 'GB')),
          isA<AppLocalizationsEn>(),
        );
        expect(
          lookupAppLocalizations(const Locale('es', 'MX')),
          isA<AppLocalizationsEs>(),
        );
        expect(
          lookupAppLocalizations(const Locale('ru', 'RU')),
          isA<AppLocalizationsRu>(),
        );
        expect(
          lookupAppLocalizations(const Locale('uk', 'UA')),
          isA<AppLocalizationsUk>(),
        );
      },
    );

    test('lookupAppLocalizations throws for unsupported locale', () {
      expect(
        () => lookupAppLocalizations(const Locale('de')),
        throwsA(
          isA<FlutterError>().having(
            (error) => error.message.toString(),
            'message',
            contains('unsupported locale'),
          ),
        ),
      );
    });

    test('delegate reports support contract', () {
      final delegate = AppLocalizations.delegate;

      expect(delegate.isSupported(const Locale('en')), isTrue);
      expect(delegate.isSupported(const Locale('es')), isTrue);
      expect(delegate.isSupported(const Locale('ru')), isTrue);
      expect(delegate.isSupported(const Locale('uk')), isTrue);
      expect(delegate.isSupported(const Locale('de')), isFalse);
      expect(delegate.isSupported(const Locale('fr', 'CA')), isFalse);
    });

    test(
      'delegate load uses synchronous futures and correct mapping',
      () async {
        final delegate = AppLocalizations.delegate;

        final enFuture = delegate.load(const Locale('en'));
        final esFuture = delegate.load(const Locale('es'));
        final ruFuture = delegate.load(const Locale('ru'));
        final ukFuture = delegate.load(const Locale('uk'));

        expect(enFuture, isA<SynchronousFuture<AppLocalizations>>());
        expect(esFuture, isA<SynchronousFuture<AppLocalizations>>());
        expect(ruFuture, isA<SynchronousFuture<AppLocalizations>>());
        expect(ukFuture, isA<SynchronousFuture<AppLocalizations>>());

        expect(await enFuture, isA<AppLocalizationsEn>());
        expect(await esFuture, isA<AppLocalizationsEs>());
        expect(await ruFuture, isA<AppLocalizationsRu>());
        expect(await ukFuture, isA<AppLocalizationsUk>());
      },
    );

    test('delegate shouldReload stays false', () {
      expect(
        AppLocalizations.delegate.shouldReload(AppLocalizations.delegate),
        isFalse,
      );
    });
  });

  group('AppLocalizations Widget Integration', () {
    testWidgets('of(context) resolves locale from localized app tree', (
      tester,
    ) async {
      for (final locale in AppLocalizations.supportedLocales) {
        final context = await pumpLocalizedContext(tester, locale: locale);
        final l10n = AppLocalizations.of(context);

        expect(l10n, isNotNull);
        expect(l10n!.localeName, startsWith(locale.languageCode));
        expect(l10n.app_name, isNotEmpty);

        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pump();
      }
    });

    testWidgets(
      'of(context) returns null when app delegate is not registered',
      (tester) async {
        late BuildContext context;
        await tester.pumpWidget(
          MaterialApp(
            home: Builder(
              builder: (buildContext) {
                context = buildContext;
                return const SizedBox.shrink();
              },
            ),
          ),
        );
        await tester.pump();

        expect(AppLocalizations.of(context), isNull);
      },
    );

    testWidgets('widget tree localization matches direct lookup contract', (
      tester,
    ) async {
      for (final locale in AppLocalizations.supportedLocales) {
        final context = await pumpLocalizedContext(tester, locale: locale);
        final fromTree = AppLocalizations.of(context)!;
        final fromLookup = lookupAppLocalizations(locale);

        expect(fromTree.app_name, fromLookup.app_name);
        expect(fromTree.version, fromLookup.version);
        expect(fromTree.app_version_from, fromLookup.app_version_from);
        expect(
          fromTree.localized_data_update('English'),
          fromLookup.localized_data_update('English'),
        );

        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pump();
      }
    });
  });
}

void _assertLocalizationContract(AppLocalizations l10n) {
  final testLanguage = 'Klingon';
  final testPath = '/tmp/revelation.db';
  expect(l10n.app_name, isNotEmpty, reason: 'app_name should not be empty');
  expect(l10n.version, isNotEmpty, reason: 'version should not be empty');
  expect(
    l10n.app_version_from,
    isNotEmpty,
    reason: 'app_version_from should not be empty',
  );
  expect(
    l10n.common_data_update,
    isNotEmpty,
    reason: 'common_data_update should not be empty',
  );
  expect(
    l10n.data_version_from,
    isNotEmpty,
    reason: 'data_version_from should not be empty',
  );
  expect(
    l10n.language_name_en,
    isNotEmpty,
    reason: 'language_name_en should not be empty',
  );
  expect(
    l10n.language_name_es,
    isNotEmpty,
    reason: 'language_name_es should not be empty',
  );
  expect(
    l10n.language_name_uk,
    isNotEmpty,
    reason: 'language_name_uk should not be empty',
  );
  expect(
    l10n.language_name_ru,
    isNotEmpty,
    reason: 'language_name_ru should not be empty',
  );
  expect(
    l10n.app_description,
    isNotEmpty,
    reason: 'app_description should not be empty',
  );
  expect(l10n.website, isNotEmpty, reason: 'website should not be empty');
  expect(
    l10n.github_project,
    isNotEmpty,
    reason: 'github_project should not be empty',
  );
  expect(
    l10n.privacy_policy,
    isNotEmpty,
    reason: 'privacy_policy should not be empty',
  );
  expect(l10n.license, isNotEmpty, reason: 'license should not be empty');
  expect(l10n.support_us, isNotEmpty, reason: 'support_us should not be empty');
  expect(
    l10n.installation_packages,
    isNotEmpty,
    reason: 'installation_packages should not be empty',
  );
  expect(
    l10n.acknowledgements_title,
    isNotEmpty,
    reason: 'acknowledgements_title should not be empty',
  );
  expect(
    l10n.acknowledgements_description_1,
    isNotEmpty,
    reason: 'acknowledgements_description_1 should not be empty',
  );
  expect(
    l10n.acknowledgements_description_2,
    isNotEmpty,
    reason: 'acknowledgements_description_2 should not be empty',
  );
  expect(
    l10n.recommended_title,
    isNotEmpty,
    reason: 'recommended_title should not be empty',
  );
  expect(
    l10n.recommended_description,
    isNotEmpty,
    reason: 'recommended_description should not be empty',
  );
  expect(l10n.bug_report, isNotEmpty, reason: 'bug_report should not be empty');
  expect(
    l10n.log_copied_message,
    isNotEmpty,
    reason: 'log_copied_message should not be empty',
  );
  expect(
    l10n.bug_report_wish,
    isNotEmpty,
    reason: 'bug_report_wish should not be empty',
  );
  expect(
    l10n.all_rights_reserved,
    isNotEmpty,
    reason: 'all_rights_reserved should not be empty',
  );
  expect(l10n.ad_loading, isNotEmpty, reason: 'ad_loading should not be empty');
  expect(l10n.menu, isNotEmpty, reason: 'menu should not be empty');
  expect(l10n.close_app, isNotEmpty, reason: 'close_app should not be empty');
  expect(l10n.todo, isNotEmpty, reason: 'todo should not be empty');
  expect(
    l10n.primary_sources_screen,
    isNotEmpty,
    reason: 'primary_sources_screen should not be empty',
  );
  expect(
    l10n.primary_sources_header,
    isNotEmpty,
    reason: 'primary_sources_header should not be empty',
  );
  expect(
    l10n.settings_screen,
    isNotEmpty,
    reason: 'settings_screen should not be empty',
  );
  expect(
    l10n.settings_header,
    isNotEmpty,
    reason: 'settings_header should not be empty',
  );
  expect(
    l10n.about_screen,
    isNotEmpty,
    reason: 'about_screen should not be empty',
  );
  expect(
    l10n.about_header,
    isNotEmpty,
    reason: 'about_header should not be empty',
  );
  expect(l10n.download, isNotEmpty, reason: 'download should not be empty');
  expect(
    l10n.download_header,
    isNotEmpty,
    reason: 'download_header should not be empty',
  );
  expect(
    l10n.download_android,
    isNotEmpty,
    reason: 'download_android should not be empty',
  );
  expect(
    l10n.download_windows,
    isNotEmpty,
    reason: 'download_windows should not be empty',
  );
  expect(
    l10n.download_linux,
    isNotEmpty,
    reason: 'download_linux should not be empty',
  );
  expect(
    l10n.download_google_play,
    isNotEmpty,
    reason: 'download_google_play should not be empty',
  );
  expect(
    l10n.download_microsoft_store,
    isNotEmpty,
    reason: 'download_microsoft_store should not be empty',
  );
  expect(
    l10n.download_snapcraft,
    isNotEmpty,
    reason: 'download_snapcraft should not be empty',
  );
  expect(
    l10n.error_loading_libraries,
    isNotEmpty,
    reason: 'error_loading_libraries should not be empty',
  );
  expect(
    l10n.error_loading_institutions,
    isNotEmpty,
    reason: 'error_loading_institutions should not be empty',
  );
  expect(
    l10n.error_loading_recommendations,
    isNotEmpty,
    reason: 'error_loading_recommendations should not be empty',
  );
  expect(
    l10n.error_loading_topics,
    isNotEmpty,
    reason: 'error_loading_topics should not be empty',
  );
  expect(
    l10n.error_loading_primary_sources,
    isNotEmpty,
    reason: 'error_loading_primary_sources should not be empty',
  );
  expect(l10n.changelog, isNotEmpty, reason: 'changelog should not be empty');
  expect(l10n.close, isNotEmpty, reason: 'close should not be empty');
  expect(l10n.error, isNotEmpty, reason: 'error should not be empty');
  expect(l10n.attention, isNotEmpty, reason: 'attention should not be empty');
  expect(l10n.info, isNotEmpty, reason: 'info should not be empty');
  expect(
    l10n.more_information,
    isNotEmpty,
    reason: 'more_information should not be empty',
  );
  expect(
    l10n.unable_to_follow_the_link,
    isNotEmpty,
    reason: 'unable_to_follow_the_link should not be empty',
  );
  expect(l10n.language, isNotEmpty, reason: 'language should not be empty');
  expect(
    l10n.color_theme,
    isNotEmpty,
    reason: 'color_theme should not be empty',
  );
  expect(
    l10n.manuscript_color_theme,
    isNotEmpty,
    reason: 'manuscript_color_theme should not be empty',
  );
  expect(
    l10n.forest_color_theme,
    isNotEmpty,
    reason: 'forest_color_theme should not be empty',
  );
  expect(
    l10n.sky_color_theme,
    isNotEmpty,
    reason: 'sky_color_theme should not be empty',
  );
  expect(
    l10n.grape_color_theme,
    isNotEmpty,
    reason: 'grape_color_theme should not be empty',
  );
  expect(l10n.font_size, isNotEmpty, reason: 'font_size should not be empty');
  expect(
    l10n.small_font_size,
    isNotEmpty,
    reason: 'small_font_size should not be empty',
  );
  expect(
    l10n.medium_font_size,
    isNotEmpty,
    reason: 'medium_font_size should not be empty',
  );
  expect(
    l10n.large_font_size,
    isNotEmpty,
    reason: 'large_font_size should not be empty',
  );
  expect(l10n.sound, isNotEmpty, reason: 'sound should not be empty');
  expect(l10n.on, isNotEmpty, reason: 'on should not be empty');
  expect(l10n.off, isNotEmpty, reason: 'off should not be empty');
  expect(l10n.vectors, isNotEmpty, reason: 'vectors should not be empty');
  expect(l10n.icons, isNotEmpty, reason: 'icons should not be empty');
  expect(l10n.and, isNotEmpty, reason: 'and should not be empty');
  expect(l10n.by, isNotEmpty, reason: 'by should not be empty');
  expect(
    l10n.strongsConcordance,
    isNotEmpty,
    reason: 'strongsConcordance should not be empty',
  );
  expect(l10n.package, isNotEmpty, reason: 'package should not be empty');
  expect(l10n.font, isNotEmpty, reason: 'font should not be empty');
  expect(l10n.wikipedia, isNotEmpty, reason: 'wikipedia should not be empty');
  expect(l10n.intf, isNotEmpty, reason: 'intf should not be empty');
  expect(
    l10n.image_source,
    isNotEmpty,
    reason: 'image_source should not be empty',
  );
  expect(l10n.topic, isNotEmpty, reason: 'topic should not be empty');
  expect(l10n.show_more, isNotEmpty, reason: 'show_more should not be empty');
  expect(l10n.hide, isNotEmpty, reason: 'hide should not be empty');
  expect(
    l10n.full_primary_sources,
    isNotEmpty,
    reason: 'full_primary_sources should not be empty',
  );
  expect(
    l10n.significant_primary_sources,
    isNotEmpty,
    reason: 'significant_primary_sources should not be empty',
  );
  expect(
    l10n.fragments_primary_sources,
    isNotEmpty,
    reason: 'fragments_primary_sources should not be empty',
  );
  expect(l10n.verses, isNotEmpty, reason: 'verses should not be empty');
  expect(
    l10n.choose_page,
    isNotEmpty,
    reason: 'choose_page should not be empty',
  );
  expect(
    l10n.images_are_missing,
    isNotEmpty,
    reason: 'images_are_missing should not be empty',
  );
  expect(
    l10n.image_not_loaded,
    isNotEmpty,
    reason: 'image_not_loaded should not be empty',
  );
  expect(
    l10n.markdown_unknown_block_title,
    isNotEmpty,
    reason: 'markdown_unknown_block_title should not be empty',
  );
  expect(
    l10n.markdown_unknown_block_description('timeline'),
    isNotEmpty,
    reason: 'markdown_unknown_block_description should not be empty',
  );
  expect(
    l10n.markdown_unknown_block_update_hint,
    isNotEmpty,
    reason: 'markdown_unknown_block_update_hint should not be empty',
  );
  expect(
    l10n.markdown_unknown_block_update_action,
    isNotEmpty,
    reason: 'markdown_unknown_block_update_action should not be empty',
  );
  expect(
    l10n.markdown_youtube_player_title,
    isNotEmpty,
    reason: 'markdown_youtube_player_title should not be empty',
  );
  expect(
    l10n.markdown_youtube_unavailable_title,
    isNotEmpty,
    reason: 'markdown_youtube_unavailable_title should not be empty',
  );
  expect(
    l10n.markdown_youtube_unavailable_description,
    isNotEmpty,
    reason: 'markdown_youtube_unavailable_description should not be empty',
  );
  expect(
    l10n.click_for_info,
    isNotEmpty,
    reason: 'click_for_info should not be empty',
  );
  expect(
    l10n.low_quality,
    isNotEmpty,
    reason: 'low_quality should not be empty',
  );
  expect(
    l10n.low_quality_message,
    isNotEmpty,
    reason: 'low_quality_message should not be empty',
  );
  expect(
    l10n.reload_image,
    isNotEmpty,
    reason: 'reload_image should not be empty',
  );
  expect(l10n.zoom_in, isNotEmpty, reason: 'zoom_in should not be empty');
  expect(l10n.zoom_out, isNotEmpty, reason: 'zoom_out should not be empty');
  expect(
    l10n.restore_original_scale,
    isNotEmpty,
    reason: 'restore_original_scale should not be empty',
  );
  expect(
    l10n.toggle_negative,
    isNotEmpty,
    reason: 'toggle_negative should not be empty',
  );
  expect(
    l10n.toggle_monochrome,
    isNotEmpty,
    reason: 'toggle_monochrome should not be empty',
  );
  expect(
    l10n.brightness_contrast,
    isNotEmpty,
    reason: 'brightness_contrast should not be empty',
  );
  expect(l10n.brightness, isNotEmpty, reason: 'brightness should not be empty');
  expect(l10n.contrast, isNotEmpty, reason: 'contrast should not be empty');
  expect(l10n.ok, isNotEmpty, reason: 'ok should not be empty');
  expect(l10n.cancel, isNotEmpty, reason: 'cancel should not be empty');
  expect(l10n.reset, isNotEmpty, reason: 'reset should not be empty');
  expect(l10n.area, isNotEmpty, reason: 'area should not be empty');
  expect(l10n.size, isNotEmpty, reason: 'size should not be empty');
  expect(
    l10n.not_selected,
    isNotEmpty,
    reason: 'not_selected should not be empty',
  );
  expect(
    l10n.area_selection,
    isNotEmpty,
    reason: 'area_selection should not be empty',
  );
  expect(
    l10n.color_replacement,
    isNotEmpty,
    reason: 'color_replacement should not be empty',
  );
  expect(
    l10n.color_to_replace,
    isNotEmpty,
    reason: 'color_to_replace should not be empty',
  );
  expect(l10n.eyedropper, isNotEmpty, reason: 'eyedropper should not be empty');
  expect(l10n.new_color, isNotEmpty, reason: 'new_color should not be empty');
  expect(l10n.palette, isNotEmpty, reason: 'palette should not be empty');
  expect(
    l10n.select_color,
    isNotEmpty,
    reason: 'select_color should not be empty',
  );
  expect(
    l10n.select_area_header,
    isNotEmpty,
    reason: 'select_area_header should not be empty',
  );
  expect(
    l10n.select_area_description,
    isNotEmpty,
    reason: 'select_area_description should not be empty',
  );
  expect(
    l10n.pick_color_header,
    isNotEmpty,
    reason: 'pick_color_header should not be empty',
  );
  expect(
    l10n.pick_color_description,
    isNotEmpty,
    reason: 'pick_color_description should not be empty',
  );
  expect(l10n.tolerance, isNotEmpty, reason: 'tolerance should not be empty');
  expect(
    l10n.replace_color_message,
    isNotEmpty,
    reason: 'replace_color_message should not be empty',
  );
  expect(
    l10n.page_settings_reset,
    isNotEmpty,
    reason: 'page_settings_reset should not be empty',
  );
  expect(
    l10n.toggle_show_word_separators,
    isNotEmpty,
    reason: 'toggle_show_word_separators should not be empty',
  );
  expect(
    l10n.toggle_show_strong_numbers,
    isNotEmpty,
    reason: 'toggle_show_strong_numbers should not be empty',
  );
  expect(
    l10n.toggle_show_verse_numbers,
    isNotEmpty,
    reason: 'toggle_show_verse_numbers should not be empty',
  );
  expect(
    l10n.strong_number,
    isNotEmpty,
    reason: 'strong_number should not be empty',
  );
  expect(
    l10n.strong_picker_unavailable_numbers,
    isNotEmpty,
    reason: 'strong_picker_unavailable_numbers should not be empty',
  );
  expect(
    l10n.strong_pronunciation,
    isNotEmpty,
    reason: 'strong_pronunciation should not be empty',
  );
  expect(
    l10n.strong_synonyms,
    isNotEmpty,
    reason: 'strong_synonyms should not be empty',
  );
  expect(
    l10n.strong_origin,
    isNotEmpty,
    reason: 'strong_origin should not be empty',
  );
  expect(
    l10n.strong_usage,
    isNotEmpty,
    reason: 'strong_usage should not be empty',
  );
  expect(
    l10n.strong_reference_commentary,
    isNotEmpty,
    reason: 'strong_reference_commentary should not be empty',
  );
  expect(
    l10n.strong_part_of_speech,
    isNotEmpty,
    reason: 'strong_part_of_speech should not be empty',
  );
  expect(
    l10n.strong_indeclNumAdj,
    isNotEmpty,
    reason: 'strong_indeclNumAdj should not be empty',
  );
  expect(
    l10n.strong_indeclLetN,
    isNotEmpty,
    reason: 'strong_indeclLetN should not be empty',
  );
  expect(
    l10n.strong_indeclinable,
    isNotEmpty,
    reason: 'strong_indeclinable should not be empty',
  );
  expect(l10n.strong_adj, isNotEmpty, reason: 'strong_adj should not be empty');
  expect(
    l10n.strong_advCor,
    isNotEmpty,
    reason: 'strong_advCor should not be empty',
  );
  expect(
    l10n.strong_advInt,
    isNotEmpty,
    reason: 'strong_advInt should not be empty',
  );
  expect(
    l10n.strong_advNeg,
    isNotEmpty,
    reason: 'strong_advNeg should not be empty',
  );
  expect(
    l10n.strong_advSup,
    isNotEmpty,
    reason: 'strong_advSup should not be empty',
  );
  expect(l10n.strong_adv, isNotEmpty, reason: 'strong_adv should not be empty');
  expect(
    l10n.strong_comp,
    isNotEmpty,
    reason: 'strong_comp should not be empty',
  );
  expect(
    l10n.strong_aramaicTransWord,
    isNotEmpty,
    reason: 'strong_aramaicTransWord should not be empty',
  );
  expect(
    l10n.strong_hebrewForm,
    isNotEmpty,
    reason: 'strong_hebrewForm should not be empty',
  );
  expect(
    l10n.strong_hebrewNoun,
    isNotEmpty,
    reason: 'strong_hebrewNoun should not be empty',
  );
  expect(
    l10n.strong_hebrew,
    isNotEmpty,
    reason: 'strong_hebrew should not be empty',
  );
  expect(
    l10n.strong_location,
    isNotEmpty,
    reason: 'strong_location should not be empty',
  );
  expect(
    l10n.strong_properNoun,
    isNotEmpty,
    reason: 'strong_properNoun should not be empty',
  );
  expect(
    l10n.strong_noun,
    isNotEmpty,
    reason: 'strong_noun should not be empty',
  );
  expect(
    l10n.strong_masc,
    isNotEmpty,
    reason: 'strong_masc should not be empty',
  );
  expect(l10n.strong_fem, isNotEmpty, reason: 'strong_fem should not be empty');
  expect(
    l10n.strong_neut,
    isNotEmpty,
    reason: 'strong_neut should not be empty',
  );
  expect(
    l10n.strong_plur,
    isNotEmpty,
    reason: 'strong_plur should not be empty',
  );
  expect(
    l10n.strong_otherType,
    isNotEmpty,
    reason: 'strong_otherType should not be empty',
  );
  expect(
    l10n.strong_verbImp,
    isNotEmpty,
    reason: 'strong_verbImp should not be empty',
  );
  expect(
    l10n.strong_verb,
    isNotEmpty,
    reason: 'strong_verb should not be empty',
  );
  expect(
    l10n.strong_pronDat,
    isNotEmpty,
    reason: 'strong_pronDat should not be empty',
  );
  expect(
    l10n.strong_pronPoss,
    isNotEmpty,
    reason: 'strong_pronPoss should not be empty',
  );
  expect(
    l10n.strong_pronPers,
    isNotEmpty,
    reason: 'strong_pronPers should not be empty',
  );
  expect(
    l10n.strong_pronRecip,
    isNotEmpty,
    reason: 'strong_pronRecip should not be empty',
  );
  expect(
    l10n.strong_pronRefl,
    isNotEmpty,
    reason: 'strong_pronRefl should not be empty',
  );
  expect(
    l10n.strong_pronRel,
    isNotEmpty,
    reason: 'strong_pronRel should not be empty',
  );
  expect(
    l10n.strong_pronCorrel,
    isNotEmpty,
    reason: 'strong_pronCorrel should not be empty',
  );
  expect(
    l10n.strong_pronIndef,
    isNotEmpty,
    reason: 'strong_pronIndef should not be empty',
  );
  expect(
    l10n.strong_pronInterr,
    isNotEmpty,
    reason: 'strong_pronInterr should not be empty',
  );
  expect(
    l10n.strong_pronDem,
    isNotEmpty,
    reason: 'strong_pronDem should not be empty',
  );
  expect(
    l10n.strong_pron,
    isNotEmpty,
    reason: 'strong_pron should not be empty',
  );
  expect(
    l10n.strong_particleCond,
    isNotEmpty,
    reason: 'strong_particleCond should not be empty',
  );
  expect(
    l10n.strong_particleDisj,
    isNotEmpty,
    reason: 'strong_particleDisj should not be empty',
  );
  expect(
    l10n.strong_particleInterr,
    isNotEmpty,
    reason: 'strong_particleInterr should not be empty',
  );
  expect(
    l10n.strong_particleNeg,
    isNotEmpty,
    reason: 'strong_particleNeg should not be empty',
  );
  expect(
    l10n.strong_particle,
    isNotEmpty,
    reason: 'strong_particle should not be empty',
  );
  expect(
    l10n.strong_interj,
    isNotEmpty,
    reason: 'strong_interj should not be empty',
  );
  expect(
    l10n.strong_participle,
    isNotEmpty,
    reason: 'strong_participle should not be empty',
  );
  expect(
    l10n.strong_prefix,
    isNotEmpty,
    reason: 'strong_prefix should not be empty',
  );
  expect(
    l10n.strong_prep,
    isNotEmpty,
    reason: 'strong_prep should not be empty',
  );
  expect(
    l10n.strong_artDef,
    isNotEmpty,
    reason: 'strong_artDef should not be empty',
  );
  expect(
    l10n.strong_phraseIdi,
    isNotEmpty,
    reason: 'strong_phraseIdi should not be empty',
  );
  expect(
    l10n.strong_phrase,
    isNotEmpty,
    reason: 'strong_phrase should not be empty',
  );
  expect(
    l10n.strong_conjNeg,
    isNotEmpty,
    reason: 'strong_conjNeg should not be empty',
  );
  expect(
    l10n.strong_conj,
    isNotEmpty,
    reason: 'strong_conj should not be empty',
  );
  expect(l10n.strong_or, isNotEmpty, reason: 'strong_or should not be empty');
  final localizedUpdate = l10n.localized_data_update(testLanguage);
  expect(localizedUpdate, contains(testLanguage));
  expect(localizedUpdate, isNotEmpty);
  final fileSaved = l10n.file_saved_at(testPath);
  expect(fileSaved, contains(testPath));
  expect(fileSaved, isNotEmpty);
}
