import 'support/about_local_folder_stub.dart'
    if (dart.library.io) 'support/about_local_folder_native.dart'
    as suite;

void main() => suite.main();
