const String strongUsageBibleReferenceTitlePrefix = 'strong_usage_ref:';
const String strongUsageMoreReferencePrefix = 'strong_usage_more:';

String strongUsageBibleReferenceTitle(String verseKey) {
  return '$strongUsageBibleReferenceTitlePrefix${verseKey.trim().toUpperCase()}';
}

String? strongUsageBibleReferenceVerseKeyFromTitle(String? title) {
  final normalized = title?.trim();
  if (normalized == null ||
      !normalized.startsWith(strongUsageBibleReferenceTitlePrefix)) {
    return null;
  }

  final verseKey = normalized
      .substring(strongUsageBibleReferenceTitlePrefix.length)
      .trim()
      .toUpperCase();
  return RegExp(r'^[0-9A-Z]{3}$').hasMatch(verseKey) ? verseKey : null;
}

String strongUsageMoreReferenceTitle(String id) {
  return '$strongUsageMoreReferencePrefix${id.trim()}';
}

String strongUsageMoreReferenceHref(String id) {
  return '$strongUsageMoreReferencePrefix${id.trim()}';
}

String? strongUsageMoreReferenceIdFromTitle(String? title) {
  return _strongUsageMoreReferenceId(title);
}

String? strongUsageMoreReferenceIdFromHref(String? href) {
  return _strongUsageMoreReferenceId(href);
}

String? _strongUsageMoreReferenceId(String? value) {
  final normalized = value?.trim();
  if (normalized == null ||
      !normalized.startsWith(strongUsageMoreReferencePrefix)) {
    return null;
  }

  final id = normalized.substring(strongUsageMoreReferencePrefix.length).trim();
  return RegExp(r'^[0-9A-Za-z_-]+$').hasMatch(id) ? id : null;
}

String stripStrongUsageBibleReferenceTitles(String markdown) {
  return markdown
      .replaceAllMapped(
        RegExp(
          r'\]\((bible:[^\s)]+)\s+"strong_usage_ref:[0-9A-Z]{3}"\)',
          caseSensitive: false,
        ),
        (match) => '](${match.group(1)!})',
      )
      .replaceAllMapped(
        RegExp(
          r'\]\((strong_usage_more:[^\s)]+)\s+"strong_usage_more:[^"]+"\)',
          caseSensitive: false,
        ),
        (match) => '](${match.group(1)!})',
      )
      .replaceAllMapped(
        RegExp(
          r'\[\.\.\.\]\(strong_usage_more:[^\s)]+\)',
          caseSensitive: false,
        ),
        (_) => '...',
      );
}
