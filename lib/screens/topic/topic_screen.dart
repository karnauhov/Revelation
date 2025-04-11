import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:provider/provider.dart';
import '../../utils/common.dart';
import '../../viewmodels/settings_view_model.dart';

class TopicScreen extends StatefulWidget {
  final String? name;
  final String? description;
  final String? file;

  const TopicScreen({super.key, this.name, this.description, this.file});

  @override
  State<TopicScreen> createState() => _TopicScreenState();
}

class _TopicScreenState extends State<TopicScreen> {
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
    final settingsViewModel = Provider.of<SettingsViewModel>(context);
    final futureMarkdown = loadMarkdownAsset(
      widget.file,
      settingsViewModel.settings.selectedLanguage,
    );

    Widget content = SizedBox.expand(
        child: FutureBuilder<String>(
      future: futureMarkdown,
      builder: (context, snapshot) {
        final data = snapshot.data ?? '';
        return SingleChildScrollView(
          controller: _scrollController,
          padding: const EdgeInsets.all(8.0),
          child: MarkdownBody(data: data),
        );
      },
    ));

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
            _scrollController.jumpTo(_scrollController.offset - dy);
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
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              locLinks(context, widget.name ?? ""),
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(
              locLinks(context, widget.description ?? ""),
              style: Theme.of(context)
                  .textTheme
                  .labelSmall
                  ?.copyWith(fontWeight: FontWeight.normal),
            ),
          ],
        ),
      ),
      body: content,
    );
  }

  Future<String> loadMarkdownAsset(String? file, String language) async {
    if (file != null) {
      final path = "assets/data/topics/${file}_$language.md";
      return await rootBundle.loadString(path);
    } else {
      return "";
    }
  }
}
