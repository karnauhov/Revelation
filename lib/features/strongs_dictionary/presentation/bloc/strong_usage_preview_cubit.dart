import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strong_usage_bible_text_provider.dart';

enum StrongUsagePreviewStatus { initial, loading, ready, unavailable }

class StrongUsagePreviewState {
  const StrongUsagePreviewState({
    this.status = StrongUsagePreviewStatus.initial,
    this.text,
    this.requestId = 0,
  });

  final StrongUsagePreviewStatus status;
  final String? text;
  final int requestId;

  @override
  bool operator ==(Object other) =>
      other is StrongUsagePreviewState &&
      status == other.status &&
      text == other.text &&
      requestId == other.requestId;

  @override
  int get hashCode => Object.hash(status, text, requestId);
}

class StrongUsagePreviewCubit extends Cubit<StrongUsagePreviewState> {
  StrongUsagePreviewCubit({
    required this.verseKey,
    required StrongUsageBibleTextProvider textProvider,
    required Future<void> Function(String) copyText,
  }) : _textProvider = textProvider,
       _copyText = copyText,
       super(const StrongUsagePreviewState());

  final String verseKey;
  final StrongUsageBibleTextProvider _textProvider;
  final Future<void> Function(String) _copyText;
  Future<void>? _activeRequest;

  Future<void> requestPreview() => _activeRequest ??= _showPreview()
      .whenComplete(() => _activeRequest = null);

  Future<void> _showPreview() async {
    if (isClosed) return;
    final requestId = state.requestId + 1;
    emit(
      StrongUsagePreviewState(
        status: StrongUsagePreviewStatus.loading,
        requestId: state.requestId,
      ),
    );
    String? text;
    try {
      text = (await _textProvider.loadVerseText(verseKey))?.trim();
    } catch (_) {}
    if (isClosed) return;
    if (text != null && text.isNotEmpty) {
      try {
        await _copyText(text);
      } catch (_) {}
      if (isClosed) return;
    }
    emit(
      StrongUsagePreviewState(
        status: text == null || text.isEmpty
            ? StrongUsagePreviewStatus.unavailable
            : StrongUsagePreviewStatus.ready,
        text: text == null || text.isEmpty ? null : text,
        requestId: requestId,
      ),
    );
  }
}
