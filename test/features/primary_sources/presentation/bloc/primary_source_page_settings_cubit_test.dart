import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';

void main() {
  test('loadSettingsForPage updates cubit state from orchestrator', () async {
    final fakeOrchestrator = _FakePageSettingsOrchestrator()
      ..nextLoadResult = const PageSettingsState(
        rawSettings: 'raw-value',
        posX: 11,
        posY: 22,
        scale: 1.25,
        isNegative: true,
        isMonochrome: true,
        brightness: 13,
        contrast: 91,
        showWordSeparators: true,
        showStrongNumbers: true,
        showVerseNumbers: false,
      );
    final cubit = PrimarySourcePageSettingsCubit(fakeOrchestrator);
    addTearDown(cubit.close);
    final source = _buildSource();
    final page = source.pages.first;

    final loaded = await cubit.loadSettingsForPage(
      source: source,
      selectedPage: page,
    );

    expect(loaded.posX, 11);
    expect(loaded.posY, 22);
    expect(loaded.scale, 1.25);
    expect(cubit.state.rawSettings, 'raw-value');
    expect(cubit.state.isNegative, isTrue);
    expect(cubit.state.isMonochrome, isTrue);
    expect(cubit.state.brightness, 13);
    expect(cubit.state.contrast, 91);
    expect(cubit.state.showWordSeparators, isTrue);
    expect(cubit.state.showStrongNumbers, isTrue);
    expect(cubit.state.showVerseNumbers, isFalse);
  });

  test('toggle and apply operations update state', () {
    final cubit = PrimarySourcePageSettingsCubit(
      _FakePageSettingsOrchestrator(),
    );
    addTearDown(cubit.close);

    cubit.toggleNegative();
    cubit.toggleMonochrome();
    cubit.applyBrightnessContrast(12, 88);
    cubit.toggleShowWordSeparators();
    cubit.toggleShowStrongNumbers();
    cubit.toggleShowVerseNumbers();

    expect(cubit.state.isNegative, isTrue);
    expect(cubit.state.isMonochrome, isTrue);
    expect(cubit.state.brightness, 12);
    expect(cubit.state.contrast, 88);
    expect(cubit.state.showWordSeparators, isTrue);
    expect(cubit.state.showStrongNumbers, isTrue);
    expect(cubit.state.showVerseNumbers, isFalse);

    cubit.resetBrightnessContrast();
    expect(cubit.state.brightness, 0);
    expect(cubit.state.contrast, 100);
  });

  test('save forwards current settings and clear resets defaults', () {
    final fakeOrchestrator = _FakePageSettingsOrchestrator();
    final cubit = PrimarySourcePageSettingsCubit(fakeOrchestrator);
    addTearDown(cubit.close);
    final source = _buildSource();
    final page = source.pages.first;

    cubit.toggleNegative();
    cubit.applyBrightnessContrast(17, 93);
    cubit.toggleShowWordSeparators();

    cubit.saveSettingsForPage(
      source: source,
      selectedPage: page,
      scaleAndPositionRestored: true,
      posX: 5,
      posY: 7,
      scale: 1.5,
    );

    final call = fakeOrchestrator.lastSaveCall;
    expect(call, isA<_SaveInvocation>());
    expect(call!.isNegative, isTrue);
    expect(call.brightness, 17);
    expect(call.contrast, 93);
    expect(call.showWordSeparators, isTrue);
    expect(cubit.state.rawSettings, 'saved-raw');

    cubit.clearSettingsForPage(source: source, selectedPage: page);

    expect(fakeOrchestrator.clearCalled, isTrue);
    expect(cubit.state.rawSettings, isEmpty);
    expect(cubit.state.isNegative, isFalse);
    expect(cubit.state.isMonochrome, isFalse);
    expect(cubit.state.brightness, 0);
    expect(cubit.state.contrast, 100);
    expect(cubit.state.showWordSeparators, isFalse);
    expect(cubit.state.showStrongNumbers, isFalse);
    expect(cubit.state.showVerseNumbers, isTrue);
  });

  test(
    'loadSettingsForPage returns safely when cubit closes before async completes',
    () async {
      final loadCompleter = Completer<PageSettingsState>();
      final fakeOrchestrator = _FakePageSettingsOrchestrator()
        ..loadCompleter = loadCompleter;
      final cubit = PrimarySourcePageSettingsCubit(fakeOrchestrator);
      final source = _buildSource();
      final page = source.pages.first;

      final loadFuture = cubit.loadSettingsForPage(
        source: source,
        selectedPage: page,
      );
      await Future<void>.delayed(Duration.zero);
      await cubit.close();

      const delayedResult = PageSettingsState(
        rawSettings: 'late-raw',
        posX: 0,
        posY: 0,
        scale: 1,
        isNegative: false,
        isMonochrome: false,
        brightness: 0,
        contrast: 100,
        showWordSeparators: false,
        showStrongNumbers: false,
        showVerseNumbers: true,
      );
      loadCompleter.complete(delayedResult);

      final loaded = await loadFuture;
      expect(loaded.rawSettings, 'late-raw');
      expect(cubit.isClosed, isTrue);
    },
  );
}

class _FakePageSettingsOrchestrator
    extends PrimarySourcePageSettingsOrchestrator {
  _FakePageSettingsOrchestrator() : super(PagesRepository());

  PageSettingsState nextLoadResult = PageSettingsState.defaults;
  Completer<PageSettingsState>? loadCompleter;
  _SaveInvocation? lastSaveCall;
  bool clearCalled = false;

  @override
  Future<PageSettingsState> loadSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
  }) async {
    if (loadCompleter != null) {
      return loadCompleter!.future;
    }
    return nextLoadResult;
  }

  @override
  String saveSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
    required bool scaleAndPositionRestored,
    required double posX,
    required double posY,
    required double scale,
    required bool isNegative,
    required bool isMonochrome,
    required double brightness,
    required double contrast,
    required bool showWordSeparators,
    required bool showStrongNumbers,
    required bool showVerseNumbers,
  }) {
    lastSaveCall = _SaveInvocation(
      isNegative: isNegative,
      isMonochrome: isMonochrome,
      brightness: brightness,
      contrast: contrast,
      showWordSeparators: showWordSeparators,
      showStrongNumbers: showStrongNumbers,
      showVerseNumbers: showVerseNumbers,
    );
    return 'saved-raw';
  }

  @override
  String clearSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
  }) {
    clearCalled = true;
    return '';
  }
}

class _SaveInvocation {
  const _SaveInvocation({
    required this.isNegative,
    required this.isMonochrome,
    required this.brightness,
    required this.contrast,
    required this.showWordSeparators,
    required this.showStrongNumbers,
    required this.showVerseNumbers,
  });

  final bool isNegative;
  final bool isMonochrome;
  final double brightness;
  final double contrast;
  final bool showWordSeparators;
  final bool showStrongNumbers;
  final bool showVerseNumbers;
}

PrimarySource _buildSource() {
  return PrimarySource(
    id: 'source-1',
    title: 'Source',
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
    pages: [model.Page(name: 'P1', content: 'C1', image: 'p1.png')],
    attributes: const [],
    permissionsReceived: true,
  );
}
