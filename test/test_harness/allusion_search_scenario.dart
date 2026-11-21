import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/allusion_search/presentation/bloc/allusion_search_cubit.dart';
import 'package:revelation/features/allusion_search/presentation/screens/allusion_search_screen.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/screens/settings_screen.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_content_service.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_dictionary_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/features/topics/presentation/widgets/drawer_content.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'fakes/fake_allusion_repositories.dart';
import 'fakes/fake_settings_repository.dart';

Future<void> exerciseAllusionSearch(WidgetTester tester) async {
  final map = (await tester.runAsync(BibleVerseMap.loadFromAssets))!;
  final settings = SettingsCubit(
    FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: 'en',
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: false,
      ),
    ),
  );
  await settings.loadSettings();
  addTearDown(settings.close);
  final library = FakeBibleLibrary(
    selectedModule: () => settings.state.settings.defaultBibleModule,
  );
  GetIt.I.pushNewScope();
  GetIt.I.registerSingleton<BibleLibraryRepository>(library);
  addTearDown(GetIt.I.popScope);
  final repository = FakeAllusionRepository(map, genesisVerses: 25);
  final cubit = AllusionSearchCubit(repository, library);
  AppDi.registerBibleVerseMap(map);
  addTearDown(cubit.close);
  final router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (_, _) => Scaffold(
          appBar: AppBar(),
          drawer: Drawer(child: DrawerContent(onItemClicked: () {})),
        ),
      ),
      GoRoute(
        path: '/allusion_search',
        builder: (_, state) => AllusionSearchScreen(cubit: cubit),
      ),
      GoRoute(
        path: '/settings',
        builder: (_, state) => SettingsScreen(
          initialSection: state.uri.queryParameters['section'],
        ),
      ),
      GoRoute(
        path: '/strongs_dictionary',
        builder: (_, state) {
          final number = StrongDictionaryRouteArgs.tryParse(
            state.extra,
            state.uri.queryParameters,
          )?.resolvedInitialStrongNumber;
          return Scaffold(body: Text('Dictionary entry G$number'));
        },
      ),
      GoRoute(
        path: '/bible',
        builder: (_, state) => Scaffold(
          body: Text(
            state.uri.toString(),
            key: const Key('reader_destination'),
          ),
        ),
      ),
    ],
  );
  addTearDown(router.dispose);
  await tester.pumpWidget(
    MultiBlocProvider(
      providers: AppDi.appBlocProviders(settingsCubit: settings),
      child: MaterialApp.router(
        routerConfig: router,
        locale: const Locale('en'),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
      ),
    ),
  );
  await tester.pumpAndSettle();
  Future<void> openFromMainMenu(String name) async {
    await tester.tap(find.byType(DrawerButton));
    await tester.pumpAndSettle();
    final item = find.text(name);
    await tester.ensureVisible(item);
    await tester.tap(item);
    await tester.pumpAndSettle();
  }

  final l10n = AppLocalizations.of(tester.element(find.byType(Scaffold)))!;
  await openFromMainMenu(l10n.allusion_search_screen);
  expect(find.byKey(const Key('allusion_verse')), findsOneWidget);
  expect(find.byKey(const Key('allusion_settings')), findsNothing);
  final first = map.referenceFor(bookId: 66, chapter: 1, verse: 1);
  expect(find.text('English passage ${first.verseKey}'), findsOneWidget);
  await tester.tap(find.byKey(const Key('allusion_search')));
  await tester.pumpAndSettle();
  expect(find.text('English passage 001'), findsOneWidget);
  expect(repository.searches, 1);
  final nextBottom = find.byKey(const Key('allusion_next_bottom'));
  expect(find.byKey(const Key('allusion_next_top')), findsOneWidget);
  await tester.ensureVisible(nextBottom);
  await tester.tap(nextBottom);
  await tester.pumpAndSettle();
  expect(cubit.state.page, 1);
  final previousTop = find.byKey(const Key('allusion_prev_top'));
  expect(previousTop.hitTestable(), findsOneWidget);
  await tester.tap(previousTop);
  await tester.pumpAndSettle();
  expect(cubit.state.page, 0);
  final books = find.byKey(const Key('allusion_tab_book'));
  await tester.ensureVisible(books);
  await tester.tap(books);
  await tester.pumpAndSettle();
  expect(find.byKey(const Key('allusion_next_top')), findsNothing);
  expect(find.byKey(const ValueKey('allusion_result_002')), findsOneWidget);
  setDefaultGreekStrongTapHandler((number, context) {
    showStrongDictionaryDialog(
      context,
      number,
      contentService: StrongsDictionaryContentService(verseMap: map),
    );
  });
  addTearDown(() => setDefaultGreekStrongTapHandler(null));
  await tester.ensureVisible(find.text('G10').first);
  await tester.tap(find.text('G10').first);
  await tester.pumpAndSettle();
  expect(find.byType(StrongDictionaryDialog), findsOneWidget);
  await tester.tap(find.byKey(const Key('strong_dialog_open_page')));
  await tester.pumpAndSettle();
  expect(find.text('Dictionary entry G10'), findsOneWidget);
  router.pop();
  await tester.pumpAndSettle();

  router.pop();
  await tester.pumpAndSettle();
  await openFromMainMenu(l10n.settings_screen);
  expect(find.byType(SettingsScreen), findsOneWidget);
  final cards = tester.widgetList<Card>(find.byType(Card)).toList();
  expect(cards.length, 5);
  expect(cards.map((card) => card.color).toSet(), hasLength(1));
  final bibleSetting = find.byKey(const Key('default_bible_setting'));
  await tester.ensureVisible(bibleSetting);
  expect(bibleSetting.hitTestable(), findsOneWidget);
  await tester.tap(bibleSetting);
  await tester.pumpAndSettle();
  await tester.tap(find.text('OH1988 · Українська'));
  await tester.pumpAndSettle();
  expect(
    settings.state.settings.defaultBibleModule,
    FakeBibleLibrary.ukrainian.fileName,
  );
  router.pop();
  await tester.pumpAndSettle();
  await openFromMainMenu(l10n.allusion_search_screen);
  expect(repository.searches, 1);
  expect(cubit.state.level.name, 'book');
  expect(find.text('Український текст 001'), findsOneWidget);
  final reference = find.byKey(const ValueKey('allusion_result_002'));
  await tester.ensureVisible(reference);
  await tester.tap(reference);
  await tester.pumpAndSettle();
  expect(find.byKey(const Key('bible_passage_dialog')), findsOneWidget);
  expect(
    find.descendant(
      of: find.byKey(const Key('bible_passage_dialog')),
      matching: find.textContaining('Український текст 002'),
    ),
    findsOneWidget,
  );
  final greekWord = find.byKey(const ValueKey('bible_passage_word_G10')).first;
  await tester.ensureVisible(greekWord);
  await tester.tap(greekWord);
  await tester.pumpAndSettle();
  expect(find.byType(StrongDictionaryDialog), findsOneWidget);
  Navigator.of(tester.element(find.byType(StrongDictionaryDialog))).pop();
  await tester.pumpAndSettle();
  expect(find.byKey(const Key('bible_passage_dialog')), findsOneWidget);
  await tester.tap(find.byKey(const Key('bible_passage_open_reader')));
  await tester.pumpAndSettle();
  expect(
    find.textContaining('module=bible_ohienko_1988.sqlite'),
    findsOneWidget,
  );
  expect(find.textContaining('book=1&chapter=1&verse=2'), findsOneWidget);
  router.pop();
  await tester.pumpAndSettle();
  expect(cubit.state.results, isNotNull);
  expect(tester.takeException(), isNull);
}
