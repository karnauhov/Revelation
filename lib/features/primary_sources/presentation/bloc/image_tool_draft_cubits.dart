import 'dart:ui';

import 'package:flutter_bloc/flutter_bloc.dart';

typedef BrightnessDraft = ({double brightness, double contrast});

class BrightnessDraftCubit extends Cubit<BrightnessDraft> {
  BrightnessDraftCubit(double brightness, double contrast)
    : super((brightness: brightness, contrast: contrast));

  void setBrightness(double value) =>
      emit((brightness: value, contrast: state.contrast));
  void setContrast(double value) =>
      emit((brightness: state.brightness, contrast: value));
}

typedef ReplacementDraft = ({Color from, Color to, double tolerance});

class ReplacementDraftCubit extends Cubit<ReplacementDraft> {
  ReplacementDraftCubit(Color from, Color to, double tolerance)
    : super((from: from, to: to, tolerance: tolerance));

  void setColor(Color color, {required bool replaceFrom}) => emit((
    from: replaceFrom ? color : state.from,
    to: replaceFrom ? state.to : color,
    tolerance: state.tolerance,
  ));
  void setTolerance(double value) =>
      emit((from: state.from, to: state.to, tolerance: value));
}
