import 'dart:math';

import 'package:flutter/material.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:url_launcher/url_launcher.dart' show LaunchMode, launchUrl;

import 'dialogs_utils.dart';
import 'common_logger.dart';
import 'platform_utils.dart';

Future<bool> launchLink(String url) async {
  try {
    // !DO NOT CALL canLaunchUrl
    AudioController().playSound("click");
    if (url.toLowerCase().startsWith('mailto:')) {
      final emailUri = Uri.parse(url);
      final launched = await launchUrl(
        emailUri,
        mode: isWeb()
            ? LaunchMode.platformDefault
            : LaunchMode.externalApplication,
      );
      if (!launched) {
        log.warning("Mailto link was not opened");
        showCustomDialog(MessageType.errorBrokenLink, param: url);
      }
      return launched;
    }

    final uri = Uri.parse(url);
    final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!launched) {
      log.warning("Link $url was not opened");
      showCustomDialog(MessageType.errorBrokenLink, param: url);
    } else {
      log.info("Link $url has been opened");
    }
    return launched;
  } catch (e) {
    showCustomDialog(
      MessageType.errorBrokenLink,
      param: url,
      markdownExtension: e.toString(),
    );
    return false;
  }
}

List<String> splitTrailingDigits(String s) {
  final str = s.trim();
  // ignore: deprecated_member_use
  final reg = RegExp(r'^(.*?)(\d+)\s*$');
  final m = reg.firstMatch(str);
  if (m != null) {
    final prefix = m.group(1)!.trimRight();
    final digits = m.group(2)!;
    return [prefix, digits];
  } else {
    return [str, ''];
  }
}

double roundTo(double value, int round) {
  return double.parse(value.toStringAsFixed(round));
}

Rect createNonZeroRect(Offset start, Offset end) {
  var left = min(start.dx, end.dx);
  var top = min(start.dy, end.dy);
  var right = max(start.dx, end.dx);
  var bottom = max(start.dy, end.dy);
  if (right - left < 1) {
    right = left + 1;
  }
  if (bottom - top < 1) {
    bottom = top + 1;
  }
  return Rect.fromLTRB(left, top, right, bottom);
}
