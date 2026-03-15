import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/xml/xml_parsers.dart';
import 'package:xml/xml.dart';

void main() {
  test('parseLibraries returns parsed entries', () async {
    final bundle = _FakeAssetBundle({
      'libraries.xml': '''
<root>
  <library>
    <name>Lib</name>
    <idIcon>icon</idIcon>
    <license>MIT</license>
    <officialSite>https://example.test</officialSite>
    <licenseLink>https://license.test</licenseLink>
  </library>
</root>
''',
    });

    final libraries = await parseLibraries(bundle, 'libraries.xml');

    expect(libraries.length, 1);
    final library = libraries.first;
    expect(library.name, 'Lib');
    expect(library.idIcon, 'icon');
    expect(library.license, 'MIT');
    expect(library.officialSite, 'https://example.test');
    expect(library.licenseLink, 'https://license.test');
  });

  test('parseLibraries throws for missing required tags', () async {
    final bundle = _FakeAssetBundle({
      'libraries.xml': '''
<root>
  <library>
    <name>Lib</name>
    <idIcon>icon</idIcon>
  </library>
</root>
''',
    });

    expect(
      () => parseLibraries(bundle, 'libraries.xml'),
      throwsA(
        predicate(
          (error) =>
              error is Exception &&
              error.toString().contains('Missing required tags in library'),
        ),
      ),
    );
  });

  test('parseLibraries rethrows XML exceptions', () async {
    final bundle = _FakeAssetBundle({
      'libraries.xml': '<root><library></root>',
    });

    expect(
      () => parseLibraries(bundle, 'libraries.xml'),
      throwsA(isA<XmlException>()),
    );
  });

  test('parseLibraries rethrows platform exceptions', () async {
    final bundle = _FakeAssetBundle(const {}, throwPlatformException: true);

    expect(
      () => parseLibraries(bundle, 'libraries.xml'),
      throwsA(isA<PlatformException>()),
    );
  });

  test('parseInstitutions parses sources map', () async {
    final bundle = _FakeAssetBundle({
      'institutions.xml': '''
<root>
  <institution>
    <name>Inst</name>
    <idIcon>icon</idIcon>
    <officialSite>https://example.test</officialSite>
    <sources>
      <source>
        <text>Source A</text>
        <link>https://a.test</link>
      </source>
    </sources>
  </institution>
</root>
''',
    });

    final institutions = await parseInstitutions(bundle, 'institutions.xml');

    expect(institutions.length, 1);
    final institution = institutions.first;
    expect(institution.name, 'Inst');
    expect(institution.idIcon, 'icon');
    expect(institution.officialSite, 'https://example.test');
    expect(institution.sources, const {'Source A': 'https://a.test'});
  });

  test('parseInstitutions throws for missing required tags', () async {
    final bundle = _FakeAssetBundle({
      'institutions.xml': '''
<root>
  <institution>
    <name>Inst</name>
    <idIcon>icon</idIcon>
  </institution>
</root>
''',
    });

    expect(
      () => parseInstitutions(bundle, 'institutions.xml'),
      throwsA(
        predicate(
          (error) =>
              error is Exception &&
              error.toString().contains('Missing required tags in institution'),
        ),
      ),
    );
  });

  test('parseRecommended parses entries', () async {
    final bundle = _FakeAssetBundle({
      'recommended.xml': '''
<root>
  <recommendation>
    <name>Rec</name>
    <idIcon>icon</idIcon>
    <officialSite>https://example.test</officialSite>
  </recommendation>
</root>
''',
    });

    final items = await parseRecommended(bundle, 'recommended.xml');

    expect(items.length, 1);
    final item = items.first;
    expect(item.name, 'Rec');
    expect(item.idIcon, 'icon');
    expect(item.officialSite, 'https://example.test');
  });

  test('parseRecommended throws for missing required tags', () async {
    final bundle = _FakeAssetBundle({
      'recommended.xml': '''
<root>
  <recommendation>
    <name>Rec</name>
  </recommendation>
</root>
''',
    });

    expect(
      () => parseRecommended(bundle, 'recommended.xml'),
      throwsA(
        predicate(
          (error) =>
              error is Exception &&
              error.toString().contains(
                'Missing required tags in recommendation',
              ),
        ),
      ),
    );
  });
}

class _FakeAssetBundle extends AssetBundle {
  _FakeAssetBundle(this._assets, {this.throwPlatformException = false});

  final Map<String, String> _assets;
  final bool throwPlatformException;

  @override
  Future<ByteData> load(String key) {
    throw UnimplementedError();
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    if (throwPlatformException) {
      throw PlatformException(code: 'asset-failure');
    }
    final value = _assets[key];
    if (value == null) {
      throw Exception('Unable to load asset: $key');
    }
    return value;
  }

  @override
  Future<T> loadStructuredData<T>(
    String key,
    Future<T> Function(String value) parser,
  ) async {
    return parser(await loadString(key));
  }

  @override
  void evict(String key) {}

  @override
  void clear() {}
}
