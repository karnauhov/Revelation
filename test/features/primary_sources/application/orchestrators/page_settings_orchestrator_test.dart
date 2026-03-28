import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/pages_settings.dart';
import 'package:revelation/shared/models/primary_source.dart';

void main() {
  test('loadSettingsForPage returns defaults for null page', () async {
    final repository = _FakePagesRepository();
    final orchestrator = PrimarySourcePageSettingsOrchestrator(repository);

    final result = await orchestrator.loadSettingsForPage(
      source: _buildSource(),
      selectedPage: null,
    );

    expect(result, PageSettingsState.defaults);
    expect(repository.loadCalls, 1);
  });

  test(
    'loadSettingsForPage returns defaults when raw settings empty',
    () async {
      final repository = _FakePagesRepository(
        initial: PagesSettings(pages: {'source-1_page-1': ''}),
      );
      final orchestrator = PrimarySourcePageSettingsOrchestrator(repository);
      final source = _buildSource();

      final result = await orchestrator.loadSettingsForPage(
        source: source,
        selectedPage: source.pages.first,
      );

      expect(result, PageSettingsState.defaults);
    },
  );

  test('loadSettingsForPage unpacks stored settings', () async {
    final raw = PagesSettings.packData(
      posX: 10,
      posY: 20,
      scale: 1.5,
      isNegative: true,
      isMonochrome: true,
      brightness: 15,
      contrast: 90,
      showWordSeparators: true,
      showStrongNumbers: true,
      showVerseNumbers: false,
    );
    final repository = _FakePagesRepository(
      initial: PagesSettings(pages: {'source-1_page-1': raw}),
    );
    final orchestrator = PrimarySourcePageSettingsOrchestrator(repository);
    final source = _buildSource();

    final result = await orchestrator.loadSettingsForPage(
      source: source,
      selectedPage: source.pages.first,
    );

    expect(result.rawSettings, raw);
    expect(result.posX, 10);
    expect(result.posY, 20);
    expect(result.scale, 1.5);
    expect(result.isNegative, isTrue);
    expect(result.isMonochrome, isTrue);
    expect(result.brightness, 15);
    expect(result.contrast, 90);
    expect(result.showWordSeparators, isTrue);
    expect(result.showStrongNumbers, isTrue);
    expect(result.showVerseNumbers, isFalse);
  });

  test(
    'saveSettingsForPage requires cached settings and restored state',
    () async {
      final repository = _FakePagesRepository();
      final orchestrator = PrimarySourcePageSettingsOrchestrator(repository);
      final source = _buildSource();

      final missingCache = orchestrator.saveSettingsForPage(
        source: source,
        selectedPage: source.pages.first,
        scaleAndPositionRestored: true,
        posX: 1,
        posY: 2,
        scale: 1,
        isNegative: false,
        isMonochrome: false,
        brightness: 0,
        contrast: 100,
        showWordSeparators: false,
        showStrongNumbers: false,
        showVerseNumbers: true,
      );
      expect(missingCache, '');
      expect(repository.saveCalls, 0);

      await orchestrator.loadSettingsForPage(
        source: source,
        selectedPage: source.pages.first,
      );

      final notRestored = orchestrator.saveSettingsForPage(
        source: source,
        selectedPage: source.pages.first,
        scaleAndPositionRestored: false,
        posX: 1,
        posY: 2,
        scale: 1,
        isNegative: false,
        isMonochrome: false,
        brightness: 0,
        contrast: 100,
        showWordSeparators: false,
        showStrongNumbers: false,
        showVerseNumbers: true,
      );
      expect(notRestored, '');
    },
  );

  test('saveSettingsForPage persists and returns raw settings', () async {
    final repository = _FakePagesRepository(
      initial: PagesSettings(pages: {'source-1_page-1': ''}),
    );
    final orchestrator = PrimarySourcePageSettingsOrchestrator(repository);
    final source = _buildSource();

    await orchestrator.loadSettingsForPage(
      source: source,
      selectedPage: source.pages.first,
    );

    final raw = orchestrator.saveSettingsForPage(
      source: source,
      selectedPage: source.pages.first,
      scaleAndPositionRestored: true,
      posX: 4,
      posY: 5,
      scale: 1.2,
      isNegative: true,
      isMonochrome: false,
      brightness: 12,
      contrast: 88,
      showWordSeparators: true,
      showStrongNumbers: false,
      showVerseNumbers: true,
    );

    expect(raw, isNotEmpty);
    expect(repository.saveCalls, 1);
    expect(repository.lastSaved?.pages['source-1_page-1'], raw);
  });

  test('clearSettingsForPage resets cache and persists', () async {
    final repository = _FakePagesRepository(
      initial: PagesSettings(
        pages: {'source-1_page-1': PagesSettings.packData()},
      ),
    );
    final orchestrator = PrimarySourcePageSettingsOrchestrator(repository);
    final source = _buildSource();

    await orchestrator.loadSettingsForPage(
      source: source,
      selectedPage: source.pages.first,
    );

    orchestrator.clearSettingsForPage(
      source: source,
      selectedPage: source.pages.first,
    );

    expect(repository.saveCalls, 1);
    expect(repository.lastSaved?.pages['source-1_page-1'], '');
  });
}

class _FakePagesRepository extends PagesRepository {
  _FakePagesRepository({PagesSettings? initial})
    : _settings = initial ?? PagesSettings(pages: {});

  PagesSettings _settings;
  int loadCalls = 0;
  int saveCalls = 0;
  PagesSettings? lastSaved;

  @override
  Future<PagesSettings> getPages() async {
    loadCalls++;
    return _settings;
  }

  @override
  Future<void> savePages(PagesSettings settings) async {
    saveCalls++;
    lastSaved = settings;
    _settings = settings;
  }
}

PrimarySource _buildSource() {
  return PrimarySource(
    id: 'source-1',
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
    pages: [
      model.Page(name: 'page-1', content: 'content', image: 'page-1.png'),
    ],
    attributes: const [],
    permissionsReceived: true,
  );
}
