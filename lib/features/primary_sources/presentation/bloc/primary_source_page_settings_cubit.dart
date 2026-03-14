import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_state.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';

class PrimarySourcePageSettingsCubit
    extends Cubit<PrimarySourcePageSettingsState> {
  PrimarySourcePageSettingsCubit(this._pageSettingsOrchestrator)
    : super(PrimarySourcePageSettingsState.defaults);

  final PrimarySourcePageSettingsOrchestrator _pageSettingsOrchestrator;

  Future<PageSettingsState> loadSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
  }) async {
    final loaded = await _pageSettingsOrchestrator.loadSettingsForPage(
      source: source,
      selectedPage: selectedPage,
    );
    applyLoadedSettings(loaded);
    return loaded;
  }

  void applyLoadedSettings(PageSettingsState loaded) {
    emit(
      state.copyWith(
        rawSettings: loaded.rawSettings,
        isNegative: loaded.isNegative,
        isMonochrome: loaded.isMonochrome,
        brightness: loaded.brightness,
        contrast: loaded.contrast,
        showWordSeparators: loaded.showWordSeparators,
        showStrongNumbers: loaded.showStrongNumbers,
        showVerseNumbers: loaded.showVerseNumbers,
      ),
    );
  }

  void toggleNegative() {
    emit(state.copyWith(isNegative: !state.isNegative));
  }

  void toggleMonochrome() {
    emit(state.copyWith(isMonochrome: !state.isMonochrome));
  }

  void applyBrightnessContrast(double brightness, double contrast) {
    emit(state.copyWith(brightness: brightness, contrast: contrast));
  }

  void resetBrightnessContrast() {
    emit(state.copyWith(brightness: 0, contrast: 100));
  }

  void toggleShowWordSeparators() {
    emit(state.copyWith(showWordSeparators: !state.showWordSeparators));
  }

  void toggleShowStrongNumbers() {
    emit(state.copyWith(showStrongNumbers: !state.showStrongNumbers));
  }

  void toggleShowVerseNumbers() {
    emit(state.copyWith(showVerseNumbers: !state.showVerseNumbers));
  }

  void saveSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
    required bool scaleAndPositionRestored,
    required double posX,
    required double posY,
    required double scale,
  }) {
    final raw = _pageSettingsOrchestrator.saveSettingsForPage(
      source: source,
      selectedPage: selectedPage,
      scaleAndPositionRestored: scaleAndPositionRestored,
      posX: posX,
      posY: posY,
      scale: scale,
      isNegative: state.isNegative,
      isMonochrome: state.isMonochrome,
      brightness: state.brightness,
      contrast: state.contrast,
      showWordSeparators: state.showWordSeparators,
      showStrongNumbers: state.showStrongNumbers,
      showVerseNumbers: state.showVerseNumbers,
    );
    emit(state.copyWith(rawSettings: raw));
  }

  void clearSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
  }) {
    _pageSettingsOrchestrator.clearSettingsForPage(
      source: source,
      selectedPage: selectedPage,
    );
    emit(PrimarySourcePageSettingsState.defaults);
  }

  void resetToDefaults() {
    emit(PrimarySourcePageSettingsState.defaults);
  }
}
