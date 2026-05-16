import 'package:revelation/core/cache/app_runtime_cache_registry.dart';

Future<void> clearAppCache() async {
  AppRuntimeCacheRegistry.clearAll();
}
