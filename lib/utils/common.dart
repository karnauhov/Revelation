import 'dart:io';
import 'dart:math';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_svg/svg.dart';
import 'package:get_it/get_it.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:revelation/controllers/audio_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/recommended_info.dart';
import 'package:revelation/utils/app_constants.dart';
import 'package:revelation/managers/server_manager.dart';
import 'package:styled_text/tags/styled_text_tag_widget_builder.dart';
import 'package:styled_text/widgets/styled_text.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:url_launcher/url_launcher.dart' show launchUrl, LaunchMode;
import 'package:xml/xml.dart';
import '../app_router.dart';
import '../models/topic_info.dart';
import '../models/library_info.dart';
import '../models/institution_info.dart';
import 'dependent.dart' as dep;

final log = GetIt.I<Talker>();

bool isDesktop() {
  return [
        TargetPlatform.windows,
        TargetPlatform.linux,
        TargetPlatform.macOS,
      ].contains(defaultTargetPlatform) &&
      !kIsWeb;
}

bool isMobile() {
  return [
        TargetPlatform.android,
        TargetPlatform.iOS,
      ].contains(defaultTargetPlatform) &&
      !kIsWeb;
}

bool isWeb() {
  return kIsWeb;
}

bool isLocalWeb() {
  if (!kIsWeb) {
    return false;
  }
  final host = Uri.base.host;
  return host == 'localhost' || host == '127.0.0.1';
}

bool isMobileBrowser() {
  return dep.isMobileBrowser();
}

String getUserAgent() {
  return dep.getUserAgent();
}

Future<int> fetchMaxTextureSize() {
  return dep.fetchMaxTextureSize();
}

TargetPlatform getPlatform() {
  return defaultTargetPlatform;
}

String locLinks(BuildContext context, String key) {
  final localizations = AppLocalizations.of(context);
  final Map<String, String> translations = {
    "topic_0_name": localizations!.topic_0_name,
    "topic_0_description": localizations.topic_0_description,
    "@indeclNumAdj": localizations.strong_indeclNumAdj,
    "@indeclLetN": localizations.strong_indeclLetN,
    "@indeclinable": localizations.strong_indeclinable,
    "@adj": localizations.strong_adj,
    "@advCor": localizations.strong_advCor,
    "@advInt": localizations.strong_advInt,
    "@advNeg": localizations.strong_advNeg,
    "@advSup": localizations.strong_advSup,
    "@adv": localizations.strong_adv,
    "@comp": localizations.strong_comp,
    "@aramaicTransWord": localizations.strong_aramaicTransWord,
    "@hebrewForm": localizations.strong_hebrewForm,
    "@hebrewNoun": localizations.strong_hebrewNoun,
    "@hebrew": localizations.strong_hebrew,
    "@location": localizations.strong_location,
    "@properNoun": localizations.strong_properNoun,
    "@noun": localizations.strong_noun,
    "@masc": localizations.strong_masc,
    "@fem": localizations.strong_fem,
    "@neut": localizations.strong_neut,
    "@plur": localizations.strong_plur,
    "@otherType": localizations.strong_otherType,
    "@verbImp": localizations.strong_verbImp,
    "@verb": localizations.strong_verb,
    "@pronDat": localizations.strong_pronDat,
    "@pronPoss": localizations.strong_pronPoss,
    "@pronPers": localizations.strong_pronPers,
    "@pronRecip": localizations.strong_pronRecip,
    "@pronRefl": localizations.strong_pronRefl,
    "@pronRel": localizations.strong_pronRel,
    "@pronCorrel": localizations.strong_pronCorrel,
    "@pronIndef": localizations.strong_pronIndef,
    "@pronInterr": localizations.strong_pronInterr,
    "@pronDem": localizations.strong_pronDem,
    "@pron": localizations.strong_pron,
    "@particleCond": localizations.strong_particleCond,
    "@particleDisj": localizations.strong_particleDisj,
    "@particleInterr": localizations.strong_particleInterr,
    "@particleNeg": localizations.strong_particleNeg,
    "@particle": localizations.strong_particle,
    "@interj": localizations.strong_interj,
    "@participle": localizations.strong_participle,
    "@prefix": localizations.strong_prefix,
    "@prep": localizations.strong_prep,
    "@artDef": localizations.strong_artDef,
    "@phraseIdi": localizations.strong_phraseIdi,
    "@phrase": localizations.strong_phrase,
    "@conjNeg": localizations.strong_conjNeg,
    "@conj": localizations.strong_conj,
    "@or": localizations.strong_or,
  };
  return translations[key] ?? key;
}

String locColorThemes(BuildContext context, String key) {
  final localizations = AppLocalizations.of(context);
  final Map<String, String> translations = {
    "manuscript": localizations!.manuscript_color_theme,
    "forest": localizations.forest_color_theme,
    "sky": localizations.sky_color_theme,
    "grape": localizations.grape_color_theme,
  };
  return translations[key] ?? key;
}

String locFontSizes(BuildContext context, String key) {
  final localizations = AppLocalizations.of(context);
  final Map<String, String> translations = {
    "small": localizations!.small_font_size,
    "medium": localizations.medium_font_size,
    "large": localizations.large_font_size,
  };
  return translations[key] ?? key;
}

String getSystemLanguage() {
  String language = 'en';
  try {
    if (isWeb()) {
      language = dep.getPlatformLanguage();
    } else {
      final localeName = Platform.localeName;
      final parts = localeName.split('_');
      if (parts.length == 1) {
        language = Locale(parts[0]).languageCode;
      } else if (parts.length >= 2) {
        language = Locale(parts[0], parts[1]).languageCode;
      } else {
        language = 'en';
      }
    }
  } catch (e) {
    log.debug(e);
  }
  return language;
}

StyledText getStyledText(String text, TextStyle? style) {
  style ??= TextStyle();
  return StyledText(
    text: text,
    style: style,
    tags: {
      'sup': StyledTextWidgetBuilderTag((_, attributes, textContent) {
        return Transform.translate(
          offset: const Offset(0.5, -4),
          child: Text(
            style: style?.copyWith(fontSize: (style.fontSize ?? 18) - 6),
            textContent ?? "",
          ),
        );
      }),
      'b': StyledTextWidgetBuilderTag((_, attributes, textContent) {
        return Text(
          style: style?.copyWith(fontWeight: FontWeight.w700),
          textContent ?? "",
        );
      }),
    },
  );
}

Future<List<LibraryInfo>> parseLibraries(
  AssetBundle bundle,
  String xmlPath,
) async {
  try {
    final xmlString = await bundle.loadString(xmlPath);
    final document = XmlDocument.parse(xmlString);
    final libraries = <LibraryInfo>[];

    for (var element in document.findAllElements('library')) {
      final name = element.getElement('name')?.innerText;
      final idIcon = element.getElement('idIcon')?.innerText;
      final license = element.getElement('license')?.innerText;
      final officialSite = element.getElement('officialSite')?.innerText;
      final licenseLink = element.getElement('licenseLink')?.innerText;

      if (name == null ||
          idIcon == null ||
          license == null ||
          officialSite == null ||
          licenseLink == null) {
        throw Exception('Missing required tags in library element');
      }

      libraries.add(
        LibraryInfo(
          name: name,
          idIcon: idIcon,
          license: license,
          officialSite: officialSite,
          licenseLink: licenseLink,
        ),
      );
    }

    return libraries;
  } on XmlException {
    rethrow;
  } on PlatformException {
    rethrow;
  } catch (e) {
    throw Exception('Unknown error: $e');
  }
}

Future<List<InstitutionInfo>> parseInstitutions(
  AssetBundle bundle,
  String xmlPath,
) async {
  try {
    final xmlString = await bundle.loadString(xmlPath);
    final document = XmlDocument.parse(xmlString);
    final institutions = <InstitutionInfo>[];

    for (var element in document.findAllElements('institution')) {
      final name = element.getElement('name')?.innerText;
      final idIcon = element.getElement('idIcon')?.innerText;
      final officialSite = element.getElement('officialSite')?.innerText;

      if (name == null || idIcon == null || officialSite == null) {
        throw Exception('Missing required tags in institution element');
      }
      final sourcesElement = element.getElement('sources');
      final sources = <String, String>{};

      if (sourcesElement != null) {
        for (var source in sourcesElement.findElements('source')) {
          final text = source.getElement('text')?.innerText ?? '';
          final link = source.getElement('link')?.innerText ?? '';
          sources[text] = link;
        }
      }

      institutions.add(
        InstitutionInfo(
          name: name,
          idIcon: idIcon,
          officialSite: officialSite,
          sources: sources,
        ),
      );
    }

    return institutions;
  } on XmlException {
    rethrow;
  } on PlatformException {
    rethrow;
  } catch (e) {
    throw Exception('Unknown error: $e');
  }
}

Future<List<TopicInfo>> parseTopics(AssetBundle bundle, String xmlPath) async {
  try {
    final xmlString = await bundle.loadString(xmlPath);
    final document = XmlDocument.parse(xmlString);
    final topics = <TopicInfo>[];

    for (var element in document.findAllElements('topic')) {
      final name = element.getElement('name')?.innerText;
      final idIcon = element.getElement('idIcon')?.innerText;
      final description = element.getElement('description')?.innerText;
      final route = element.getElement('route')?.innerText;

      if (name == null ||
          idIcon == null ||
          description == null ||
          route == null) {
        throw Exception('Missing required tags in topic element');
      }

      topics.add(
        TopicInfo(
          name: name,
          idIcon: idIcon,
          description: description,
          route: route,
        ),
      );
    }

    return topics;
  } on XmlException {
    rethrow;
  } on PlatformException {
    rethrow;
  } catch (e) {
    throw Exception('Unknown error: $e');
  }
}

Future<List<RecommendedInfo>> parseRecommended(
  AssetBundle bundle,
  String xmlPath,
) async {
  try {
    final xmlString = await bundle.loadString(xmlPath);
    final document = XmlDocument.parse(xmlString);
    final recommendations = <RecommendedInfo>[];

    for (var element in document.findAllElements('recommendation')) {
      final name = element.getElement('name')?.innerText;
      final idIcon = element.getElement('idIcon')?.innerText;
      final officialSite = element.getElement('officialSite')?.innerText;

      if (name == null || idIcon == null || officialSite == null) {
        throw Exception('Missing required tags in recommendation element');
      }

      recommendations.add(
        RecommendedInfo(name: name, idIcon: idIcon, officialSite: officialSite),
      );
    }

    return recommendations;
  } on XmlException {
    rethrow;
  } on PlatformException {
    rethrow;
  } catch (e) {
    throw Exception('Unknown error: $e');
  }
}

MarkdownStyleSheet getMarkdownStyleSheet(
  ThemeData theme,
  ColorScheme colorScheme,
) {
  return MarkdownStyleSheet.fromTheme(theme).copyWith(
    p: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurface),
    h1: theme.textTheme.headlineSmall?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h2: theme.textTheme.titleLarge?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h3: theme.textTheme.titleMedium?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h4: theme.textTheme.titleSmall?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h5: theme.textTheme.bodyLarge?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    h6: theme.textTheme.bodyMedium?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    a: TextStyle(
      decoration: TextDecoration.underline,
      decorationColor: colorScheme.primary,
    ).copyWith(color: colorScheme.primary, inherit: true),
    strong: theme.textTheme.bodyMedium?.copyWith(
      fontWeight: FontWeight.bold,
      color: colorScheme.onSurface,
    ),
    em: theme.textTheme.bodyMedium?.copyWith(
      fontStyle: FontStyle.italic,
      color: colorScheme.onSurface,
    ),
    listBullet: theme.textTheme.bodyMedium?.copyWith(
      color: colorScheme.onSurface,
    ),
    blockquote: theme.textTheme.bodyMedium?.copyWith(
      fontStyle: FontStyle.italic,
      color: colorScheme.onSurfaceVariant,
    ),
    blockquoteDecoration: BoxDecoration(
      color: colorScheme.surfaceContainer,
      border: Border(left: BorderSide(color: colorScheme.primary, width: 4)),
    ),
    blockquotePadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    code: theme.textTheme.bodySmall?.copyWith(
      fontFamily: 'monospace',
      backgroundColor: colorScheme.surfaceContainerHighest,
      color: colorScheme.onSurface,
    ),
    codeblockDecoration: BoxDecoration(
      color: colorScheme.surfaceContainerHighest,
      borderRadius: BorderRadius.circular(4),
    ),
  );
}

Future<bool> launchLink(String url) async {
  try {
    // !DO NOT CALL canLaunchUrl
    AudioController().playSound("click");
    if (url.toLowerCase().startsWith('mailto:')) {
      final Uri emailUri = Uri.parse(url);
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

    final Uri uri = Uri.parse(url);
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

enum MessageType { errorCommon, errorBrokenLink, warningCommon, infoCommon }

void showCustomDialog(
  MessageType type, {
  String param = "",
  String markdownExtension = "",
}) {
  BuildContext? context =
      AppRouter().navigatorKey.currentState?.overlay?.context;
  log.debug("${type.name}: $param [$markdownExtension]");
  if (context == null) {
    log.error("The context is not available to display dialog.");
    return;
  }

  String title = "";
  String icon = "";
  String message = "";
  String name = "";
  String additional = markdownExtension;
  switch (type) {
    case MessageType.errorCommon:
      title = AppLocalizations.of(context)!.error;
      icon = "assets/images/UI/error.svg";
      message = param;
      name = "error_dialog";
      break;
    case MessageType.errorBrokenLink:
      title = AppLocalizations.of(context)!.error;
      icon = "assets/images/UI/error.svg";
      message =
          "${AppLocalizations.of(context)!.unable_to_follow_the_link}: $param";
      name = "error_dialog";
      break;
    case MessageType.warningCommon:
      title = AppLocalizations.of(context)!.attention;
      icon = "assets/images/UI/attention.svg";
      message = param;
      name = "warning_dialog";
      break;
    case MessageType.infoCommon:
      title = AppLocalizations.of(context)!.info;
      icon = "assets/images/UI/info.svg";
      message = param;
      name = "info_dialog";
      break;
  }

  showDialog(
    context: context,
    routeSettings: RouteSettings(name: name),
    builder: (BuildContext dialogContext) {
      final theme = Theme.of(context);
      final colorScheme = theme.colorScheme;

      return AlertDialog(
        title: Center(
          child: Text(
            title,
            style: const TextStyle(fontSize: 24.0, fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                SvgPicture.asset(
                  icon,
                  width: 48,
                  height: 48,
                  colorFilter: ColorFilter.mode(
                    colorScheme.primary,
                    BlendMode.srcIn,
                  ),
                ),
                const SizedBox(width: 10.0),
                Expanded(
                  child: Text(message, style: const TextStyle(fontSize: 18.0)),
                ),
              ],
            ),
            const SizedBox(height: 10),
            if (additional.isNotEmpty)
              ExpansionTile(
                title: ConstrainedBox(
                  constraints: const BoxConstraints(minWidth: 300.0),
                  child: Row(
                    children: [
                      SvgPicture.asset(
                        "assets/images/UI/additional.svg",
                        width: 24,
                        height: 24,
                        colorFilter: ColorFilter.mode(
                          colorScheme.primary,
                          BlendMode.srcIn,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Text(
                        AppLocalizations.of(context)!.more_information,
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                children: [MarkdownBody(data: additional)],
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              AudioController().playSound("click");
              Navigator.of(dialogContext).pop();
            },
            child: Text(AppLocalizations.of(context)!.close),
          ),
        ],
      );
    },
  );
}

Rect createNonZeroRect(Offset start, Offset end) {
  double left = min(start.dx, end.dx);
  double top = min(start.dy, end.dy);
  double right = max(start.dx, end.dx);
  double bottom = max(start.dy, end.dy);
  if (right - left < 1) {
    right = left + 1;
  }
  if (bottom - top < 1) {
    bottom = top + 1;
  }
  return Rect.fromLTRB(left, top, right, bottom);
}

Future<String> getAppFolder() async {
  final directory = await getApplicationDocumentsDirectory();
  return '${directory.path}/${AppConstants.folder}';
}

Future<bool> isUpdateNeeded(String folder, String fileName) async {
  try {
    final loc = await getLastUpdateFileLocal(folder, fileName);
    final serv = await ServerManager().getLastUpdateFileFromServer(
      folder,
      fileName,
    );
    return loc == null ||
        loc.millisecondsSinceEpoch < serv!.millisecondsSinceEpoch;
  } catch (e) {
    log.error('Checking is update needed error: $e');
  }
  return false;
}

Future<String> updateLocalFile(String folder, String filePath) async {
  final appFolder = await getAppFolder();
  final file = File(p.join(appFolder, folder, filePath));

  try {
    final Uint8List? fileBytes = await ServerManager().downloadDB(
      folder,
      filePath,
    );
    if (fileBytes != null) {
      if (file.existsSync()) {
        file.delete();
      }
      await file.create(recursive: true);
      await file.writeAsBytes(fileBytes);
    }
  } catch (e) {
    log.error('Update local file error: $e');
  }

  return file.path;
}

Future<DateTime?> getLastUpdateFileLocal(String folder, String filePath) async {
  try {
    final appFolder = await getAppFolder();
    final file = File(p.join(appFolder, folder, filePath));
    if (file.existsSync()) {
      return file.lastModifiedSync();
    } else {
      return null;
    }
  } catch (e) {
    log.error('Getting file info local error: $e');
    return null;
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

Future<String> collectSystemAndAppInfo({BuildContext? context}) async {
  final buf = StringBuffer();
  final deviceInfo = DeviceInfoPlugin();
  void safeWrite(String key, Object? value) {
    buf.writeln('$key: ${value ?? "null"}');
  }

  // PLATFORM / DART
  try {
    buf.write("=======PLATFORM / DART=======\r\n");
    safeWrite('IsWeb', kIsWeb);
    safeWrite('Platform.operatingSystem', Platform.operatingSystem);
    safeWrite(
      'Platform.operatingSystemVersion',
      Platform.operatingSystemVersion,
    );
    safeWrite('dartVersion', Platform.version);
    safeWrite('isAndroid', Platform.isAndroid);
    safeWrite('isIOS', Platform.isIOS);
    safeWrite('isMacOS', Platform.isMacOS);
    safeWrite('isWindows', Platform.isWindows);
    safeWrite('isLinux', Platform.isLinux);
  } catch (e) {
    safeWrite('PlatformInfoError', e);
  }

  // PACKAGE / APP
  try {
    buf.write("\r\n=======PACKAGE / APP=======\r\n");
    final pkg = await PackageInfo.fromPlatform();
    safeWrite('appName', pkg.appName);
    safeWrite('packageName', pkg.packageName);
    safeWrite('version', pkg.version);
    safeWrite('buildNumber', pkg.buildNumber);
    safeWrite('buildSignature', pkg.buildSignature);
  } catch (e) {
    safeWrite('PackageInfoError', e);
  }

  // DEVICE INFO (device_info_plus)
  try {
    buf.write("\r\n=======DEVICE INFO=======\r\n");
    if (kIsWeb) {
      final web = await deviceInfo.webBrowserInfo;
      safeWrite('web_userAgent', web.userAgent);
      safeWrite('web_platform', web.platform);
      safeWrite('web_vendor', web.vendor);
      safeWrite('web_language', web.language);
      safeWrite('web_languages', web.languages);
      safeWrite('web_hardwareConcurrency', web.hardwareConcurrency);
      safeWrite('web_maxTouchPoints', web.maxTouchPoints);
      safeWrite('web_product', web.product);
    } else if (Platform.isAndroid) {
      final a = await deviceInfo.androidInfo;
      try {
        final map = a.data;
        map.forEach((k, v) => safeWrite('android.$k', v));
      } catch (_) {
        safeWrite('android.model', a.model);
        safeWrite('android.manufacturer', a.manufacturer);
        safeWrite('android.version.sdkInt', a.version.sdkInt);
        safeWrite('android.version.release', a.version.release);
        safeWrite('android.isPhysicalDevice', a.isPhysicalDevice);
      }
    } else if (Platform.isIOS) {
      final i = await deviceInfo.iosInfo;
      try {
        final map = i.data;
        map.forEach((k, v) => safeWrite('ios.$k', v));
      } catch (_) {
        safeWrite('ios.name', i.name);
        safeWrite('ios.systemName', i.systemName);
        safeWrite('ios.systemVersion', i.systemVersion);
        safeWrite('ios.model', i.model);
        safeWrite('ios.identifierForVendor', i.identifierForVendor);
        safeWrite('ios.utsname.sysname', i.utsname.sysname);
      }
    } else if (Platform.isMacOS) {
      final m = await deviceInfo.macOsInfo;
      try {
        final map = m.data;
        map.forEach((k, v) => safeWrite('macos.$k', v));
      } catch (_) {
        safeWrite('macos.computerName', m.computerName);
        safeWrite('macos.arch', m.arch);
        safeWrite('macos.kernelVersion', m.kernelVersion);
      }
    } else if (Platform.isWindows) {
      final w = await deviceInfo.windowsInfo;
      try {
        final map = w.data;
        map.forEach((k, v) => safeWrite('windows.$k', v));
      } catch (_) {
        safeWrite('windows.computerName', w.computerName);
        safeWrite('windows.numberOfCores', w.numberOfCores);
        safeWrite('windows.systemMemoryInMegabytes', w.systemMemoryInMegabytes);
      }
    } else if (Platform.isLinux) {
      final l = await deviceInfo.linuxInfo;
      try {
        final map = l.data;
        map.forEach((k, v) => safeWrite('linux.$k', v));
      } catch (_) {
        safeWrite('linux.name', l.name);
        safeWrite('linux.version', l.version);
        safeWrite('linux.id', l.id);
      }
    } else {
      safeWrite('deviceInfo', 'unknown platform');
    }
  } catch (e) {
    safeWrite('DeviceInfoError', e);
  }

  // SCREEN / DISPLAY
  try {
    buf.write("\r\n=======SCREEN / DISPLAY=======\r\n");
    double devicePixelRatio;
    Size physicalSize;
    if (context != null) {
      // ignore: use_build_context_synchronously
      final mq = MediaQuery.of(context);
      devicePixelRatio = mq.devicePixelRatio;
      physicalSize = Size(
        mq.size.width * mq.devicePixelRatio,
        mq.size.height * mq.devicePixelRatio,
      );
      safeWrite('screen.logicalWidth', mq.size.width);
      safeWrite('screen.logicalHeight', mq.size.height);
      safeWrite('screen.devicePixelRatio', mq.devicePixelRatio);
      safeWrite('screen.orientation', mq.orientation.toString());
    } else {
      // ignore: deprecated_member_use
      final window = WidgetsBinding.instance.window;
      devicePixelRatio = window.devicePixelRatio;
      physicalSize = window.physicalSize;
      safeWrite('screen.physicalWidth', physicalSize.width);
      safeWrite('screen.physicalHeight', physicalSize.height);
      safeWrite('screen.devicePixelRatio', devicePixelRatio);
    }
  } catch (e) {
    safeWrite('ScreenInfoError', e);
  }

  // LOCALE / TIMEZONE
  try {
    buf.write("\r\n=======LOCALE / TIMEZONE=======\r\n");
    String? locale;
    if (context != null) {
      // ignore: use_build_context_synchronously
      locale = Localizations.localeOf(context).toString();
    } else {
      locale = PlatformDispatcher.instance.locale.toString();
    }
    safeWrite('locale', locale);
    safeWrite('timeZoneName', DateTime.now().timeZoneName);
    safeWrite('timeZoneOffset', DateTime.now().timeZoneOffset.toString());
  } catch (e) {
    safeWrite('LocaleOrTimezoneError', e);
  }

  // ENVIRONMENT (Debug / Release)
  try {
    buf.write("\r\n=======ENVIRONMENT=======\r\n");
    var isDebug = false;
    assert(() {
      isDebug = true;
      return true;
    }());
    safeWrite('buildMode.isDebug', isDebug);
  } catch (e) {
    safeWrite('BuildModeError', e);
  }

  return buf.toString();
}
