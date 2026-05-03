import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_image_service.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_word_images_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_word_images_state.dart';
import 'package:revelation/shared/models/primary_source_word_link_target.dart';

void main() {
  const target = PrimarySourceWordLinkTarget(
    sourceId: 'U001',
    pageName: '325v',
    wordIndex: 2,
  );

  test('starts with target loading placeholders', () async {
    final cubit = PrimarySourceWordImagesCubit(
      targets: const [target],
      isWeb: false,
      isMobileWeb: false,
      localizations: lookupAppLocalizations(const Locale('en')),
      imageService: _FakeWordImageService(),
      autoLoad: false,
    );
    addTearDown(cubit.close);

    expect(cubit.state.status, PrimarySourceWordImagesStatus.loading);
    expect(cubit.state.items, hasLength(1));
    expect(cubit.state.items.single.isLoading, isTrue);
    expect(cubit.state.items.single.sourceTitle, 'U001');
  });

  test('load emits loaded items from service', () async {
    final item = PrimarySourceWordImageResult.unavailable(target: target);
    final service = _FakeWordImageService(
      responses: [
        Future.value(
          PrimarySourceWordsDialogData(
            items: [item],
            sharedWordDetailsMarkdown: 'shared',
          ),
        ),
      ],
    );
    final cubit = PrimarySourceWordImagesCubit(
      targets: const [target],
      isWeb: false,
      isMobileWeb: false,
      localizations: lookupAppLocalizations(const Locale('en')),
      imageService: service,
      autoLoad: false,
    );
    addTearDown(cubit.close);

    await cubit.load();

    expect(cubit.state.status, PrimarySourceWordImagesStatus.loaded);
    expect(cubit.state.items, [item]);
    expect(cubit.state.sharedWordDetailsMarkdown, 'shared');
    expect(service.calls, 1);
  });

  test(
    'load emits progressive loading items before final loaded state',
    () async {
      final loadingItem = PrimarySourceWordImageResult.loading(
        target: target,
        sourceTitle: 'Source',
        displayWordText: 'Word',
      );
      final loadedItem = PrimarySourceWordImageResult.unavailable(
        target: target,
        sourceTitle: 'Source',
        displayWordText: 'Word',
      );
      final completer = Completer<void>();
      final service = _FakeWordImageService(
        streamResponses: [
          Stream<PrimarySourceWordsDialogData>.multi((controller) {
            controller.add(PrimarySourceWordsDialogData(items: [loadingItem]));
            unawaited(
              completer.future.then((_) async {
                controller
                  ..add(
                    PrimarySourceWordsDialogData(
                      items: [loadedItem],
                      sharedWordDetailsMarkdown: 'shared',
                    ),
                  )
                  ..close();
              }),
            );
          }),
        ],
      );
      final cubit = PrimarySourceWordImagesCubit(
        targets: const [target],
        isWeb: true,
        isMobileWeb: false,
        localizations: lookupAppLocalizations(const Locale('en')),
        imageService: service,
        autoLoad: false,
      );
      addTearDown(cubit.close);

      final states = <PrimarySourceWordImagesState>[];
      final subscription = cubit.stream.listen(states.add);
      addTearDown(subscription.cancel);

      final loadFuture = cubit.load();
      await Future<void>.delayed(Duration.zero);

      expect(
        states,
        contains(
          predicate<PrimarySourceWordImagesState>(
            (state) =>
                state.status == PrimarySourceWordImagesStatus.loading &&
                state.items.length == 1 &&
                state.items.single.isLoading,
          ),
        ),
      );

      completer.complete();
      await loadFuture;

      expect(cubit.state.status, PrimarySourceWordImagesStatus.loaded);
      expect(cubit.state.items, [loadedItem]);
      expect(cubit.state.sharedWordDetailsMarkdown, 'shared');
    },
  );

  test('stale load result is ignored when a newer request wins', () async {
    final firstCompleter = Completer<PrimarySourceWordsDialogData>();
    final secondItem = PrimarySourceWordImageResult.unavailable(
      target: target,
      sourceTitle: 'Second',
    );
    final secondCompleter = Completer<PrimarySourceWordsDialogData>();
    final service = _FakeWordImageService(
      responses: [firstCompleter.future, secondCompleter.future],
    );
    final cubit = PrimarySourceWordImagesCubit(
      targets: const [target],
      isWeb: false,
      isMobileWeb: false,
      localizations: lookupAppLocalizations(const Locale('en')),
      imageService: service,
      autoLoad: false,
    );
    addTearDown(cubit.close);

    final firstLoad = cubit.load();
    final secondLoad = cubit.load();

    firstCompleter.complete(
      PrimarySourceWordsDialogData(
        items: [
          PrimarySourceWordImageResult.unavailable(
            target: target,
            sourceTitle: 'First',
          ),
        ],
      ),
    );
    await firstLoad;
    expect(cubit.state.status, PrimarySourceWordImagesStatus.loading);

    secondCompleter.complete(
      PrimarySourceWordsDialogData(
        items: [secondItem],
        sharedWordDetailsMarkdown: 'shared',
      ),
    );
    await secondLoad;

    expect(cubit.state.status, PrimarySourceWordImagesStatus.loaded);
    expect(cubit.state.items, [secondItem]);
    expect(cubit.state.sharedWordDetailsMarkdown, 'shared');
  });

  test('close before async load completes does not apply state', () async {
    final completer = Completer<PrimarySourceWordsDialogData>();
    final service = _FakeWordImageService(responses: [completer.future]);
    final cubit = PrimarySourceWordImagesCubit(
      targets: const [target],
      isWeb: false,
      isMobileWeb: false,
      localizations: lookupAppLocalizations(const Locale('en')),
      imageService: service,
      autoLoad: false,
    );

    final loadFuture = cubit.load();
    await cubit.close();
    completer.complete(
      PrimarySourceWordsDialogData(
        items: [PrimarySourceWordImageResult.unavailable(target: target)],
      ),
    );
    await loadFuture;

    expect(cubit.isClosed, isTrue);
  });
}

class _FakeWordImageService extends PrimarySourceWordImageService {
  _FakeWordImageService({
    List<Future<PrimarySourceWordsDialogData>> responses = const [],
    List<Stream<PrimarySourceWordsDialogData>> streamResponses = const [],
  }) : _responses = List<Future<PrimarySourceWordsDialogData>>.from(responses),
       _streamResponses = List<Stream<PrimarySourceWordsDialogData>>.from(
         streamResponses,
       );

  final List<Future<PrimarySourceWordsDialogData>> _responses;
  final List<Stream<PrimarySourceWordsDialogData>> _streamResponses;
  int calls = 0;

  @override
  Stream<PrimarySourceWordsDialogData> loadDialogDataStream({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    required AppLocalizations localizations,
  }) {
    if (_streamResponses.isNotEmpty) {
      calls++;
      return _streamResponses.removeAt(0);
    }
    return Stream.fromFuture(
      loadDialogData(
        targets: targets,
        isWeb: isWeb,
        isMobileWeb: isMobileWeb,
        localizations: localizations,
      ),
    );
  }

  @override
  Future<PrimarySourceWordsDialogData> loadDialogData({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    required AppLocalizations localizations,
  }) {
    calls++;
    if (_responses.isEmpty) {
      return Future.value(
        PrimarySourceWordsDialogData(items: <PrimarySourceWordImageResult>[]),
      );
    }
    return _responses.removeAt(0);
  }
}
