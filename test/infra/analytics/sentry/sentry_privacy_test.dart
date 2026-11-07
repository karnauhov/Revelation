import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/analytics/sentry/sentry_privacy.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

void main() {
  test(
    'scrubs payloads while preserving symbolication and database evidence',
    () {
      final event = SentryEvent.fromJson({
        'event_id': '0123456789abcdef0123456789abcdef',
        'release': 'revelation@1.0.8+174',
        'dist': '174',
        'user': {'id': 'private-user', 'email': 'person@example.com'},
        'request': {'url': 'https://example.com?token=private-token'},
        'server_name': 'private-host',
        'extra': {'secret': 'private-extra'},
        'transaction': '/bible?text=private-text',
        'contexts': {
          'device': {
            'name': 'private-device',
            'id': 'private-device-id',
            'model': 'test-model',
          },
          'revelation.data': {'language_code': 'uk', 'schema_version': 3},
          'revelation.error': {'source': 'bootstrap', 'fatal': true},
          'arbitrary': {'value': 'private-context'},
        },
        'exception': {
          'values': [
            {
              'type': 'StateError',
              'value':
                  'person@example.com Bearer private-auth token=private-value',
              'stacktrace': {
                'frames': [
                  {
                    'filename': 'web.dart',
                    'function': 'openDatabase',
                    'lineno': 42,
                    'abs_path':
                        'https://example.com/main.dart.js?token=private-query#private-fragment',
                    'vars': {'password': 'private-variable'},
                  },
                ],
              },
            },
          ],
        },
        'debug_meta': {
          'images': [
            {
              'type': 'sourcemap',
              'debug_id': 'abcd-1234',
              'code_file': 'https://example.com/main.dart.js',
            },
          ],
        },
        'breadcrumbs': [
          {'category': 'console', 'message': 'private-console'},
          {
            'category': 'navigation',
            'data': {
              'from': '/settings?secret=private',
              'to': '/bible?text=private-text',
              'arguments': 'private-args',
            },
          },
        ],
      });
      final cleaned = scrubSentryEvent(event, Hint());
      final json = cleaned.toJson();
      expect(jsonEncode(json), isNot(contains('private')));
      expect(jsonEncode(json), isNot(contains('person@example.com')));
      expect(cleaned.release, 'revelation@1.0.8+174');
      expect(cleaned.transaction, '/bible');
      expect(cleaned.contexts['revelation.data']['schema_version'], 3);
      final exception = cleaned.exceptions!.single;
      expect(exception.mechanism?.handled, isFalse);
      final frame = exception.stackTrace!.frames.single;
      expect(frame.function, 'openDatabase');
      expect(frame.lineNo, 42);
      expect(frame.absPath, 'https://example.com/main.dart.js');
      expect(cleaned.debugMeta!.images.single.debugId, 'abcd-1234');
      expect(cleaned.breadcrumbs!.single.data, {
        'from': '/settings',
        'to': '/bible',
      });
    },
  );

  test(
    'handled reports keep handled mechanism and unknown routes are bounded',
    () {
      final event = SentryEvent(
        contexts: Contexts()..['revelation.error'] = {'fatal': false},
        exceptions: [SentryException(type: 'Exception', value: 'test')],
      );
      expect(
        scrubSentryEvent(event, Hint()).exceptions!.single.mechanism!.handled,
        isTrue,
      );
      expect(safeSentryRoute('settings'), '/settings');
      expect(safeSentryRoute('privacy_policy'), '/privacy-policy');
      expect(safeSentryRoute('/users/secret'), '/unknown');
    },
  );
}
