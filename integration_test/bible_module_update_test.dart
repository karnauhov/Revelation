import 'support/bible_module_update_stub.dart'
    if (dart.library.io) 'support/bible_module_update_native.dart'
    as suite;

void main() => suite.main();
