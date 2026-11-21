import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:revelation/shared/config/app_constants.dart';

typedef BiblePanePlace = ({
  String module,
  int book,
  int chapter,
  int verse,
  int? topVerse,
  int selectionStart,
  int selectionEnd,
  bool showStrongNumbers,
});

class BibleReadingSession {
  BibleReadingSession({
    required this.linkedNavigation,
    required Iterable<BiblePanePlace> panes,
  }) : panes = List.unmodifiable(panes);

  final bool linkedNavigation;
  final List<BiblePanePlace> panes;

  String encode() => jsonEncode({
    'version': 1,
    'linked': linkedNavigation,
    'panes': [
      for (final pane in panes)
        {
          'module': pane.module,
          'book': pane.book,
          'chapter': pane.chapter,
          'verse': pane.verse,
          'top': pane.topVerse,
          'start': pane.selectionStart,
          'end': pane.selectionEnd,
          'strong': pane.showStrongNumbers,
        },
    ],
  });

  static BibleReadingSession? decode(String? value) {
    if (value == null) return null;
    try {
      final data = jsonDecode(value);
      if (data is! Map ||
          data['version'] != 1 ||
          data['linked'] is! bool ||
          data['panes'] is! List)
        return null;
      final panes = <BiblePanePlace>[];
      for (final row in (data['panes'] as List).take(
        AppConstants.maxParallelBibleReaders,
      )) {
        if (row
            case {
              'module': String module,
              'book': int book,
              'chapter': int chapter,
              'verse': int verse,
              'top': int? top,
              'start': int start,
              'end': int end,
              'strong': bool strong,
            }
            when module.trim().isNotEmpty &&
                book > 0 &&
                chapter > 0 &&
                verse > 0 &&
                (top == null || top > 0) &&
                start > 0 &&
                end > 0) {
          panes.add((
            module: module,
            book: book,
            chapter: chapter,
            verse: verse,
            topVerse: top,
            selectionStart: start,
            selectionEnd: end,
            showStrongNumbers: strong,
          ));
        } else {
          return null;
        }
      }
      return panes.isEmpty
          ? null
          : BibleReadingSession(
              linkedNavigation: data['linked'] as bool,
              panes: panes,
            );
    } on FormatException {
      return null;
    }
  }

  @override
  bool operator ==(Object other) =>
      other is BibleReadingSession &&
      linkedNavigation == other.linkedNavigation &&
      listEquals(panes, other.panes);

  @override
  int get hashCode => Object.hash(linkedNavigation, Object.hashAll(panes));
}
