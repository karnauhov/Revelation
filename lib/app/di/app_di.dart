import 'package:get_it/get_it.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:provider/provider.dart';
import 'package:provider/single_child_widget.dart';
import 'package:revelation/core/state/change_notifier_bridge_cubit.dart';
import 'package:revelation/features/settings/settings.dart' show SettingsCubit;
import 'package:revelation/features/topics/topics.dart'
    show TopicsCatalogCubit, TopicsRepository;
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

  static PrimarySourcesViewModel createPrimarySourcesViewModel() {
    return PrimarySourcesViewModel(PrimarySourcesDbRepository());
  }

  static List<SingleChildWidget> appBlocProviders({
    required SettingsCubit settingsCubit,
    required PrimarySourcesViewModel primarySourcesViewModel,
  }) {
    return <SingleChildWidget>[
      BlocProvider<SettingsCubit>.value(value: settingsCubit),
      BlocProvider<TopicsCatalogCubit>(
        create: (_) => TopicsCatalogCubit(
          topicsRepository: TopicsRepository(),
          settingsCubit: settingsCubit,
        ),
      ),
      BlocProvider<ChangeNotifierBridgeCubit<PrimarySourcesViewModel>>(
        create: (_) => ChangeNotifierBridgeCubit<PrimarySourcesViewModel>(
          primarySourcesViewModel,
        ),
      ),
    ];
  }

  static List<SingleChildWidget> appProviders({
    required PrimarySourcesViewModel primarySourcesViewModel,
  }) {
    return <SingleChildWidget>[
      ChangeNotifierProvider<PrimarySourcesViewModel>.value(
        value: primarySourcesViewModel,
      ),
    ];
  }
}
