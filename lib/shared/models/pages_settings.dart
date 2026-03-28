import 'dart:convert';
import 'dart:typed_data';

class PagesSettings {
  final Map<String, dynamic> pages;

  PagesSettings({required this.pages});

  Map<String, dynamic> toMap() {
    return {'pages': pages};
  }

  factory PagesSettings.fromMap(Map<String, dynamic> map) {
    if (map.containsKey("pages")) {
      return PagesSettings(pages: map['pages']);
    } else {
      return PagesSettings(pages: {});
    }
  }

  static String packData({
    double posX = 0,
    double posY = 0,
    double scale = 0,
    bool isNegative = false,
    bool isMonochrome = false,
    double brightness = 0,
    double contrast = 100,
    bool showWordSeparators = false,
    bool showStrongNumbers = false,
    bool showVerseNumbers = true,
  }) {
    const int doublesCount = 5;
    const int flagsOffset = 8 * doublesCount;
    const int totalBytes = flagsOffset + 2; // flags + format marker
    final buffer = ByteData(totalBytes);

    int offset = 0;
    buffer.setFloat64(offset, posX, Endian.little);
    offset += 8;
    buffer.setFloat64(offset, posY, Endian.little);
    offset += 8;
    buffer.setFloat64(offset, scale, Endian.little);
    offset += 8;
    buffer.setFloat64(offset, brightness, Endian.little);
    offset += 8;
    buffer.setFloat64(offset, contrast, Endian.little);
    offset += 8;

    int flags =
        (isNegative ? 1 : 0) |
        (isMonochrome ? 2 : 0) |
        (showWordSeparators ? 4 : 0) |
        (showStrongNumbers ? 8 : 0) |
        (showVerseNumbers ? 16 : 0);
    buffer.setUint8(offset, flags);
    buffer.setUint8(offset + 1, 1); // format marker

    final bytes = buffer.buffer.asUint8List();
    String b64 = base64Url.encode(bytes);
    b64 = b64.replaceAll('=', '');
    return b64;
  }

  static Map<String, dynamic> unpackData(String b64) {
    int mod4 = b64.length % 4;
    if (mod4 > 0) {
      b64 = b64.padRight(b64.length + (4 - mod4), '=');
    }

    final bytes = base64Url.decode(b64);
    final buffer = ByteData.sublistView(Uint8List.fromList(bytes));

    int offset = 0;
    double posX = buffer.getFloat64(offset, Endian.little);
    offset += 8;
    double posY = buffer.getFloat64(offset, Endian.little);
    offset += 8;
    double scale = buffer.getFloat64(offset, Endian.little);
    offset += 8;
    double brightness = buffer.getFloat64(offset, Endian.little);
    offset += 8;
    double contrast = buffer.getFloat64(offset, Endian.little);
    offset += 8;

    int flags = buffer.getUint8(offset);
    final bool hasVerseNumbersFlag = bytes.length >= (8 * 5 + 2);
    bool isNegative = (flags & 1) != 0;
    bool isMonochrome = (flags & 2) != 0;
    bool showWordSeparators = (flags & 4) != 0;
    bool showStrongNumbers = (flags & 8) != 0;
    bool showVerseNumbers = hasVerseNumbersFlag ? (flags & 16) != 0 : true;

    return {
      'position': {'x': posX, 'y': posY},
      'scale': scale,
      'brightness': brightness,
      'contrast': contrast,
      'isNegative': isNegative,
      'isMonochrome': isMonochrome,
      'wordSeparators': showWordSeparators,
      'strongNumbers': showStrongNumbers,
      'verseNumbers': showVerseNumbers,
    };
  }
}
