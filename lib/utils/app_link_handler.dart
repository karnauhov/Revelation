import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/utils/app_constants.dart';
import 'package:revelation/utils/common.dart';

typedef GreekStrongTapHandler =
    void Function(int strongNumber, BuildContext context);

Future<bool> handleAppLink(
  BuildContext context,
  String? href, {
  bool popBeforeScreenPush = false,
  GreekStrongTapHandler? onGreekStrongTap,
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

  if (_hasScheme(link, 'strong')) {
    return _handleStrongLink(
      context,
      link,
      onGreekStrongTap: onGreekStrongTap,
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
    if (onGreekStrongTap == null) {
      log.warning("Greek Strong's callback is not set for link: '$href'");
      return false;
    }
    onGreekStrongTap(greekNum, context);
    return true;
  }

  log.warning("Wrong Strong's number: '$strongCode'");
  return false;
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
