import 'package:get_it/get_it.dart';
import 'package:provider/provider.dart';
import 'package:provider/single_child_widget.dart';
import 'package:revelation/features/settings/presentation/viewmodels/settings_view_model.dart';
import 'package:revelation/repositories/primary_sources_db_repository.dart';
import 'package:revelation/viewmodels/main_view_model.dart';
import 'package:revelation/viewmodels/primary_sources_view_model.dart';
import 'package:talker_flutter/talker_flutter.dart';

class AppDi {
  AppDi._();

  static final GetIt _getIt = GetIt.instance;

  static void registerCore({required Talker talker}) {
    if (_getIt.isRegistered<Talker>()) {
      _getIt.unregister<Talker>();
    }
    _getIt.registerSingleton<Talker>(talker);
  }

  static List<SingleChildWidget> appProviders({
    required SettingsViewModel settingsViewModel,
  }) {
    return <SingleChildWidget>[
      ChangeNotifierProvider<MainViewModel>(create: (_) => MainViewModel()),
      ChangeNotifierProvider<SettingsViewModel>(
        create: (_) => settingsViewModel,
      ),
      ChangeNotifierProvider<PrimarySourcesViewModel>(
        create: (_) => PrimarySourcesViewModel(PrimarySourcesDbRepository()),
      ),
    ];
  }
}
