import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_es.dart';
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
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

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
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('es'),
    Locale('ru'),
    Locale('uk'),
  ];

  /// No description provided for @app_name.
  ///
  /// In en, this message translates to:
  /// **'Revelation'**
  String get app_name;

  /// No description provided for @startup_title.
  ///
  /// In en, this message translates to:
  /// **'Launching the app...'**
  String get startup_title;

  /// No description provided for @startup_step_preparing.
  ///
  /// In en, this message translates to:
  /// **'Preparing the app'**
  String get startup_step_preparing;

  /// No description provided for @startup_step_loading_settings.
  ///
  /// In en, this message translates to:
  /// **'Loading your settings'**
  String get startup_step_loading_settings;

  /// No description provided for @startup_step_initializing_server.
  ///
  /// In en, this message translates to:
  /// **'Connecting to online services'**
  String get startup_step_initializing_server;

  /// No description provided for @startup_step_initializing_databases.
  ///
  /// In en, this message translates to:
  /// **'Opening app data'**
  String get startup_step_initializing_databases;

  /// No description provided for @startup_step_configuring_links.
  ///
  /// In en, this message translates to:
  /// **'Preparing Strong’s dictionary'**
  String get startup_step_configuring_links;

  /// Shows the current startup step number out of the total
  ///
  /// In en, this message translates to:
  /// **'Step {current} of {total}'**
  String startup_progress(int current, int total);

  /// No description provided for @startup_error.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t start the app :('**
  String get startup_error;

  /// No description provided for @startup_retry.
  ///
  /// In en, this message translates to:
  /// **'Try again'**
  String get startup_retry;

  /// App version and build number shown on the startup screen
  ///
  /// In en, this message translates to:
  /// **'Version {version} ({build})'**
  String startup_version_build(String version, String build);

  /// No description provided for @version.
  ///
  /// In en, this message translates to:
  /// **'App version:'**
  String get version;

  /// No description provided for @app_version_from.
  ///
  /// In en, this message translates to:
  /// **'App version from'**
  String get app_version_from;

  /// No description provided for @common_data_update.
  ///
  /// In en, this message translates to:
  /// **'Data version'**
  String get common_data_update;

  /// Label for localized DB data version by language
  ///
  /// In en, this message translates to:
  /// **'Data version in {language}'**
  String localized_data_update(String language);

  /// No description provided for @data_version_from.
  ///
  /// In en, this message translates to:
  /// **'from'**
  String get data_version_from;

  /// No description provided for @language_name_en.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get language_name_en;

  /// No description provided for @language_name_es.
  ///
  /// In en, this message translates to:
  /// **'Spanish'**
  String get language_name_es;

  /// No description provided for @language_name_uk.
  ///
  /// In en, this message translates to:
  /// **'Ukrainian'**
  String get language_name_uk;

  /// No description provided for @language_name_ru.
  ///
  /// In en, this message translates to:
  /// **'Russian'**
  String get language_name_ru;

  /// No description provided for @app_description.
  ///
  /// In en, this message translates to:
  /// **'Revelation Study app.'**
  String get app_description;

  /// No description provided for @website.
  ///
  /// In en, this message translates to:
  /// **'Revelation.website'**
  String get website;

  /// No description provided for @github_project.
  ///
  /// In en, this message translates to:
  /// **'GitHub project'**
  String get github_project;

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

  /// No description provided for @support_us.
  ///
  /// In en, this message translates to:
  /// **'Support us'**
  String get support_us;

  /// No description provided for @installation_packages.
  ///
  /// In en, this message translates to:
  /// **'Installation packages'**
  String get installation_packages;

  /// No description provided for @acknowledgements_title.
  ///
  /// In en, this message translates to:
  /// **'Acknowledgments'**
  String get acknowledgements_title;

  /// No description provided for @acknowledgements_description_1.
  ///
  /// In en, this message translates to:
  /// **'First and foremost, I would like to thank God for life; my wife, Ira, for her love and care; and my mother for her help and support.\nAlso, my sincere gratitude goes to the institutions that provided access to information and invaluable manuscripts:'**
  String get acknowledgements_description_1;

  /// No description provided for @acknowledgements_description_2.
  ///
  /// In en, this message translates to:
  /// **'Many thanks to the creators of the following software and resources:'**
  String get acknowledgements_description_2;

  /// No description provided for @recommended_title.
  ///
  /// In en, this message translates to:
  /// **'Recommended'**
  String get recommended_title;

  /// No description provided for @recommended_description.
  ///
  /// In en, this message translates to:
  /// **'Recommended resources for studying Revelation and the Bible as a whole:'**
  String get recommended_description;

  /// No description provided for @bug_report.
  ///
  /// In en, this message translates to:
  /// **'Report a bug'**
  String get bug_report;

  /// No description provided for @log_copied_message.
  ///
  /// In en, this message translates to:
  /// **'Logs have been copied to the clipboard. Please send them to me at:'**
  String get log_copied_message;

  /// No description provided for @bug_report_wish.
  ///
  /// In en, this message translates to:
  /// **'Please briefly describe the error and paste into the email the technical information that the application has just automatically copied to the clipboard (this is important!). If possible, attach a screenshot to your message. Thank you, you’re helping make the app better.'**
  String get bug_report_wish;

  /// No description provided for @all_rights_reserved.
  ///
  /// In en, this message translates to:
  /// **'All rights reserved'**
  String get all_rights_reserved;

  /// No description provided for @ad_loading.
  ///
  /// In en, this message translates to:
  /// **'Ad Loading...'**
  String get ad_loading;

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

  /// No description provided for @settings_header.
  ///
  /// In en, this message translates to:
  /// **'Saving automatically'**
  String get settings_header;

  /// No description provided for @about_screen.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about_screen;

  /// No description provided for @about_header.
  ///
  /// In en, this message translates to:
  /// **'General Information About the Application'**
  String get about_header;

  /// No description provided for @download.
  ///
  /// In en, this message translates to:
  /// **'Download'**
  String get download;

  /// No description provided for @download_header.
  ///
  /// In en, this message translates to:
  /// **'Install the application for your platform'**
  String get download_header;

  /// No description provided for @download_android.
  ///
  /// In en, this message translates to:
  /// **'Android'**
  String get download_android;

  /// No description provided for @download_windows.
  ///
  /// In en, this message translates to:
  /// **'Windows'**
  String get download_windows;

  /// No description provided for @download_linux.
  ///
  /// In en, this message translates to:
  /// **'Linux'**
  String get download_linux;

  /// No description provided for @download_google_play.
  ///
  /// In en, this message translates to:
  /// **'Google Play'**
  String get download_google_play;

  /// No description provided for @download_microsoft_store.
  ///
  /// In en, this message translates to:
  /// **'Microsoft Store'**
  String get download_microsoft_store;

  /// No description provided for @download_snapcraft.
  ///
  /// In en, this message translates to:
  /// **'Snapcraft'**
  String get download_snapcraft;

  /// No description provided for @file_saved_at.
  ///
  /// In en, this message translates to:
  /// **'Saved: {path}'**
  String file_saved_at(Object path);

  /// No description provided for @error_loading_libraries.
  ///
  /// In en, this message translates to:
  /// **'Error loading libraries'**
  String get error_loading_libraries;

  /// No description provided for @error_loading_institutions.
  ///
  /// In en, this message translates to:
  /// **'Error loading institutions'**
  String get error_loading_institutions;

  /// No description provided for @error_loading_recommendations.
  ///
  /// In en, this message translates to:
  /// **'Error loading recommendations'**
  String get error_loading_recommendations;

  /// No description provided for @error_loading_topics.
  ///
  /// In en, this message translates to:
  /// **'Error loading topics'**
  String get error_loading_topics;

  /// No description provided for @error_loading_primary_sources.
  ///
  /// In en, this message translates to:
  /// **'Error loading primary sources'**
  String get error_loading_primary_sources;

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

  /// No description provided for @color_theme.
  ///
  /// In en, this message translates to:
  /// **'Color theme'**
  String get color_theme;

  /// No description provided for @manuscript_color_theme.
  ///
  /// In en, this message translates to:
  /// **'Manuscript'**
  String get manuscript_color_theme;

  /// No description provided for @forest_color_theme.
  ///
  /// In en, this message translates to:
  /// **'Forest'**
  String get forest_color_theme;

  /// No description provided for @sky_color_theme.
  ///
  /// In en, this message translates to:
  /// **'Sky'**
  String get sky_color_theme;

  /// No description provided for @grape_color_theme.
  ///
  /// In en, this message translates to:
  /// **'Grape'**
  String get grape_color_theme;

  /// No description provided for @font_size.
  ///
  /// In en, this message translates to:
  /// **'Font size'**
  String get font_size;

  /// No description provided for @small_font_size.
  ///
  /// In en, this message translates to:
  /// **'Small'**
  String get small_font_size;

  /// No description provided for @medium_font_size.
  ///
  /// In en, this message translates to:
  /// **'Medium'**
  String get medium_font_size;

  /// No description provided for @large_font_size.
  ///
  /// In en, this message translates to:
  /// **'Large'**
  String get large_font_size;

  /// No description provided for @sound.
  ///
  /// In en, this message translates to:
  /// **'Sound'**
  String get sound;

  /// No description provided for @on.
  ///
  /// In en, this message translates to:
  /// **'On'**
  String get on;

  /// No description provided for @off.
  ///
  /// In en, this message translates to:
  /// **'Off'**
  String get off;

  /// No description provided for @vectors.
  ///
  /// In en, this message translates to:
  /// **'Vectors'**
  String get vectors;

  /// No description provided for @icons.
  ///
  /// In en, this message translates to:
  /// **'Icons'**
  String get icons;

  /// No description provided for @and.
  ///
  /// In en, this message translates to:
  /// **'and'**
  String get and;

  /// No description provided for @by.
  ///
  /// In en, this message translates to:
  /// **'by'**
  String get by;

  /// No description provided for @strongsConcordance.
  ///
  /// In en, this message translates to:
  /// **'Strong\'s Concordance'**
  String get strongsConcordance;

  /// No description provided for @package.
  ///
  /// In en, this message translates to:
  /// **'Package'**
  String get package;

  /// No description provided for @font.
  ///
  /// In en, this message translates to:
  /// **'Font'**
  String get font;

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

  /// No description provided for @image_source.
  ///
  /// In en, this message translates to:
  /// **'Image source'**
  String get image_source;

  /// No description provided for @topic.
  ///
  /// In en, this message translates to:
  /// **'Topic'**
  String get topic;

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

  /// No description provided for @primary_source_word_source_unavailable.
  ///
  /// In en, this message translates to:
  /// **'Primary source unavailable'**
  String get primary_source_word_source_unavailable;

  /// No description provided for @primary_source_word_page_unavailable.
  ///
  /// In en, this message translates to:
  /// **'Page unavailable'**
  String get primary_source_word_page_unavailable;

  /// No description provided for @primary_source_word_word_unavailable.
  ///
  /// In en, this message translates to:
  /// **'Word unavailable'**
  String get primary_source_word_word_unavailable;

  /// No description provided for @primary_source_word_image_unavailable.
  ///
  /// In en, this message translates to:
  /// **'Image unavailable'**
  String get primary_source_word_image_unavailable;

  /// No description provided for @primary_source_words_image_hint.
  ///
  /// In en, this message translates to:
  /// **'Tap the image to see the word in the primary source.'**
  String get primary_source_words_image_hint;

  /// No description provided for @click_for_info.
  ///
  /// In en, this message translates to:
  /// **'Click on the image element you’re interested in to get information about it.'**
  String get click_for_info;

  /// No description provided for @low_quality.
  ///
  /// In en, this message translates to:
  /// **'Quality reduced'**
  String get low_quality;

  /// No description provided for @low_quality_message.
  ///
  /// In en, this message translates to:
  /// **'A lower-quality image is used in the mobile browser. To view in maximum quality, install the app or open the page on a computer.'**
  String get low_quality_message;

  /// No description provided for @reload_image.
  ///
  /// In en, this message translates to:
  /// **'Reloading the image'**
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

  /// No description provided for @toggle_negative.
  ///
  /// In en, this message translates to:
  /// **'Negative'**
  String get toggle_negative;

  /// No description provided for @toggle_monochrome.
  ///
  /// In en, this message translates to:
  /// **'Monochrome'**
  String get toggle_monochrome;

  /// No description provided for @brightness_contrast.
  ///
  /// In en, this message translates to:
  /// **'Brightness, Contrast'**
  String get brightness_contrast;

  /// No description provided for @brightness.
  ///
  /// In en, this message translates to:
  /// **'Brightness'**
  String get brightness;

  /// No description provided for @contrast.
  ///
  /// In en, this message translates to:
  /// **'Contrast'**
  String get contrast;

  /// No description provided for @ok.
  ///
  /// In en, this message translates to:
  /// **'OK'**
  String get ok;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Сancel'**
  String get cancel;

  /// No description provided for @reset.
  ///
  /// In en, this message translates to:
  /// **'Reset'**
  String get reset;

  /// No description provided for @area.
  ///
  /// In en, this message translates to:
  /// **'Area'**
  String get area;

  /// No description provided for @size.
  ///
  /// In en, this message translates to:
  /// **'Size'**
  String get size;

  /// No description provided for @not_selected.
  ///
  /// In en, this message translates to:
  /// **'Not selected'**
  String get not_selected;

  /// No description provided for @area_selection.
  ///
  /// In en, this message translates to:
  /// **'Area selection'**
  String get area_selection;

  /// No description provided for @color_replacement.
  ///
  /// In en, this message translates to:
  /// **'Color replacement'**
  String get color_replacement;

  /// No description provided for @color_to_replace.
  ///
  /// In en, this message translates to:
  /// **'Color to replace'**
  String get color_to_replace;

  /// No description provided for @eyedropper.
  ///
  /// In en, this message translates to:
  /// **'Color selection'**
  String get eyedropper;

  /// No description provided for @new_color.
  ///
  /// In en, this message translates to:
  /// **'New color'**
  String get new_color;

  /// No description provided for @palette.
  ///
  /// In en, this message translates to:
  /// **'Palette'**
  String get palette;

  /// No description provided for @select_color.
  ///
  /// In en, this message translates to:
  /// **'Select color'**
  String get select_color;

  /// No description provided for @select_area_header.
  ///
  /// In en, this message translates to:
  /// **'Select an area on the image'**
  String get select_area_header;

  /// No description provided for @select_area_description.
  ///
  /// In en, this message translates to:
  /// **'Select a rectangular area on the image: touch the starting point, drag, and release. You can zoom in if needed.'**
  String get select_area_description;

  /// No description provided for @pick_color_header.
  ///
  /// In en, this message translates to:
  /// **'Select a point on the image'**
  String get pick_color_header;

  /// No description provided for @pick_color_description.
  ///
  /// In en, this message translates to:
  /// **'Click on the area of the image where you want to pick a color. You can zoom in and move the image if needed.'**
  String get pick_color_description;

  /// No description provided for @tolerance.
  ///
  /// In en, this message translates to:
  /// **'Tolerance'**
  String get tolerance;

  /// No description provided for @replace_color_message.
  ///
  /// In en, this message translates to:
  /// **'On the first call, generating the pixel matrix will take some time.'**
  String get replace_color_message;

  /// No description provided for @page_settings_reset.
  ///
  /// In en, this message translates to:
  /// **'Page settings reset'**
  String get page_settings_reset;

  /// No description provided for @toggle_show_word_separators.
  ///
  /// In en, this message translates to:
  /// **'Word separators'**
  String get toggle_show_word_separators;

  /// No description provided for @toggle_show_strong_numbers.
  ///
  /// In en, this message translates to:
  /// **'Strong\'s numbers'**
  String get toggle_show_strong_numbers;

  /// No description provided for @toggle_show_verse_numbers.
  ///
  /// In en, this message translates to:
  /// **'Verse numbers'**
  String get toggle_show_verse_numbers;

  /// No description provided for @strong_number.
  ///
  /// In en, this message translates to:
  /// **'Strong’s number'**
  String get strong_number;

  /// No description provided for @strong_picker_unavailable_numbers.
  ///
  /// In en, this message translates to:
  /// **'2717 and 3203-3302 are unavailable'**
  String get strong_picker_unavailable_numbers;

  /// No description provided for @strong_pronunciation.
  ///
  /// In en, this message translates to:
  /// **'Pronunciation'**
  String get strong_pronunciation;

  /// No description provided for @strong_synonyms.
  ///
  /// In en, this message translates to:
  /// **'Synonyms'**
  String get strong_synonyms;

  /// No description provided for @strong_origin.
  ///
  /// In en, this message translates to:
  /// **'Word analysis'**
  String get strong_origin;

  /// No description provided for @strong_usage.
  ///
  /// In en, this message translates to:
  /// **'Usage'**
  String get strong_usage;

  /// No description provided for @strong_reference_commentary.
  ///
  /// In en, this message translates to:
  /// **'Translation source: https://github.com/openscriptures/strongs'**
  String get strong_reference_commentary;

  /// No description provided for @strong_origin_tooltip.
  ///
  /// In en, this message translates to:
  /// **'Word analysis may include the following elements: derivatives, comparative words, phrases, and related words.'**
  String get strong_origin_tooltip;

  /// No description provided for @strong_part_of_speech.
  ///
  /// In en, this message translates to:
  /// **'Part of speech'**
  String get strong_part_of_speech;

  /// No description provided for @strong_indeclNumAdj.
  ///
  /// In en, this message translates to:
  /// **'indeclinable numeral (adjective)'**
  String get strong_indeclNumAdj;

  /// No description provided for @strong_indeclLetN.
  ///
  /// In en, this message translates to:
  /// **'indeclinable letter (noun)'**
  String get strong_indeclLetN;

  /// No description provided for @strong_indeclinable.
  ///
  /// In en, this message translates to:
  /// **'indeclinable'**
  String get strong_indeclinable;

  /// No description provided for @strong_adj.
  ///
  /// In en, this message translates to:
  /// **'adjective'**
  String get strong_adj;

  /// No description provided for @strong_advCor.
  ///
  /// In en, this message translates to:
  /// **'adverb, correlative'**
  String get strong_advCor;

  /// No description provided for @strong_advInt.
  ///
  /// In en, this message translates to:
  /// **'adverb, interrogative'**
  String get strong_advInt;

  /// No description provided for @strong_advNeg.
  ///
  /// In en, this message translates to:
  /// **'adverb, negative'**
  String get strong_advNeg;

  /// No description provided for @strong_advSup.
  ///
  /// In en, this message translates to:
  /// **'adverb, superlative'**
  String get strong_advSup;

  /// No description provided for @strong_adv.
  ///
  /// In en, this message translates to:
  /// **'adverb'**
  String get strong_adv;

  /// No description provided for @strong_comp.
  ///
  /// In en, this message translates to:
  /// **'comparative'**
  String get strong_comp;

  /// No description provided for @strong_aramaicTransWord.
  ///
  /// In en, this message translates to:
  /// **'aramaic transliterated word'**
  String get strong_aramaicTransWord;

  /// No description provided for @strong_hebrewForm.
  ///
  /// In en, this message translates to:
  /// **'hebrew form'**
  String get strong_hebrewForm;

  /// No description provided for @strong_hebrewNoun.
  ///
  /// In en, this message translates to:
  /// **'hebrew noun'**
  String get strong_hebrewNoun;

  /// No description provided for @strong_hebrew.
  ///
  /// In en, this message translates to:
  /// **'hebrew'**
  String get strong_hebrew;

  /// No description provided for @strong_location.
  ///
  /// In en, this message translates to:
  /// **'location'**
  String get strong_location;

  /// No description provided for @strong_properNoun.
  ///
  /// In en, this message translates to:
  /// **'proper noun'**
  String get strong_properNoun;

  /// No description provided for @strong_noun.
  ///
  /// In en, this message translates to:
  /// **'noun'**
  String get strong_noun;

  /// No description provided for @strong_masc.
  ///
  /// In en, this message translates to:
  /// **'masculine'**
  String get strong_masc;

  /// No description provided for @strong_fem.
  ///
  /// In en, this message translates to:
  /// **'feminine'**
  String get strong_fem;

  /// No description provided for @strong_neut.
  ///
  /// In en, this message translates to:
  /// **'neuter'**
  String get strong_neut;

  /// No description provided for @strong_plur.
  ///
  /// In en, this message translates to:
  /// **'plural'**
  String get strong_plur;

  /// No description provided for @strong_otherType.
  ///
  /// In en, this message translates to:
  /// **'other Type'**
  String get strong_otherType;

  /// No description provided for @strong_verbImp.
  ///
  /// In en, this message translates to:
  /// **'verb (imperative)'**
  String get strong_verbImp;

  /// No description provided for @strong_verb.
  ///
  /// In en, this message translates to:
  /// **'verb'**
  String get strong_verb;

  /// No description provided for @strong_pronDat.
  ///
  /// In en, this message translates to:
  /// **'pronoun, dative case'**
  String get strong_pronDat;

  /// No description provided for @strong_pronPoss.
  ///
  /// In en, this message translates to:
  /// **'possessive pronoun'**
  String get strong_pronPoss;

  /// No description provided for @strong_pronPers.
  ///
  /// In en, this message translates to:
  /// **'personal pronoun'**
  String get strong_pronPers;

  /// No description provided for @strong_pronRecip.
  ///
  /// In en, this message translates to:
  /// **'reciprocal pronoun'**
  String get strong_pronRecip;

  /// No description provided for @strong_pronRefl.
  ///
  /// In en, this message translates to:
  /// **'reflexive pronoun'**
  String get strong_pronRefl;

  /// No description provided for @strong_pronRel.
  ///
  /// In en, this message translates to:
  /// **'relative pronoun'**
  String get strong_pronRel;

  /// No description provided for @strong_pronCorrel.
  ///
  /// In en, this message translates to:
  /// **'correlative pronoun'**
  String get strong_pronCorrel;

  /// No description provided for @strong_pronIndef.
  ///
  /// In en, this message translates to:
  /// **'indefinite pronoun'**
  String get strong_pronIndef;

  /// No description provided for @strong_pronInterr.
  ///
  /// In en, this message translates to:
  /// **'interrogative pronoun'**
  String get strong_pronInterr;

  /// No description provided for @strong_pronDem.
  ///
  /// In en, this message translates to:
  /// **'demonstrative pronoun'**
  String get strong_pronDem;

  /// No description provided for @strong_pron.
  ///
  /// In en, this message translates to:
  /// **'pronoun'**
  String get strong_pron;

  /// No description provided for @strong_particleCond.
  ///
  /// In en, this message translates to:
  /// **'conditional particle'**
  String get strong_particleCond;

  /// No description provided for @strong_particleDisj.
  ///
  /// In en, this message translates to:
  /// **'disjunctive particle'**
  String get strong_particleDisj;

  /// No description provided for @strong_particleInterr.
  ///
  /// In en, this message translates to:
  /// **'interrogative particle'**
  String get strong_particleInterr;

  /// No description provided for @strong_particleNeg.
  ///
  /// In en, this message translates to:
  /// **'negative particle'**
  String get strong_particleNeg;

  /// No description provided for @strong_particle.
  ///
  /// In en, this message translates to:
  /// **'particle'**
  String get strong_particle;

  /// No description provided for @strong_interj.
  ///
  /// In en, this message translates to:
  /// **'interjection'**
  String get strong_interj;

  /// No description provided for @strong_participle.
  ///
  /// In en, this message translates to:
  /// **'participle'**
  String get strong_participle;

  /// No description provided for @strong_prefix.
  ///
  /// In en, this message translates to:
  /// **'prefix'**
  String get strong_prefix;

  /// No description provided for @strong_prep.
  ///
  /// In en, this message translates to:
  /// **'preposition'**
  String get strong_prep;

  /// No description provided for @strong_artDef.
  ///
  /// In en, this message translates to:
  /// **'definite article'**
  String get strong_artDef;

  /// No description provided for @strong_phraseIdi.
  ///
  /// In en, this message translates to:
  /// **'phrase (idiomatic expression)'**
  String get strong_phraseIdi;

  /// No description provided for @strong_phrase.
  ///
  /// In en, this message translates to:
  /// **'phrase'**
  String get strong_phrase;

  /// No description provided for @strong_conjNeg.
  ///
  /// In en, this message translates to:
  /// **'negative conjunction'**
  String get strong_conjNeg;

  /// No description provided for @strong_conj.
  ///
  /// In en, this message translates to:
  /// **'conjunction'**
  String get strong_conj;

  /// No description provided for @strong_or.
  ///
  /// In en, this message translates to:
  /// **'or'**
  String get strong_or;

  /// No description provided for @markdown_unknown_block_title.
  ///
  /// In en, this message translates to:
  /// **'Unsupported content block'**
  String get markdown_unknown_block_title;

  /// Explains that the current app build does not support a custom markdown block
  ///
  /// In en, this message translates to:
  /// **'This version of the app cannot display the `{blockName}` block.'**
  String markdown_unknown_block_description(String blockName);

  /// No description provided for @markdown_unknown_block_update_hint.
  ///
  /// In en, this message translates to:
  /// **'Open the downloads page to install a newer app version for your platform.'**
  String get markdown_unknown_block_update_hint;

  /// No description provided for @markdown_unknown_block_update_action.
  ///
  /// In en, this message translates to:
  /// **'Update app'**
  String get markdown_unknown_block_update_action;

  /// No description provided for @markdown_youtube_player_title.
  ///
  /// In en, this message translates to:
  /// **'Embedded YouTube video'**
  String get markdown_youtube_player_title;

  /// No description provided for @markdown_youtube_unavailable_title.
  ///
  /// In en, this message translates to:
  /// **'YouTube video unavailable'**
  String get markdown_youtube_unavailable_title;

  /// No description provided for @markdown_youtube_unavailable_description.
  ///
  /// In en, this message translates to:
  /// **'This YouTube block could not be rendered in the embedded player.'**
  String get markdown_youtube_unavailable_description;

  /// No description provided for @markdown_image_loading.
  ///
  /// In en, this message translates to:
  /// **'Loading image...'**
  String get markdown_image_loading;

  /// No description provided for @copy_content.
  ///
  /// In en, this message translates to:
  /// **'Copy content'**
  String get copy_content;

  /// No description provided for @export_pdf_content.
  ///
  /// In en, this message translates to:
  /// **'Export to PDF'**
  String get export_pdf_content;

  /// No description provided for @markdown_copied.
  ///
  /// In en, this message translates to:
  /// **'Content copied to the clipboard.'**
  String get markdown_copied;

  /// No description provided for @markdown_copy_failed.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t copy the content.'**
  String get markdown_copy_failed;

  /// No description provided for @markdown_pdf_export_failed.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t export the PDF.'**
  String get markdown_pdf_export_failed;

  /// No description provided for @previous_description_item.
  ///
  /// In en, this message translates to:
  /// **'Previous item'**
  String get previous_description_item;

  /// No description provided for @next_description_item.
  ///
  /// In en, this message translates to:
  /// **'Next item'**
  String get next_description_item;

  /// No description provided for @previous_word.
  ///
  /// In en, this message translates to:
  /// **'Previous word'**
  String get previous_word;

  /// No description provided for @next_word.
  ///
  /// In en, this message translates to:
  /// **'Next word'**
  String get next_word;

  /// No description provided for @previous_verse.
  ///
  /// In en, this message translates to:
  /// **'Previous verse'**
  String get previous_verse;

  /// No description provided for @next_verse.
  ///
  /// In en, this message translates to:
  /// **'Next verse'**
  String get next_verse;

  /// No description provided for @previous_dictionary_entry.
  ///
  /// In en, this message translates to:
  /// **'Previous dictionary entry'**
  String get previous_dictionary_entry;

  /// No description provided for @next_dictionary_entry.
  ///
  /// In en, this message translates to:
  /// **'Next dictionary entry'**
  String get next_dictionary_entry;

  /// Progress label for markdown image preloading in topic articles
  ///
  /// In en, this message translates to:
  /// **'Loading images: {loaded} of {total}'**
  String markdown_images_loading_progress(int loaded, int total);
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'es', 'ru', 'uk'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'es':
      return AppLocalizationsEs();
    case 'ru':
      return AppLocalizationsRu();
    case 'uk':
      return AppLocalizationsUk();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
