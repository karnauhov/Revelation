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

  /// No description provided for @intf.
  ///
  /// In en, this message translates to:
  /// **'INTF'**
  String get intf;

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

  /// No description provided for @full_primary_sources.
  ///
  /// In en, this message translates to:
  /// **'The whole book'**
  String get full_primary_sources;

  /// No description provided for @significant_primary_sources.
  ///
  /// In en, this message translates to:
  /// **'Significant part'**
  String get significant_primary_sources;

  /// No description provided for @fragments_primary_sources.
  ///
  /// In en, this message translates to:
  /// **'Small fragments'**
  String get fragments_primary_sources;

  /// No description provided for @verses.
  ///
  /// In en, this message translates to:
  /// **'Quantity of verses'**
  String get verses;

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

  /// No description provided for @papyrus_18_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_18_material;

  /// No description provided for @papyrus_18_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_18_textStyle;

  /// No description provided for @papyrus_18_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_18_found;

  /// No description provided for @papyrus_18_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_18_classification;

  /// No description provided for @papyrus_18_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_18_currentLocation;

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

  /// No description provided for @papyrus_24_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_24_material;

  /// No description provided for @papyrus_24_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_24_textStyle;

  /// No description provided for @papyrus_24_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_24_found;

  /// No description provided for @papyrus_24_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_24_classification;

  /// No description provided for @papyrus_24_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_24_currentLocation;

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

  /// No description provided for @papyrus_43_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_43_material;

  /// No description provided for @papyrus_43_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_43_textStyle;

  /// No description provided for @papyrus_43_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_43_found;

  /// No description provided for @papyrus_43_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_43_classification;

  /// No description provided for @papyrus_43_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_43_currentLocation;

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

  /// No description provided for @papyrus_47_material.
  ///
  /// In en, this message translates to:
  /// **'The original source is written on papyrus, a material characteristic of early manuscripts. It consists of 10 sheets, approximately 24 by 13 cm in size. The manuscript is one of the oldest surviving fragments of the New Testament.'**
  String get papyrus_47_material;

  /// No description provided for @papyrus_47_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in a compact Greek uncial script using black ink, arranged in a single column per page with approximately 25–30 lines per folio. It employs scriptio continua (continuous writing without word separation).'**
  String get papyrus_47_textStyle;

  /// No description provided for @papyrus_47_found.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 47 was acquired in the 1930s by Alfred Chester Beatty from an antiquities dealer in Egypt, with the most likely place of discovery being the Faiyum region in Egypt.'**
  String get papyrus_47_found;

  /// No description provided for @papyrus_47_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, it belongs to the Alexandrian text-type and is classified as Category I among New Testament manuscripts.'**
  String get papyrus_47_classification;

  /// No description provided for @papyrus_47_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Today, Papyrus 47 is housed at the Chester Beatty Library in Dublin, Ireland, as part of the Chester Beatty Papyri collection.'**
  String get papyrus_47_currentLocation;

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

  /// No description provided for @papyrus_85_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_85_material;

  /// No description provided for @papyrus_85_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_85_textStyle;

  /// No description provided for @papyrus_85_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_85_found;

  /// No description provided for @papyrus_85_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_85_classification;

  /// No description provided for @papyrus_85_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_85_currentLocation;

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

  /// No description provided for @papyrus_98_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_98_material;

  /// No description provided for @papyrus_98_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_98_textStyle;

  /// No description provided for @papyrus_98_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_98_found;

  /// No description provided for @papyrus_98_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_98_classification;

  /// No description provided for @papyrus_98_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get papyrus_98_currentLocation;

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

  /// No description provided for @papyrus_115_material.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 115 is a fragmented Greek manuscript of the New Testament, written on papyrus. It comprises 26 fragments of a codex containing portions of the Book of Revelation. The original pages measured approximately 15.5 × 23.5 cm.'**
  String get papyrus_115_material;

  /// No description provided for @papyrus_115_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in Greek uncial script, arranged in a single column per page with 33-36 lines per column. It follows scriptio continua style without word separation, and features occasional use of punctuation marks and abbreviations typical for biblical manuscripts of its period.'**
  String get papyrus_115_textStyle;

  /// No description provided for @papyrus_115_found.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 115 was discovered in Oxyrhynchus, Egypt, by scholars Bernard Pyne Grenfell and Arthur Hunt in the late 19th or early 20th century, although it was not deciphered and published until the end of the 20th century.'**
  String get papyrus_115_found;

  /// No description provided for @papyrus_115_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, this primary source aligns with the Alexandrian text-type. It is classified as Category I among New Testament manuscripts.'**
  String get papyrus_115_classification;

  /// No description provided for @papyrus_115_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 115 is currently housed at the Ashmolean Museum in Oxford, United Kingdom.'**
  String get papyrus_115_currentLocation;

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

  /// No description provided for @uncial_01_material.
  ///
  /// In en, this message translates to:
  /// **'Codex Sinaiticus is written on vellum parchment, primarily made from calfskin, with some portions made from sheepskin. Originally, it was produced on double sheets, likely measuring approximately 40 × 70 cm. The portion held in the British Library consists of 346½ folios (694 pages), each measuring about 38.1 × 34.5 cm.'**
  String get uncial_01_material;

  /// No description provided for @uncial_01_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The manuscript is written in a formal uncial script (biblical majuscule) in Greek, featuring scriptio continua (continuous script without spaces between words). The text is arranged in columns: four per page in the New Testament and two per page for poetic texts. It also includes carefully regulated line breaks, nomina sacra, and distinctive punctuation.'**
  String get uncial_01_textStyle;

  /// No description provided for @uncial_01_found.
  ///
  /// In en, this message translates to:
  /// **'Codex Sinaiticus was discovered in 1844 at Saint Catherine’s Monastery on the Sinai Peninsula by Constantin von Tischendorf.'**
  String get uncial_01_found;

  /// No description provided for @uncial_01_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, Codex Sinaiticus belongs to the Alexandrian text-type and is classified as Category I among New Testament manuscripts.'**
  String get uncial_01_classification;

  /// No description provided for @uncial_01_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Today, parts of the codex are preserved in several institutions: primarily in the British Library (London), as well as in the Leipzig University Library, Saint Catherine’s Monastery (Sinai), and the National Library of Russia (Saint Petersburg).'**
  String get uncial_01_currentLocation;

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

  /// No description provided for @uncial_02_material.
  ///
  /// In en, this message translates to:
  /// **'Codex Alexandrinus is written on parchment (vellum) made from thin, high-quality material. It consists of 773 folios, each measuring approximately 32 × 26 cm, originally gathered into quires (typically eight leaves per quire). The manuscript comprises four volumes: three containing the Septuagint (Old Testament) and one containing the New Testament.'**
  String get uncial_02_material;

  /// No description provided for @uncial_02_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in an elegant uncial script in Greek, arranged in two columns per page, with 49–51 lines per column and approximately 20–25 letters per line. It follows scriptio continua (without spaces), with red ink used for the initial lines of each book and decorative tailpieces at the end of each book. Occasional punctuation marks and annotations (e.g., enlarged initials indicating new sections) are present.'**
  String get uncial_02_textStyle;

  /// No description provided for @uncial_02_found.
  ///
  /// In en, this message translates to:
  /// **'Codex Alexandrinus takes its name from Alexandria, Egypt, where it was kept for some time. In the 17th century, Patriarch Cyril Lucaris brought it from Alexandria to Constantinople and later presented it to Charles I of England.'**
  String get uncial_02_found;

  /// No description provided for @uncial_02_classification.
  ///
  /// In en, this message translates to:
  /// **'Textually, the codex exhibits a mixed character: the Gospels reflect the Byzantine text-type (Category III), while the rest of the New Testament belongs to the Alexandrian text-type (Category I).'**
  String get uncial_02_classification;

  /// No description provided for @uncial_02_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Today, Codex Alexandrinus is housed in the British Library in London, displayed alongside Codex Sinaiticus in the John Ritblat Gallery.'**
  String get uncial_02_currentLocation;

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

  /// No description provided for @uncial_04_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_04_material;

  /// No description provided for @uncial_04_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_04_textStyle;

  /// No description provided for @uncial_04_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_04_found;

  /// No description provided for @uncial_04_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_04_classification;

  /// No description provided for @uncial_04_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_04_currentLocation;

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

  /// No description provided for @uncial_25_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_25_material;

  /// No description provided for @uncial_25_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_25_textStyle;

  /// No description provided for @uncial_25_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_25_found;

  /// No description provided for @uncial_25_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_25_classification;

  /// No description provided for @uncial_25_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_25_currentLocation;

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

  /// No description provided for @uncial_46_material.
  ///
  /// In en, this message translates to:
  /// **'Codex Vaticanus 2066 is written on parchment (vellum), typical of uncial manuscripts. The codex contains the complete text of the Book of Revelation on 20 parchment leaves, each measuring approximately 27.5 cm by 19 cm.'**
  String get uncial_46_material;

  /// No description provided for @uncial_46_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in one column per page, with 35 lines per page and approximately 36 letters per line. It is rendered in a formal uncial script using scriptio continua. The uncial letters are executed in a distinctive style—slightly inclined to the right—and occupy an intermediate form between square and oblong characters. The breathings and accents rendered with considerable accuracy.'**
  String get uncial_46_textStyle;

  /// No description provided for @uncial_46_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript once belonged to Philippo Vitali (1590–1653). The text of the codex was published by Cardinal Angelo Mai in 1859 in Rome.'**
  String get uncial_46_found;

  /// No description provided for @uncial_46_classification.
  ///
  /// In en, this message translates to:
  /// **'The Greek text of this codex represents the Byzantine text-type and is closely related to minuscules 61 and 69. Aland classified it as Category V. Uncial 046 is the earliest manuscript representing the main Byzantine group (\'a\').'**
  String get uncial_46_classification;

  /// No description provided for @uncial_46_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Codex is currently housed in the Vatican Library in Rome.'**
  String get uncial_46_currentLocation;

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

  /// No description provided for @uncial_51_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_51_material;

  /// No description provided for @uncial_51_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_51_textStyle;

  /// No description provided for @uncial_51_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_51_found;

  /// No description provided for @uncial_51_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_51_classification;

  /// No description provided for @uncial_51_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_51_currentLocation;

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

  /// No description provided for @uncial_52_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_52_material;

  /// No description provided for @uncial_52_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_52_textStyle;

  /// No description provided for @uncial_52_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_52_found;

  /// No description provided for @uncial_52_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_52_classification;

  /// No description provided for @uncial_52_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_52_currentLocation;

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

  /// No description provided for @uncial_163_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_163_material;

  /// No description provided for @uncial_163_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_163_textStyle;

  /// No description provided for @uncial_163_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_163_found;

  /// No description provided for @uncial_163_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_163_classification;

  /// No description provided for @uncial_163_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_163_currentLocation;

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

  /// No description provided for @uncial_169_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_169_material;

  /// No description provided for @uncial_169_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_169_textStyle;

  /// No description provided for @uncial_169_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_169_found;

  /// No description provided for @uncial_169_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_169_classification;

  /// No description provided for @uncial_169_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_169_currentLocation;

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

  /// No description provided for @uncial_207_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_207_material;

  /// No description provided for @uncial_207_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_207_textStyle;

  /// No description provided for @uncial_207_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_207_found;

  /// No description provided for @uncial_207_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_207_classification;

  /// No description provided for @uncial_207_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_207_currentLocation;

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

  /// No description provided for @uncial_229_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_229_material;

  /// No description provided for @uncial_229_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_229_textStyle;

  /// No description provided for @uncial_229_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_229_found;

  /// No description provided for @uncial_229_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_229_classification;

  /// No description provided for @uncial_229_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_229_currentLocation;

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

  /// No description provided for @uncial_308_material.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_308_material;

  /// No description provided for @uncial_308_textStyle.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_308_textStyle;

  /// No description provided for @uncial_308_found.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_308_found;

  /// No description provided for @uncial_308_classification.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_308_classification;

  /// No description provided for @uncial_308_currentLocation.
  ///
  /// In en, this message translates to:
  /// **''**
  String get uncial_308_currentLocation;
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
