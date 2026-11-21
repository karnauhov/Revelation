import 'dart:js_interop';
import 'dart:js_interop_unsafe';
import 'dart:typed_data';
import 'package:web/web.dart' as web;

const _name = 'revelation-allusion-index-v1';
String get _key => Uri.base.resolve('db/allusions-v1.bin').toString();

Future<Uint8List?> readCachedAllusionIndex() async {
  if (!web.window.has('caches')) return null;
  final cache = await web.window.caches.open(_name).toDart;
  final response = await cache.match(_key.toJS).toDart;
  if (response == null) return null;
  return (await response.arrayBuffer().toDart).toDart.asUint8List();
}

Future<void> writeCachedAllusionIndex(Uint8List bytes) async {
  if (!web.window.has('caches')) return;
  final cache = await web.window.caches.open(_name).toDart;
  await cache.put(_key.toJS, web.Response(bytes.toJS)).toDart;
}
