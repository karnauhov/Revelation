import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:supabase_flutter/supabase_flutter.dart';

typedef PixelDimensions = ({int width, int height});

/// Reads the stored pixel dimensions without decoding the manuscript bitmap.
PixelDimensions? manuscriptDimensions(Uint8List bytes) {
  final data = ByteData.sublistView(bytes);
  if (bytes.length >= 24 &&
      data.getUint32(0) == 0x89504e47 &&
      data.getUint32(4) == 0x0d0a1a0a &&
      data.getUint32(12) == 0x49484452) {
    return _dimensions(data.getUint32(16), data.getUint32(20));
  }
  if (bytes.length < 2 || data.getUint16(0) != 0xffd8) return null;

  // JPEG metadata segments (including EXIF and ICC profiles) precede the
  // start-of-frame segment that contains the height and width.
  var offset = 2;
  while (offset + 3 < bytes.length && bytes[offset++] == 0xff) {
    while (offset < bytes.length && bytes[offset] == 0xff) {
      offset++;
    }
    if (offset + 2 >= bytes.length) return null;
    final marker = bytes[offset++];
    if (marker == 0xda || marker == 0xd9) return null;
    final length = data.getUint16(offset);
    if (length < 2) return null;
    if (marker >= 0xc0 &&
        marker <= 0xcf &&
        marker != 0xc4 &&
        marker != 0xc8 &&
        marker != 0xcc) {
      if (length < 8 || offset + 7 > bytes.length) return null;
      return _dimensions(
        data.getUint16(offset + 5),
        data.getUint16(offset + 3),
      );
    }
    offset += length;
  }
  return null;
}

PixelDimensions? _dimensions(int width, int height) =>
    width > 0 && height > 0 ? (width: width, height: height) : null;

Future<bool> mobileManuscriptIsReduced(
  String page,
  Uint8List mobileBytes,
) async {
  final mobile = manuscriptDimensions(mobileBytes);
  if (mobile == null) return false;
  final divider = page.indexOf('/');
  if (divider < 1) return false;
  final client = http.Client();
  try {
    final url = Supabase.instance.client.storage
        .from(page.substring(0, divider))
        .getPublicUrl(page.substring(divider + 1));
    const limit = 64 * 1024;
    final request = http.Request('GET', Uri.parse(url))
      ..headers['Range'] = 'bytes=0-${limit - 1}';
    final response = await client
        .send(request)
        .timeout(const Duration(seconds: 8));
    final size = response.contentLength;
    final smallCompleteFile =
        response.statusCode == 200 && size != null && size <= limit;
    if ((!smallCompleteFile && response.statusCode != 206) ||
        (size ?? 0) > limit) {
      await response.stream.listen(null).cancel();
      return false;
    }
    final header = BytesBuilder(copy: false);
    await for (final chunk in response.stream.timeout(
      const Duration(seconds: 8),
    )) {
      if (header.length + chunk.length > limit) return false;
      header.add(chunk);
    }
    final original = manuscriptDimensions(header.takeBytes());
    return original != null &&
        mobile.width <= original.width &&
        mobile.height <= original.height &&
        (mobile.width < original.width || mobile.height < original.height);
  } on Exception {
    return false;
  } finally {
    client.close();
  }
}
