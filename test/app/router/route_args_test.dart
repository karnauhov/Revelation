import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/shared/models/primary_source.dart';

void main() {
  group('TopicRouteArgs.tryParse', () {
    test('returns typed args as-is', () {
      const args = TopicRouteArgs(
        file: 'rev-1',
        name: 'Revelation 1',
        description: 'Intro',
      );

      final parsed = TopicRouteArgs.tryParse(args, const <String, String>{});

      expect(parsed, same(args));
      expect(parsed!.file, 'rev-1');
      expect(parsed.name, 'Revelation 1');
      expect(parsed.description, 'Intro');
    });

    test('rejects legacy map extra contract', () {
      final parsed = TopicRouteArgs.tryParse(<String, dynamic>{
        'file': 'rev-2',
        'name': 'Revelation 2',
        'description': 'Legacy',
      }, const <String, String>{});

      expect(parsed, isNull);
    });

    test('parses query parameters fallback', () {
      final parsed = TopicRouteArgs.tryParse(null, const <String, String>{
        'file': 'rev-3',
        'name': 'Revelation 3',
      });

      expect(parsed, isA<TopicRouteArgs>());
      expect(parsed!.file, 'rev-3');
      expect(parsed.name, 'Revelation 3');
      expect(parsed.description, isNull);
    });

    test('returns null when required file is missing', () {
      final parsed = TopicRouteArgs.tryParse(null, const <String, String>{});
      expect(parsed, isNull);
    });

    test('returns null when required file is blank', () {
      final parsed = TopicRouteArgs.tryParse(null, const <String, String>{
        'file': '   ',
      });
      expect(parsed, isNull);
    });
  });

  group('PrimarySourceRouteArgs.tryParse', () {
    test('parses typed args', () {
      final source = _buildSource('ps-1');
      final args = PrimarySourceRouteArgs(
        primarySource: source,
        pageName: 'page1',
        wordIndex: 5,
      );

      final parsed = PrimarySourceRouteArgs.tryParse(args);

      expect(parsed, same(args));
      expect(parsed!.primarySource, source);
      expect(parsed.pageName, 'page1');
      expect(parsed.wordIndex, 5);
    });

    test('returns null for any legacy map contract', () {
      final parsed = PrimarySourceRouteArgs.tryParse(<String, dynamic>{
        'primarySource': _buildSource('ps-3'),
        'pageName': 'A-01',
        'wordIndex': '7',
      });
      expect(parsed, isNull);
    });
  });

  group('BibleRouteArgs.tryParse', () {
    test('parses typed args as-is', () {
      const args = BibleRouteArgs(
        initialBookId: 40,
        initialChapter: 17,
        initialVerse: 5,
        initialModuleFile: 'bible_lxx_tr.sqlite',
      );

      final parsed = BibleRouteArgs.tryParse(args, const <String, String>{});

      expect(parsed, same(args));
    });

    test('parses positive query parameters with defaults', () {
      final parsed = BibleRouteArgs.tryParse(null, const <String, String>{
        'book': '40',
        'chapter': '17',
        'verse': '5',
        'module': 'bible_lxx_tr.sqlite',
      });

      expect(parsed.initialBookId, 40);
      expect(parsed.initialChapter, 17);
      expect(parsed.initialVerse, 5);
      expect(parsed.initialModuleFile, 'bible_lxx_tr.sqlite');
    });

    test('falls back to Revelation 1:1 for invalid values', () {
      final parsed = BibleRouteArgs.tryParse(null, const <String, String>{
        'book': '0',
        'chapter': '-1',
        'verse': 'x',
      });

      expect(parsed.initialBookId, 66);
      expect(parsed.initialChapter, 1);
      expect(parsed.initialVerse, 1);
      expect(parsed.initialModuleFile, isNull);
    });
  });
}

PrimarySource _buildSource(String id) {
  return PrimarySource(
    id: id,
    title: 'Title $id',
    date: '100',
    content: 'content',
    quantity: 1,
    material: 'papyrus',
    textStyle: 'uncial',
    found: 'found',
    classification: 'classification',
    currentLocation: 'location',
    preview: 'assets/images/UI/app_icon.png',
    maxScale: 1.0,
    isMonochrome: false,
    pages: const [],
    attributes: null,
    permissionsReceived: false,
  );
}
