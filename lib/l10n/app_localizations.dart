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

  /// No description provided for @privacy_policy.
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacy_policy;

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

  /// No description provided for @primary_sources_header.
  ///
  /// In en, this message translates to:
  /// **'Click on the image to open'**
  String get primary_sources_header;

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
  /// **'Primary sources and principles'**
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

  /// No description provided for @show_more.
  ///
  /// In en, this message translates to:
  /// **'show more information'**
  String get show_more;

  /// No description provided for @hide.
  ///
  /// In en, this message translates to:
  /// **'hide'**
  String get hide;

  /// No description provided for @full_primary_sources.
  ///
  /// In en, this message translates to:
  /// **'Contain the entire Revelation in full'**
  String get full_primary_sources;

  /// No description provided for @significant_primary_sources.
  ///
  /// In en, this message translates to:
  /// **'Contain a significant part of the Revelation'**
  String get significant_primary_sources;

  /// No description provided for @fragments_primary_sources.
  ///
  /// In en, this message translates to:
  /// **'Contain small fragments of the Revelation'**
  String get fragments_primary_sources;

  /// No description provided for @verses.
  ///
  /// In en, this message translates to:
  /// **'Quantity of verses'**
  String get verses;

  /// No description provided for @choose_page.
  ///
  /// In en, this message translates to:
  /// **'Choose page'**
  String get choose_page;

  /// No description provided for @images_are_missing.
  ///
  /// In en, this message translates to:
  /// **'Images are missing'**
  String get images_are_missing;

  /// No description provided for @image_not_loaded.
  ///
  /// In en, this message translates to:
  /// **'Image not loaded'**
  String get image_not_loaded;

  /// No description provided for @reload_image.
  ///
  /// In en, this message translates to:
  /// **'Reload image'**
  String get reload_image;

  /// No description provided for @zoom_in.
  ///
  /// In en, this message translates to:
  /// **'Zoom in'**
  String get zoom_in;

  /// No description provided for @zoom_out.
  ///
  /// In en, this message translates to:
  /// **'Zoom out'**
  String get zoom_out;

  /// No description provided for @restore_original_scale.
  ///
  /// In en, this message translates to:
  /// **'Original scale'**
  String get restore_original_scale;

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
  /// **'Papyrus 18 is an early Greek New Testament manuscript containing a fragment of the Book of Revelation, also known as Oxyrhynchus Papyrus #1079. It consists of a single papyrus leaf measuring approximately 15 × 10 cm, with text written on both sides. The recto contains the end of Exodus, while the verso features the beginning of Revelation, suggesting it may have been part of a codex with miscellaneous contents or a reused scroll.'**
  String get papyrus_18_material;

  /// No description provided for @papyrus_18_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in a clear, medium-sized cursive script. It follows scriptio continua (continuous writing without spaces) and employs nomina sacra (sacred names) in abbreviated forms.'**
  String get papyrus_18_textStyle;

  /// No description provided for @papyrus_18_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered in Oxyrhynchus, Egypt, by scholars Bernard Pyne Grenfell and Arthur Hunt in the late 19th or early 20th century. The fragment subsequently published in 1911.'**
  String get papyrus_18_found;

  /// No description provided for @papyrus_18_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the manuscript is classified as a representative of the Alexandrian text-type and is placed in Category I among New Testament manuscripts according to the Aland classification.'**
  String get papyrus_18_classification;

  /// No description provided for @papyrus_18_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Currently, Papyrus 18 is housed in the British Library in London.'**
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
  /// **'Papyrus 24 is an early Greek New Testament manuscript, also known as Oxyrhynchus Papyrus #1230. It consists of light-colored papyrus fragment measuring approximately 4 × 7 cm, with text from the Book of Revelation preserved on both sides. It is believed that initially the text was written on a larger sheet measuring approximately 19 × 28 cm.'**
  String get papyrus_24_material;

  /// No description provided for @papyrus_24_textStyle.
  ///
  /// In en, this message translates to:
  /// **'Fragment of a leaf written in a medium-sized sloping informal hand. The lines appear to have been fairly long, containing about 30-32 letters. The text follows scriptio continua (continuous writing without spaces between words).'**
  String get papyrus_24_textStyle;

  /// No description provided for @papyrus_24_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered in Oxyrhynchus, Egypt, by scholars Bernard Pyne Grenfell and Arthur Hunt in the late 19th or early 20th century. The fragment subsequently published in 1914.'**
  String get papyrus_24_found;

  /// No description provided for @papyrus_24_classification.
  ///
  /// In en, this message translates to:
  /// **'The manuscript is a representative of the Alexandrian text-type (rather proto-Alexandrian). Aland classified it as Category I. It shows textual agreement with Papyrus 18, Papyrus 47, and Codex Sinaiticus, but the surviving fragment is too small to determine its overall textual character with certainty.'**
  String get papyrus_24_classification;

  /// No description provided for @papyrus_24_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 24 is currently housed at the Yale Divinity Library in New Haven, Connecticut, as part of the Andover Newton Oxyrhynchus Papyri collection.'**
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
  /// **'Papyrus 43 is New Testament manuscript. It consists of light-colored papyrus fragment measuring approximately 4 × 7 cm, with text from the Book of Revelation preserved on both sides.'**
  String get papyrus_43_material;

  /// No description provided for @papyrus_43_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in Greek using two inelegant sloping hands and follows scriptio continua (continuous writing without spaces). The writing on the verso is oriented in the opposite direction to that on the recto.'**
  String get papyrus_43_textStyle;

  /// No description provided for @papyrus_43_found.
  ///
  /// In en, this message translates to:
  /// **'The primary source was discovered during the excavations at Wadi Sarga in Egypt during the winter of 1913-1914, led by Mr. R. Campbell Thompson.'**
  String get papyrus_43_found;

  /// No description provided for @papyrus_43_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the manuscript is considered a representative of the Alexandrian text-type and is classified as Category II in Kurt Aland\'s New Testament manuscripts classification system.'**
  String get papyrus_43_classification;

  /// No description provided for @papyrus_43_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Currently, Papyrus 43 is housed in the British Library in London.'**
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
  /// **'The original source is written on papyrus, a material characteristic of early manuscripts. It consists of 10 sheets, approximately 24 × 13 cm in size. The manuscript is one of the oldest surviving fragments of the New Testament.'**
  String get papyrus_47_material;

  /// No description provided for @papyrus_47_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in a compact Greek uncial script using black ink, arranged in a single column per page with approximately 25-30 lines per folio. It employs scriptio continua (continuous writing without word separation).'**
  String get papyrus_47_textStyle;

  /// No description provided for @papyrus_47_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was acquired in the 1930s by Alfred Chester Beatty from an antiquities dealer in Egypt, with the most likely place of discovery being the Faiyum region in Egypt.'**
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
  /// **'Papyrus 85 consists of three fragments of a papyrus leaf, with the largest measuring approximately 4 × 7 cm. The fragments contain text from the Book of Revelation written on both sides.'**
  String get papyrus_85_material;

  /// No description provided for @papyrus_85_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in Greek uncial script, arranged in a single column per page with 37 lines. It follows scriptio continua style without word separation.'**
  String get papyrus_85_textStyle;

  /// No description provided for @papyrus_85_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was probably discovered in Egypt. Later, it was identified by Jacques Schwartz, who published his findings in 1969.'**
  String get papyrus_85_found;

  /// No description provided for @papyrus_85_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the manuscript is considered a representative of the Alexandrian text-type and is classified as Category II in Kurt Aland\'s New Testament manuscripts classification system.'**
  String get papyrus_85_classification;

  /// No description provided for @papyrus_85_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 85 is currently housed at the National Academic Library in Strasbourg, France.'**
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
  /// **'The primary source is written on papyrus and comprises a single fragment measuring approximately 7 × 13 cm, originally forming part of a scroll containing Revelation.'**
  String get papyrus_98_material;

  /// No description provided for @papyrus_98_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The surviving text of Revelation is in a fragmentary state. The script is large and well-formed, written in uncial style. The fragment was part of a scroll. The biblical text is located on the verso side, while the recto contains another documentary text, dated to the late 1st or early 2nd century.'**
  String get papyrus_98_textStyle;

  /// No description provided for @papyrus_98_found.
  ///
  /// In en, this message translates to:
  /// **'The papyrus was discovered in Egypt and first published by Wagner in 1971, although he did not initially recognize it as a biblical text. It wasn\'t until 1992 that Dieter Hagedorn identified it as a fragment of the Book of Revelation.'**
  String get papyrus_98_found;

  /// No description provided for @papyrus_98_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the manuscript has not been assigned to any of Aland\'s established categories of New Testament manuscripts.'**
  String get papyrus_98_classification;

  /// No description provided for @papyrus_98_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Papyrus 98 is currently housed at the French Institute for Oriental Archaeology in Cairo, Egypt.'**
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
  /// **'Papyrus 115 is a fragmented Greek manuscript of the New Testament, written on papyrus, also known as Oxyrhynchus Papyrus #4499. It comprises 26 fragments of a codex containing portions of the Book of Revelation. The original pages measured approximately 15.5 × 23.5 cm.'**
  String get papyrus_115_material;

  /// No description provided for @papyrus_115_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in Greek uncial script, arranged in a single column per page with 33-36 lines. It follows scriptio continua style without word separation, and features occasional use of punctuation marks and abbreviations typical for biblical manuscripts of its period.'**
  String get papyrus_115_textStyle;

  /// No description provided for @papyrus_115_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered in Oxyrhynchus, Egypt, by scholars Bernard Pyne Grenfell and Arthur Hunt in the late 19th or early 20th century, although it was not deciphered and published until the end of the 20th century.'**
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
  /// **'The manuscript is written in a formal uncial script (biblical majuscule) in Greek, featuring scriptio continua (continuous script without spaces between words). The text is arranged in columns: four columns per page in the New Testament and two per page for poetic texts. It also includes carefully regulated line breaks, nomina sacra, and distinctive punctuation.'**
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
  /// **'The text is written in an elegant uncial script in Greek, arranged in two columns per page, with 49-51 lines per column and approximately 20-25 letters per line. It follows scriptio continua (without spaces), with red ink used for the initial lines of each book and decorative tailpieces at the end of each book. Occasional punctuation marks and annotations (e.g., enlarged initials indicating new sections) are present.'**
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
  /// **'The Codex Ephraemi Rescriptus is a palimpsest manuscript of the Greek Bible, written on parchment. It consists of 209 leaves, measuring approximately 33 x 27 cm, with 145 leaves belonging to the New Testament and 64 to the Old Testament.'**
  String get uncial_04_material;

  /// No description provided for @uncial_04_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in medium-sized uncial script in Greek, arranged in a single column per page with 40-46 lines per column. The codex follows scriptio continua without word separation, using only a single point for punctuation, and features enlarged letters at the beginning of sections protruding into the margin. The manuscript includes nomina sacra contracted into three-letter forms.'**
  String get uncial_04_textStyle;

  /// No description provided for @uncial_04_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was brought to Florence by an émigré scholar after the fall of Constantinople in 1453, and then transported to France in the 16th century by Catherine de\' Medici. The oldest biblical text was first noticed by Pierre Allix, a Protestant pastor, in the early 18th century. Various scholars occasionally made excerpts from the manuscript, but Tischendorf was the first to read it in its entirety in 1845.'**
  String get uncial_04_found;

  /// No description provided for @uncial_04_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the codex primarily represents the Alexandrian text-type, although its affiliation varies across different books of the New Testament. Kurt Aland classified it as a Category II manuscript in his New Testament manuscript text classification system.'**
  String get uncial_04_classification;

  /// No description provided for @uncial_04_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'The Codex Ephraemi Rescriptus is currently housed in the National Library of France in Paris.'**
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
  /// **'The Codex Porphyrianus is written on parchment and consists of 327 folios measuring approximately 16 × 13 cm. It is a palimpsest containing Euthalius\' commentary on Acts and Paul’s epistles alongside the biblical text.'**
  String get uncial_25_material;

  /// No description provided for @uncial_25_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in a Greek uncial script, arranged in a single column per page with 24 lines each, and incorporates breathings, accents, and apostrophes.'**
  String get uncial_25_textStyle;

  /// No description provided for @uncial_25_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered by Constantin von Tischendorf in 1862 in Saint Petersburg, Russia, in the possession of Archimandrite Porphyrius Uspensky. Tischendorf was allowed to take the manuscript to Leipzig to decipher its lower script.'**
  String get uncial_25_found;

  /// No description provided for @uncial_25_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the codex is a mixed manuscript; its text of the Pauline and General Epistles exhibits the characteristics of the Alexandrian text-type and is classified as Category III, while the text of Acts and Revelation follows the Byzantine tradition, placing it in Category V.'**
  String get uncial_25_classification;

  /// No description provided for @uncial_25_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Codex Porphyrianus is currently housed at the National Library of Russia in Saint Petersburg.'**
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
  /// **'Codex Vaticanus 2066 is written on parchment (vellum), typical of uncial manuscripts. The codex contains the complete text of the Book of Revelation on 20 parchment leaves, each measuring approximately 27.5 × 19 cm.'**
  String get uncial_46_material;

  /// No description provided for @uncial_46_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in one column per page, with 35 lines per page and approximately 36 letters per line. It is rendered in a formal uncial script using scriptio continua. The uncial letters are executed in a distinctive style – slightly inclined to the right – and occupy an intermediate form between square and oblong characters. The breathings and accents rendered with considerable accuracy.'**
  String get uncial_46_textStyle;

  /// No description provided for @uncial_46_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript once belonged to Philippo Vitali (1590-1653). The text of the codex was published by Cardinal Angelo Mai in 1859 in Rome.'**
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
  /// **'Uncial is written on parchment (vellum). It consists of 92 folios, each measuring approximately 23 × 18 cm. The manuscript contains an incomplete text of the Book of Revelation along with a commentary by Andreas of Caesarea.'**
  String get uncial_51_material;

  /// No description provided for @uncial_51_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is inscribed in uncial letters, arranged in a single column per page with 22 lines (the text block measuring 16.6 × 10.5 cm). The uncial letters are slightly inclined to the right, and a commentary is rendered in cursive script. The manuscript features breathings and accents.'**
  String get uncial_51_textStyle;

  /// No description provided for @uncial_51_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was brought to scholarly attention in 1899 when it was photographed by Kirsopp Lake at the Monastery of Pantokratoros on Mount Athos.'**
  String get uncial_51_found;

  /// No description provided for @uncial_51_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, uncial exhibits a mixed text-type and is classified as Category III among New Testament manuscripts.'**
  String get uncial_51_classification;

  /// No description provided for @uncial_51_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Today, Uncial 051 continues to be preserved at the Pantokratoros Monastery on Mount Athos, Greece.'**
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
  /// **'Codex Athous Panteleimon, also known as Uncial 052, is a Greek uncial manuscript of the New Testament. It contains a fragment of the Revelation with a commentary by Andreas of Caesarea, written on 4 parchment leaves, each measuring 29.5 × 23 cm.'**
  String get uncial_52_material;

  /// No description provided for @uncial_52_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text arranged in two columns per page with 27 lines per column. It features chapter divisions with numbers in the margins and titles at the top of the pages.'**
  String get uncial_52_textStyle;

  /// No description provided for @uncial_52_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered in the Panteleimon Monastery on Mount Athos in Greece and became known to scholars at least since the beginning of the 20th century.'**
  String get uncial_52_found;

  /// No description provided for @uncial_52_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the codex belongs to the Byzantine text-type. Aland classified it as Category V.'**
  String get uncial_52_classification;

  /// No description provided for @uncial_52_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Codex Athous Panteleimon (Uncial 052) continues to be preserved in the library of the Monastery of St. Panteleimon on Mount Athos, Greece.'**
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
  /// **'Uncial 0163, also known as Oxyrhynchus Manuscript #848, is a fragment of a parchment leaf measuring approximately 3 × 9 cm, on which text from the Book of Revelation is written on both sides. It is believed that the original dimensions of the leaf were only 10 × 9 cm.'**
  String get uncial_163_material;

  /// No description provided for @uncial_163_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in bold, upright Greek uncial letters arranged in a single column with 17 lines per page. Its calligraphic style is reminiscent of the Codex Alexandrinus.'**
  String get uncial_163_textStyle;

  /// No description provided for @uncial_163_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered in Oxyrhynchus, Egypt, by scholars Bernard Pyne Grenfell and Arthur Hunt in the late 19th or early 20th century. The fragment subsequently published in 1908.'**
  String get uncial_163_found;

  /// No description provided for @uncial_163_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the uncial belongs to the Alexandrian text-type and is classified as Category III among New Testament manuscripts.'**
  String get uncial_163_classification;

  /// No description provided for @uncial_163_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Uncial 0169 currently is housed at the Institute for the Study of Ancient Cultures in Chicago, USA.'**
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
  /// **'Uncial 0169, also known as the Princeton fragment or Oxyrhynchus Manuscript #1080, is a Greek uncial manuscript written on parchment (vellum). It consists of a single, nearly complete leaf measuring 9.3 × 7.7 cm, containing two pages numbered 33 and 34, with small portions of the Book of Revelation.'**
  String get uncial_169_material;

  /// No description provided for @uncial_169_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in a fair-sized upright uncial script, fairly regular with some ornamental finish, arranged in one column with 14 lines per page, and follows scriptio continua (continuous writing without spaces).'**
  String get uncial_169_textStyle;

  /// No description provided for @uncial_169_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered in Oxyrhynchus, Egypt, by scholars Bernard Pyne Grenfell and Arthur Hunt in the late 19th or early 20th century. The fragment subsequently published in 1911.'**
  String get uncial_169_found;

  /// No description provided for @uncial_169_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the uncial belongs to the Alexandrian text-type and is classified as Category III among New Testament manuscripts.'**
  String get uncial_169_classification;

  /// No description provided for @uncial_169_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Today, Uncial 0169 is housed in the library of Princeton Theological Seminary in Princeton, USA.'**
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
  /// **'Uncial 0207 is a Greek uncial manuscript of the New Testament. It consists of a single parchment leaf measuring 19 × 15 cm, containing a small portion of the Book of Revelation.'**
  String get uncial_207_material;

  /// No description provided for @uncial_207_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in small uncial Greek letters, arranged in two columns per page with 29 lines per column. It follows the scriptio continua style (without spaces between words). The leaf is paginated with the number 478, indicating it was part of a larger codex.'**
  String get uncial_207_textStyle;

  /// No description provided for @uncial_207_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered in Egypt and was added to the list of New Testament manuscripts by Ernst von Dobschütz in 1933.'**
  String get uncial_207_found;

  /// No description provided for @uncial_207_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the uncial belongs to the Alexandrian text-type and is classified as Category III among New Testament manuscripts.'**
  String get uncial_207_classification;

  /// No description provided for @uncial_207_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Uncial 0207 is currently housed at the Laurentian Library in Florence, Italy.'**
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
  /// **'Uncial 0229 is a Greek uncial manuscript of the New Testament, containing a small portion of the Book of Revelation. It is a palimpsest, with the lower text written in Coptic, featuring a calendrical text listing the Egyptian months. The manuscript consists of two parchment leaves, each measuring approximately 11 × 23 см.'**
  String get uncial_229_material;

  /// No description provided for @uncial_229_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in small uncial Greek letters, arranged in a single column per page with 16 lines per column. It follows the scriptio continua style (without spaces between words).'**
  String get uncial_229_textStyle;

  /// No description provided for @uncial_229_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered in Antinoopolis (El-Sheikh Ibada) in Egypt during excavations conducted by Evaristo Breccia in 1937.'**
  String get uncial_229_found;

  /// No description provided for @uncial_229_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, the primary source is classified as a mixed text-type manuscript and is categorized as Category III among New Testament manuscripts.'**
  String get uncial_229_classification;

  /// No description provided for @uncial_229_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Today, Uncial 0229 is housed at the Girolamo Vitelli Papyrological Institute in Florence, Italy.'**
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
  /// **'Uncial 0308, also known as Oxyrhynchus Manuscript #4500, is a fragment of a parchment leaf measuring approximately 5 × 6 cm, on which text from the Book of Revelation is written on both sides. It is believed that the original dimensions of the leaf were only 8 × 8 cm.'**
  String get uncial_308_material;

  /// No description provided for @uncial_308_textStyle.
  ///
  /// In en, this message translates to:
  /// **'The text is written in a mannered, clear, seriffed, round uncial script in Greek, arranged in one column with 14 lines per page. The scribe used carbon ink, wrote with bilinear letters without rulings or prickings, employing nomina sacra and a cipher for numbers.'**
  String get uncial_308_textStyle;

  /// No description provided for @uncial_308_found.
  ///
  /// In en, this message translates to:
  /// **'The manuscript was discovered in Oxyrhynchus, Egypt, by scholars Bernard Pyne Grenfell and Arthur Hunt in the late 19th or early 20th century, although it was not deciphered and published until the end of the 20th century.'**
  String get uncial_308_found;

  /// No description provided for @uncial_308_classification.
  ///
  /// In en, this message translates to:
  /// **'From a textological perspective, uncial exhibits strong affinities with the Alexandrian text-type – showing notable agreement with Codex Sinaiticus and Papyrus 47 – although its fragmentary nature prevents a definitive classification.'**
  String get uncial_308_classification;

  /// No description provided for @uncial_308_currentLocation.
  ///
  /// In en, this message translates to:
  /// **'Uncial 0308 is currently housed in the Sackler Library at Oxford University, United Kingdom.'**
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
