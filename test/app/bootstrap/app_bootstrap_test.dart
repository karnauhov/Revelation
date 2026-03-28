import 'dart:async';
import 'dart:convert';
import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/infra/db/runtime/database_runtime.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../test_harness/test_harness.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  void Function(FlutterErrorDetails details)? previousFlutterErrorHandler;
  bool Function(Object, StackTrace)? previousPlatformErrorHandler;

  setUp(() async {
    previousFlutterErrorHandler = FlutterError.onError;
    previousPlatformErrorHandler = PlatformDispatcher.instance.onError;
    SharedPreferences.setMockInitialValues(<String, Object>{});
    await GetIt.I.reset();
  });

  tearDown(() async {
    FlutterError.onError = previousFlutterErrorHandler;
    PlatformDispatcher.instance.onError = previousPlatformErrorHandler;
    setDefaultGreekStrongTapHandler(null);
    setDefaultGreekStrongPickerTapHandler(null);
    setDefaultWordTapHandler(null);
    await GetIt.I.reset();
  });

  test('constructor supports default database runtime', () {
    final bootstrap = AppBootstrap(
      talker: Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    expect(bootstrap, isA<AppBootstrap>());
  });

  test(
    'initialize configures startup path and reacts to language changes',
    () async {
      await _seedSettings(language: 'ru');
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      AppDi.registerCore(talker: talker);
      final runtime = _FakeDatabaseRuntime();
      final progressSteps = <AppBootstrapStep>[];

      final bootstrap = AppBootstrap(talker: talker, databaseRuntime: runtime);
      final settingsCubit = await bootstrap.initialize(
        onProgress: (progress) {
          progressSteps.add(progress.step);
        },
      );
      addTearDown(settingsCubit.close);

      expect(settingsCubit.state.settings.selectedLanguage, 'ru');
      expect(runtime.initializedLanguages, <String>['ru']);
      expect(progressSteps, <AppBootstrapStep>[
        AppBootstrapStep.preparing,
        AppBootstrapStep.loadingSettings,
        AppBootstrapStep.initializingServer,
        AppBootstrapStep.initializingDatabases,
        AppBootstrapStep.configuringLinks,
        AppBootstrapStep.ready,
      ]);

      await settingsCubit.changeLanguage('en');
      final updatedLanguage = await runtime.firstUpdatedLanguage.future;
      expect(updatedLanguage, 'en');
      expect(runtime.updatedLanguages, <String>['en']);
    },
  );

  test('initialize keeps app startup alive when database init fails', () async {
    await _seedSettings(language: 'uk');
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    final runtime = _FakeDatabaseRuntime(failOnInitialize: true);

    final bootstrap = AppBootstrap(talker: talker, databaseRuntime: runtime);
    final settingsCubit = await bootstrap.initialize();
    addTearDown(settingsCubit.close);

    expect(settingsCubit.state.settings.selectedLanguage, 'uk');
    expect(runtime.initializedLanguages, <String>['uk']);

    await settingsCubit.changeLanguage('es');
    await Future<void>.delayed(Duration.zero);
    expect(runtime.updatedLanguages, isEmpty);
  });

  test('initialize configures global error handlers', () async {
    await _seedSettings(language: 'en');
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    final bootstrap = AppBootstrap(
      talker: talker,
      databaseRuntime: _FakeDatabaseRuntime(),
    );
    final settingsCubit = await bootstrap.initialize();
    addTearDown(settingsCubit.close);

    final flutterHandler = FlutterError.onError;
    final platformHandler = PlatformDispatcher.instance.onError;

    expect(flutterHandler, isNotNull);
    expect(platformHandler, isNotNull);

    flutterHandler!(
      FlutterErrorDetails(exception: StateError('forced framework error')),
    );
    final handled = platformHandler!(
      StateError('forced platform error'),
      StackTrace.current,
    );
    expect(handled, isTrue);
  });

  testWidgets('initialize wires default strong link handlers', (tester) async {
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    final bootstrap = AppBootstrap(
      talker: talker,
      databaseRuntime: _SilentRuntime(),
    );
    final settingsCubit = await bootstrap.initialize();
    addTearDown(settingsCubit.close);

    final context = await pumpLocalizedContext(tester);

    final strongHandled = await handleAppLink(context, 'strong:G1');
    await pumpFrames(tester, count: 4);
    await Navigator.of(context, rootNavigator: true).maybePop();
    await pumpFrames(tester, count: 2);

    final pickerHandled = await handleAppLink(context, 'strong_picker:G2');
    await pumpFrames(tester, count: 4);

    expect(strongHandled, isTrue);
    expect(pickerHandled, isTrue);
  });

  testWidgets(
    'word link handler covers missing source, missing page and success branch',
    (tester) async {
      await _seedSettings(language: 'en');
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      AppDi.registerCore(talker: talker);
      final source = _buildPrimarySource(id: 'source-1', pageName: 'page-1');
      final referenceResolver = PrimarySourceReferenceService(
        repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
      );
      final navigations = <PrimarySourceRouteArgs>[];
      final bootstrap = AppBootstrap(
        talker: talker,
        databaseRuntime: _SilentRuntime(),
        referenceResolver: referenceResolver,
        navigateToPrimarySource: (_, routeArgs) {
          navigations.add(routeArgs);
        },
      );
      final settingsCubit = await bootstrap.initialize();
      addTearDown(settingsCubit.close);

      final context = await pumpContext(tester);

      final missingSourceHandled = await handleAppLink(
        context,
        'word:missing-source-id:page-1:0',
      );
      final missingPageHandled = await handleAppLink(
        context,
        'word:${source.id}:missing-page-name:0',
      );
      final successHandled = await handleAppLink(
        context,
        'word:${source.id}:page-1:0',
      );
      final noPageHandled = await handleAppLink(context, 'word:${source.id}');

      expect(missingSourceHandled, isTrue);
      expect(missingPageHandled, isTrue);
      expect(successHandled, isTrue);
      expect(noPageHandled, isTrue);
      expect(navigations, hasLength(2));
      expect(navigations.first.primarySource.id, source.id);
      expect(navigations.first.pageName, 'page-1');
      expect(navigations.first.wordIndex, 0);
      expect(navigations.last.primarySource.id, source.id);
      expect(navigations.last.pageName, isNull);
      expect(navigations.last.wordIndex, isNull);
    },
  );
}

Future<void> _seedSettings({required String language}) async {
  SharedPreferences.setMockInitialValues(<String, Object>{
    'revelation_settings': jsonEncode(<String, dynamic>{
      'selectedLanguage': language,
      'selectedTheme': 'manuscript',
      'selectedFontSize': 'medium',
      'soundEnabled': true,
    }),
  });
}

class _FakeDatabaseRuntime implements DatabaseRuntime {
  _FakeDatabaseRuntime({this.failOnInitialize = false});

  final bool failOnInitialize;
  final List<String> initializedLanguages = <String>[];
  final List<String> updatedLanguages = <String>[];
  final Completer<String> firstUpdatedLanguage = Completer<String>();

  @override
  Future<void> initialize(String language) async {
    initializedLanguages.add(language);
    if (failOnInitialize) {
      throw StateError('forced database initialization failure');
    }
  }

  @override
  Future<void> updateLanguage(String language) async {
    updatedLanguages.add(language);
    if (!firstUpdatedLanguage.isCompleted) {
      firstUpdatedLanguage.complete(language);
    }
  }
}

class _SilentRuntime implements DatabaseRuntime {
  @override
  Future<void> initialize(String language) async {}

  @override
  Future<void> updateLanguage(String language) async {}
}

class _FakePrimarySourcesDbRepository extends PrimarySourcesDbRepository {
  _FakePrimarySourcesDbRepository(this._sources);

  final List<PrimarySource> _sources;

  @override
  List<PrimarySource> getAllSourcesSync() {
    return _sources;
  }
}

PrimarySource _buildPrimarySource({
  required String id,
  required String pageName,
}) {
  return PrimarySource(
    id: id,
    title: 'Title',
    date: 'Date',
    content: 'Content',
    quantity: 1,
    material: 'Material',
    textStyle: 'Text style',
    found: 'Found',
    classification: 'Classification',
    currentLocation: 'Location',
    preview: 'preview.png',
    maxScale: 1,
    isMonochrome: false,
    pages: <model.Page>[
      model.Page(name: pageName, content: 'Page content', image: 'image.png'),
    ],
    attributes: const <Map<String, String>>[],
    permissionsReceived: true,
  );
}
