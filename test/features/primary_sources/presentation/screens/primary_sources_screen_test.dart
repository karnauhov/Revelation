@Tags(['widget'])
import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/data_sources/primary_sources_data_source.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/screens/primary_sources_screen.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/source_item.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:talker_flutter/talker_flutter.dart';
import '../../../../test_harness/test_harness.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  testWidgets(
    'PrimarySourcesScreen shows error fallback when load fails and there is no data',
    (tester) async {
      final cubit = PrimarySourcesCubit(_FailurePrimarySourcesRepository());
      addTearDown(cubit.close);

      await tester.pumpWidget(_buildPrimarySourcesScreenApp(cubit));
      await pumpFrames(tester, count: 2);

      expect(find.byType(ErrorMessage), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    },
  );

  testWidgets(
    'PrimarySourcesScreen shows loading state while request is in progress',
    (tester) async {
      final repository = _ControlledPrimarySourcesRepository();
      final cubit = PrimarySourcesCubit(repository);
      addTearDown(cubit.close);

      await tester.pumpWidget(_buildPrimarySourcesScreenApp(cubit));
      await pumpFrames(tester);

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.byType(ErrorMessage), findsNothing);

      repository.completeRequest(
        0,
        AppSuccess<PrimarySourcesLoadResult>(
          PrimarySourcesLoadResult(
            fullPrimarySources: const <PrimarySource>[],
            significantPrimarySources: const <PrimarySource>[],
            fragmentsPrimarySources: const <PrimarySource>[],
          ),
        ),
      );
      await pumpAndSettleSafe(tester);

      expect(find.byType(CircularProgressIndicator), findsNothing);
    },
  );

  testWidgets(
    'PrimarySourcesScreen renders grouped source sections after successful load',
    (tester) async {
      final cubit = PrimarySourcesCubit(_SuccessPrimarySourcesRepository());
      addTearDown(cubit.close);

      await tester.pumpWidget(_buildPrimarySourcesScreenApp(cubit));
      await pumpFrames(tester);
      await pumpAndSettleSafe(tester);

      final context = tester.element(find.byType(PrimarySourcesScreen));
      final l10n = AppLocalizations.of(context)!;

      expect(find.text('${l10n.full_primary_sources} (1)'), findsOneWidget);
      expect(
        find.text('${l10n.significant_primary_sources} (1)'),
        findsOneWidget,
      );
      await tester.drag(find.byType(Scrollable).first, const Offset(0, -900));
      await pumpAndSettleSafe(tester);

      expect(
        find.text('${l10n.fragments_primary_sources} (1)'),
        findsOneWidget,
      );
      expect(find.byType(SourceItemWidget), findsWidgets);
      expect(find.byType(ErrorMessage), findsNothing);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    },
  );

  testWidgets(
    'PrimarySourcesScreen toggles source details without mutating model state',
    (tester) async {
      final cubit = PrimarySourcesCubit(_SuccessPrimarySourcesRepository());
      addTearDown(cubit.close);

      await tester.pumpWidget(_buildPrimarySourcesScreenApp(cubit));
      await pumpFrames(tester);
      await pumpAndSettleSafe(tester);

      final context = tester.element(find.byType(PrimarySourcesScreen));
      final l10n = AppLocalizations.of(context)!;

      expect(
        find.text('(${l10n.show_more})', findRichText: true),
        findsWidgets,
      );
      expect(find.text('(${l10n.hide})', findRichText: true), findsNothing);

      await tester.tap(
        find.text('(${l10n.show_more})', findRichText: true).first,
      );
      await pumpFrames(tester);

      expect(find.text('(${l10n.hide})', findRichText: true), findsOneWidget);
    },
  );

  testWidgets(
    'expansion state is retained only for source ids that still exist after reload',
    (tester) async {
      final repository = _SequentialPrimarySourcesRepository([
        PrimarySourcesLoadResult(
          fullPrimarySources: <PrimarySource>[_buildSource('old-id')],
          significantPrimarySources: const <PrimarySource>[],
          fragmentsPrimarySources: const <PrimarySource>[],
        ),
        PrimarySourcesLoadResult(
          fullPrimarySources: <PrimarySource>[_buildSource('new-id')],
          significantPrimarySources: const <PrimarySource>[],
          fragmentsPrimarySources: const <PrimarySource>[],
        ),
      ]);
      final cubit = PrimarySourcesCubit(repository);
      addTearDown(cubit.close);

      await tester.pumpWidget(_buildPrimarySourcesScreenApp(cubit));
      await pumpFrames(tester);
      await pumpAndSettleSafe(tester);

      final context = tester.element(find.byType(PrimarySourcesScreen));
      final l10n = AppLocalizations.of(context)!;

      await tester.tap(
        find.text('(${l10n.show_more})', findRichText: true).first,
      );
      await pumpFrames(tester);
      expect(find.text('(${l10n.hide})', findRichText: true), findsOneWidget);

      await cubit.loadPrimarySources();
      await pumpFrames(tester, count: 2);
      await pumpAndSettleSafe(tester);

      expect(find.text('(${l10n.hide})', findRichText: true), findsNothing);
      expect(
        find.text('(${l10n.show_more})', findRichText: true),
        findsWidgets,
      );
    },
  );

  testWidgets(
    'listener compares significant and fragments groups on sequential reloads',
    (tester) async {
      final repository = _SequentialPrimarySourcesRepository([
        PrimarySourcesLoadResult(
          fullPrimarySources: <PrimarySource>[_buildSource('stable')],
          significantPrimarySources: const <PrimarySource>[],
          fragmentsPrimarySources: const <PrimarySource>[],
        ),
        PrimarySourcesLoadResult(
          fullPrimarySources: <PrimarySource>[_buildSource('stable')],
          significantPrimarySources: <PrimarySource>[_buildSource('sig-1')],
          fragmentsPrimarySources: const <PrimarySource>[],
        ),
        PrimarySourcesLoadResult(
          fullPrimarySources: <PrimarySource>[_buildSource('stable')],
          significantPrimarySources: <PrimarySource>[_buildSource('sig-1')],
          fragmentsPrimarySources: <PrimarySource>[_buildSource('frag-1')],
        ),
      ]);
      final cubit = PrimarySourcesCubit(repository);
      addTearDown(cubit.close);

      await tester.pumpWidget(_buildPrimarySourcesScreenApp(cubit));
      await pumpFrames(tester, count: 2);
      await pumpAndSettleSafe(tester);

      await cubit.loadPrimarySources();
      await pumpFrames(tester, count: 2);
      await pumpAndSettleSafe(tester);

      await cubit.loadPrimarySources();
      await pumpFrames(tester, count: 2);
      await pumpAndSettleSafe(tester);

      expect(find.byType(PrimarySourcesScreen), findsOneWidget);
      expect(find.byType(SourceItemWidget), findsWidgets);
    },
  );

  testWidgets(
    'desktop drag listener updates scrolling state without throwing',
    (tester) async {
      final repository = _SequentialPrimarySourcesRepository([
        PrimarySourcesLoadResult(
          fullPrimarySources: List<PrimarySource>.generate(
            20,
            (index) => _buildSource('full-$index'),
          ),
          significantPrimarySources: List<PrimarySource>.generate(
            20,
            (index) => _buildSource('sig-$index'),
          ),
          fragmentsPrimarySources: List<PrimarySource>.generate(
            20,
            (index) => _buildSource('frag-$index'),
          ),
        ),
      ]);
      final cubit = PrimarySourcesCubit(repository);
      addTearDown(cubit.close);

      await tester.pumpWidget(_buildPrimarySourcesScreenApp(cubit));
      await pumpFrames(tester, count: 2);
      await pumpAndSettleSafe(tester);

      final dragListeners = tester
          .widgetList<Listener>(find.byType(Listener))
          .where((widget) {
            return widget.onPointerDown != null &&
                widget.onPointerMove != null &&
                widget.onPointerUp != null;
          })
          .toList();
      expect(dragListeners, isNotEmpty);
      final listener = dragListeners.first;

      listener.onPointerDown?.call(
        const PointerDownEvent(
          position: Offset(100, 350),
          buttons: kPrimaryMouseButton,
        ),
      );
      await tester.pump();

      listener.onPointerMove?.call(
        const PointerMoveEvent(
          position: Offset(100, 310),
          buttons: kPrimaryMouseButton,
        ),
      );
      await tester.pump();

      listener.onPointerUp?.call(
        const PointerUpEvent(position: Offset(100, 310)),
      );
      await tester.pump();

      expect(find.byType(PrimarySourcesScreen), findsOneWidget);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.linux),
  );
}

Widget _buildPrimarySourcesScreenApp(PrimarySourcesCubit cubit) {
  return BlocProvider<PrimarySourcesCubit>.value(
    value: cubit,
    child: buildLocalizedTestApp(
      child: const PrimarySourcesScreen(),
      withScaffold: false,
    ),
  );
}

class _FailurePrimarySourcesRepository extends PrimarySourcesDbRepository {
  _FailurePrimarySourcesRepository()
    : super(dataSource: _EmptyPrimarySourcesDataSource());

  @override
  Future<AppResult<PrimarySourcesLoadResult>> loadGroupedSourcesResult() async {
    return const AppFailureResult<PrimarySourcesLoadResult>(
      AppFailure.dataSource('Widget test forced failure'),
    );
  }
}

class _SuccessPrimarySourcesRepository extends PrimarySourcesDbRepository {
  _SuccessPrimarySourcesRepository()
    : super(dataSource: _EmptyPrimarySourcesDataSource());

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

class _ControlledPrimarySourcesRepository extends PrimarySourcesDbRepository {
  _ControlledPrimarySourcesRepository()
    : super(dataSource: _EmptyPrimarySourcesDataSource());

  final List<Completer<AppResult<PrimarySourcesLoadResult>>> _requests =
      <Completer<AppResult<PrimarySourcesLoadResult>>>[];

  @override
  Future<AppResult<PrimarySourcesLoadResult>> loadGroupedSourcesResult() {
    final completer = Completer<AppResult<PrimarySourcesLoadResult>>();
    _requests.add(completer);
    return completer.future;
  }

  void completeRequest(int index, AppResult<PrimarySourcesLoadResult> result) {
    _requests[index].complete(result);
  }
}

class _SequentialPrimarySourcesRepository extends PrimarySourcesDbRepository {
  _SequentialPrimarySourcesRepository(this._results)
    : super(dataSource: _EmptyPrimarySourcesDataSource());

  final List<PrimarySourcesLoadResult> _results;
  int _index = 0;

  @override
  Future<AppResult<PrimarySourcesLoadResult>> loadGroupedSourcesResult() async {
    final safeIndex = _index < _results.length ? _index : _results.length - 1;
    final result = _results[safeIndex];
    _index++;
    return AppSuccess<PrimarySourcesLoadResult>(result);
  }
}

PrimarySource _buildSource(String id) {
  return PrimarySource(
    id: id,
    title: id,
    date: '',
    content: '',
    quantity: 0,
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

class _EmptyPrimarySourcesDataSource implements PrimarySourcesDataSource {
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
  Future<Uint8List?> getCommonResourceData(String key) async {
    return null;
  }
}
