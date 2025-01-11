import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import '../utils/common.dart';
import '../models/primary_source.dart';

class PrimarySourcesScreen extends StatefulWidget {
  const PrimarySourcesScreen({super.key});

  @override
  State<PrimarySourcesScreen> createState() => _PrimarySourcesScreenState();
}

class _PrimarySourcesScreenState extends State<PrimarySourcesScreen> {
  final ScrollController _scrollController = ScrollController();
  bool _isDragging = false;
  Offset _lastOffset = Offset.zero;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final sources = [
      PrimarySource(
        title: AppLocalizations.of(context)!.papyrus_18_title,
        date: AppLocalizations.of(context)!.papyrus_18_date,
        content: AppLocalizations.of(context)!.papyrus_18_content,
        features: AppLocalizations.of(context)!.papyrus_18_features,
        linkTitle: AppLocalizations.of(context)!.wikipedia,
        linkUrl: 'https://en.wikipedia.org/wiki/Papyrus_18',
        imagePath: 'assets/images/Resources/10018/preview.png',
      ),
    ];

    Widget content = CustomScrollView(
      controller: _scrollController,
      physics: const BouncingScrollPhysics(),
      slivers: [
        SliverAppBar(
          pinned: true,
          title: Text(AppLocalizations.of(context)!.primary_sources_screen),
        ),
        SliverList(
          delegate: SliverChildBuilderDelegate(
            (context, index) {
              final source = sources[index];
              return _buildSourceItem(context, source);
            },
            childCount: sources.length,
          ),
        ),
      ],
    );

    if (isDesktop() || isWeb()) {
      content = Listener(
        onPointerDown: (event) {
          if (event.buttons == kPrimaryMouseButton) {
            setState(() {
              _isDragging = true;
              _lastOffset = event.position;
            });
          }
        },
        onPointerMove: (event) {
          if (_isDragging) {
            final dy = event.position.dy - _lastOffset.dy;
            final oldOffset = _scrollController.offset;
            final newOffset = oldOffset - dy;

            _scrollController.jumpTo(
              newOffset.clamp(
                0.0,
                _scrollController.position.maxScrollExtent,
              ),
            );
            setState(() {
              _lastOffset = event.position;
            });
          }
        },
        onPointerUp: (event) {
          if (event.buttons == 0) {
            setState(() {
              _isDragging = false;
            });
          }
        },
        child: content,
      );
    }

    return Scaffold(
      body: SizedBox.expand(
        child: content,
      ),
    );
  }

  Widget _buildSourceItem(BuildContext context, PrimarySource source) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () {
          //context.push('/primary');
        },
        child: Card(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.asset(
                    source.imagePath,
                    fit: BoxFit.cover,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        source.title,
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        source.date,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        source.content,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        source.features,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: 8),
                      InkWell(
                        onTap: () {
                          launchLink(source.linkUrl);
                        },
                        child: Text(
                          source.linkTitle,
                          style: const TextStyle(
                            color: Colors.blue,
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
