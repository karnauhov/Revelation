const String strongOriginInfoMarkdownMarker = '{{strong_origin_info}}';
const String strongOriginInfoMarkdownTag = 'strong-origin-info';

String stripDescriptionMarkdownPresentationMarkers(String markdown) {
  return markdown
      .replaceAll('$strongOriginInfoMarkdownMarker ', '')
      .replaceAll(strongOriginInfoMarkdownMarker, '');
}
