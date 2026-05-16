typedef AppRuntimeCacheClearer = void Function();

class AppRuntimeCacheRegistry {
  const AppRuntimeCacheRegistry._();

  static final Set<AppRuntimeCacheClearer> _clearers =
      <AppRuntimeCacheClearer>{};

  static void register(AppRuntimeCacheClearer clearer) {
    _clearers.add(clearer);
  }

  static void clearAll() {
    for (final clearer in List<AppRuntimeCacheClearer>.of(_clearers)) {
      clearer();
    }
  }
}
