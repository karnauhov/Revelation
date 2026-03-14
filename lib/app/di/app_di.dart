import 'package:get_it/get_it.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:provider/provider.dart';
import 'package:provider/single_child_widget.dart';
import 'package:revelation/core/state/change_notifier_bridge_cubit.dart';
import 'package:revelation/features/settings/settings.dart'
    show SettingsViewModel;
import 'package:revelation/features/topics/topics.dart' show MainViewModel;
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/primary_sources_view_model.dart';
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

  static MainViewModel createMainViewModel() => MainViewModel();

  static PrimarySourcesViewModel createPrimarySourcesViewModel() {
    return PrimarySourcesViewModel(PrimarySourcesDbRepository());
  }

  static List<SingleChildWidget> appBlocProviders({
    required SettingsViewModel settingsViewModel,
    required MainViewModel mainViewModel,
    required PrimarySourcesViewModel primarySourcesViewModel,
  }) {
    return <SingleChildWidget>[
      BlocProvider<ChangeNotifierBridgeCubit<SettingsViewModel>>(
        create: (_) =>
            ChangeNotifierBridgeCubit<SettingsViewModel>(settingsViewModel),
      ),
      BlocProvider<ChangeNotifierBridgeCubit<MainViewModel>>(
        create: (_) => ChangeNotifierBridgeCubit<MainViewModel>(mainViewModel),
      ),
      BlocProvider<ChangeNotifierBridgeCubit<PrimarySourcesViewModel>>(
        create: (_) => ChangeNotifierBridgeCubit<PrimarySourcesViewModel>(
          primarySourcesViewModel,
        ),
      ),
    ];
  }

  static List<SingleChildWidget> appProviders({
    required SettingsViewModel settingsViewModel,
    required MainViewModel mainViewModel,
    required PrimarySourcesViewModel primarySourcesViewModel,
  }) {
    return <SingleChildWidget>[
      ChangeNotifierProvider<MainViewModel>.value(value: mainViewModel),
      ChangeNotifierProvider<SettingsViewModel>.value(value: settingsViewModel),
      ChangeNotifierProvider<PrimarySourcesViewModel>.value(
        value: primarySourcesViewModel,
      ),
    ];
  }
}
