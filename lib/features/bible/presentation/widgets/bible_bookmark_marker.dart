import 'package:flutter/material.dart';
import 'package:revelation/features/bible/domain/models/bible_bookmark.dart';

class BibleBookmarkMarker extends StatelessWidget {
  const BibleBookmarkMarker({
    required this.bookmark,
    required this.onEdit,
    super.key,
  });

  final BibleBookmark bookmark;
  final VoidCallback onEdit;

  @override
  Widget build(BuildContext context) {
    final color = bibleBookmarkColor(context, bookmark.color);
    return Tooltip(
      message: bookmark.name,
      triggerMode: TooltipTriggerMode.manual,
      child: MouseRegion(
        cursor: SystemMouseCursors.grab,
        child: Draggable<BibleBookmark>(
          data: bookmark,
          dragAnchorStrategy: pointerDragAnchorStrategy,
          maxSimultaneousDrags: 1,
          feedback: Transform.translate(
            offset: const Offset(-10, -10),
            child: Icon(Icons.bookmark, color: color, size: 21),
          ),
          childWhenDragging: Icon(
            Icons.bookmark,
            color: color.withValues(alpha: 0.35),
            size: 19,
          ),
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: onEdit,
            child: Icon(Icons.bookmark, color: color, size: 19),
          ),
        ),
      ),
    );
  }
}

Color bibleBookmarkColor(BuildContext context, BibleBookmarkColor color) {
  final dark = Theme.of(context).brightness == Brightness.dark;
  return switch (color) {
    BibleBookmarkColor.blue =>
      dark ? Colors.blue.shade200 : Colors.blue.shade800,
    BibleBookmarkColor.green =>
      dark ? Colors.green.shade200 : Colors.green.shade800,
    BibleBookmarkColor.amber =>
      dark ? Colors.amber.shade200 : Colors.amber.shade900,
    BibleBookmarkColor.red => dark ? Colors.red.shade200 : Colors.red.shade800,
    BibleBookmarkColor.violet =>
      dark ? Colors.deepPurple.shade200 : Colors.deepPurple.shade700,
  };
}
