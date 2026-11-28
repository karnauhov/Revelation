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

  /// Default bookmark title, numbered in the order the user creates numbered bookmarks.
  ///
  /// In en, this message translates to:
  /// **'Bookmark {number}'**
  String bible_bookmark_default_name(String number);

  /// Title of the Bible bookmarks list.
  ///
  /// In en, this message translates to:
  /// **'Bookmarks'**
  String get bible_bookmarks;

  /// Explains where Bible bookmarks are stored in the bookmarks dialog.
  ///
  /// In en, this message translates to:
  /// **'Revelation stores your bookmarks only on this device.'**
  String get bible_bookmarks_local_storage;

  /// Empty state of the Bible bookmarks list.
  ///
  /// In en, this message translates to:
  /// **'No bookmarks yet.'**
  String get bible_bookmarks_empty;

  /// Error shown when the Bible bookmarks list could not be loaded.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t load bookmarks.'**
  String get bible_bookmarks_load_failed;

  /// Error shown when a Bible bookmark change could not be saved.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t save the change. Try again.'**
  String get bible_bookmarks_save_failed;

  /// Action and dialog title for bookmarking a Bible verse.
  ///
  /// In en, this message translates to:
  /// **'Add bookmark'**
  String get bible_bookmark_add;

  /// Action and dialog title for editing an existing Bible bookmark.
  ///
  /// In en, this message translates to:
  /// **'Edit bookmark'**
  String get bible_bookmark_edit;

  /// Delete action for a Bible bookmark, also used for confirmation.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get bible_bookmark_delete;

  /// Confirmation prompt before deleting a Bible bookmark.
  ///
  /// In en, this message translates to:
  /// **'Delete bookmark?'**
  String get bible_bookmark_delete_confirm;

  /// Label of the bookmark name field.
  ///
  /// In en, this message translates to:
  /// **'Name'**
  String get bible_bookmark_name;

  /// Validation message for an empty bookmark name.
  ///
  /// In en, this message translates to:
  /// **'Enter a bookmark name.'**
  String get bible_bookmark_name_required;

  /// Label of the bookmark color selector.
  ///
  /// In en, this message translates to:
  /// **'Color'**
  String get bible_bookmark_color;

  /// Action to save the bookmark editor.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get bible_bookmark_save;

  /// Accessible label for the blue bookmark color.
  ///
  /// In en, this message translates to:
  /// **'Blue'**
  String get bible_bookmark_blue;

  /// Accessible label for the green bookmark color.
  ///
  /// In en, this message translates to:
  /// **'Green'**
  String get bible_bookmark_green;

  /// Accessible label for the amber bookmark color.
  ///
  /// In en, this message translates to:
  /// **'Amber'**
  String get bible_bookmark_amber;

  /// Accessible label for the red bookmark color.
  ///
  /// In en, this message translates to:
  /// **'Red'**
  String get bible_bookmark_red;

  /// Accessible label for the violet bookmark color.
  ///
  /// In en, this message translates to:
  /// **'Violet'**
  String get bible_bookmark_violet;

  /// Public name of the Revelation app.
  ///
  /// In en, this message translates to:
  /// **'Revelation'**
  String get app_name;

  /// Heading of the startup screen while the application initializes.
  ///
  /// In en, this message translates to:
  /// **'Launching the app...'**
  String get startup_title;

  /// Startup status while preparing the application.
  ///
  /// In en, this message translates to:
  /// **'Preparing the app'**
  String get startup_step_preparing;

  /// Startup status while loading saved settings.
  ///
  /// In en, this message translates to:
  /// **'Loading your settings'**
  String get startup_step_loading_settings;

  /// Startup status while configuring the connection to online services.
  ///
  /// In en, this message translates to:
  /// **'Connecting to online services'**
  String get startup_step_initializing_server;

  /// Startup status while opening the local application databases.
  ///
  /// In en, this message translates to:
  /// **'Opening app data'**
  String get startup_step_initializing_databases;

  /// Startup status while configuring Strong's dictionary links.
  ///
  /// In en, this message translates to:
  /// **'Preparing Strong’s dictionary'**
  String get startup_step_configuring_links;

  /// Shows the current startup step number out of the total
  ///
  /// In en, this message translates to:
  /// **'Step {current} of {total}'**
  String startup_progress(int current, int total);

  /// Heading of the startup failure state.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t start the app :('**
  String get startup_error;

  /// Action to retry initialization after a startup failure.
  ///
  /// In en, this message translates to:
  /// **'Try again'**
  String get startup_retry;

  /// App version and build number shown on the startup screen
  ///
  /// In en, this message translates to:
  /// **'Version {version} ({build})'**
  String startup_version_build(String version, String build);

  /// Label before the application version number.
  ///
  /// In en, this message translates to:
  /// **'App version:'**
  String get version;

  /// Label before the application build date on the About page.
  ///
  /// In en, this message translates to:
  /// **'App version from'**
  String get app_version_from;

  /// Label for the version of the language-independent database.
  ///
  /// In en, this message translates to:
  /// **'Data version'**
  String get common_data_update;

  /// Label for localized DB data version by language
  ///
  /// In en, this message translates to:
  /// **'Data version in {language}'**
  String localized_data_update(String language);

  /// Connector between a database version label and its date on the About page.
  ///
  /// In en, this message translates to:
  /// **'from'**
  String get data_version_from;

  /// Language name for English in language and data-version labels.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get language_name_en;

  /// Language name for Spanish in language and data-version labels.
  ///
  /// In en, this message translates to:
  /// **'Spanish'**
  String get language_name_es;

  /// Language name for Ukrainian in language and data-version labels.
  ///
  /// In en, this message translates to:
  /// **'Ukrainian'**
  String get language_name_uk;

  /// Language name for Russian in language and data-version labels.
  ///
  /// In en, this message translates to:
  /// **'Russian'**
  String get language_name_ru;

  /// Short description of the app on the About page.
  ///
  /// In en, this message translates to:
  /// **'Revelation Study app.'**
  String get app_description;

  /// Link label for the official Revelation website.
  ///
  /// In en, this message translates to:
  /// **'Revelation.website'**
  String get website;

  /// Link label for the Revelation source repository on GitHub.
  ///
  /// In en, this message translates to:
  /// **'GitHub project'**
  String get github_project;

  /// Link label for the app's privacy policy.
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacy_policy;

  /// Link label for the app's license.
  ///
  /// In en, this message translates to:
  /// **'License'**
  String get license;

  /// Link label for supporting the Revelation project.
  ///
  /// In en, this message translates to:
  /// **'Support us'**
  String get support_us;

  /// Link label for downloadable installers.
  ///
  /// In en, this message translates to:
  /// **'Installation packages'**
  String get installation_packages;

  /// Heading of the About acknowledgments section.
  ///
  /// In en, this message translates to:
  /// **'Acknowledgments'**
  String get acknowledgements_title;

  /// Opening acknowledgments and introduction to the contributing institutions.
  ///
  /// In en, this message translates to:
  /// **'First and foremost, I would like to thank God for life; my wife, Ira, for her love and care; and my mother for her help and support.\nAlso, my sincere gratitude goes to the institutions that provided access to information and invaluable manuscripts:'**
  String get acknowledgements_description_1;

  /// Introduction to the credited software and resources.
  ///
  /// In en, this message translates to:
  /// **'Many thanks to the creators of the following software and resources:'**
  String get acknowledgements_description_2;

  /// Heading of the recommended resources section.
  ///
  /// In en, this message translates to:
  /// **'Recommended'**
  String get recommended_title;

  /// Introduction to recommended Bible and Revelation study resources.
  ///
  /// In en, this message translates to:
  /// **'Recommended resources for studying Revelation and the Bible as a whole:'**
  String get recommended_description;

  /// Action to start preparing a bug report.
  ///
  /// In en, this message translates to:
  /// **'Report a bug'**
  String get bug_report;

  /// Heading of the application maintenance tools section.
  ///
  /// In en, this message translates to:
  /// **'Tools'**
  String get tools;

  /// Maintenance action to check for and download database updates.
  ///
  /// In en, this message translates to:
  /// **'Update databases'**
  String get refresh_databases;

  /// Success feedback after updating the local databases.
  ///
  /// In en, this message translates to:
  /// **'Databases updated'**
  String get databases_refreshed;

  /// Feedback when the local database files already match the available versions.
  ///
  /// In en, this message translates to:
  /// **'Database files are up to date. No update is required.'**
  String get databases_up_to_date;

  /// Warning that the database files differ in size from the manifest.
  ///
  /// In en, this message translates to:
  /// **'Some database file sizes don\'t match the manifest. Please update the databases again.'**
  String get database_size_mismatch;

  /// Error shown after a failed database update.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t update databases'**
  String get database_refresh_failed;

  /// Action to open the local application data directory.
  ///
  /// In en, this message translates to:
  /// **'Show local folder'**
  String get show_local_folder;

  /// Error when opening the local application data directory fails.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t open local folder'**
  String get local_folder_open_failed;

  /// Opening the local application folder failed; shows its resolved filesystem path
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t open local folder:\n{path}'**
  String local_folder_open_failed_with_path(String path);

  /// Maintenance action to remove cached files.
  ///
  /// In en, this message translates to:
  /// **'Clear cache'**
  String get clear_cache;

  /// Success feedback after removing cached files.
  ///
  /// In en, this message translates to:
  /// **'Cache cleared'**
  String get cache_cleared;

  /// Error shown if the app cannot clear cached files.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t clear cache'**
  String get cache_clear_failed;

  /// Bug report instructions shown after copying technical logs to the clipboard.
  ///
  /// In en, this message translates to:
  /// **'Logs have been copied to the clipboard. Please send them to me at:'**
  String get log_copied_message;

  /// Draft email asking the reporter for steps, copied diagnostics, and a screenshot if available.
  ///
  /// In en, this message translates to:
  /// **'Please briefly describe the error and paste into the email the technical information that the application has just automatically copied to the clipboard (this is important!). If possible, attach a screenshot to your message. Thank you, you’re helping make the app better.'**
  String get bug_report_wish;

  /// Copyright footer wording.
  ///
  /// In en, this message translates to:
  /// **'All rights reserved'**
  String get all_rights_reserved;

  /// Status label while an advertisement loads.
  ///
  /// In en, this message translates to:
  /// **'Ad Loading...'**
  String get ad_loading;

  /// Label for the app navigation menu.
  ///
  /// In en, this message translates to:
  /// **'Menu'**
  String get menu;

  /// Action to exit the application.
  ///
  /// In en, this message translates to:
  /// **'Close app'**
  String get close_app;

  /// Short placeholder label for unfinished content.
  ///
  /// In en, this message translates to:
  /// **'TODO'**
  String get todo;

  /// Navigation label and page title for the manuscript catalogue.
  ///
  /// In en, this message translates to:
  /// **'Primary Sources'**
  String get primary_sources_screen;

  /// Subtitle explaining how to open a manuscript from the catalogue.
  ///
  /// In en, this message translates to:
  /// **'Click on the image to open'**
  String get primary_sources_header;

  /// Navigation label and page title for Strong's dictionary.
  ///
  /// In en, this message translates to:
  /// **'Strong\'s Dictionary'**
  String get strongs_dictionary_screen;

  /// Subtitle describing the scope of Strong's dictionary.
  ///
  /// In en, this message translates to:
  /// **'Greek word meanings and usage'**
  String get strongs_dictionary_header;

  /// Navigation label and page title for the biblical allusion search.
  ///
  /// In en, this message translates to:
  /// **'Allusion Search'**
  String get allusion_search_screen;

  /// Allusion search page subtitle naming the Greek Bible corpus.
  ///
  /// In en, this message translates to:
  /// **'The whole Ancient Greek Bible (LXX + TR)'**
  String get allusion_search_header;

  /// Navigation label and page title for the Bible reader.
  ///
  /// In en, this message translates to:
  /// **'Bible'**
  String get bible_screen;

  /// Subtitle of the Bible reading and study page.
  ///
  /// In en, this message translates to:
  /// **'Reading and studying Scripture'**
  String get bible_header;

  /// Label for the Bible module selector.
  ///
  /// In en, this message translates to:
  /// **'Module'**
  String get bible_module;

  /// Label for the Bible book selector.
  ///
  /// In en, this message translates to:
  /// **'Book'**
  String get bible_book;

  /// Label for the Bible chapter selector.
  ///
  /// In en, this message translates to:
  /// **'Chapter'**
  String get bible_chapter;

  /// Label for the Bible verse selector.
  ///
  /// In en, this message translates to:
  /// **'Verse'**
  String get bible_verse;

  /// Status shown while opening the Bible reader.
  ///
  /// In en, this message translates to:
  /// **'Opening Bible...'**
  String get bible_loading;

  /// Status shown while loading the selected Bible chapter.
  ///
  /// In en, this message translates to:
  /// **'Loading chapter...'**
  String get bible_loading_chapter;

  /// Status while downloading or opening the selected Bible module.
  ///
  /// In en, this message translates to:
  /// **'Downloading and opening module...'**
  String get bible_loading_module;

  /// Bible reader empty state with instructions for obtaining module files.
  ///
  /// In en, this message translates to:
  /// **'Bible modules were not found. Update databases or add bible_*.sqlite to the local data folder.'**
  String get bible_no_modules;

  /// Action to navigate to the preceding Bible chapter.
  ///
  /// In en, this message translates to:
  /// **'Previous chapter'**
  String get bible_previous_chapter;

  /// Action to navigate to the following Bible chapter.
  ///
  /// In en, this message translates to:
  /// **'Next chapter'**
  String get bible_next_chapter;

  /// Label for showing or hiding Strong's annotations in the Bible reader.
  ///
  /// In en, this message translates to:
  /// **'Strong'**
  String get bible_strong_toggle_label;

  /// Action or heading for the selected Bible module's details.
  ///
  /// In en, this message translates to:
  /// **'About this module'**
  String get bible_module_info;

  /// Label for the title in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Title'**
  String get bible_module_info_title;

  /// Label for the description in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get bible_module_info_description;

  /// Label for the text language in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get bible_module_info_language;

  /// English language value in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get bible_module_info_language_en;

  /// Spanish language value in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Spanish'**
  String get bible_module_info_language_es;

  /// Ukrainian language value in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Ukrainian'**
  String get bible_module_info_language_uk;

  /// Russian language value in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Russian'**
  String get bible_module_info_language_ru;

  /// Label for the Bible module's canon or book coverage.
  ///
  /// In en, this message translates to:
  /// **'Books'**
  String get bible_module_info_canon;

  /// Label for the Bible module's verse numbering scheme.
  ///
  /// In en, this message translates to:
  /// **'Verse numbering'**
  String get bible_module_info_versification;

  /// Label for the license in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'License'**
  String get bible_module_info_license;

  /// Label for the short source attribution in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Source'**
  String get bible_module_info_source_summary;

  /// Label for the content version in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Data version'**
  String get bible_module_info_data_version;

  /// Label for the database format version in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Database format'**
  String get bible_module_info_schema_version;

  /// Label for the update date in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Updated'**
  String get bible_module_info_date;

  /// Heading for source attribution and technical module details.
  ///
  /// In en, this message translates to:
  /// **'Source and details'**
  String get bible_module_info_details;

  /// Fallback value for missing Bible module metadata.
  ///
  /// In en, this message translates to:
  /// **'Not specified'**
  String get bible_module_info_unknown;

  /// Ancient Greek language value in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Ancient Greek'**
  String get bible_module_info_greek;

  /// Hebrew language value in the Bible module details.
  ///
  /// In en, this message translates to:
  /// **'Hebrew'**
  String get bible_module_info_hebrew;

  /// Canon coverage value for a Bible module containing all 66 books.
  ///
  /// In en, this message translates to:
  /// **'66 books'**
  String get bible_module_info_66_books;

  /// Action to copy the selected Bible verses to the clipboard.
  ///
  /// In en, this message translates to:
  /// **'Copy selected verses'**
  String get bible_copy_selected_verses;

  /// Confirmation that the selected Bible verses were copied.
  ///
  /// In en, this message translates to:
  /// **'Selected verses copied to the clipboard.'**
  String get bible_selected_verses_copied;

  /// Action to open the second Bible reading pane.
  ///
  /// In en, this message translates to:
  /// **'Open parallel Bible reader'**
  String get bible_open_parallel_reader;

  /// Action to close the second Bible reading pane.
  ///
  /// In en, this message translates to:
  /// **'Close parallel reader'**
  String get bible_close_parallel_reader;

  /// Control label for moving both parallel reading panes together.
  ///
  /// In en, this message translates to:
  /// **'Linked navigation'**
  String get bible_linked_navigation;

  /// Control label for navigating the parallel reading panes independently.
  ///
  /// In en, this message translates to:
  /// **'Independent navigation'**
  String get bible_unlinked_navigation;

  /// Action to search within the currently selected Bible module.
  ///
  /// In en, this message translates to:
  /// **'Search this module'**
  String get bible_search_in_module;

  /// Title of the search dialog for a Bible module.
  ///
  /// In en, this message translates to:
  /// **'Bible search'**
  String get bible_search_dialog_title;

  /// Label of the query field in the Bible search dialog.
  ///
  /// In en, this message translates to:
  /// **'Search text'**
  String get bible_search_query_label;

  /// Hint shown inside the Bible search query field.
  ///
  /// In en, this message translates to:
  /// **'Phrase'**
  String get bible_search_query_hint;

  /// Action to submit the Bible search query.
  ///
  /// In en, this message translates to:
  /// **'Search'**
  String get bible_search_button;

  /// Label for choosing what a tap on a Bible search result does.
  ///
  /// In en, this message translates to:
  /// **'Tap action'**
  String get bible_search_result_action;

  /// Option to copy the verse when a Bible search result is activated.
  ///
  /// In en, this message translates to:
  /// **'Copy verse'**
  String get bible_search_action_copy;

  /// Option to open the verse when a Bible search result is activated.
  ///
  /// In en, this message translates to:
  /// **'Open verse'**
  String get bible_search_action_open;

  /// Action to copy Bible search results in bulk.
  ///
  /// In en, this message translates to:
  /// **'Copy results'**
  String get bible_search_copy_results;

  /// Status displayed while a Bible text search is running.
  ///
  /// In en, this message translates to:
  /// **'Searching...'**
  String get bible_search_loading;

  /// Error shown after a failed Bible text search.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t search.'**
  String get bible_search_failed;

  /// Empty state when the Bible text search finds no matches.
  ///
  /// In en, this message translates to:
  /// **'No matches found.'**
  String get bible_search_no_results;

  /// Search result count label with total occurrences and verses
  ///
  /// In en, this message translates to:
  /// **'Matches: {matches}; verses: {verses}'**
  String bible_search_match_count(int matches, int verses);

  /// Search results pager label
  ///
  /// In en, this message translates to:
  /// **'Page {current} of {total}'**
  String bible_search_page_label(int current, int total);

  /// Action to return to the preceding page of Bible search results.
  ///
  /// In en, this message translates to:
  /// **'Previous page'**
  String get bible_search_previous_page;

  /// Action to continue to the next page of Bible search results.
  ///
  /// In en, this message translates to:
  /// **'Next page'**
  String get bible_search_next_page;

  /// Confirmation that one Bible search result verse was copied.
  ///
  /// In en, this message translates to:
  /// **'Verse copied to the clipboard.'**
  String get bible_search_verse_copied;

  /// Confirmation that the Bible search result references were copied.
  ///
  /// In en, this message translates to:
  /// **'References copied to the clipboard.'**
  String get bible_search_references_copied;

  /// Confirmation that Bible search result verse texts were copied.
  ///
  /// In en, this message translates to:
  /// **'Verses copied to the clipboard.'**
  String get bible_search_verses_copied;

  /// Hint for loading and copying a passage from a press-and-hold on a Bible reference.
  ///
  /// In en, this message translates to:
  /// **'Long-press a verse link to load and copy the verse text.'**
  String get bible_reference_preview_loading_hint;

  /// Status while the Bible reference preview retrieves verse text.
  ///
  /// In en, this message translates to:
  /// **'Loading verse text...'**
  String get bible_reference_preview_loading;

  /// Fallback when verse text cannot be loaded for a Bible reference preview.
  ///
  /// In en, this message translates to:
  /// **'Verse text is unavailable.'**
  String get bible_reference_preview_unavailable;

  /// Navigation label and page title for the Revelation structure section.
  ///
  /// In en, this message translates to:
  /// **'Revelation Structure'**
  String get revelation_structure_screen;

  /// Subtitle describing the outline and narrative focus of the Revelation structure section.
  ///
  /// In en, this message translates to:
  /// **'Book outline and narrative structure'**
  String get revelation_structure_header;

  /// Navigation label and page title for the historical background section.
  ///
  /// In en, this message translates to:
  /// **'Historical Background'**
  String get historical_background_screen;

  /// Subtitle describing the historical background section's scope.
  ///
  /// In en, this message translates to:
  /// **'Key events in church and world history'**
  String get historical_background_header;

  /// Navigation label and page title for the practical faith section.
  ///
  /// In en, this message translates to:
  /// **'Practical Faith'**
  String get practical_faith_screen;

  /// Subtitle describing the practical faith section's focus.
  ///
  /// In en, this message translates to:
  /// **'Reflection and application'**
  String get practical_faith_header;

  /// Message shown on placeholder pages for planned sections
  ///
  /// In en, this message translates to:
  /// **'The {featureTitle} page is planned for a future version.'**
  String planned_feature_message(String featureTitle);

  /// Navigation label and page title for the application settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings_screen;

  /// Settings subtitle explaining that changes are saved automatically.
  ///
  /// In en, this message translates to:
  /// **'Saving automatically'**
  String get settings_header;

  /// Navigation label and page title for application information.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about_screen;

  /// Subtitle of the application information page.
  ///
  /// In en, this message translates to:
  /// **'General Information About the Application'**
  String get about_header;

  /// Navigation label and page title for application downloads.
  ///
  /// In en, this message translates to:
  /// **'Download'**
  String get download;

  /// Subtitle prompting users to choose their platform for installation.
  ///
  /// In en, this message translates to:
  /// **'Install the application for your platform'**
  String get download_header;

  /// Platform label in the app download list for Android.
  ///
  /// In en, this message translates to:
  /// **'Android'**
  String get download_android;

  /// Platform label in the app download list for Windows.
  ///
  /// In en, this message translates to:
  /// **'Windows'**
  String get download_windows;

  /// Platform label in the app download list for Linux.
  ///
  /// In en, this message translates to:
  /// **'Linux'**
  String get download_linux;

  /// Store link label for the Google Play listing.
  ///
  /// In en, this message translates to:
  /// **'Google Play'**
  String get download_google_play;

  /// Store link label for the Microsoft Store listing.
  ///
  /// In en, this message translates to:
  /// **'Microsoft Store'**
  String get download_microsoft_store;

  /// Store link label for the Snapcraft listing.
  ///
  /// In en, this message translates to:
  /// **'Snapcraft'**
  String get download_snapcraft;

  /// Feedback after saving an exported file. The path parameter is its location.
  ///
  /// In en, this message translates to:
  /// **'Saved: {path}'**
  String file_saved_at(Object path);

  /// Error when the About page cannot load credited software.
  ///
  /// In en, this message translates to:
  /// **'Error loading libraries'**
  String get error_loading_libraries;

  /// Error when the About page cannot load contributing institutions.
  ///
  /// In en, this message translates to:
  /// **'Error loading institutions'**
  String get error_loading_institutions;

  /// Error when the About page cannot load recommended resources.
  ///
  /// In en, this message translates to:
  /// **'Error loading recommendations'**
  String get error_loading_recommendations;

  /// Error when the topic list cannot be loaded.
  ///
  /// In en, this message translates to:
  /// **'Error loading topics'**
  String get error_loading_topics;

  /// Error when the manuscript catalogue cannot be loaded.
  ///
  /// In en, this message translates to:
  /// **'Error loading primary sources'**
  String get error_loading_primary_sources;

  /// Heading or action for opening the release changelog.
  ///
  /// In en, this message translates to:
  /// **'Changelog'**
  String get changelog;

  /// Shared action to dismiss a dialog or panel.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get close;

  /// Shared title for messages reporting an error.
  ///
  /// In en, this message translates to:
  /// **'Error'**
  String get error;

  /// Shared title for a warning dialog.
  ///
  /// In en, this message translates to:
  /// **'Attention'**
  String get attention;

  /// Shared label for an information action or panel.
  ///
  /// In en, this message translates to:
  /// **'Information'**
  String get info;

  /// Action to expand or open further information.
  ///
  /// In en, this message translates to:
  /// **'More information'**
  String get more_information;

  /// Error shown when the app cannot open a link.
  ///
  /// In en, this message translates to:
  /// **'Unable to follow the link'**
  String get unable_to_follow_the_link;

  /// Application setting for the interface language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// Application setting for the interface color scheme.
  ///
  /// In en, this message translates to:
  /// **'Color theme'**
  String get color_theme;

  /// Theme selection label for the Manuscript palette.
  ///
  /// In en, this message translates to:
  /// **'Manuscript'**
  String get manuscript_color_theme;

  /// Theme selection label for the Forest palette.
  ///
  /// In en, this message translates to:
  /// **'Forest'**
  String get forest_color_theme;

  /// Theme selection label for the Sky palette.
  ///
  /// In en, this message translates to:
  /// **'Sky'**
  String get sky_color_theme;

  /// Theme selection label for the Grape palette.
  ///
  /// In en, this message translates to:
  /// **'Grape'**
  String get grape_color_theme;

  /// Application setting for the interface text size.
  ///
  /// In en, this message translates to:
  /// **'Font size'**
  String get font_size;

  /// Label for the small text size setting.
  ///
  /// In en, this message translates to:
  /// **'Small'**
  String get small_font_size;

  /// Label for the medium text size setting.
  ///
  /// In en, this message translates to:
  /// **'Medium'**
  String get medium_font_size;

  /// Label for the large text size setting.
  ///
  /// In en, this message translates to:
  /// **'Large'**
  String get large_font_size;

  /// Application setting for sound.
  ///
  /// In en, this message translates to:
  /// **'Sound'**
  String get sound;

  /// Shared label for the enabled state of a toggle.
  ///
  /// In en, this message translates to:
  /// **'On'**
  String get on;

  /// Shared label for the disabled state of a toggle.
  ///
  /// In en, this message translates to:
  /// **'Off'**
  String get off;

  /// Resource category used in the About page's software and asset credits.
  ///
  /// In en, this message translates to:
  /// **'Vectors'**
  String get vectors;

  /// Resource category for icons in the About page's asset credits.
  ///
  /// In en, this message translates to:
  /// **'Icons'**
  String get icons;

  /// Conjunction between credited resources or creators in the About page.
  ///
  /// In en, this message translates to:
  /// **'and'**
  String get and;

  /// Connector before the credited creator in the About page.
  ///
  /// In en, this message translates to:
  /// **'by'**
  String get by;

  /// Resource category for a software package in the About page's credits.
  ///
  /// In en, this message translates to:
  /// **'Package'**
  String get package;

  /// Resource category for a typeface in the About page's credits.
  ///
  /// In en, this message translates to:
  /// **'Font'**
  String get font;

  /// Link label for a manuscript's external Wikipedia article.
  ///
  /// In en, this message translates to:
  /// **'Wikipedia'**
  String get wikipedia;

  /// Link label for a manuscript record at the Institute for New Testament Textual Research.
  ///
  /// In en, this message translates to:
  /// **'INTF'**
  String get intf;

  /// Link label for the provider of a manuscript image.
  ///
  /// In en, this message translates to:
  /// **'Image source'**
  String get image_source;

  /// Field label for the dating of a manuscript.
  ///
  /// In en, this message translates to:
  /// **'Date'**
  String get source_date;

  /// Field label for the biblical contents of a manuscript.
  ///
  /// In en, this message translates to:
  /// **'Contents'**
  String get source_contents;

  /// Field label for the manuscript's physical writing material.
  ///
  /// In en, this message translates to:
  /// **'Material'**
  String get source_material;

  /// Field label for the manuscript's writing system or hand.
  ///
  /// In en, this message translates to:
  /// **'Script'**
  String get source_script;

  /// Field label for the manuscript's classification.
  ///
  /// In en, this message translates to:
  /// **'Classification'**
  String get source_classification;

  /// Field label for a manuscript's discovery information.
  ///
  /// In en, this message translates to:
  /// **'Discovery'**
  String get source_discovery;

  /// Field label for a manuscript's known location.
  ///
  /// In en, this message translates to:
  /// **'Location'**
  String get source_location;

  /// Label for the internal and external links in a primary source card.
  ///
  /// In en, this message translates to:
  /// **'Links'**
  String get primary_source_links;

  /// Link in an expanded card that opens the primary source in the app.
  ///
  /// In en, this message translates to:
  /// **'Open primary source'**
  String get open_primary_source;

  /// Invites a reader to reveal the deeper study after the opening passage.
  ///
  /// In en, this message translates to:
  /// **'Explore the passage more deeply'**
  String get topic_explore_passage;

  /// Hides the expanded study within an article.
  ///
  /// In en, this message translates to:
  /// **'Collapse study'**
  String get topic_collapse_study;

  /// Fallback title of a study article with no available title.
  ///
  /// In en, this message translates to:
  /// **'Topic'**
  String get topic;

  /// Action to expand the details of a manuscript card.
  ///
  /// In en, this message translates to:
  /// **'show more information'**
  String get show_more;

  /// Action to collapse the expanded details of a manuscript card.
  ///
  /// In en, this message translates to:
  /// **'hide'**
  String get hide;

  /// Catalogue group heading for manuscripts preserving all of Revelation.
  ///
  /// In en, this message translates to:
  /// **'Contain the entire Revelation in full'**
  String get full_primary_sources;

  /// Catalogue group heading for manuscripts preserving a substantial part of Revelation.
  ///
  /// In en, this message translates to:
  /// **'Contain a significant part of the Revelation'**
  String get significant_primary_sources;

  /// Catalogue group heading for manuscripts with short fragments of Revelation.
  ///
  /// In en, this message translates to:
  /// **'Contain small fragments of the Revelation'**
  String get fragments_primary_sources;

  /// Label for the number of Revelation verses preserved by a manuscript.
  ///
  /// In en, this message translates to:
  /// **'Quantity of verses'**
  String get verses;

  /// Prompt to choose a page of the selected manuscript.
  ///
  /// In en, this message translates to:
  /// **'Choose page'**
  String get choose_page;

  /// Empty state when no manuscript page images are available.
  ///
  /// In en, this message translates to:
  /// **'Images are missing'**
  String get images_are_missing;

  /// Fallback shown when the current manuscript image fails to load.
  ///
  /// In en, this message translates to:
  /// **'Image not loaded'**
  String get image_not_loaded;

  /// Word comparison error when the requested manuscript cannot be opened.
  ///
  /// In en, this message translates to:
  /// **'Primary source unavailable'**
  String get primary_source_word_source_unavailable;

  /// Word comparison error when the requested manuscript page cannot be found.
  ///
  /// In en, this message translates to:
  /// **'Page unavailable'**
  String get primary_source_word_page_unavailable;

  /// Word comparison error when the requested word cannot be located.
  ///
  /// In en, this message translates to:
  /// **'Word unavailable'**
  String get primary_source_word_word_unavailable;

  /// Word comparison error when the word's image cannot be loaded.
  ///
  /// In en, this message translates to:
  /// **'Image unavailable'**
  String get primary_source_word_image_unavailable;

  /// Instruction for opening a word in its manuscript from the comparison image.
  ///
  /// In en, this message translates to:
  /// **'Tap the image to see the word in the primary source.'**
  String get primary_source_words_image_hint;

  /// Initial instruction to select an annotated element on the manuscript image.
  ///
  /// In en, this message translates to:
  /// **'Click on the image element you’re interested in to get information about it.'**
  String get click_for_info;

  /// Short warning when a lower-resolution manuscript image is displayed.
  ///
  /// In en, this message translates to:
  /// **'Quality reduced'**
  String get low_quality;

  /// Explains how to access the full-quality manuscript image on another platform.
  ///
  /// In en, this message translates to:
  /// **'A lower-quality image is used in the mobile browser. To view in maximum quality, install the app or open the page on a computer.'**
  String get low_quality_message;

  /// Manuscript viewer toolbar action to reload the current image.
  ///
  /// In en, this message translates to:
  /// **'Reloading the image'**
  String get reload_image;

  /// Manuscript viewer action to increase image magnification.
  ///
  /// In en, this message translates to:
  /// **'Zoom in'**
  String get zoom_in;

  /// Manuscript viewer action to decrease image magnification.
  ///
  /// In en, this message translates to:
  /// **'Zoom out'**
  String get zoom_out;

  /// Manuscript viewer action to restore the original image scale.
  ///
  /// In en, this message translates to:
  /// **'Original scale'**
  String get restore_original_scale;

  /// Manuscript viewer control for inverting image colors.
  ///
  /// In en, this message translates to:
  /// **'Negative'**
  String get toggle_negative;

  /// Manuscript viewer control for switching the image to monochrome.
  ///
  /// In en, this message translates to:
  /// **'Monochrome'**
  String get toggle_monochrome;

  /// Title and toolbar label for the manuscript image adjustment controls.
  ///
  /// In en, this message translates to:
  /// **'Brightness, Contrast'**
  String get brightness_contrast;

  /// Label of the brightness control for a manuscript image.
  ///
  /// In en, this message translates to:
  /// **'Brightness'**
  String get brightness;

  /// Label of the contrast control for a manuscript image.
  ///
  /// In en, this message translates to:
  /// **'Contrast'**
  String get contrast;

  /// Shared action to confirm and dismiss a dialog.
  ///
  /// In en, this message translates to:
  /// **'OK'**
  String get ok;

  /// Primary action to accept a selection in a dialog.
  ///
  /// In en, this message translates to:
  /// **'Select'**
  String get dialog_select;

  /// Action to close a tool dialog after changes have already been applied.
  ///
  /// In en, this message translates to:
  /// **'Done'**
  String get dialog_done;

  /// Shared action to dismiss without applying the pending choice.
  ///
  /// In en, this message translates to:
  /// **'Сancel'**
  String get cancel;

  /// Shared action to restore defaults for the current controls.
  ///
  /// In en, this message translates to:
  /// **'Reset'**
  String get reset;

  /// Label for the image region selected for color replacement.
  ///
  /// In en, this message translates to:
  /// **'Area'**
  String get area;

  /// Label for the dimensions of the region selected for color replacement.
  ///
  /// In en, this message translates to:
  /// **'Size'**
  String get size;

  /// Placeholder when the requested region or color has not been selected.
  ///
  /// In en, this message translates to:
  /// **'Not selected'**
  String get not_selected;

  /// Action to select an image region for color replacement.
  ///
  /// In en, this message translates to:
  /// **'Area selection'**
  String get area_selection;

  /// Title and toolbar label for the image color replacement tool.
  ///
  /// In en, this message translates to:
  /// **'Color replacement'**
  String get color_replacement;

  /// Label of the source color selected for replacement.
  ///
  /// In en, this message translates to:
  /// **'Color to replace'**
  String get color_to_replace;

  /// Action to sample a color directly from the manuscript image.
  ///
  /// In en, this message translates to:
  /// **'Color selection'**
  String get eyedropper;

  /// Label of the replacement color to be applied to the image.
  ///
  /// In en, this message translates to:
  /// **'New color'**
  String get new_color;

  /// Control for choosing a replacement color from the palette.
  ///
  /// In en, this message translates to:
  /// **'Palette'**
  String get palette;

  /// Prompt to choose a color in the color picker.
  ///
  /// In en, this message translates to:
  /// **'Select color'**
  String get select_color;

  /// Heading of the manual image area selection mode.
  ///
  /// In en, this message translates to:
  /// **'Select an area on the image'**
  String get select_area_header;

  /// Instructions for dragging a rectangle on the manuscript image.
  ///
  /// In en, this message translates to:
  /// **'Select a rectangular area on the image: touch the starting point, drag, and release. You can zoom in if needed.'**
  String get select_area_description;

  /// Heading of the mode that samples one point on the manuscript image.
  ///
  /// In en, this message translates to:
  /// **'Select a point on the image'**
  String get pick_color_header;

  /// Instructions for selecting a pixel on the manuscript image.
  ///
  /// In en, this message translates to:
  /// **'Click on the area of the image where you want to pick a color. You can zoom in and move the image if needed.'**
  String get pick_color_description;

  /// Label for how closely pixels must match the selected source color.
  ///
  /// In en, this message translates to:
  /// **'Tolerance'**
  String get tolerance;

  /// Notice about preparing pixel data when color replacement is first used.
  ///
  /// In en, this message translates to:
  /// **'On the first call, generating the pixel matrix will take some time.'**
  String get replace_color_message;

  /// Manuscript viewer action to restore the current page's display settings.
  ///
  /// In en, this message translates to:
  /// **'Page settings reset'**
  String get page_settings_reset;

  /// Manuscript viewer control for word-boundary overlays.
  ///
  /// In en, this message translates to:
  /// **'Word separators'**
  String get toggle_show_word_separators;

  /// Manuscript viewer control for Strong's number overlays.
  ///
  /// In en, this message translates to:
  /// **'Strong\'s numbers'**
  String get toggle_show_strong_numbers;

  /// Manuscript viewer control for verse number overlays.
  ///
  /// In en, this message translates to:
  /// **'Verse numbers'**
  String get toggle_show_verse_numbers;

  /// Label for a Strong's identifier in the dictionary picker or entry.
  ///
  /// In en, this message translates to:
  /// **'Strong’s number'**
  String get strong_number;

  /// Dictionary picker help listing unavailable Strong's number ranges.
  ///
  /// In en, this message translates to:
  /// **'2717 and 3203-3302 are unavailable'**
  String get strong_picker_unavailable_numbers;

  /// Action to open full-text search in Strong's dictionary.
  ///
  /// In en, this message translates to:
  /// **'Full-text search'**
  String get strong_dictionary_search;

  /// Query field hint showing accepted Strong's number or text searches.
  ///
  /// In en, this message translates to:
  /// **'#/word/translation'**
  String get strong_dictionary_search_hint;

  /// Empty state when no dictionary entries are available.
  ///
  /// In en, this message translates to:
  /// **'Strong’s dictionary entries are unavailable'**
  String get strong_dictionary_no_entries;

  /// Empty state when the dictionary search has no matching entries.
  ///
  /// In en, this message translates to:
  /// **'No matching entries'**
  String get strong_dictionary_no_results;

  /// Tooltip for opening the Greek keyboard in dictionary search.
  ///
  /// In en, this message translates to:
  /// **'Greek keyboard'**
  String get greek_keyboard_tooltip;

  /// Label for the pronunciation field of a Strong's dictionary entry.
  ///
  /// In en, this message translates to:
  /// **'Pronunciation'**
  String get strong_pronunciation;

  /// Heading for synonyms of a Strong's dictionary entry.
  ///
  /// In en, this message translates to:
  /// **'Synonyms'**
  String get strong_synonyms;

  /// Heading for the origin and word analysis of a Strong's dictionary entry.
  ///
  /// In en, this message translates to:
  /// **'Word analysis'**
  String get strong_origin;

  /// Heading for the usage information of a Strong's dictionary entry.
  ///
  /// In en, this message translates to:
  /// **'Usage'**
  String get strong_usage;

  /// Source attribution displayed by the dictionary reference information icon.
  ///
  /// In en, this message translates to:
  /// **'Translation source: https://github.com/openscriptures/strongs'**
  String get strong_reference_commentary;

  /// Explains what can appear in the dictionary's word analysis section.
  ///
  /// In en, this message translates to:
  /// **'Word analysis may include the following elements: derivatives, comparative words, phrases, and related words.'**
  String get strong_origin_tooltip;

  /// Label for grammatical classification in a Strong's dictionary entry.
  ///
  /// In en, this message translates to:
  /// **'Part of speech'**
  String get strong_part_of_speech;

  /// Strong's grammar label for an indeclinable numeral used as an adjective.
  ///
  /// In en, this message translates to:
  /// **'indeclinable numeral (adjective)'**
  String get strong_indeclNumAdj;

  /// Strong's grammar label for an indeclinable letter used as a noun.
  ///
  /// In en, this message translates to:
  /// **'indeclinable letter (noun)'**
  String get strong_indeclLetN;

  /// Strong's grammar label for a word with no inflection.
  ///
  /// In en, this message translates to:
  /// **'indeclinable'**
  String get strong_indeclinable;

  /// Strong's grammar label for an adjective.
  ///
  /// In en, this message translates to:
  /// **'adjective'**
  String get strong_adj;

  /// Strong's grammar label for a correlative adverb.
  ///
  /// In en, this message translates to:
  /// **'adverb, correlative'**
  String get strong_advCor;

  /// Strong's grammar label for an interrogative adverb.
  ///
  /// In en, this message translates to:
  /// **'adverb, interrogative'**
  String get strong_advInt;

  /// Strong's grammar label for a negative adverb.
  ///
  /// In en, this message translates to:
  /// **'adverb, negative'**
  String get strong_advNeg;

  /// Strong's grammar label for a superlative adverb.
  ///
  /// In en, this message translates to:
  /// **'adverb, superlative'**
  String get strong_advSup;

  /// Strong's grammar label for an adverb.
  ///
  /// In en, this message translates to:
  /// **'adverb'**
  String get strong_adv;

  /// Strong's grammar label for a comparative form.
  ///
  /// In en, this message translates to:
  /// **'comparative'**
  String get strong_comp;

  /// Strong's grammar label for a word transliterated from Aramaic.
  ///
  /// In en, this message translates to:
  /// **'aramaic transliterated word'**
  String get strong_aramaicTransWord;

  /// Strong's grammar label for a Hebrew form.
  ///
  /// In en, this message translates to:
  /// **'hebrew form'**
  String get strong_hebrewForm;

  /// Strong's grammar label for a Hebrew noun.
  ///
  /// In en, this message translates to:
  /// **'hebrew noun'**
  String get strong_hebrewNoun;

  /// Strong's grammar label identifying a Hebrew term.
  ///
  /// In en, this message translates to:
  /// **'hebrew'**
  String get strong_hebrew;

  /// Strong's grammar label for a place name.
  ///
  /// In en, this message translates to:
  /// **'location'**
  String get strong_location;

  /// Strong's grammar label for a proper noun.
  ///
  /// In en, this message translates to:
  /// **'proper noun'**
  String get strong_properNoun;

  /// Strong's grammar label for a noun.
  ///
  /// In en, this message translates to:
  /// **'noun'**
  String get strong_noun;

  /// Strong's grammar label for masculine gender.
  ///
  /// In en, this message translates to:
  /// **'masculine'**
  String get strong_masc;

  /// Strong's grammar label for feminine gender.
  ///
  /// In en, this message translates to:
  /// **'feminine'**
  String get strong_fem;

  /// Strong's grammar label for neuter gender.
  ///
  /// In en, this message translates to:
  /// **'neuter'**
  String get strong_neut;

  /// Strong's grammar label for plural number.
  ///
  /// In en, this message translates to:
  /// **'plural'**
  String get strong_plur;

  /// Strong's grammar label for the other-type category.
  ///
  /// In en, this message translates to:
  /// **'other Type'**
  String get strong_otherType;

  /// Strong's grammar label for an imperative verb.
  ///
  /// In en, this message translates to:
  /// **'verb (imperative)'**
  String get strong_verbImp;

  /// Strong's grammar label for a verb.
  ///
  /// In en, this message translates to:
  /// **'verb'**
  String get strong_verb;

  /// Strong's grammar label for a dative pronoun.
  ///
  /// In en, this message translates to:
  /// **'pronoun, dative case'**
  String get strong_pronDat;

  /// Strong's grammar label for a possessive pronoun.
  ///
  /// In en, this message translates to:
  /// **'possessive pronoun'**
  String get strong_pronPoss;

  /// Strong's grammar label for a personal pronoun.
  ///
  /// In en, this message translates to:
  /// **'personal pronoun'**
  String get strong_pronPers;

  /// Strong's grammar label for a reciprocal pronoun.
  ///
  /// In en, this message translates to:
  /// **'reciprocal pronoun'**
  String get strong_pronRecip;

  /// Strong's grammar label for a reflexive pronoun.
  ///
  /// In en, this message translates to:
  /// **'reflexive pronoun'**
  String get strong_pronRefl;

  /// Strong's grammar label for a relative pronoun.
  ///
  /// In en, this message translates to:
  /// **'relative pronoun'**
  String get strong_pronRel;

  /// Strong's grammar label for a correlative pronoun.
  ///
  /// In en, this message translates to:
  /// **'correlative pronoun'**
  String get strong_pronCorrel;

  /// Strong's grammar label for an indefinite pronoun.
  ///
  /// In en, this message translates to:
  /// **'indefinite pronoun'**
  String get strong_pronIndef;

  /// Strong's grammar label for an interrogative pronoun.
  ///
  /// In en, this message translates to:
  /// **'interrogative pronoun'**
  String get strong_pronInterr;

  /// Strong's grammar label for a demonstrative pronoun.
  ///
  /// In en, this message translates to:
  /// **'demonstrative pronoun'**
  String get strong_pronDem;

  /// Strong's grammar label for a pronoun.
  ///
  /// In en, this message translates to:
  /// **'pronoun'**
  String get strong_pron;

  /// Strong's grammar label for a conditional particle.
  ///
  /// In en, this message translates to:
  /// **'conditional particle'**
  String get strong_particleCond;

  /// Strong's grammar label for a disjunctive particle.
  ///
  /// In en, this message translates to:
  /// **'disjunctive particle'**
  String get strong_particleDisj;

  /// Strong's grammar label for an interrogative particle.
  ///
  /// In en, this message translates to:
  /// **'interrogative particle'**
  String get strong_particleInterr;

  /// Strong's grammar label for a negative particle.
  ///
  /// In en, this message translates to:
  /// **'negative particle'**
  String get strong_particleNeg;

  /// Strong's grammar label for a particle.
  ///
  /// In en, this message translates to:
  /// **'particle'**
  String get strong_particle;

  /// Strong's grammar label for an interjection.
  ///
  /// In en, this message translates to:
  /// **'interjection'**
  String get strong_interj;

  /// Strong's grammar label for a participle.
  ///
  /// In en, this message translates to:
  /// **'participle'**
  String get strong_participle;

  /// Strong's grammar label for a prefix.
  ///
  /// In en, this message translates to:
  /// **'prefix'**
  String get strong_prefix;

  /// Strong's grammar label for a preposition.
  ///
  /// In en, this message translates to:
  /// **'preposition'**
  String get strong_prep;

  /// Strong's grammar label for the definite article.
  ///
  /// In en, this message translates to:
  /// **'definite article'**
  String get strong_artDef;

  /// Strong's grammar label for an idiomatic expression.
  ///
  /// In en, this message translates to:
  /// **'phrase (idiomatic expression)'**
  String get strong_phraseIdi;

  /// Strong's grammar label for a phrase.
  ///
  /// In en, this message translates to:
  /// **'phrase'**
  String get strong_phrase;

  /// Strong's grammar label for a negative conjunction.
  ///
  /// In en, this message translates to:
  /// **'negative conjunction'**
  String get strong_conjNeg;

  /// Strong's grammar label for a conjunction.
  ///
  /// In en, this message translates to:
  /// **'conjunction'**
  String get strong_conj;

  /// Conjunction between alternative grammatical classifications in Strong's dictionary.
  ///
  /// In en, this message translates to:
  /// **'or'**
  String get strong_or;

  /// Heading of the placeholder for an unsupported Markdown block.
  ///
  /// In en, this message translates to:
  /// **'Unsupported content block'**
  String get markdown_unknown_block_title;

  /// Explains that the current app build does not support a custom markdown block
  ///
  /// In en, this message translates to:
  /// **'This version of the app cannot display the `{blockName}` block.'**
  String markdown_unknown_block_description(String blockName);

  /// Explains how to get a newer app version when a Markdown block is unsupported.
  ///
  /// In en, this message translates to:
  /// **'Open the downloads page to install a newer app version for your platform.'**
  String get markdown_unknown_block_update_hint;

  /// Action to open the downloads page from an unsupported Markdown block.
  ///
  /// In en, this message translates to:
  /// **'Update app'**
  String get markdown_unknown_block_update_action;

  /// Accessible title of the embedded YouTube player in Markdown content.
  ///
  /// In en, this message translates to:
  /// **'Embedded YouTube video'**
  String get markdown_youtube_player_title;

  /// Heading when the embedded YouTube player is unavailable.
  ///
  /// In en, this message translates to:
  /// **'YouTube video unavailable'**
  String get markdown_youtube_unavailable_title;

  /// Explains that a YouTube block could not be displayed inside the app.
  ///
  /// In en, this message translates to:
  /// **'This YouTube block could not be rendered in the embedded player.'**
  String get markdown_youtube_unavailable_description;

  /// Status shown while an image in Markdown content loads.
  ///
  /// In en, this message translates to:
  /// **'Loading image...'**
  String get markdown_image_loading;

  /// Toolbar action to copy the current article or description.
  ///
  /// In en, this message translates to:
  /// **'Copy content'**
  String get copy_content;

  /// Toolbar action to export the current article or description to PDF.
  ///
  /// In en, this message translates to:
  /// **'Export to PDF'**
  String get export_pdf_content;

  /// Clipboard success feedback after copying Markdown content.
  ///
  /// In en, this message translates to:
  /// **'Content copied to the clipboard.'**
  String get markdown_copied;

  /// Error when copying Markdown content fails.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t copy the content.'**
  String get markdown_copy_failed;

  /// Error when exporting Markdown content to PDF fails.
  ///
  /// In en, this message translates to:
  /// **'Couldn\'t export the PDF.'**
  String get markdown_pdf_export_failed;

  /// Action to open the preceding item in the description panel.
  ///
  /// In en, this message translates to:
  /// **'Previous item'**
  String get previous_description_item;

  /// Action to open the following item in the description panel.
  ///
  /// In en, this message translates to:
  /// **'Next item'**
  String get next_description_item;

  /// Action to select the preceding word in the current passage or manuscript.
  ///
  /// In en, this message translates to:
  /// **'Previous word'**
  String get previous_word;

  /// Action to select the following word in the current passage or manuscript.
  ///
  /// In en, this message translates to:
  /// **'Next word'**
  String get next_word;

  /// Action to select the preceding verse in the manuscript description.
  ///
  /// In en, this message translates to:
  /// **'Previous verse'**
  String get previous_verse;

  /// Action to select the following verse in the manuscript description.
  ///
  /// In en, this message translates to:
  /// **'Next verse'**
  String get next_verse;

  /// Action to show the preceding entry in Strong's dictionary.
  ///
  /// In en, this message translates to:
  /// **'Previous dictionary entry'**
  String get previous_dictionary_entry;

  /// Action to show the following entry in Strong's dictionary.
  ///
  /// In en, this message translates to:
  /// **'Next dictionary entry'**
  String get next_dictionary_entry;

  /// Progress label for markdown image preloading in topic articles
  ///
  /// In en, this message translates to:
  /// **'Loading images: {loaded} of {total}'**
  String markdown_images_loading_progress(int loaded, int total);

  /// Short form of Genesis in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Gen'**
  String get book_code_1;

  /// Full book name for Genesis in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Genesis'**
  String get book_name_1;

  /// Short form of Exodus in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Exod'**
  String get book_code_2;

  /// Full book name for Exodus in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Exodus'**
  String get book_name_2;

  /// Short form of Leviticus in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Lev'**
  String get book_code_3;

  /// Full book name for Leviticus in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Leviticus'**
  String get book_name_3;

  /// Short form of Numbers in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Num'**
  String get book_code_4;

  /// Full book name for Numbers in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Numbers'**
  String get book_name_4;

  /// Short form of Deuteronomy in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Deut'**
  String get book_code_5;

  /// Full book name for Deuteronomy in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Deuteronomy'**
  String get book_name_5;

  /// Short form of Joshua in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Josh'**
  String get book_code_6;

  /// Full book name for Joshua in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Joshua'**
  String get book_name_6;

  /// Short form of Judges in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Judg'**
  String get book_code_7;

  /// Full book name for Judges in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Judges'**
  String get book_name_7;

  /// Short form of Ruth in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Ruth'**
  String get book_code_8;

  /// Full book name for Ruth in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Ruth'**
  String get book_name_8;

  /// Short form of 1 Samuel in Bible references.
  ///
  /// In en, this message translates to:
  /// **'1Sam'**
  String get book_code_9;

  /// Full book name for 1 Samuel in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'1 Samuel'**
  String get book_name_9;

  /// Short form of 2 Samuel in Bible references.
  ///
  /// In en, this message translates to:
  /// **'2Sam'**
  String get book_code_10;

  /// Full book name for 2 Samuel in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'2 Samuel'**
  String get book_name_10;

  /// Short form of 1 Kings in Bible references.
  ///
  /// In en, this message translates to:
  /// **'1Kgs'**
  String get book_code_11;

  /// Full book name for 1 Kings in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'1 Kings'**
  String get book_name_11;

  /// Short form of 2 Kings in Bible references.
  ///
  /// In en, this message translates to:
  /// **'2Kgs'**
  String get book_code_12;

  /// Full book name for 2 Kings in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'2 Kings'**
  String get book_name_12;

  /// Short form of 1 Chronicles in Bible references.
  ///
  /// In en, this message translates to:
  /// **'1Chr'**
  String get book_code_13;

  /// Full book name for 1 Chronicles in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'1 Chronicles'**
  String get book_name_13;

  /// Short form of 2 Chronicles in Bible references.
  ///
  /// In en, this message translates to:
  /// **'2Chr'**
  String get book_code_14;

  /// Full book name for 2 Chronicles in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'2 Chronicles'**
  String get book_name_14;

  /// Short form of Ezra in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Ezra'**
  String get book_code_15;

  /// Full book name for Ezra in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Ezra'**
  String get book_name_15;

  /// Short form of Nehemiah in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Neh'**
  String get book_code_16;

  /// Full book name for Nehemiah in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Nehemiah'**
  String get book_name_16;

  /// Short form of Esther in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Esth'**
  String get book_code_17;

  /// Full book name for Esther in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Esther'**
  String get book_name_17;

  /// Short form of Job in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Job'**
  String get book_code_18;

  /// Full book name for Job in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Job'**
  String get book_name_18;

  /// Short form of Psalms in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Ps'**
  String get book_code_19;

  /// Full book name for Psalms in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Psalms'**
  String get book_name_19;

  /// Short form of Proverbs in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Prov'**
  String get book_code_20;

  /// Full book name for Proverbs in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Proverbs'**
  String get book_name_20;

  /// Short form of Ecclesiastes in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Eccl'**
  String get book_code_21;

  /// Full book name for Ecclesiastes in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Ecclesiastes'**
  String get book_name_21;

  /// Short form of Song of Songs in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Song'**
  String get book_code_22;

  /// Full book name for Song of Songs in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Song of Songs'**
  String get book_name_22;

  /// Short form of Isaiah in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Isa'**
  String get book_code_23;

  /// Full book name for Isaiah in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Isaiah'**
  String get book_name_23;

  /// Short form of Jeremiah in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Jer'**
  String get book_code_24;

  /// Full book name for Jeremiah in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Jeremiah'**
  String get book_name_24;

  /// Short form of Lamentations in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Lam'**
  String get book_code_25;

  /// Full book name for Lamentations in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Lamentations'**
  String get book_name_25;

  /// Short form of Ezekiel in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Ezek'**
  String get book_code_26;

  /// Full book name for Ezekiel in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Ezekiel'**
  String get book_name_26;

  /// Short form of Daniel in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Dan'**
  String get book_code_27;

  /// Full book name for Daniel in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Daniel'**
  String get book_name_27;

  /// Short form of Hosea in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Hos'**
  String get book_code_28;

  /// Full book name for Hosea in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Hosea'**
  String get book_name_28;

  /// Short form of Joel in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Joel'**
  String get book_code_29;

  /// Full book name for Joel in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Joel'**
  String get book_name_29;

  /// Short form of Amos in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Amos'**
  String get book_code_30;

  /// Full book name for Amos in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Amos'**
  String get book_name_30;

  /// Short form of Obadiah in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Obad'**
  String get book_code_31;

  /// Full book name for Obadiah in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Obadiah'**
  String get book_name_31;

  /// Short form of Jonah in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Jonah'**
  String get book_code_32;

  /// Full book name for Jonah in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Jonah'**
  String get book_name_32;

  /// Short form of Micah in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Mic'**
  String get book_code_33;

  /// Full book name for Micah in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Micah'**
  String get book_name_33;

  /// Short form of Nahum in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Nah'**
  String get book_code_34;

  /// Full book name for Nahum in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Nahum'**
  String get book_name_34;

  /// Short form of Habakkuk in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Hab'**
  String get book_code_35;

  /// Full book name for Habakkuk in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Habakkuk'**
  String get book_name_35;

  /// Short form of Zephaniah in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Zeph'**
  String get book_code_36;

  /// Full book name for Zephaniah in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Zephaniah'**
  String get book_name_36;

  /// Short form of Haggai in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Hag'**
  String get book_code_37;

  /// Full book name for Haggai in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Haggai'**
  String get book_name_37;

  /// Short form of Zechariah in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Zech'**
  String get book_code_38;

  /// Full book name for Zechariah in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Zechariah'**
  String get book_name_38;

  /// Short form of Malachi in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Mal'**
  String get book_code_39;

  /// Full book name for Malachi in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Malachi'**
  String get book_name_39;

  /// Short form of Matthew in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Mat'**
  String get book_code_40;

  /// Full book name for Matthew in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Matthew'**
  String get book_name_40;

  /// Short form of Mark in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Mark'**
  String get book_code_41;

  /// Full book name for Mark in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Mark'**
  String get book_name_41;

  /// Short form of Luke in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Luke'**
  String get book_code_42;

  /// Full book name for Luke in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Luke'**
  String get book_name_42;

  /// Short form of John in Bible references.
  ///
  /// In en, this message translates to:
  /// **'John'**
  String get book_code_43;

  /// Full book name for John in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'John'**
  String get book_name_43;

  /// Short form of Acts in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Acts'**
  String get book_code_44;

  /// Full book name for Acts in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Acts'**
  String get book_name_44;

  /// Short form of Romans in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Rom'**
  String get book_code_45;

  /// Full book name for Romans in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Romans'**
  String get book_name_45;

  /// Short form of 1 Corinthians in Bible references.
  ///
  /// In en, this message translates to:
  /// **'1Cor'**
  String get book_code_46;

  /// Full book name for 1 Corinthians in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'1 Corinthians'**
  String get book_name_46;

  /// Short form of 2 Corinthians in Bible references.
  ///
  /// In en, this message translates to:
  /// **'2Cor'**
  String get book_code_47;

  /// Full book name for 2 Corinthians in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'2 Corinthians'**
  String get book_name_47;

  /// Short form of Galatians in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Gal'**
  String get book_code_48;

  /// Full book name for Galatians in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Galatians'**
  String get book_name_48;

  /// Short form of Ephesians in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Eph'**
  String get book_code_49;

  /// Full book name for Ephesians in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Ephesians'**
  String get book_name_49;

  /// Short form of Philippians in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Phil'**
  String get book_code_50;

  /// Full book name for Philippians in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Philippians'**
  String get book_name_50;

  /// Short form of Colossians in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Col'**
  String get book_code_51;

  /// Full book name for Colossians in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Colossians'**
  String get book_name_51;

  /// Short form of 1 Thessalonians in Bible references.
  ///
  /// In en, this message translates to:
  /// **'1Thess'**
  String get book_code_52;

  /// Full book name for 1 Thessalonians in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'1 Thessalonians'**
  String get book_name_52;

  /// Short form of 2 Thessalonians in Bible references.
  ///
  /// In en, this message translates to:
  /// **'2Thess'**
  String get book_code_53;

  /// Full book name for 2 Thessalonians in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'2 Thessalonians'**
  String get book_name_53;

  /// Short form of 1 Timothy in Bible references.
  ///
  /// In en, this message translates to:
  /// **'1Tim'**
  String get book_code_54;

  /// Full book name for 1 Timothy in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'1 Timothy'**
  String get book_name_54;

  /// Short form of 2 Timothy in Bible references.
  ///
  /// In en, this message translates to:
  /// **'2Tim'**
  String get book_code_55;

  /// Full book name for 2 Timothy in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'2 Timothy'**
  String get book_name_55;

  /// Short form of Titus in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Titus'**
  String get book_code_56;

  /// Full book name for Titus in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Titus'**
  String get book_name_56;

  /// Short form of Philemon in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Phlm'**
  String get book_code_57;

  /// Full book name for Philemon in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Philemon'**
  String get book_name_57;

  /// Short form of Hebrews in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Heb'**
  String get book_code_58;

  /// Full book name for Hebrews in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Hebrews'**
  String get book_name_58;

  /// Short form of James in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Jas'**
  String get book_code_59;

  /// Full book name for James in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'James'**
  String get book_name_59;

  /// Short form of 1 Peter in Bible references.
  ///
  /// In en, this message translates to:
  /// **'1Pet'**
  String get book_code_60;

  /// Full book name for 1 Peter in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'1 Peter'**
  String get book_name_60;

  /// Short form of 2 Peter in Bible references.
  ///
  /// In en, this message translates to:
  /// **'2Pet'**
  String get book_code_61;

  /// Full book name for 2 Peter in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'2 Peter'**
  String get book_name_61;

  /// Short form of 1 John in Bible references.
  ///
  /// In en, this message translates to:
  /// **'1John'**
  String get book_code_62;

  /// Full book name for 1 John in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'1 John'**
  String get book_name_62;

  /// Short form of 2 John in Bible references.
  ///
  /// In en, this message translates to:
  /// **'2John'**
  String get book_code_63;

  /// Full book name for 2 John in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'2 John'**
  String get book_name_63;

  /// Short form of 3 John in Bible references.
  ///
  /// In en, this message translates to:
  /// **'3John'**
  String get book_code_64;

  /// Full book name for 3 John in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'3 John'**
  String get book_name_64;

  /// Short form of Jude in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Jude'**
  String get book_code_65;

  /// Full book name for Jude in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Jude'**
  String get book_name_65;

  /// Short form of Revelation in Bible references.
  ///
  /// In en, this message translates to:
  /// **'Rev'**
  String get book_code_66;

  /// Full book name for Revelation in Bible navigation and references.
  ///
  /// In en, this message translates to:
  /// **'Revelation'**
  String get book_name_66;

  /// Tooltip on the footnote button for a verse. The verse parameter is its number.
  ///
  /// In en, this message translates to:
  /// **'Show footnotes for verse {verse}'**
  String bible_show_footnotes(int verse);

  /// Title of the footnotes dialog. The reference parameter identifies the Bible verse.
  ///
  /// In en, this message translates to:
  /// **'Footnotes: {reference}'**
  String bible_verse_footnotes(String reference);

  /// Global Bible module preference in the existing application settings.
  ///
  /// In en, this message translates to:
  /// **'Default Bible'**
  String get bible_default;

  /// Automatic Bible choice using the interface language with an English fallback.
  ///
  /// In en, this message translates to:
  /// **'Automatic'**
  String get bible_automatic;

  /// Action to refresh the published Bible module catalog.
  ///
  /// In en, this message translates to:
  /// **'Refresh list'**
  String get bible_catalog_refresh;

  /// Catalog refresh failure while retaining saved modules.
  ///
  /// In en, this message translates to:
  /// **'Could not refresh the Bible list. Saved modules are still available.'**
  String get bible_catalog_failed;

  /// Open the previewed Bible passage in the full reader.
  ///
  /// In en, this message translates to:
  /// **'Open in reader'**
  String get bible_open_reader;

  /// Open the current Strong entry on the full dictionary page.
  ///
  /// In en, this message translates to:
  /// **'Open in dictionary'**
  String get strong_open_dictionary;

  /// Explains automatic Bible translation selection in the picker.
  ///
  /// In en, this message translates to:
  /// **'Uses the app language when available, then English.'**
  String get bible_automatic_hint;

  /// Subtitle of the shared Bible passage dialog.
  ///
  /// In en, this message translates to:
  /// **'Bible passage'**
  String get bible_passage_subtitle;

  /// Show the preceding Bible verse.
  ///
  /// In en, this message translates to:
  /// **'Previous verse'**
  String get bible_previous_verse;

  /// Show the following Bible verse.
  ///
  /// In en, this message translates to:
  /// **'Next verse'**
  String get bible_next_verse;

  /// Heading for the selected source passage.
  ///
  /// In en, this message translates to:
  /// **'Source passage'**
  String get allusion_source;

  /// Open additional allusion search parameters.
  ///
  /// In en, this message translates to:
  /// **'More search options'**
  String get allusion_options;

  /// Prompt to search after selecting the source passage.
  ///
  /// In en, this message translates to:
  /// **'Use the search button to find matches for this passage.'**
  String get allusion_search_hint;

  /// Collapse the expanded source passage.
  ///
  /// In en, this message translates to:
  /// **'Collapse'**
  String get allusion_collapse;

  /// Reveal the rest of the source passage.
  ///
  /// In en, this message translates to:
  /// **'{count, plural, one{Show 1 more verse} other{Show {count} more verses}}'**
  String allusion_expand_verses(int count);

  /// Number of consecutive verses to search.
  ///
  /// In en, this message translates to:
  /// **'{count, plural, one{1 verse} other{{count} verses}}'**
  String allusion_verse_count(int count);

  /// Number of consecutive source verses included in the search.
  ///
  /// In en, this message translates to:
  /// **'Verse count'**
  String get allusion_length;

  /// Label for the Bible search scope picker.
  ///
  /// In en, this message translates to:
  /// **'Search in'**
  String get allusion_scope;

  /// Search both testaments.
  ///
  /// In en, this message translates to:
  /// **'Whole Bible'**
  String get allusion_scope_all;

  /// Search the Old Testament only.
  ///
  /// In en, this message translates to:
  /// **'Old Testament'**
  String get allusion_scope_ot;

  /// Search the New Testament only.
  ///
  /// In en, this message translates to:
  /// **'New Testament'**
  String get allusion_scope_nt;

  /// Heading for proposed lexical connections requiring interpretation.
  ///
  /// In en, this message translates to:
  /// **'Possible connections'**
  String get allusion_candidates;

  /// Verse-level candidate results.
  ///
  /// In en, this message translates to:
  /// **'Verses'**
  String get allusion_verses;

  /// Chapter-level candidate results.
  ///
  /// In en, this message translates to:
  /// **'Chapters'**
  String get allusion_chapters;

  /// Book-level candidate results.
  ///
  /// In en, this message translates to:
  /// **'Books'**
  String get allusion_books;

  /// Preview the selected source passage.
  ///
  /// In en, this message translates to:
  /// **'Preview passage'**
  String get allusion_show_source;

  /// No candidate passes the minimum meaningful-word threshold.
  ///
  /// In en, this message translates to:
  /// **'No candidates meet the lexical threshold. Try another passage or a wider range.'**
  String get allusion_no_results;

  /// Initial Greek corpus indexing progress message.
  ///
  /// In en, this message translates to:
  /// **'Preparing the Greek index...'**
  String get allusion_loading;

  /// Failure to load data or perform the allusion search.
  ///
  /// In en, this message translates to:
  /// **'Could not load the search data.'**
  String get allusion_failed;

  /// Source passage has no searchable Greek Strong tokens.
  ///
  /// In en, this message translates to:
  /// **'This passage has no searchable Greek words.'**
  String get allusion_no_source_words;

  /// Distinct searchable Greek Strong identifiers and their combined ranking weight.
  ///
  /// In en, this message translates to:
  /// **'Unique search words: {count} (weight {weight})'**
  String allusion_source_word_count(int count, String weight);

  /// Occurrence count, semantic weight and rarity-adjusted weight in the source passage. A question mark indicates missing verse text.
  ///
  /// In en, this message translates to:
  /// **'Occurrences in passage: {count}\nBase weight: {base}\nSearch weight: {weight}'**
  String allusion_source_word_details(String count, String base, String weight);

  /// Weighted overlap and normalized score used for ranking
  ///
  /// In en, this message translates to:
  /// **'weight {weight} · similarity {score}'**
  String allusion_match_score(String weight, String score);

  /// Verse score explanation
  ///
  /// In en, this message translates to:
  /// **'Sorted by similarity. It accounts for word weights, rarity and the length of both passages.'**
  String get allusion_verse_score_hint;

  /// Chapter and book score explanation
  ///
  /// In en, this message translates to:
  /// **'Sorted by the share of the source passage’s weighted vocabulary found in this group.'**
  String get allusion_group_score_hint;

  /// Strong identifier and base weight on a source word
  ///
  /// In en, this message translates to:
  /// **'{code} · weight {weight}'**
  String allusion_word_weight(String code, String weight);

  /// Number of distinct Strong IDs shared by the source and candidate.
  ///
  /// In en, this message translates to:
  /// **'Shared words: {count}'**
  String allusion_common_count(int count);
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
