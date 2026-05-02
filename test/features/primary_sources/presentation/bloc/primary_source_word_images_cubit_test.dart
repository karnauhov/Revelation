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
    required List<Future<PrimarySourceWordsDialogData>> responses,
  }) : _responses = List<Future<PrimarySourceWordsDialogData>>.from(responses);

  final List<Future<PrimarySourceWordsDialogData>> _responses;
  int calls = 0;

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
