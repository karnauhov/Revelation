import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/services/primary_source_reference_resolver.dart';
import 'package:revelation/utils/app_constants.dart';
import 'package:revelation/utils/common.dart';

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

GreekStrongTapHandler? _defaultGreekStrongTapHandler;
GreekStrongPickerTapHandler? _defaultGreekStrongPickerTapHandler;
final PrimarySourceReferenceResolver _referenceResolver =
    PrimarySourceReferenceResolver();

void setDefaultGreekStrongTapHandler(GreekStrongTapHandler? handler) {
  _defaultGreekStrongTapHandler = handler;
}

void setDefaultGreekStrongPickerTapHandler(
  GreekStrongPickerTapHandler? handler,
) {
  _defaultGreekStrongPickerTapHandler = handler;
}

Future<bool> handleAppLink(
  BuildContext context,
  String? href, {
  bool popBeforeScreenPush = false,
  GreekStrongTapHandler? onGreekStrongTap,
  GreekStrongPickerTapHandler? onGreekStrongPickerTap,
  WordTapHandler? onWordTap,
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

  return _openPrimarySourceFromWordLink(
    context,
    sourceId: sourceId,
    pageName: pageName,
    wordIndex: wordIndex,
    popBeforeScreenPush: popBeforeScreenPush,
  );
}

Future<bool> _openPrimarySourceFromWordLink(
  BuildContext context, {
  required String sourceId,
  String? pageName,
  int? wordIndex,
  required bool popBeforeScreenPush,
}) async {
  final source = _referenceResolver.findSourceById(context, sourceId);
  if (source == null) {
    log.warning("Primary source '$sourceId' was not found for word link.");
    return false;
  }

  if (pageName != null &&
      _referenceResolver.findPageByName(source, pageName) == null) {
    log.warning("Page '$pageName' was not found in source '$sourceId'.");
    return false;
  }

  if (popBeforeScreenPush && Navigator.of(context).canPop()) {
    Navigator.pop(context);
  }

  final extra = <String, dynamic>{'primarySource': source};
  if (pageName != null) {
    extra['pageName'] = pageName;
  }
  if (wordIndex != null) {
    extra['wordIndex'] = wordIndex;
  }

  context.push('/primary_source', extra: extra);
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
