class FakeEnv {
  FakeEnv([Map<String, String>? seed])
    : _values = Map<String, String>.from(seed ?? const <String, String>{});

  final Map<String, String> _values;

  String read(String key, {String fallback = ''}) {
    return _values[key] ?? fallback;
  }

  void write(String key, String value) {
    _values[key] = value;
  }
}
