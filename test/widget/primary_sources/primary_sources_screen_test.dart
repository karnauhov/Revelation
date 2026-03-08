@Tags(['widget'])
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:provider/provider.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/data_sources/primary_sources_data_source.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/features/primary_sources/presentation/list/primary_sources_screen.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/primary_sources_view_model.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(Talker());
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  testWidgets(
    'PrimarySourcesScreen shows error fallback when load fails and there is no data',
    (tester) async {
      final viewModel = PrimarySourcesViewModel(
        _FailurePrimarySourcesRepository(),
      );

      await tester.pumpWidget(
        ChangeNotifierProvider<PrimarySourcesViewModel>.value(
          value: viewModel,
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: const PrimarySourcesScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump();

      expect(find.byType(ErrorMessage), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    },
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
