import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/shared/models/app_settings.dart';

class FakeSettingsRepository extends SettingsRepository {
  FakeSettingsRepository({required this.initialSettings});

  AppSettings initialSettings;
  final List<AppSettings> savedSettings = <AppSettings>[];

  @override
  Future<AppSettings> getSettings() async => initialSettings;

  @override
  Future<void> saveSettings(AppSettings settings) async {
    initialSettings = settings;
    savedSettings.add(settings);
  }
}
