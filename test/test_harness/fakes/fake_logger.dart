enum FakeLogLevel { info, warning, error }

class FakeLogRecord {
  const FakeLogRecord({
    required this.level,
    required this.message,
    this.error,
    this.stackTrace,
  });

  final FakeLogLevel level;
  final String message;
  final Object? error;
  final StackTrace? stackTrace;
}

class FakeLogger {
  final List<FakeLogRecord> records = <FakeLogRecord>[];

  void info(String message) {
    records.add(FakeLogRecord(level: FakeLogLevel.info, message: message));
  }

  void warning(String message) {
    records.add(FakeLogRecord(level: FakeLogLevel.warning, message: message));
  }

  void error(String message, {Object? error, StackTrace? stackTrace}) {
    records.add(
      FakeLogRecord(
        level: FakeLogLevel.error,
        message: message,
        error: error,
        stackTrace: stackTrace,
      ),
    );
  }

  void clear() {
    records.clear();
  }
}
