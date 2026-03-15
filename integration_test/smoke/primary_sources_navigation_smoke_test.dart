import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/screens/primary_sources_screen.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/data_sources/primary_sources_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(Talker());
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  testWidgets('Primary sources smoke: list renders and opens detail route', (
    tester,
  ) async {
    final cubit = PrimarySourcesCubit(_SuccessPrimarySourcesRepository());
    addTearDown(cubit.close);

    final router = GoRouter(
      routes: <RouteBase>[
        GoRoute(
          path: '/',
          builder: (context, state) => const PrimarySourcesScreen(),
        ),
        GoRoute(
          path: '/primary_source',
          builder: (context, state) =>
              const Scaffold(body: Center(child: Text('detail-stub'))),
        ),
      ],
    );
    addTearDown(router.dispose);

    await tester.pumpWidget(
      BlocProvider<PrimarySourcesCubit>.value(
        value: cubit,
        child: MaterialApp.router(
          routerConfig: router,
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
        ),
      ),
    );
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(PrimarySourcesScreen));
    final l10n = AppLocalizations.of(context)!;
    expect(find.text('${l10n.full_primary_sources} (1)'), findsOneWidget);
    expect(find.byType(ElevatedButton), findsWidgets);

    await tester.tap(find.byType(ElevatedButton).first);
    await tester.pumpAndSettle();

    expect(find.text('detail-stub'), findsOneWidget);
  });
}

class _SuccessPrimarySourcesRepository extends PrimarySourcesDbRepository {
  _SuccessPrimarySourcesRepository() : super(dataSource: _EmptyDataSource());

  @override
  Future<AppResult<PrimarySourcesLoadResult>> loadGroupedSourcesResult() async {
    return AppSuccess<PrimarySourcesLoadResult>(
      PrimarySourcesLoadResult(
        fullPrimarySources: <PrimarySource>[_buildSource('full')],
        significantPrimarySources: <PrimarySource>[_buildSource('significant')],
        fragmentsPrimarySources: <PrimarySource>[_buildSource('fragment')],
      ),
    );
  }
}

PrimarySource _buildSource(String id) {
  return PrimarySource(
    id: id,
    title: id,
    date: '',
    content: '',
    quantity: 1,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    preview: '',
    maxScale: 1,
    isMonochrome: false,
    pages: const [],
    attributes: const [],
    permissionsReceived: false,
  );
}

class _EmptyDataSource implements PrimarySourcesDataSource {
  @override
  bool get isInitialized => true;

  @override
  List<common_db.PrimarySource> get primarySourceRows => const [];

  @override
  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows =>
      const [];

  @override
  List<common_db.PrimarySourceLink> get primarySourceLinkRows => const [];

  @override
  List<common_db.PrimarySourcePage> get primarySourcePageRows => const [];

  @override
  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows =>
      const [];

  @override
  List<localized_db.PrimarySourceText> get primarySourceTextRows => const [];

  @override
  List<common_db.PrimarySourceVerse> get primarySourceVerseRows => const [];

  @override
  List<common_db.PrimarySourceWord> get primarySourceWordRows => const [];

  @override
  Future<Uint8List?> getCommonResourceData(String key) async => null;
}
