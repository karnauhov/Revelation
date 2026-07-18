const String strongOriginInfoMarkdownMarker = '{{strong_origin_info}}';
const String strongOriginInfoMarkdownTag = 'strong-origin-info';
const String strongUsageInfoMarkdownMarker = '{{strong_usage_info}}';
const String strongUsageInfoMarkdownTag = 'strong-usage-info';

String stripStrongOriginInfoMarkdownMarker(String markdown) {
  return markdown
      .replaceAll('$strongOriginInfoMarkdownMarker ', ' ')
      .replaceAll(strongOriginInfoMarkdownMarker, ' ');
}

String stripStrongArticleInfoMarkdownMarkers(String markdown) {
  return markdown
      .replaceAll('$strongOriginInfoMarkdownMarker ', ' ')
      .replaceAll(strongOriginInfoMarkdownMarker, ' ')
      .replaceAll('$strongUsageInfoMarkdownMarker ', ' ')
      .replaceAll(strongUsageInfoMarkdownMarker, ' ');
}
