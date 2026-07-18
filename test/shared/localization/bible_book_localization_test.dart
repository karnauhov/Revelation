import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/bible_book_localization.dart';

void main() {
  test('returns localized Bible book codes and names by canonical book id', () {
    final en = lookupAppLocalizations(const Locale('en'));
    final es = lookupAppLocalizations(const Locale('es'));
    final ru = lookupAppLocalizations(const Locale('ru'));
    final uk = lookupAppLocalizations(const Locale('uk'));

    expect(localizedBibleBookCode(en, 1), 'Gen');
    expect(localizedBibleBookName(en, 66), 'Revelation');
    expect(localizedBibleBookCode(es, 48), 'G\u00e1');
    expect(localizedBibleBookName(es, 1), 'G\u00e9nesis');
    expect(localizedBibleBookCode(ru, 1), '\u0411\u044b\u0442');
    expect(
      localizedBibleBookName(ru, 66),
      '\u041e\u0442\u043a\u0440\u043e\u0432\u0435\u043d\u0438\u0435',
    );
    expect(localizedBibleBookCode(uk, 66), '\u041e\u0431');
    expect(
      localizedBibleBookName(uk, 66),
      '\u041e\u0431\u2019\u044f\u0432\u043b\u0435\u043d\u043d\u044f',
    );
  });

  test('rejects out-of-range canonical book ids', () {
    final en = lookupAppLocalizations(const Locale('en'));

    expect(() => localizedBibleBookCode(en, 0), throwsRangeError);
    expect(() => localizedBibleBookName(en, 67), throwsRangeError);
  });
}
