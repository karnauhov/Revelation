import 'package:sentry_flutter/sentry_flutter.dart';

/// Keep route identity, never parameters or arbitrary route arguments.
String safeSentryRoute(String? value) {
  final path = Uri.tryParse(value ?? '')?.path;
  const routes = {
    '/',
    '/topic',
    '/primary_sources',
    '/strongs_dictionary',
    '/allusion_search',
    '/bible',
    '/revelation_structure',
    '/historical_background',
    '/practical_faith',
    '/primary_source',
    '/settings',
    '/about',
    '/privacy-policy',
    '/license',
    '/download',
  };
  if (routes.contains(path)) return path!;
  if (path == 'main') return '/';
  final namedPath = '/${path?.replaceAll('_', '-')}';
  if (routes.contains(namedPath)) return namedPath;
  if (routes.contains('/$path')) return '/$path';
  return '/unknown';
}

String _scrubText(String value) => value
    .replaceAllMapped(RegExp(r'https?://[^\s<>"\x27]+'), (match) {
      final uri = Uri.tryParse(match[0]!);
      if (uri == null) return '[url]';
      return Uri(
        scheme: uri.scheme,
        host: uri.host,
        port: uri.hasPort ? uri.port : null,
        path: uri.path,
      ).toString();
    })
    .replaceAll(
      RegExp(r'\bBearer\s+\S+', caseSensitive: false),
      'Bearer [redacted]',
    )
    .replaceAll(
      RegExp(
        r'\b(?:token|password|secret|api[_-]?key)\s*[=:]\s*[^\s,;]+',
        caseSensitive: false,
      ),
      '[credential]',
    )
    .replaceAll(
      RegExp(
        r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
        caseSensitive: false,
      ),
      '[email]',
    )
    .replaceAll(
      RegExp(
        r'(?:[A-Za-z]:[\\/](?:Users|home)[\\/]|/Users/|/home/)[^\s"\x27]+',
        caseSensitive: false,
      ),
      '[local-path]',
    )
    .replaceAll(RegExp(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), '[ip]');

dynamic _scrub(dynamic value) {
  if (value is String) return _scrubText(value);
  if (value is List) return value.map(_scrub).toList();
  if (value is Map) {
    return <String, dynamic>{
      for (final entry in value.entries)
        if (!RegExp(
          r'token|password|secret|api[_-]?key|authorization|cookie|headers|query_string|^vars$|^email$|^ip_address$|^device_id$|^installation_id$',
          caseSensitive: false,
        ).hasMatch(entry.key.toString()))
          entry.key.toString(): _scrub(entry.value),
    };
  }
  return value;
}

Breadcrumb? scrubSentryBreadcrumb(Breadcrumb? breadcrumb, Hint hint) {
  if (breadcrumb == null || breadcrumb.category != 'navigation') return null;
  return Breadcrumb(
    timestamp: breadcrumb.timestamp,
    category: 'navigation',
    type: 'navigation',
    data: {
      'from': safeSentryRoute(breadcrumb.data?['from']?.toString()),
      'to': safeSentryRoute(breadcrumb.data?['to']?.toString()),
    },
  );
}

/// Scrub the serialized boundary while retaining native debug IDs, frames,
/// release identity and the app/database metadata needed for diagnosis.
SentryEvent scrubSentryEvent(SentryEvent event, Hint hint) {
  final json = Map<String, dynamic>.from(_scrub(event.toJson()));
  for (final key in ['user', 'request', 'server_name', 'extra']) {
    json.remove(key);
  }
  final contexts = json['contexts'] as Map?;
  contexts?.removeWhere(
    (key, value) => !const {
      'app',
      'os',
      'device',
      'browser',
      'runtime',
      'runtimes',
      'gpu',
      'culture',
      'trace',
      'flutter',
      'revelation.app',
      'revelation.data',
      'revelation.error',
    }.contains(key),
  );
  final device = contexts?['device'];
  if (device is Map) {
    device.remove('id');
    device.remove('name');
  }
  if (json['transaction'] != null && json['transaction'] != 'app.session') {
    json['transaction'] = safeSentryRoute(json['transaction']?.toString());
  }
  final app = contexts?['app'];
  if (app is Map && app['view_names'] is List) {
    app['view_names'] = (app['view_names'] as List)
        .map((value) => safeSentryRoute(value?.toString()))
        .toList();
  }
  // Returning a new SentryEvent for a transaction would discard its spans.
  final clean = SentryEvent.fromJson(json);
  event.user = null;
  event.request = null;
  event.serverName = null;
  // ignore: deprecated_member_use
  event.extra = null;
  event.contexts = clean.contexts;
  event.tags = clean.tags;
  event.message = clean.message;
  event.exceptions = clean.exceptions;
  event.threads = clean.threads;
  event.transaction = clean.transaction;
  event.debugMeta = clean.debugMeta;
  event.logger = clean.logger;
  event.culprit = clean.culprit;
  event.fingerprint = clean.fingerprint;
  event.breadcrumbs = event.breadcrumbs
      ?.map((crumb) => scrubSentryBreadcrumb(crumb, hint))
      .whereType<Breadcrumb>()
      .toList();
  final errorContext = event.contexts['revelation.error'];
  if (errorContext is Map) {
    for (final exception in event.exceptions ?? <SentryException>[]) {
      exception.mechanism = Mechanism(
        type: 'revelation.application',
        handled: errorContext['fatal'] != true,
      );
    }
  }
  return event;
}
