import 'dart:convert';
import 'dart:typed_data';

/// Two compressed sparse rows: verse -> term and term -> verse.
/// The v1 file uses little-endian arrays, with its header aligned to 8 bytes.
class AllusionPostings {
  const AllusionPostings({
    required this.documents,
    required this.baseWeights,
    required this.verseOffsets,
    required this.termOffsets,
    required this.terms,
    required this.verses,
  });

  final int documents;
  final Float64List baseWeights;
  final Uint32List verseOffsets;
  final Uint32List termOffsets;
  final Uint16List terms;
  final Uint16List verses;

  Uint16List numbersFor(int ordinal) => Uint16List.sublistView(
    terms,
    verseOffsets[ordinal],
    verseOffsets[ordinal + 1],
  );

  Uint16List versesFor(int number) => Uint16List.sublistView(
    verses,
    termOffsets[number],
    termOffsets[number + 1],
  );

  Uint8List encode(Map<String, Object?> metadata) {
    final payload = BytesBuilder(copy: false);
    for (final data in <TypedData>[
      baseWeights,
      verseOffsets,
      termOffsets,
      terms,
      verses,
    ]) {
      payload.add(Uint8List.sublistView(data));
    }
    final bytes = payload.takeBytes();
    final header = utf8.encode(
      jsonEncode({
        ...metadata,
        'verses': verseOffsets.length - 2,
        'terms': baseWeights.length - 1,
        'documents': documents,
        'pairs': terms.length,
        'checksum': _checksum(bytes),
      }),
    );
    final length = (header.length + 7) & ~7;
    final out = Uint8List(8 + length + bytes.length);
    final fields = ByteData.sublistView(out);
    fields.setUint32(0, 0x414c5831);
    fields.setUint32(4, length, Endian.little);
    out.setRange(8, 8 + header.length, header);
    out.fillRange(8 + header.length, 8 + length, 32);
    out.setRange(8 + length, out.length, bytes);
    return out;
  }

  static ({Map<String, dynamic> metadata, AllusionPostings postings}) decode(
    Uint8List bytes, {
    int? verseCount,
  }) {
    const invalid = FormatException('Invalid allusion index');
    if (bytes.length < 8 || Endian.host != Endian.little) throw invalid;
    if (bytes.offsetInBytes % 8 != 0) bytes = Uint8List.fromList(bytes);
    final fields = ByteData.sublistView(bytes);
    final headerSize = fields.getUint32(4, Endian.little);
    if (fields.getUint32(0) != 0x414c5831 ||
        headerSize % 8 != 0 ||
        headerSize > 16384 ||
        bytes.length < 8 + headerSize)
      throw invalid;
    final decoded = jsonDecode(utf8.decode(bytes.sublist(8, 8 + headerSize)));
    if (decoded is! Map<String, dynamic>) throw invalid;
    final terms = decoded['terms'],
        pairs = decoded['pairs'],
        documents = decoded['documents'];
    final recordedCount = decoded['verses'];
    if (recordedCount is! int ||
        recordedCount < 1 ||
        recordedCount > 65535 ||
        (verseCount != null && recordedCount != verseCount) ||
        terms is! int ||
        terms < 1 ||
        terms > 65535 ||
        pairs is! int ||
        pairs < 1 ||
        documents is! int ||
        documents < 1 ||
        documents > recordedCount) {
      throw invalid;
    }
    verseCount = recordedCount;
    final offset = 8 + headerSize;
    final expected =
        offset + 8 * (terms + 1) + 4 * (verseCount + 2 + terms + 2 + pairs);
    if (expected != bytes.length ||
        _checksum(Uint8List.sublistView(bytes, offset)) !=
            decoded['checksum']) {
      throw invalid;
    }
    final verseOffsetsStart = offset + 8 * (terms + 1);
    final termOffsetsStart = verseOffsetsStart + 4 * (verseCount + 2);
    final termValuesStart = termOffsetsStart + 4 * (terms + 2);
    final verseValuesStart = termValuesStart + 2 * pairs;
    final weights = Float64List.sublistView(bytes, offset, verseOffsetsStart);
    final verseOffsets = Uint32List.sublistView(
      bytes,
      verseOffsetsStart,
      termOffsetsStart,
    );
    final termOffsets = Uint32List.sublistView(
      bytes,
      termOffsetsStart,
      termValuesStart,
    );
    final termValues = Uint16List.sublistView(
      bytes,
      termValuesStart,
      verseValuesStart,
    );
    final verseValues = Uint16List.sublistView(bytes, verseValuesStart);
    for (final offsets in [verseOffsets, termOffsets]) {
      if (offsets.first != 0 || offsets.last != pairs) throw invalid;
      for (var i = 1; i < offsets.length; i++) {
        if (offsets[i] < offsets[i - 1]) throw invalid;
      }
    }
    if (weights.any((w) => !w.isFinite || w < 0 || w > 1) ||
        termValues.any((n) => n < 1 || n > terms || weights[n] <= 0) ||
        verseValues.any((v) => v < 1 || v > recordedCount))
      throw invalid;
    return (
      metadata: decoded,
      postings: AllusionPostings(
        documents: documents,
        baseWeights: weights,
        verseOffsets: verseOffsets,
        termOffsets: termOffsets,
        terms: termValues,
        verses: verseValues,
      ),
    );
  }

  // Adler-32, using zlib's safe interval before taking the moduli.
  static int _checksum(Uint8List bytes) {
    var a = 1, b = 0;
    for (var offset = 0; offset < bytes.length;) {
      final end = (offset + 5552).clamp(0, bytes.length);
      while (offset < end) {
        a += bytes[offset++];
        b += a;
      }
      a %= 65521;
      b %= 65521;
    }
    return b * 65536 + a;
  }
}
