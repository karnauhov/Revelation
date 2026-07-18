export 'bible_module_connector_unsupported.dart'
    if (dart.library.io) 'bible_module_connector_native.dart'
    if (dart.library.js_interop) 'bible_module_connector_web.dart';
