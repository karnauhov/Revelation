import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:float_column/float_column.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/viewmodels/primary_sources_view_model.dart';
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
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final viewModel =
          Provider.of<PrimarySourcesViewModel>(context, listen: false);
      viewModel.loadPrimarySources(context);
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final primarySourcesViewModel =
        Provider.of<PrimarySourcesViewModel>(context);
    List<PrimarySource> sources = primarySourcesViewModel.primarySources;

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
    TextTheme theme = Theme.of(context).textTheme;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () {
          //context.push('/primary');
        },
        child: Card(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
            child: FloatColumn(
              children: [
                Text.rich(
                  textAlign: TextAlign.center,
                  TextSpan(children: [
                    WidgetSpan(
                      child: Floatable(
                        float: FCFloat.none,
                        padding: EdgeInsets.only(right: 0),
                        child: getStyledText(
                          source.title,
                          theme.titleMedium
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                  ]),
                ),
                Floatable(
                  float: FCFloat.start,
                  padding: EdgeInsets.only(right: 8),
                  child: Image.asset(
                    source.preview,
                    fit: BoxFit.cover,
                  ),
                ),
                WrappableText(
                  text: TextSpan(
                    text: source.date,
                    style: theme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ),
                WrappableText(
                  text: TextSpan(
                    text: source.content,
                    style: theme.bodyMedium?.copyWith(
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
                WrappableText(
                  text: TextSpan(
                    text: source.features,
                    style: theme.bodyMedium,
                    children: [
                      TextSpan(
                        text: ' [${source.linkTitle}]',
                        style: TextStyle(color: Colors.blue),
                        recognizer: TapGestureRecognizer()
                          ..onTap = () {
                            launchLink(source.linkUrl);
                          },
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
