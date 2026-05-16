import 'package:revelation/infra/storage/app_cache_manager_stub.dart'
    if (dart.library.io) 'package:revelation/infra/storage/app_cache_manager_io.dart'
    if (dart.library.js_interop) 'package:revelation/infra/storage/app_cache_manager_web.dart'
    as impl;

Future<void> clearAppCache() => impl.clearAppCache();
