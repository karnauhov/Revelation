import 'dart:js_interop';
import 'dart:js_interop_unsafe';

import 'package:revelation/core/cache/app_runtime_cache_registry.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:web/web.dart' as web;

const _runtimeImageCachePrefix = 'revelation-runtime-image-cache';
const _wordCropPreferencesPrefix = 'primary_source_word_crop_v1.';

Future<void> clearAppCache() async {
  await _clearRuntimeImageCaches();
  await _clearWordCropPreferences();
  AppRuntimeCacheRegistry.clearAll();
}

Future<void> _clearRuntimeImageCaches() async {
  if (!web.window.has('caches')) {
    return;
  }

  final cacheNames = (await web.window.caches.keys().toDart).toDart;
  for (final cacheName in cacheNames) {
    final name = cacheName.toDart;
    if (name.startsWith(_runtimeImageCachePrefix)) {
      await web.window.caches.delete(name).toDart;
    }
  }
}

Future<void> _clearWordCropPreferences() async {
  final prefs = await SharedPreferences.getInstance();
  final keys = prefs
      .getKeys()
      .where((key) => key.startsWith(_wordCropPreferencesPrefix))
      .toList(growable: false);
  for (final key in keys) {
    await prefs.remove(key);
  }
}
