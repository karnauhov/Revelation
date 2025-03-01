import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_ru.dart';
import 'app_localizations_uk.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale) : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('ru'),
    Locale('uk')
  ];

  /// No description provided for @app_name.
  ///
  /// In en, this message translates to:
  /// **'Revelation'**
  String get app_name;

  /// No description provided for @version.
  ///
  /// In en, this message translates to:
  /// **'Version'**
  String get version;

  /// No description provided for @app_description.
  ///
  /// In en, this message translates to:
  /// **'Revelation Study app.'**
  String get app_description;

  /// No description provided for @license.
  ///
  /// In en, this message translates to:
  /// **'License'**
  String get license;

  /// No description provided for @acknowledgements_title.
  ///
  /// In en, this message translates to:
  /// **'Acknowledgments'**
  String get acknowledgements_title;

  /// No description provided for @acknowledgements_description_1.
  ///
  /// In en, this message translates to:
  /// **'Many thanks to the developers who worked on the following software:'**
  String get acknowledgements_description_1;

  /// No description provided for @acknowledgements_description_2.
  ///
  /// In en, this message translates to:
  /// **''**
  String get acknowledgements_description_2;

  /// No description provided for @all_rights_reserved.
  ///
  /// In en, this message translates to:
  /// **'All rights reserved'**
  String get all_rights_reserved;

  /// No description provided for @menu.
  ///
  /// In en, this message translates to:
  /// **'Menu'**
  String get menu;

  /// No description provided for @close_app.
  ///
  /// In en, this message translates to:
  /// **'Close app'**
  String get close_app;

  /// No description provided for @todo.
  ///
  /// In en, this message translates to:
  /// **'TODO'**
  String get todo;

  /// No description provided for @primary_sources_screen.
  ///
  /// In en, this message translates to:
  /// **'Primary Sources'**
  String get primary_sources_screen;

  /// No description provided for @settings_screen.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings_screen;

  /// No description provided for @about_screen.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about_screen;

  /// No description provided for @error_loading_libraries.
  ///
  /// In en, this message translates to:
  /// **'Error loading libraries'**
  String get error_loading_libraries;

  /// No description provided for @error_loading_topics.
  ///
  /// In en, this message translates to:
  /// **'Error loading topics'**
  String get error_loading_topics;

  /// No description provided for @changelog.
  ///
  /// In en, this message translates to:
  /// **'Changelog'**
  String get changelog;

  /// No description provided for @close.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get close;

  /// No description provided for @error.
  ///
  /// In en, this message translates to:
  /// **'Error'**
  String get error;

  /// No description provided for @attention.
  ///
  /// In en, this message translates to:
  /// **'Attention'**
  String get attention;

  /// No description provided for @info.
  ///
  /// In en, this message translates to:
  /// **'Information'**
  String get info;

  /// No description provided for @more_information.
  ///
  /// In en, this message translates to:
  /// **'More information'**
  String get more_information;

  /// No description provided for @unable_to_follow_the_link.
  ///
  /// In en, this message translates to:
  /// **'Unable to follow the link'**
  String get unable_to_follow_the_link;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @wikipedia.
  ///
  /// In en, this message translates to:
  /// **'Wikipedia'**
  String get wikipedia;

  /// No description provided for @topic.
  ///
  /// In en, this message translates to:
  /// **'Topic'**
  String get topic;

  /// No description provided for @topic_0_name.
  ///
  /// In en, this message translates to:
  /// **'Preface'**
  String get topic_0_name;

  /// No description provided for @topic_0_description.
  ///
  /// In en, this message translates to:
  /// **'Primary sources, principles, stages'**
  String get topic_0_description;

  /// No description provided for @topic_1_name.
  ///
  /// In en, this message translates to:
  /// **'Introduction'**
  String get topic_1_name;

  /// No description provided for @topic_1_description.
  ///
  /// In en, this message translates to:
  /// **'Revelation 1:1-3'**
  String get topic_1_description;

  /// No description provided for @papyrus_18_title.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 18 (P<sup>18</sup>)'**
  String get papyrus_18_title;

  /// No description provided for @papyrus_18_date.
  ///
  /// In en, this message translates to:
  /// **'3rd or early 4th century AD'**
  String get papyrus_18_date;

  /// No description provided for @papyrus_18_content.
  ///
  /// In en, this message translates to:
  /// **'Fragment of Revelation (1:4-7).'**
  String get papyrus_18_content;

  /// No description provided for @papyrus_18_features.
  ///
  /// In en, this message translates to:
  /// **'On one side of the papyrus, there is a text from the Book of Revelation, and on the other side, the conclusion of the Book of Exodus. The texts were written by different scribes, which may indicate the reuse of the material. The papyrus is housed at the British Library, London.'**
  String get papyrus_18_features;

  /// No description provided for @papyrus_24_title.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 24 (P<sup>24</sup>)'**
  String get papyrus_24_title;

  /// No description provided for @papyrus_24_date.
  ///
  /// In en, this message translates to:
  /// **'Early 4th century AD'**
  String get papyrus_24_date;

  /// No description provided for @papyrus_24_content.
  ///
  /// In en, this message translates to:
  /// **'Fragments of Revelation (5:5-8) and (6:5-8).'**
  String get papyrus_24_content;

  /// No description provided for @papyrus_24_features.
  ///
  /// In en, this message translates to:
  /// **'The papyrus is written on a large sheet approximately 19 x 28 cm in size. The text represents the Alexandrian type (or proto-Alexandrian) and aligns with Papyrus 18, Papyrus 47, and the Codex Sinaiticus. Currently, the papyrus is housed at the library of Yale Divinity School.'**
  String get papyrus_24_features;

  /// No description provided for @papyrus_43_title.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 43 (P<sup>43</sup>)'**
  String get papyrus_43_title;

  /// No description provided for @papyrus_43_date.
  ///
  /// In en, this message translates to:
  /// **'6th or 7th century AD'**
  String get papyrus_43_date;

  /// No description provided for @papyrus_43_content.
  ///
  /// In en, this message translates to:
  /// **'Fragments of Revelation (2:12-13) and (15:8-16:2).'**
  String get papyrus_43_content;

  /// No description provided for @papyrus_43_features.
  ///
  /// In en, this message translates to:
  /// **'The papyrus was written in two different, careless handwritings, which may indicate its use for selective excerpts rather than continuous text. The text on the reverse side is oriented in the opposite direction to the front side, supporting the assumption of discontinuous content. The text belongs to the Alexandrian type and is classified as Category II according to Kurt Aland\'s system. Currently, the papyrus is housed at the British Library in London.'**
  String get papyrus_43_features;

  /// No description provided for @papyrus_47_title.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 47 (P<sup>47</sup>)'**
  String get papyrus_47_title;

  /// No description provided for @papyrus_47_date.
  ///
  /// In en, this message translates to:
  /// **'Early 3rd century AD'**
  String get papyrus_47_date;

  /// No description provided for @papyrus_47_content.
  ///
  /// In en, this message translates to:
  /// **'Fragments of Revelation (9:10-11:3); (11:5-16:15) and (16:17-17:2).'**
  String get papyrus_47_content;

  /// No description provided for @papyrus_47_features.
  ///
  /// In en, this message translates to:
  /// **'The manuscript is a codex, written with black ink on papyrus. Although fragmentary, the manuscript is considered representative of the Alexandrian text-type. The papyrus text is most closely related to the Codex Sinaiticus, and together they testify to one of the early textual types of the Book of Revelation. The papyrus is currently housed at the Chester Beatty Library in Dublin.'**
  String get papyrus_47_features;

  /// No description provided for @papyrus_85_title.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 85 (P<sup>85</sup>)'**
  String get papyrus_85_title;

  /// No description provided for @papyrus_85_date.
  ///
  /// In en, this message translates to:
  /// **'4th or 5th century AD'**
  String get papyrus_85_date;

  /// No description provided for @papyrus_85_content.
  ///
  /// In en, this message translates to:
  /// **'Fragments of Revelation (9:19-10:2) and (10:5-9).'**
  String get papyrus_85_content;

  /// No description provided for @papyrus_85_features.
  ///
  /// In en, this message translates to:
  /// **'The text belongs to the Alexandrian text-type and is classified as Category II according to Kurt Aland’s system. The papyrus is currently housed at the National Academic Library of Strasbourg.'**
  String get papyrus_85_features;

  /// No description provided for @papyrus_98_title.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 98 (P<sup>98</sup>)'**
  String get papyrus_98_title;

  /// No description provided for @papyrus_98_date.
  ///
  /// In en, this message translates to:
  /// **'Between 150 and 250 AD'**
  String get papyrus_98_date;

  /// No description provided for @papyrus_98_content.
  ///
  /// In en, this message translates to:
  /// **'Fragment of Revelation (1:13-2:1).'**
  String get papyrus_98_content;

  /// No description provided for @papyrus_98_features.
  ///
  /// In en, this message translates to:
  /// **'The text is written in a large, neat script on a papyrus scroll. The biblical text appears on the reverse side of the scroll, while the front side contains another document dated to the late 1st or early 2nd century AD. The papyrus is currently housed at the French Institute for Eastern Archaeology in Cairo.'**
  String get papyrus_98_features;

  /// No description provided for @papyrus_115_title.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 115 (P<sup>115</sup>)'**
  String get papyrus_115_title;

  /// No description provided for @papyrus_115_date.
  ///
  /// In en, this message translates to:
  /// **'Between 225 and 275 AD'**
  String get papyrus_115_date;

  /// No description provided for @papyrus_115_content.
  ///
  /// In en, this message translates to:
  /// **'Fragments of Revelation (2:1-3, 13-15, 27-29); (3:10-12); (5:8-9); (6:4-6); (8:3-8, 11-13); (9:1-5, 7-16, 18-21); (10:1-4, 8-11); (11:1-5, 8-15, 18-19); (12:1-5, 8-10, 12-17); (13:1-3, 6-16, 18); (14:1-3, 5-7, 10-11, 14-15, 18-20); (15:1, 4-7).'**
  String get papyrus_115_content;

  /// No description provided for @papyrus_115_features.
  ///
  /// In en, this message translates to:
  /// **'It contains 26 fragments of a codex measuring 15.5 x 23.5 cm, with 33-36 lines per page. The text belongs to the Alexandrian text-type and is closely related to the Alexandrian Codex and the Codex Ephraemi. It was discovered in Oxyrhynchus, Egypt, and is currently housed at the Ashmolean Museum in Oxford.'**
  String get papyrus_115_features;

  /// No description provided for @uncial_01_title.
  ///
  /// In en, this message translates to:
  /// **'Codex Sinaiticus (ℵ 01)'**
  String get uncial_01_title;

  /// No description provided for @uncial_01_date.
  ///
  /// In en, this message translates to:
  /// **'4th century AD'**
  String get uncial_01_date;

  /// No description provided for @uncial_01_content.
  ///
  /// In en, this message translates to:
  /// **'The entire book of Revelation.'**
  String get uncial_01_content;

  /// No description provided for @uncial_01_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_01_features;

  /// No description provided for @uncial_02_title.
  ///
  /// In en, this message translates to:
  /// **'Codex Alexandrinus (A 02)'**
  String get uncial_02_title;

  /// No description provided for @uncial_02_date.
  ///
  /// In en, this message translates to:
  /// **'5th century AD'**
  String get uncial_02_date;

  /// No description provided for @uncial_02_content.
  ///
  /// In en, this message translates to:
  /// **'The entire book of Revelation.'**
  String get uncial_02_content;

  /// No description provided for @uncial_02_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_02_features;

  /// No description provided for @uncial_04_title.
  ///
  /// In en, this message translates to:
  /// **'Codex Ephraemi Rescriptus (C 04)'**
  String get uncial_04_title;

  /// No description provided for @uncial_04_date.
  ///
  /// In en, this message translates to:
  /// **'5th century AD'**
  String get uncial_04_date;

  /// No description provided for @uncial_04_content.
  ///
  /// In en, this message translates to:
  /// **'Fragments of Revelation (1:2-20); (2:1-29); (3:1-19); (5:14); (6:1-17); (7:1-14,17); (8:1-4); (9:17-21); (10:1-10); (11:3-19); (12:1-18); (13:1-18); (14:1-20); (15:1-8); (16:1-13); (18:2-24); (19:1-5).'**
  String get uncial_04_content;

  /// No description provided for @uncial_04_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_04_features;

  /// No description provided for @uncial_25_title.
  ///
  /// In en, this message translates to:
  /// **'Codex Porphyrianus (P<sup>apr</sup> 025)'**
  String get uncial_25_title;

  /// No description provided for @uncial_25_date.
  ///
  /// In en, this message translates to:
  /// **'9th century AD'**
  String get uncial_25_date;

  /// No description provided for @uncial_25_content.
  ///
  /// In en, this message translates to:
  /// **'The entire book of Revelation except fragments (16:13-21); (20:1-8); (22:7-21).'**
  String get uncial_25_content;

  /// No description provided for @uncial_25_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_25_features;

  /// No description provided for @uncial_46_title.
  ///
  /// In en, this message translates to:
  /// **'Codex Vaticanus 2066 (Uncial 046)'**
  String get uncial_46_title;

  /// No description provided for @uncial_46_date.
  ///
  /// In en, this message translates to:
  /// **'10th century AD'**
  String get uncial_46_date;

  /// No description provided for @uncial_46_content.
  ///
  /// In en, this message translates to:
  /// **'The entire book of Revelation.'**
  String get uncial_46_content;

  /// No description provided for @uncial_46_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_46_features;

  /// No description provided for @uncial_51_title.
  ///
  /// In en, this message translates to:
  /// **'Codex Athous Pantokratoros (Uncial 051)'**
  String get uncial_51_title;

  /// No description provided for @uncial_51_date.
  ///
  /// In en, this message translates to:
  /// **'10th century AD'**
  String get uncial_51_date;

  /// No description provided for @uncial_51_content.
  ///
  /// In en, this message translates to:
  /// **'Fragments of Revelation (11:15-19); (12:1-18); (13:1,3-18); (14:1-20); (15:1-8); (16:1-21); (17:1-18); (18:1-24); (19:1-21); (20:1-15); (21:1-27); (22:1-7,15-21).'**
  String get uncial_51_content;

  /// No description provided for @uncial_51_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_51_features;

  /// No description provided for @uncial_52_title.
  ///
  /// In en, this message translates to:
  /// **'Codex Athous Panteleimon (Uncial 052)'**
  String get uncial_52_title;

  /// No description provided for @uncial_52_date.
  ///
  /// In en, this message translates to:
  /// **'10th century AD'**
  String get uncial_52_date;

  /// No description provided for @uncial_52_content.
  ///
  /// In en, this message translates to:
  /// **'Fragments of Revelation (7:16-17); (8:1-12).'**
  String get uncial_52_content;

  /// No description provided for @uncial_52_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_52_features;

  /// No description provided for @uncial_163_title.
  ///
  /// In en, this message translates to:
  /// **'Uncial 0163'**
  String get uncial_163_title;

  /// No description provided for @uncial_163_date.
  ///
  /// In en, this message translates to:
  /// **'5th century AD'**
  String get uncial_163_date;

  /// No description provided for @uncial_163_content.
  ///
  /// In en, this message translates to:
  /// **'Fragment of Revelation (16:17-20).'**
  String get uncial_163_content;

  /// No description provided for @uncial_163_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_163_features;

  /// No description provided for @uncial_169_title.
  ///
  /// In en, this message translates to:
  /// **'Uncial 0169'**
  String get uncial_169_title;

  /// No description provided for @uncial_169_date.
  ///
  /// In en, this message translates to:
  /// **'4th century AD'**
  String get uncial_169_date;

  /// No description provided for @uncial_169_content.
  ///
  /// In en, this message translates to:
  /// **'Fragment of Revelation (3:19-4:3).'**
  String get uncial_169_content;

  /// No description provided for @uncial_169_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_169_features;

  /// No description provided for @uncial_207_title.
  ///
  /// In en, this message translates to:
  /// **'Uncial 0207'**
  String get uncial_207_title;

  /// No description provided for @uncial_207_date.
  ///
  /// In en, this message translates to:
  /// **'4th century AD'**
  String get uncial_207_date;

  /// No description provided for @uncial_207_content.
  ///
  /// In en, this message translates to:
  /// **'Fragment of Revelation (9:2-15).'**
  String get uncial_207_content;

  /// No description provided for @uncial_207_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_207_features;

  /// No description provided for @uncial_229_title.
  ///
  /// In en, this message translates to:
  /// **'Uncial 0229'**
  String get uncial_229_title;

  /// No description provided for @uncial_229_date.
  ///
  /// In en, this message translates to:
  /// **'8th century AD'**
  String get uncial_229_date;

  /// No description provided for @uncial_229_content.
  ///
  /// In en, this message translates to:
  /// **'Fragments of Revelation (18:16-17); (19:4-6).'**
  String get uncial_229_content;

  /// No description provided for @uncial_229_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_229_features;

  /// No description provided for @uncial_308_title.
  ///
  /// In en, this message translates to:
  /// **'Uncial 0308'**
  String get uncial_308_title;

  /// No description provided for @uncial_308_date.
  ///
  /// In en, this message translates to:
  /// **'4th century AD'**
  String get uncial_308_date;

  /// No description provided for @uncial_308_content.
  ///
  /// In en, this message translates to:
  /// **'Fragment of Revelation (11:15-18).'**
  String get uncial_308_content;

  /// No description provided for @uncial_308_features.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_308_features;
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>['en', 'ru', 'uk'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {


  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en': return AppLocalizationsEn();
    case 'ru': return AppLocalizationsRu();
    case 'uk': return AppLocalizationsUk();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.'
  );
}
