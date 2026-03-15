import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/models/pages_settings.dart';

void main() {
  test('packData and unpackData round-trip values', () {
    final packed = PagesSettings.packData(
      posX: 12.5,
      posY: -3.75,
      scale: 1.4,
      isNegative: true,
      isMonochrome: true,
      brightness: 22,
      contrast: 88,
      showWordSeparators: true,
      showStrongNumbers: false,
      showVerseNumbers: true,
    );

    final unpacked = PagesSettings.unpackData(packed);

    expect(unpacked['position']['x'], 12.5);
    expect(unpacked['position']['y'], -3.75);
    expect(unpacked['scale'], 1.4);
    expect(unpacked['isNegative'], isTrue);
    expect(unpacked['isMonochrome'], isTrue);
    expect(unpacked['brightness'], 22);
    expect(unpacked['contrast'], 88);
    expect(unpacked['wordSeparators'], isTrue);
    expect(unpacked['strongNumbers'], isFalse);
    expect(unpacked['verseNumbers'], isTrue);
  });

  test('unpackData defaults verseNumbers to true for legacy payload', () {
    const doublesCount = 5;
    const int flagsOffset = 8 * doublesCount;
    const int totalBytes = flagsOffset + 1;
    final buffer = ByteData(totalBytes);
    var offset = 0;
    buffer.setFloat64(offset, 0, Endian.little);
    offset += 8;
    buffer.setFloat64(offset, 0, Endian.little);
    offset += 8;
    buffer.setFloat64(offset, 1, Endian.little);
    offset += 8;
    buffer.setFloat64(offset, 0, Endian.little);
    offset += 8;
    buffer.setFloat64(offset, 100, Endian.little);
    offset += 8;

    const int flags = 0;
    buffer.setUint8(offset, flags);

    final bytes = buffer.buffer.asUint8List();
    var b64 = base64Url.encode(bytes);
    b64 = b64.replaceAll('=', '');

    final unpacked = PagesSettings.unpackData(b64);

    expect(unpacked['verseNumbers'], isTrue);
  });
}
