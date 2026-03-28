import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_state.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';

class PrimarySourceSessionCubit extends Cubit<PrimarySourceSessionState> {
  PrimarySourceSessionCubit({required PrimarySource source})
    : super(PrimarySourceSessionState.initial(source: source));

  void setSelectedPage(model.Page? page) {
    emit(state.copyWith(selectedPage: page, selectedPageSet: true));
  }

  void setImageName(String imageName) {
    emit(state.copyWith(imageName: imageName));
  }

  void setMenuOpen(bool isMenuOpen) {
    emit(state.copyWith(isMenuOpen: isMenuOpen));
  }
}
