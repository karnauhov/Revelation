import 'dart:async';

import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/pages_settings.dart';
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';

class PageSettingsState {
  const PageSettingsState({
    required this.rawSettings,
    required this.posX,
    required this.posY,
    required this.scale,
    required this.isNegative,
    required this.isMonochrome,
    required this.brightness,
    required this.contrast,
    required this.showWordSeparators,
    required this.showStrongNumbers,
    required this.showVerseNumbers,
  });

  final String rawSettings;
  final double posX;
  final double posY;
  final double scale;
  final bool isNegative;
  final bool isMonochrome;
  final double brightness;
  final double contrast;
  final bool showWordSeparators;
  final bool showStrongNumbers;
  final bool showVerseNumbers;

  static const PageSettingsState defaults = PageSettingsState(
    rawSettings: '',
    posX: 0,
    posY: 0,
    scale: 0,
    isNegative: false,
    isMonochrome: false,
    brightness: 0,
    contrast: 100,
    showWordSeparators: false,
    showStrongNumbers: false,
    showVerseNumbers: true,
  );
}

class PrimarySourcePageSettingsOrchestrator {
  PrimarySourcePageSettingsOrchestrator(this._pagesRepository);

  final PagesRepository _pagesRepository;
  PagesSettings? _cachedPagesSettings;

  Future<PageSettingsState> loadSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
  }) async {
    _cachedPagesSettings ??= await _pagesRepository.getPages();
    if (selectedPage == null) {
      return PageSettingsState.defaults;
    }

    final pageId = '${source.id}_${selectedPage.name}';
    final raw = _cachedPagesSettings!.pages[pageId] ?? '';
    if (raw.isEmpty) {
      return PageSettingsState.defaults;
    }

    final unpacked = PagesSettings.unpackData(raw);
    return PageSettingsState(
      rawSettings: raw,
      posX: unpacked['position']['x'] as double,
      posY: unpacked['position']['y'] as double,
      scale: unpacked['scale'] as double,
      isNegative: unpacked['isNegative'] as bool,
      isMonochrome: unpacked['isMonochrome'] as bool,
      brightness: unpacked['brightness'] as double,
      contrast: unpacked['contrast'] as double,
      showWordSeparators: unpacked['wordSeparators'] as bool,
      showStrongNumbers: unpacked['strongNumbers'] as bool,
      showVerseNumbers: unpacked['verseNumbers'] as bool,
    );
  }

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
    if (_cachedPagesSettings == null ||
        selectedPage == null ||
        !scaleAndPositionRestored) {
      return '';
    }

    final pageId = '${source.id}_${selectedPage.name}';
    final raw = PagesSettings.packData(
      posX: posX,
      posY: posY,
      scale: scale,
      isNegative: isNegative,
      isMonochrome: isMonochrome,
      brightness: brightness,
      contrast: contrast,
      showWordSeparators: showWordSeparators,
      showStrongNumbers: showStrongNumbers,
      showVerseNumbers: showVerseNumbers,
    );
    _cachedPagesSettings!.pages[pageId] = raw;
    unawaited(_pagesRepository.savePages(_cachedPagesSettings!));
    return raw;
  }

  String clearSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
  }) {
    if (_cachedPagesSettings == null || selectedPage == null) {
      return '';
    }

    final pageId = '${source.id}_${selectedPage.name}';
    _cachedPagesSettings!.pages[pageId] = '';
    unawaited(_pagesRepository.savePages(_cachedPagesSettings!));
    return '';
  }
}
