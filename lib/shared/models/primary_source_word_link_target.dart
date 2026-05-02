class PrimarySourceWordLinkTarget {
  const PrimarySourceWordLinkTarget({
    required this.sourceId,
    this.pageName,
    this.wordIndex,
  });

  final String sourceId;
  final String? pageName;
  final int? wordIndex;

  bool get hasWordReference => pageName != null && wordIndex != null;

  String get fallbackLabel {
    final buffer = StringBuffer(sourceId);
    final page = pageName;
    if (page != null && page.isNotEmpty) {
      buffer.write(':$page');
    }
    final index = wordIndex;
    if (index != null) {
      buffer.write(':$index');
    }
    return buffer.toString();
  }

  String? get wordLink {
    final page = pageName;
    final index = wordIndex;
    if (page == null || page.isEmpty || index == null) {
      return null;
    }
    return 'word:$sourceId:$page:$index';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourceWordLinkTarget &&
            runtimeType == other.runtimeType &&
            sourceId == other.sourceId &&
            pageName == other.pageName &&
            wordIndex == other.wordIndex;
  }

  @override
  int get hashCode => Object.hash(sourceId, pageName, wordIndex);
}
