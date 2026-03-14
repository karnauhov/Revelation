import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:revelation/core/platform/platform_utils.dart';

class SettingsState {
  const SettingsState({
    required this.settings,
    required this.isLoading,
    this.failure,
  });

  factory SettingsState.initial() {
    return SettingsState(
      settings: AppSettings(
        selectedLanguage: getSystemLanguage(),
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
      isLoading: true,
    );
  }

  final AppSettings settings;
  final bool isLoading;
  final AppFailure? failure;

  SettingsState copyWith({
    AppSettings? settings,
    bool? isLoading,
    AppFailure? failure,
    bool clearFailure = false,
  }) {
    return SettingsState(
      settings: settings ?? this.settings,
      isLoading: isLoading ?? this.isLoading,
      failure: clearFailure ? null : (failure ?? this.failure),
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is SettingsState &&
            runtimeType == other.runtimeType &&
            settings == other.settings &&
            isLoading == other.isLoading &&
            failure == other.failure;
  }

  @override
  int get hashCode => Object.hash(settings, isLoading, failure);
}
