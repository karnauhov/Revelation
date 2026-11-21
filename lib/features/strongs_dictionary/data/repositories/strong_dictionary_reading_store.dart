import 'package:shared_preferences/shared_preferences.dart';

typedef StrongDictionaryPlace = ({int number, double offset});

class StrongDictionaryReadingStore {
  static const preferenceKey = 'strongs_dictionary.reading_place.v1';

  Future<void>? _writing;
  StrongDictionaryPlace? _pending;

  Future<StrongDictionaryPlace?> load() async {
    await _writing;
    final prefs = await SharedPreferences.getInstance();
    if (prefs.get(preferenceKey) case [String code, String position]) {
      final number = int.tryParse(code);
      final offset = double.tryParse(position);
      if (number != null &&
          number > 0 &&
          offset != null &&
          offset.isFinite &&
          offset >= 0) {
        return (number: number, offset: offset);
      }
    }
    return null;
  }

  // A fling can cross many positions before one platform write finishes.
  Future<void> save(StrongDictionaryPlace place) {
    _pending = place;
    return _writing ??= _flush();
  }

  Future<void> _flush() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      while (_pending != null) {
        final place = _pending!;
        _pending = null;
        if (!await prefs.setStringList(preferenceKey, [
          '${place.number}',
          '${place.offset}',
        ])) {
          throw StateError(
            'Could not save the Strong dictionary reading place',
          );
        }
      }
    } finally {
      _writing = null;
    }
  }
}
