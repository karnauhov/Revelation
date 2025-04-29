import 'dart:js_interop';
import 'common.dart';

@JS('globalThis')
external GlobalThis get globalThis;

@JS('GlobalThis')
@staticInterop
class GlobalThis {}

extension GlobalThisExt on GlobalThis {
  external Document? get document;
}

@JS('Document')
@staticInterop
class Document {}

extension DocumentExt on Document {
  external CanvasElement createElement(String tag);
}

@JS('CanvasElement')
@staticInterop
class CanvasElement {}

extension CanvasElementExt on CanvasElement {
  external set width(int w);
  external set height(int h);
  external WebGLRenderingContext? getContext(String id);
}

@JS('WebGLRenderingContext')
@staticInterop
class WebGLRenderingContext {}

extension WebGLExt on WebGLRenderingContext {
  // ignore: non_constant_identifier_names
  external int get MAX_TEXTURE_SIZE;
  external int getParameter(int pname);
}

class WebGLInterop {
  static Future<int> fetchMaxTextureSize() async {
    if (!isWeb()) {
      return 0;
    }
    final doc = globalThis.document;
    if (doc == null) {
      return 4096;
    }
    final canvas = doc.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    final gl = canvas.getContext('webgl');
    if (gl == null) {
      return 4096;
    }
    return gl.getParameter(gl.MAX_TEXTURE_SIZE);
  }
}
