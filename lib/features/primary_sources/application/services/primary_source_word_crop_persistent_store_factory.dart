import 'package:revelation/features/primary_sources/application/services/primary_source_word_crop_persistent_store.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_crop_persistent_store_stub.dart'
    if (dart.library.io) 'package:revelation/features/primary_sources/application/services/primary_source_word_crop_persistent_store_io.dart'
    as impl;

PrimarySourceWordCropPersistentStore
createPrimarySourceWordCropPersistentStore() {
  return impl.createPrimarySourceWordCropPersistentStore();
}
