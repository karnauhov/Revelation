import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:revelation/shared/ui/markdown/revelation_markdown_body.dart';

const studyReferencesMarker = '<!-- study:references -->';

class TopicStudyBody extends StatefulWidget {
  const TopicStudyBody({
    required this.markdown,
    required this.onTapLink,
    super.key,
  });

  final String markdown;
  final MarkdownTapLinkCallback onTapLink;

  @override
  State<TopicStudyBody> createState() => _TopicStudyBodyState();
}

class _TopicStudyBodyState extends State<TopicStudyBody> {
  static final _divider = RegExp(
    '^$studyReferencesMarker\\r?\$',
    multiLine: true,
  );
  static final _entry = RegExp(r'^(\d+)\. (.+)$');
  late final _content = widget.markdown.split(_divider);
  late final _references = _readReferences();
  late final _targets = List<GlobalKey>.generate(
    _references.length,
    (_) => GlobalKey(),
  );
  late final _referenceSyntax = _StudyReferenceSyntax(_references.length);

  List<String> _readReferences() {
    if (_content.length != 2 || _content.first.trim().isEmpty) return const [];
    final lines = _content.last.trim().split(RegExp(r'\r?\n'));
    if (lines.first.trim() != '---') return const [];
    final references = <String>[];
    for (final line in lines.skip(1)) {
      if (line.trim().isEmpty) continue;
      final match = _entry.firstMatch(line);
      if (match == null || int.tryParse(match[1]!) != references.length + 1) {
        return const [];
      }
      references.add('${match[1]}\\. ${match[2]}');
    }
    return references;
  }

  @override
  Widget build(BuildContext context) {
    if (_references.isEmpty) {
      return _render(widget.markdown);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _render(_content.first.trimRight(), inlineSyntaxes: [_referenceSyntax]),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 8),
          child: Divider(),
        ),
        for (var index = 0; index < _references.length; index++)
          KeyedSubtree(
            key: _targets[index],
            child: _render(_references[index]),
          ),
      ],
    );
  }

  Widget _render(
    String markdown, {
    List<md.InlineSyntax> inlineSyntaxes = const [],
  }) {
    return RevelationMarkdownBody(
      data: markdown,
      padding: const EdgeInsets.all(8),
      showImagePreloadProgress: true,
      inlineSyntaxes: inlineSyntaxes,
      onTapLink: (text, href, title) async {
        if (href != null && href.startsWith(_StudyReferenceSyntax.linkPrefix)) {
          final number = int.tryParse(
            href.substring(_StudyReferenceSyntax.linkPrefix.length),
          );
          if (number != null && number > 0 && number <= _targets.length) {
            final target = _targets[number - 1].currentContext;
            if (target != null) {
              await Scrollable.ensureVisible(
                target,
                duration: const Duration(milliseconds: 240),
              );
            }
          }
          return;
        }
        widget.onTapLink(text, href, title);
      },
    );
  }
}

class _StudyReferenceSyntax extends md.InlineSyntax {
  _StudyReferenceSyntax(this.referenceCount) : super('[$_digits]+');

  static const _digits = '⁰¹²³⁴⁵⁶⁷⁸⁹';
  static const linkPrefix = 'study-ref:';
  final int referenceCount;

  @override
  bool onMatch(md.InlineParser parser, Match match) {
    final marker = match[0]!;
    final number = int.tryParse(marker.split('').map(_digits.indexOf).join());
    if (number == null || number < 1 || number > referenceCount) {
      parser.addNode(md.Text(marker));
    } else {
      parser.addNode(
        md.Element.text('a', marker)..attributes['href'] = '$linkPrefix$number',
      );
    }
    return true;
  }
}
