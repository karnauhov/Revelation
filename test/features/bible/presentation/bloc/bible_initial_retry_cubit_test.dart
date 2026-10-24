import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_state.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late _Repository repository;
  late BibleReaderCubit cubit;
  late BibleInitialData data;

  setUp(() async {
    repository = _Repository();
    cubit = BibleReaderCubit(
      repository: repository,
      languageCode: 'uk',
      initialBookId: 1,
      initialChapter: 2,
      initialVerse: 3,
      initialModuleFile: 'bible_test.sqlite',
      loadingBibleMessage: 'loading',
      loadingChapterMessage: 'chapter',
      loadingModuleMessage: 'module',
      modulesUnavailableMessage: 'unavailable',
    );
    final map = await BibleVerseMap.loadFromAssets();
    final reference = map.referenceFor(bookId: 1, chapter: 2, verse: 3);
    const module = BibleModuleInfo(
      fileName: 'bible_test.sqlite',
      code: 'TEST',
      moduleId: 'test',
      title: 'Fixture',
      description: '',
      language: 'uk',
      canon: '',
      versification: '',
      license: '',
      sourceSummary: '',
    );
    data = BibleInitialData(
      verseMap: map,
      modules: [module],
      selectedModule: module,
      reference: reference,
      verses: [BibleChapterVerse(reference: reference, text: 'Readable')],
    );
  });

  tearDown(() async {
    if (!cubit.isClosed) await cubit.close();
  });

  Future<void> failInitial() async {
    final pending = cubit.loadInitial();
    repository.requests.last.completeError(
      const BibleModulesUnavailableException(),
    );
    await pending;
    expect(cubit.state.status, BibleReaderStatus.failure);
  }

  test(
    'retry preserves route arguments and merges rapid taps into one load',
    () async {
      await failInitial();
      final retry = cubit.retryInitialLoad();
      await cubit.retryInitialLoad();
      await cubit.retryInitialLoad();
      expect(repository.requests, hasLength(2));
      expect(cubit.state.isBusy, isTrue);
      expect(cubit.state.errorMessage, isNull);
      expect(repository.arguments.last, ['uk', 1, 2, 3, 'bible_test.sqlite']);
      repository.requests.last.complete(data);
      await retry;
      expect(cubit.state.status, BibleReaderStatus.ready);
      expect(cubit.state.selectedReference, data.reference);
      await cubit.retryInitialLoad();
      expect(repository.requests, hasLength(2));
    },
  );

  test(
    'retry after close and close before retry completion are safe',
    () async {
      await failInitial();
      final retry = cubit.retryInitialLoad();
      await cubit.close();
      repository.requests.last.complete(data);
      await retry;
      await cubit.retryInitialLoad();
      expect(repository.requests, hasLength(2));
      expect(cubit.state.status, BibleReaderStatus.initialLoading);
    },
  );

  test(
    'a superseded retry failure cannot overwrite a newer successful load',
    () async {
      await failInitial();
      final retry = cubit.retryInitialLoad();
      final superseded = repository.requests.last;
      final newer = cubit.loadInitial();
      repository.requests.last.complete(data);
      await newer;
      superseded.completeError(StateError('late network error'));
      await retry;
      expect(cubit.state.status, BibleReaderStatus.ready);
      expect(cubit.state.errorMessage, isNull);
    },
  );

  test(
    'repeated failure remains retryable without automatic network loops',
    () async {
      await failInitial();
      final retry = cubit.retryInitialLoad();
      repository.requests.last.completeError(StateError('still offline'));
      await retry;
      expect(cubit.state.status, BibleReaderStatus.failure);
      expect(repository.requests, hasLength(2));
      final recovered = cubit.retryInitialLoad();
      repository.requests.last.complete(data);
      await recovered;
      expect(cubit.state.status, BibleReaderStatus.ready);
    },
  );
}

class _Repository extends BibleRepository {
  final requests = <Completer<BibleInitialData>>[];
  final arguments = <List<Object?>>[];

  @override
  Future<BibleInitialData> loadInitial({
    required String languageCode,
    int initialBookId = 66,
    int initialChapter = 1,
    int initialVerse = 1,
    String? initialModuleFile,
  }) {
    arguments.add([
      languageCode,
      initialBookId,
      initialChapter,
      initialVerse,
      initialModuleFile,
    ]);
    final request = Completer<BibleInitialData>();
    requests.add(request);
    return request.future;
  }
}
