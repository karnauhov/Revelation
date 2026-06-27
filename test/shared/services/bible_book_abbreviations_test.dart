import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/services/bible_book_abbreviations.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late BibleBookAbbreviationCatalog catalog;

  setUpAll(() async {
    catalog = await BibleBookAbbreviationCatalog.loadFromAssets();
  });

  test('resolves localized Bible book aliases to canonical book ids', () {
    expect(catalog.bookIdForAlias('Rev'), 66);
    expect(catalog.bookIdForAlias('Apocalipsis'), 66);
    expect(catalog.bookIdForAlias('Откр.'), 66);
    expect(catalog.bookIdForAlias('Об’явл.'), 66);
    expect(catalog.bookIdForAlias('Gál'), 48);
    expect(catalog.bookIdForAlias('Joh'), 43);
    expect(catalog.bookIdForAlias('1 Ів'), 62);
    expect(catalog.bookIdForAlias('1 Jn'), 62);
  });

  test('resolves Bible link aliases used by bundled database content', () {
    expect(catalog.bookIdForAlias('Lev'), 3);
    expect(catalog.bookIdForAlias('Num'), 4);
    expect(catalog.bookIdForAlias('Mat'), 40);
    expect(catalog.bookIdForAlias('Mar'), 41);
    expect(catalog.bookIdForAlias('Luk'), 42);
    expect(catalog.bookIdForAlias('Joh'), 43);
    expect(catalog.bookIdForAlias('Act'), 44);
    expect(catalog.bookIdForAlias('Rom'), 45);
    expect(catalog.bookIdForAlias('1Co'), 46);
    expect(catalog.bookIdForAlias('2Co'), 47);
    expect(catalog.bookIdForAlias('Gal'), 48);
    expect(catalog.bookIdForAlias('1Ti'), 54);
    expect(catalog.bookIdForAlias('2Ti'), 55);
    expect(catalog.bookIdForAlias('Heb'), 58);
    expect(catalog.bookIdForAlias('1Pe'), 60);
    expect(catalog.bookIdForAlias('Rev'), 66);
  });

  test('returns null for unknown book aliases', () {
    expect(catalog.bookIdForAlias('Unknown book'), isNull);
  });
}
