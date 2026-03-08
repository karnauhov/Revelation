class RequestToken {
  const RequestToken._(this.value);

  final int value;
}

class LatestRequestGuard {
  int _activeVersion = 0;

  RequestToken start() {
    _activeVersion += 1;
    return RequestToken._(_activeVersion);
  }

  bool isActive(RequestToken token) {
    return token.value == _activeVersion;
  }

  void cancelActive() {
    _activeVersion += 1;
  }
}
