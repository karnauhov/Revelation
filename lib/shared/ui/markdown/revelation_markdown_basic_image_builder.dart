import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';

Widget buildBasicRevelationMarkdownImage(
  BuildContext context,
  RevelationMarkdownImageData image,
) {
  Widget child;
  switch (image.source.kind) {
    case RevelationMarkdownImageSourceKind.asset:
      child = _buildAssetImage(context, image);
    case RevelationMarkdownImageSourceKind.supabaseStorage:
      child = _buildSupabaseImage(context, image);
    case RevelationMarkdownImageSourceKind.network:
      child = _buildNetworkImage(context, image);
    case RevelationMarkdownImageSourceKind.databaseResource:
    case RevelationMarkdownImageSourceKind.unsupported:
      child = _buildStateFrame(
        context,
        image,
        label: _fallbackLabel(context, image),
      );
  }

  if (!image.isBlockImage) {
    return child;
  }

  return Align(
    alignment: _alignmentFor(image.alignment),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: _crossAxisAlignmentFor(image.alignment),
      children: [
        child,
        if (image.caption != null && image.caption!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              image.caption!,
              textAlign: _textAlignFor(image.alignment),
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ),
      ],
    ),
  );
}

Widget _buildSupabaseImage(
  BuildContext context,
  RevelationMarkdownImageData image,
) {
  final uri = image.source.supabasePublicUri;
  if (uri == null) {
    return _buildStateFrame(
      context,
      image,
      label: _fallbackLabel(context, image),
    );
  }

  return _buildRemoteUriImage(context, image, uri);
}

Widget _buildAssetImage(
  BuildContext context,
  RevelationMarkdownImageData image,
) {
  final assetPath = image.source.assetPath;
  if (assetPath == null || assetPath.isEmpty) {
    return _buildStateFrame(
      context,
      image,
      label: _fallbackLabel(context, image),
    );
  }

  if (image.source.isSvg) {
    return _sizeWrapper(
      image,
      SvgPicture.asset(
        assetPath,
        width: image.width,
        height: image.height,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) => _buildStateFrame(
          context,
          image,
          label: _fallbackLabel(context, image),
        ),
      ),
    );
  }

  return _sizeWrapper(
    image,
    Image.asset(
      assetPath,
      width: image.width,
      height: image.height,
      fit: BoxFit.contain,
      errorBuilder: (context, error, stackTrace) => _buildStateFrame(
        context,
        image,
        label: _fallbackLabel(context, image),
      ),
    ),
  );
}

Widget _buildNetworkImage(
  BuildContext context,
  RevelationMarkdownImageData image,
) {
  final uri = image.source.networkUri;
  if (uri == null) {
    return _buildStateFrame(
      context,
      image,
      label: _fallbackLabel(context, image),
    );
  }

  return _buildRemoteUriImage(context, image, uri);
}

Widget _buildRemoteUriImage(
  BuildContext context,
  RevelationMarkdownImageData image,
  Uri uri,
) {
  if (image.source.isSvg) {
    return _sizeWrapper(
      image,
      SvgPicture.network(
        uri.toString(),
        width: image.width,
        height: image.height,
        fit: BoxFit.contain,
        placeholderBuilder: (context) => _buildStateFrame(
          context,
          image,
          label: _loadingLabel(context),
          showLoader: true,
        ),
        errorBuilder: (context, error, stackTrace) => _buildStateFrame(
          context,
          image,
          label: _fallbackLabel(context, image),
        ),
      ),
    );
  }

  return _sizeWrapper(
    image,
    Image.network(
      uri.toString(),
      width: image.width,
      height: image.height,
      fit: BoxFit.contain,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) {
          return child;
        }
        return _buildStateFrame(
          context,
          image,
          label: _loadingLabel(context),
          showLoader: true,
        );
      },
      errorBuilder: (context, error, stackTrace) => _buildStateFrame(
        context,
        image,
        label: _fallbackLabel(context, image),
      ),
    ),
  );
}

Widget _buildStateFrame(
  BuildContext context,
  RevelationMarkdownImageData image, {
  required String label,
  bool showLoader = false,
}) {
  final theme = Theme.of(context);
  final colorScheme = theme.colorScheme;

  return _sizeWrapper(
    image,
    DecoratedBox(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: colorScheme.outlineVariant),
      ),
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (showLoader) ...[
                const SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
                const SizedBox(height: 12),
              ] else ...[
                Icon(
                  Icons.image_not_supported_outlined,
                  color: colorScheme.error,
                  size: 32,
                ),
                const SizedBox(height: 12),
              ],
              Text(
                label,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

Widget _sizeWrapper(RevelationMarkdownImageData image, Widget child) {
  if (image.width != null || image.height != null) {
    return SizedBox(width: image.width, height: image.height, child: child);
  }
  if (!image.isBlockImage) {
    return child;
  }
  return SizedBox(width: 320, height: 180, child: child);
}

String _loadingLabel(BuildContext context) {
  return AppLocalizations.of(context)!.markdown_image_loading;
}

String _fallbackLabel(BuildContext context, RevelationMarkdownImageData image) {
  if (image.alt.isNotEmpty) {
    return image.alt;
  }
  return AppLocalizations.of(context)!.image_not_loaded;
}

Alignment _alignmentFor(RevelationMarkdownImageAlignment alignment) {
  switch (alignment) {
    case RevelationMarkdownImageAlignment.left:
      return Alignment.centerLeft;
    case RevelationMarkdownImageAlignment.right:
      return Alignment.centerRight;
    case RevelationMarkdownImageAlignment.center:
      return Alignment.center;
  }
}

CrossAxisAlignment _crossAxisAlignmentFor(
  RevelationMarkdownImageAlignment alignment,
) {
  switch (alignment) {
    case RevelationMarkdownImageAlignment.left:
      return CrossAxisAlignment.start;
    case RevelationMarkdownImageAlignment.right:
      return CrossAxisAlignment.end;
    case RevelationMarkdownImageAlignment.center:
      return CrossAxisAlignment.center;
  }
}

TextAlign _textAlignFor(RevelationMarkdownImageAlignment alignment) {
  switch (alignment) {
    case RevelationMarkdownImageAlignment.left:
      return TextAlign.left;
    case RevelationMarkdownImageAlignment.right:
      return TextAlign.right;
    case RevelationMarkdownImageAlignment.center:
      return TextAlign.center;
  }
}
