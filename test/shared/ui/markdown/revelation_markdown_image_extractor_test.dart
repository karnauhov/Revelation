import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/config/supabase_storage_paths.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_extractor.dart';

void main() {
  test('extracts regular and custom block markdown images with metadata', () {
    const markdown = '''
![Inline](https://adfdfxnzxmzyoioedwuy.supabase.co/storage/v1/object/public/images/inline.svg#320x180)

{{image}}
src: images/chart.svg
alt: Chart alt
align: right
width: 240
height: 120
caption: Chart caption
{{/image}}

{{image}}
src: resource:assets/images/example.png
alt: Asset alt
align: left
{{/image}}
''';

    final images = extractRevelationMarkdownImages(markdown);

    expect(images, hasLength(3));

    final inline = images[0];
    expect(inline.isBlockImage, isFalse);
    expect(
      inline.source.kind,
      RevelationMarkdownImageSourceKind.supabaseStorage,
    );
    expect(inline.source.isSvg, isTrue);
    expect(inline.width, 320);
    expect(inline.height, 180);
    expect(inline.source.supabaseBucket, 'images');
    expect(inline.source.supabasePath, 'inline.svg');
    expect(inline.source.buildLocalRelativePath(), 'inline.svg');

    final block = images[1];
    expect(block.isBlockImage, isTrue);
    expect(
      block.source.kind,
      RevelationMarkdownImageSourceKind.supabaseStorage,
    );
    expect(block.source.supabaseBucket, 'images');
    expect(block.source.supabasePath, 'chart.svg');
    expect(block.alignment, RevelationMarkdownImageAlignment.right);
    expect(block.width, 240);
    expect(block.height, 120);
    expect(block.caption, 'Chart caption');
    expect(block.source.buildLocalRelativePath(), 'chart.svg');

    final asset = images[2];
    expect(asset.isBlockImage, isTrue);
    expect(asset.source.kind, RevelationMarkdownImageSourceKind.asset);
    expect(asset.alignment, RevelationMarkdownImageAlignment.left);
    expect(asset.alt, 'Asset alt');
  });

  test('supabase public storage helper builds and parses object urls', () {
    const bucket = 'images';
    const objectPath = 'maps/seal map.jpg';

    final uri = buildSupabasePublicStorageUri(
      bucket: bucket,
      objectPath: objectPath,
      baseUrl: 'https://demo.supabase.co',
    );

    expect(
      uri.toString(),
      'https://demo.supabase.co/storage/v1/object/public/images/maps/seal%20map.jpg',
    );
    expect(
      parseSupabasePublicStorageUri(uri!),
      const SupabasePublicStorageObjectRef(
        bucket: bucket,
        objectPath: objectPath,
      ),
    );
  });

  test('full Supabase public urls stay directly reusable for rendering', () {
    const sourceUrl =
        'https://adfdfxnzxmzyoioedwuy.supabase.co/storage/v1/object/public/images/map.svg';

    final source = RevelationMarkdownImageSource.parse(sourceUrl);

    expect(source.supabasePublicUri?.toString(), sourceUrl);
  });

  test('only the configured Supabase host is treated as owned storage', () {
    const ownedBaseUrl = 'https://adfdfxnzxmzyoioedwuy.supabase.co';
    const ownedUrl =
        'https://adfdfxnzxmzyoioedwuy.supabase.co/storage/v1/object/public/images/map.jpg';
    const externalSupabaseUrl =
        'https://other-project.supabase.co/storage/v1/object/public/images/map.jpg';

    final ownedSource = RevelationMarkdownImageSource.parse(
      ownedUrl,
      ownedSupabaseBaseUrl: ownedBaseUrl,
    );
    final externalSource = RevelationMarkdownImageSource.parse(
      externalSupabaseUrl,
      ownedSupabaseBaseUrl: ownedBaseUrl,
    );

    expect(ownedSource.kind, RevelationMarkdownImageSourceKind.supabaseStorage);
    expect(externalSource.kind, RevelationMarkdownImageSourceKind.network);
    expect(
      externalSource.buildLocalRelativePath(),
      'external/other-project.supabase.co/storage/v1/object/public/images/map.jpg',
    );
  });

  test('network query suffix hash stays stable and JS-safe', () {
    final source = RevelationMarkdownImageSource.parse(
      'https://images.example.com/map.jpg?size=large&lang=ru',
    );

    expect(source.kind, RevelationMarkdownImageSourceKind.network);
    expect(
      source.buildLocalRelativePath(),
      'external/images.example.com/map_acb4f33a.jpg',
    );
  });
}
