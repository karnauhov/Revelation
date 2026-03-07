class PrimarySourceLinkInfo {
  final String role;
  final String url;
  final String titleOverride;

  const PrimarySourceLinkInfo({
    required this.role,
    required this.url,
    this.titleOverride = '',
  });
}
