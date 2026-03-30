import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_state.dart';

class RevelationMarkdownImageView extends StatelessWidget {
  const RevelationMarkdownImageView({
    required this.image,
    this.imageState,
    super.key,
  });

  final RevelationMarkdownImageData image;
  final RevelationMarkdownImageState? imageState;

  @override
  Widget build(BuildContext context) {
    final child = _buildBody(context);
    final caption = image.caption;

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
          if (caption != null && caption.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                caption,
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

  Widget _buildBody(BuildContext context) {
    switch (image.source.kind) {
      case RevelationMarkdownImageSourceKind.asset:
        return _buildAssetImage(context);
      case RevelationMarkdownImageSourceKind.databaseResource:
      case RevelationMarkdownImageSourceKind.supabaseStorage:
      case RevelationMarkdownImageSourceKind.network:
        return _buildAsyncImage(context);
      case RevelationMarkdownImageSourceKind.unsupported:
        return _buildStateFrame(
          context,
          child: Icon(
            Icons.image_not_supported_outlined,
            color: Theme.of(context).colorScheme.error,
            size: 32,
          ),
          label: _fallbackLabel(context),
        );
    }
  }

  Widget _buildAssetImage(BuildContext context) {
    final assetPath = image.source.assetPath;
    if (assetPath == null || assetPath.isEmpty) {
      return _buildStateFrame(context, label: _fallbackLabel(context));
    }

    final errorLabel = _fallbackLabel(context);
    if (image.source.isSvg) {
      return _sizeWrapper(
        SvgPicture.asset(
          assetPath,
          width: image.width,
          height: image.height,
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) =>
              _buildStateFrame(context, label: errorLabel),
        ),
      );
    }

    return _sizeWrapper(
      Image.asset(
        assetPath,
        width: image.width,
        height: image.height,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) =>
            _buildStateFrame(context, label: errorLabel),
      ),
    );
  }

  Widget _buildAsyncImage(BuildContext context) {
    final resolvedState = imageState;
    if (resolvedState == null ||
        resolvedState.status == RevelationMarkdownImageStatus.loading) {
      return _buildStateFrame(
        context,
        label: _loadingLabel(context),
        child: const SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }

    if (resolvedState.status == RevelationMarkdownImageStatus.failure ||
        resolvedState.bytes == null) {
      return _buildStateFrame(context, label: _fallbackLabel(context));
    }

    if (resolvedState.isSvg) {
      return _sizeWrapper(
        SvgPicture.memory(
          resolvedState.bytes!,
          width: image.width,
          height: image.height,
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) =>
              _buildStateFrame(context, label: _fallbackLabel(context)),
        ),
      );
    }

    return _sizeWrapper(
      Image.memory(
        resolvedState.bytes!,
        width: image.width,
        height: image.height,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) =>
            _buildStateFrame(context, label: _fallbackLabel(context)),
      ),
    );
  }

  Widget _buildStateFrame(
    BuildContext context, {
    required String label,
    Widget? child,
  }) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return _sizeWrapper(
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
                child ?? const SizedBox.shrink(),
                if (child != null) const SizedBox(height: 12),
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

  Widget _sizeWrapper(Widget child) {
    final hasExplicitSize = image.width != null || image.height != null;
    if (hasExplicitSize) {
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

  String _fallbackLabel(BuildContext context) {
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
}
