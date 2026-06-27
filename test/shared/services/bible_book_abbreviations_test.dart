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
    expect(catalog.bookIdForAlias('1 Ів'), 62);
    expect(catalog.bookIdForAlias('1 Jn'), 62);
  });

  test('returns null for unknown book aliases', () {
    expect(catalog.bookIdForAlias('Unknown book'), isNull);
  });
}
