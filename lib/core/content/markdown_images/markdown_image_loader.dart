import 'package:revelation/core/content/markdown_images/markdown_image_load_result.dart';

enum MarkdownImageRequestKind { databaseResource, supabaseStorage, network }

class MarkdownImageRequest {
  const MarkdownImageRequest({
    required this.kind,
    required this.cacheKey,
    this.databaseResourceKey,
    this.supabaseBucket,
    this.supabasePath,
    this.networkUri,
    this.guessedMimeType,
    this.localRelativePath,
  });

  final MarkdownImageRequestKind kind;
  final String cacheKey;
  final String? databaseResourceKey;
  final String? supabaseBucket;
  final String? supabasePath;
  final Uri? networkUri;
  final String? guessedMimeType;
  final String? localRelativePath;
}

abstract class MarkdownImageLoader {
  Future<MarkdownImageLoadResult> loadImage(MarkdownImageRequest request);
}
