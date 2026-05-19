import 'package:revelation/infra/storage/local_app_folder_stub.dart'
    if (dart.library.io) 'package:revelation/infra/storage/local_app_folder_io.dart'
    if (dart.library.js_interop) 'package:revelation/infra/storage/local_app_folder_stub.dart'
    as impl;

Future<void> showLocalAppFolder() {
  return impl.showLocalAppFolder();
}
