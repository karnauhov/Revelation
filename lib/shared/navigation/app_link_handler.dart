import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/shared/models/primary_source_word_link_target.dart';
import 'package:revelation/shared/utils/links_utils.dart';

typedef GreekStrongTapHandler =
    void Function(int strongNumber, BuildContext context);
typedef GreekStrongPickerTapHandler =
    void Function(int strongNumber, BuildContext context);
typedef WordTapHandler =
    FutureOr<void> Function(
      String sourceId,
      String? pageName,
      int? wordIndex,
      BuildContext context,
    );
typedef WordsTapHandler =
    FutureOr<void> Function(
      List<PrimarySourceWordLinkTarget> targets,
      BuildContext context,
    );

GreekStrongTapHandler? _defaultGreekStrongTapHandler;
GreekStrongPickerTapHandler? _defaultGreekStrongPickerTapHandler;
WordTapHandler? _defaultWordTapHandler;
WordsTapHandler? _defaultWordsTapHandler;

void setDefaultGreekStrongTapHandler(GreekStrongTapHandler? handler) {
  _defaultGreekStrongTapHandler = handler;
}

void setDefaultGreekStrongPickerTapHandler(
  GreekStrongPickerTapHandler? handler,
) {
  _defaultGreekStrongPickerTapHandler = handler;
}

void setDefaultWordTapHandler(WordTapHandler? handler) {
  _defaultWordTapHandler = handler;
}

void setDefaultWordsTapHandler(WordsTapHandler? handler) {
  _defaultWordsTapHandler = handler;
}

Future<bool> handleAppLink(
  BuildContext context,
  String? href, {
  bool popBeforeScreenPush = false,
  GreekStrongTapHandler? onGreekStrongTap,
  GreekStrongPickerTapHandler? onGreekStrongPickerTap,
  WordTapHandler? onWordTap,
  WordsTapHandler? onWordsTap,
}) async {
  final link = href?.trim();
  if (link == null || link.isEmpty) {
    return false;
  }

  if (_hasScheme(link, 'screen')) {
    return _handleScreenLink(
      context,
      link,
      popBeforeScreenPush: popBeforeScreenPush,
    );
  }

  if (_hasScheme(link, 'topic')) {
    return _handleTopicLink(
      context,
      link,
      popBeforeScreenPush: popBeforeScreenPush,
    );
  }

  if (_hasScheme(link, 'strong')) {
    return _handleStrongLink(context, link, onGreekStrongTap: onGreekStrongTap);
  }

  if (_hasScheme(link, 'strong_picker')) {
    return _handleStrongPickerLink(
      context,
      link,
      onGreekStrongPickerTap: onGreekStrongPickerTap,
    );
  }

  if (_hasScheme(link, 'word')) {
    return _handleWordLink(
      context,
      link,
      onWordTap: onWordTap,
      popBeforeScreenPush: popBeforeScreenPush,
    );
  }

  if (_hasScheme(link, 'words')) {
    return _handleWordsLink(
      context,
      link,
      onWordsTap: onWordsTap,
      popBeforeScreenPush: popBeforeScreenPush,
    );
  }

  if (_hasScheme(link, 'bible')) {
    return _handleBibleLink(context, link);
  }

  return launchLink(link);
}

bool _hasScheme(String href, String scheme) {
  return href.toLowerCase().startsWith('$scheme:');
}

Future<bool> _handleScreenLink(
  BuildContext context,
  String href, {
  required bool popBeforeScreenPush,
}) async {
  final address = href.split(':');
  if (address.length < 2) {
    log.warning("Wrong screen link: '$href'");
    return false;
  }

  final route = address[1].trim();
  if (route.isEmpty) {
    log.warning("Wrong screen link: '$href'");
    return false;
  }

  if (popBeforeScreenPush && Navigator.of(context).canPop()) {
    Navigator.pop(context);
  }

  final targetRoute = route.startsWith('/') ? route : '/$route';
  context.push(targetRoute);
  return true;
}

Future<bool> _handleTopicLink(
  BuildContext context,
  String href, {
  required bool popBeforeScreenPush,
}) async {
  final separatorIndex = href.indexOf(':');
  if (separatorIndex == -1 || separatorIndex >= href.length - 1) {
    log.warning("Wrong topic link: '$href'");
    return false;
  }

  final route = href.substring(separatorIndex + 1).trim();
  if (route.isEmpty) {
    log.warning("Wrong topic link: '$href'");
    return false;
  }

  if (popBeforeScreenPush && Navigator.of(context).canPop()) {
    Navigator.pop(context);
  }

  final topicRoute = Uri(
    path: '/topic',
    queryParameters: <String, String>{'file': route},
  ).toString();
  context.push(topicRoute);
  return true;
}

Future<bool> _handleStrongLink(
  BuildContext context,
  String href, {
  GreekStrongTapHandler? onGreekStrongTap,
}) async {
  final address = href.split(':');
  if (address.length < 2) {
    log.warning("Wrong Strong's link: '$href'");
    return false;
  }

  final strongCode = address[1].trim();
  if (strongCode.isEmpty) {
    log.warning("Wrong Strong's link: '$href'");
    return false;
  }

  if (strongCode.startsWith('H') || strongCode.startsWith('h')) {
    if (strongCode.length < 2) {
      log.warning("Wrong Strong's Hebrew number: '$strongCode'");
      return false;
    }
    final hebrewUrl = AppConstants.hebrewUrl.replaceFirst(
      '@index',
      strongCode.substring(1),
    );
    return launchLink(hebrewUrl);
  }

  if (strongCode.startsWith('G') || strongCode.startsWith('g')) {
    final greekNum = int.tryParse(strongCode.substring(1));
    if (greekNum == null) {
      log.warning("Wrong Strong's Greek number: '$strongCode'");
      return false;
    }
    final strongHandler = onGreekStrongTap ?? _defaultGreekStrongTapHandler;
    if (strongHandler == null) {
      log.warning("Greek Strong's callback is not set for link: '$href'");
      return false;
    }
    strongHandler(greekNum, context);
    return true;
  }

  log.warning("Wrong Strong's number: '$strongCode'");
  return false;
}

Future<bool> _handleStrongPickerLink(
  BuildContext context,
  String href, {
  GreekStrongPickerTapHandler? onGreekStrongPickerTap,
}) async {
  final address = href.split(':');
  if (address.length < 2) {
    log.warning("Wrong Strong picker link: '$href'");
    return false;
  }

  final strongCode = address[1].trim();
  if (strongCode.isEmpty) {
    log.warning("Wrong Strong picker link: '$href'");
    return false;
  }

  if (!(strongCode.startsWith('G') || strongCode.startsWith('g'))) {
    log.warning("Wrong Strong picker number: '$strongCode'");
    return false;
  }

  final greekNum = int.tryParse(strongCode.substring(1));
  if (greekNum == null) {
    log.warning("Wrong Strong picker number: '$strongCode'");
    return false;
  }

  final pickerHandler =
      onGreekStrongPickerTap ?? _defaultGreekStrongPickerTapHandler;
  if (pickerHandler != null) {
    pickerHandler(greekNum, context);
    return true;
  }

  final strongHandler = _defaultGreekStrongTapHandler;
  if (strongHandler != null) {
    strongHandler(greekNum, context);
    return true;
  }

  log.warning("Strong picker callback is not set for link: '$href'");
  return false;
}

Future<bool> _handleWordLink(
  BuildContext context,
  String href, {
  WordTapHandler? onWordTap,
  required bool popBeforeScreenPush,
}) async {
  final address = href.split(':');
  if (address.length < 2 || address.length > 4) {
    log.warning("Wrong word link: '$href'");
    return false;
  }

  final sourceId = address[1].trim();
  if (sourceId.isEmpty) {
    log.warning("Wrong source id in word link: '$href'");
    return false;
  }

  String? pageName;
  int? wordIndex;

  if (address.length >= 3) {
    pageName = address[2].trim();
    if (pageName.isEmpty) {
      log.warning("Wrong page name in word link: '$href'");
      return false;
    }
  }

  if (address.length == 4) {
    wordIndex = int.tryParse(address[3].trim());
    if (wordIndex == null || wordIndex < 0) {
      log.warning("Wrong word index in link: '$href'");
      return false;
    }
  }

  if (onWordTap != null) {
    await onWordTap(sourceId, pageName, wordIndex, context);
    return true;
  }

  final defaultWordTapHandler = _defaultWordTapHandler;
  if (defaultWordTapHandler == null) {
    log.warning("Word callback is not set for link: '$href'");
    return false;
  }

  if (popBeforeScreenPush && Navigator.of(context).canPop()) {
    Navigator.pop(context);
  }

  await defaultWordTapHandler(sourceId, pageName, wordIndex, context);
  return true;
}

Future<bool> _handleWordsLink(
  BuildContext context,
  String href, {
  WordsTapHandler? onWordsTap,
  required bool popBeforeScreenPush,
}) async {
  final separatorIndex = href.indexOf(':');
  if (separatorIndex == -1 || separatorIndex >= href.length - 1) {
    log.warning("Wrong words link: '$href'");
    return false;
  }

  final payload = href.substring(separatorIndex + 1).trim();
  if (payload.isEmpty) {
    log.warning("Wrong words link: '$href'");
    return false;
  }

  final targets = <PrimarySourceWordLinkTarget>[];
  for (final rawPart in payload.split(';')) {
    final part = rawPart.trim();
    if (part.isEmpty) {
      log.warning("Wrong words link item: '$href'");
      return false;
    }

    final address = part.split(':');
    if (address.isEmpty || address.length > 3) {
      log.warning("Wrong words link item: '$part'");
      return false;
    }

    final sourceId = address[0].trim();
    if (sourceId.isEmpty) {
      log.warning("Wrong words link item: '$part'");
      return false;
    }

    String? pageName;
    if (address.length >= 2) {
      final rawPageName = address[1].trim();
      if (rawPageName.isNotEmpty) {
        pageName = rawPageName;
      }
    }

    int? wordIndex;
    if (address.length == 3) {
      final rawWordIndex = address[2].trim();
      if (rawWordIndex.isNotEmpty) {
        wordIndex = int.tryParse(rawWordIndex);
        if (wordIndex == null || wordIndex < 0) {
          log.warning("Wrong words link item: '$part'");
          return false;
        }
      }
    }

    targets.add(
      PrimarySourceWordLinkTarget(
        sourceId: sourceId,
        pageName: pageName,
        wordIndex: wordIndex,
      ),
    );
  }

  if (targets.isEmpty) {
    log.warning("Wrong words link: '$href'");
    return false;
  }

  final handler = onWordsTap ?? _defaultWordsTapHandler;
  if (handler == null) {
    log.warning("Words callback is not set for link: '$href'");
    return false;
  }

  await handler(
    List<PrimarySourceWordLinkTarget>.unmodifiable(targets),
    context,
  );
  return true;
}

Future<bool> _handleBibleLink(BuildContext context, String href) async {
  final address = href.split(':');
  if (address.length < 2) {
    log.warning("Wrong Bible link: '$href'");
    return false;
  }

  final bookAndChapterRaw = address[1].trim();
  if (bookAndChapterRaw.isEmpty) {
    log.warning("Wrong Bible link: '$href'");
    return false;
  }

  final locale = Localizations.localeOf(context);
  final bibleTranslation =
      AppConstants.onlineBibleBooks[locale.languageCode] ??
      AppConstants.onlineBibleBooks['en'] ??
      'kjv';
  final bookAndChapter = splitTrailingDigits(bookAndChapterRaw);
  final bibleBook = bookAndChapter[0];
  final bibleChapter = bookAndChapter[1];

  var bibleLink =
      "${AppConstants.onlineBibleUrl}?b=$bibleTranslation&bk=$bibleBook&ch=$bibleChapter";
  if (address.length > 2 && address[2].trim().isNotEmpty) {
    bibleLink += "&v=${address[2].trim()}";
  }
  return launchLink(bibleLink);
}
