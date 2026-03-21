import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/models/page.dart';
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/verse.dart';

void main() {
  test('page keeps required and optional fields', () {
    final words = <PageWord>[
      PageWord(
        'word',
        <PageRect>[PageRect(0, 0, 4, 3)],
        notExist: const <int>[1],
        sn: 12,
        snPronounce: true,
        snXshift: 1.5,
      ),
    ];
    const verses = <Verse>[
      Verse(
        chapterNumber: 1,
        verseNumber: 2,
        labelPosition: Offset(12, 30),
        wordIndexes: <int>[0, 1],
        contours: <List<Offset>>[
          <Offset>[Offset(0, 0), Offset(1, 1)],
        ],
      ),
    ];

    final page = Page(
      name: 'page-1',
      content: 'text',
      image: 'image.png',
      words: words,
      verses: verses,
    );

    expect(page.name, 'page-1');
    expect(page.content, 'text');
    expect(page.image, 'image.png');
    expect(page.words, same(words));
    expect(page.verses, same(verses));
  });

  test('page defaults words and verses to empty lists', () {
    final page = Page(name: 'name', content: 'content', image: 'img');

    expect(page.words, isEmpty);
    expect(page.verses, isEmpty);
  });

  test('equality ignores words and verses and matches metadata only', () {
    final left = Page(
      name: 'name',
      content: 'content',
      image: 'image',
      words: <PageWord>[
        PageWord('left', <PageRect>[PageRect(0, 0, 1, 1)]),
      ],
      verses: const <Verse>[
        Verse(chapterNumber: 1, verseNumber: 1, labelPosition: Offset.zero),
      ],
    );
    final right = Page(
      name: 'name',
      content: 'content',
      image: 'image',
      words: <PageWord>[
        PageWord('right', <PageRect>[PageRect(2, 2, 3, 3)]),
      ],
      verses: const <Verse>[
        Verse(chapterNumber: 2, verseNumber: 9, labelPosition: Offset(5, 5)),
      ],
    );

    expect(left, right);
    expect(left.hashCode, right.hashCode);
  });

  test('equality changes when key metadata changes', () {
    final base = Page(name: 'name', content: 'content', image: 'image');

    expect(
      base,
      isNot(Page(name: 'other', content: 'content', image: 'image')),
    );
    expect(base, isNot(Page(name: 'name', content: 'other', image: 'image')));
    expect(base, isNot(Page(name: 'name', content: 'content', image: 'other')));
    expect(base, isNot('not-a-page'));
  });
}
