// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get app_name => 'Revelation';

  @override
  String get startup_title => 'Launching the app...';

  @override
  String get startup_step_preparing => 'Preparing the app';

  @override
  String get startup_step_loading_settings => 'Loading your settings';

  @override
  String get startup_step_initializing_server =>
      'Connecting to online services';

  @override
  String get startup_step_initializing_databases => 'Opening app data';

  @override
  String get startup_step_configuring_links => 'Preparing Strong’s dictionary';

  @override
  String startup_progress(int current, int total) {
    return 'Step $current of $total';
  }

  @override
  String get startup_error => 'Couldn\'t start the app :(';

  @override
  String get startup_retry => 'Try again';

  @override
  String startup_version_build(String version, String build) {
    return 'Version $version ($build)';
  }

  @override
  String get version => 'App version:';

  @override
  String get app_version_from => 'App version from';

  @override
  String get common_data_update => 'Data version';

  @override
  String localized_data_update(String language) {
    return 'Data version in $language';
  }

  @override
  String get data_version_from => 'from';

  @override
  String get language_name_en => 'English';

  @override
  String get language_name_es => 'Spanish';

  @override
  String get language_name_uk => 'Ukrainian';

  @override
  String get language_name_ru => 'Russian';

  @override
  String get app_description => 'Revelation Study app.';

  @override
  String get website => 'Revelation.website';

  @override
  String get github_project => 'GitHub project';

  @override
  String get privacy_policy => 'Privacy Policy';

  @override
  String get license => 'License';

  @override
  String get support_us => 'Support us';

  @override
  String get installation_packages => 'Installation packages';

  @override
  String get acknowledgements_title => 'Acknowledgments';

  @override
  String get acknowledgements_description_1 =>
      'First and foremost, I would like to thank God for life; my wife, Ira, for her love and care; and my mother for her help and support.\nAlso, my sincere gratitude goes to the institutions that provided access to information and invaluable manuscripts:';

  @override
  String get acknowledgements_description_2 =>
      'Many thanks to the creators of the following software and resources:';

  @override
  String get recommended_title => 'Recommended';

  @override
  String get recommended_description =>
      'Recommended resources for studying Revelation and the Bible as a whole:';

  @override
  String get bug_report => 'Report a bug';

  @override
  String get tools => 'Tools';

  @override
  String get refresh_databases => 'Update databases';

  @override
  String get databases_refreshed => 'Databases updated';

  @override
  String get databases_up_to_date =>
      'Database files are up to date. No update is required.';

  @override
  String get database_size_mismatch =>
      'Some database file sizes don\'t match the manifest. Please update the databases again.';

  @override
  String get database_refresh_failed => 'Couldn\'t update databases';

  @override
  String get show_local_folder => 'Show local folder';

  @override
  String get local_folder_open_failed => 'Couldn\'t open local folder';

  @override
  String get clear_cache => 'Clear cache';

  @override
  String get cache_cleared => 'Cache cleared';

  @override
  String get cache_clear_failed => 'Couldn\'t clear cache';

  @override
  String get log_copied_message =>
      'Logs have been copied to the clipboard. Please send them to me at:';

  @override
  String get bug_report_wish =>
      'Please briefly describe the error and paste into the email the technical information that the application has just automatically copied to the clipboard (this is important!). If possible, attach a screenshot to your message. Thank you, you’re helping make the app better.';

  @override
  String get all_rights_reserved => 'All rights reserved';

  @override
  String get ad_loading => 'Ad Loading...';

  @override
  String get menu => 'Menu';

  @override
  String get close_app => 'Close app';

  @override
  String get todo => 'TODO';

  @override
  String get primary_sources_screen => 'Primary Sources';

  @override
  String get primary_sources_header => 'Click on the image to open';

  @override
  String get strongs_dictionary_screen => 'Strong\'s Dictionary';

  @override
  String get strongs_dictionary_header => 'Greek word meanings and usage';

  @override
  String get allusion_search_screen => 'Allusion Search';

  @override
  String get allusion_search_header => 'Connections with biblical texts';

  @override
  String get bible_screen => 'Bible';

  @override
  String get bible_header => 'Reading and studying Scripture';

  @override
  String get bible_module => 'Module';

  @override
  String get bible_book => 'Book';

  @override
  String get bible_chapter => 'Chapter';

  @override
  String get bible_verse => 'Verse';

  @override
  String get bible_loading => 'Opening Bible...';

  @override
  String get bible_loading_chapter => 'Loading chapter...';

  @override
  String get bible_loading_module => 'Downloading and opening module...';

  @override
  String get bible_no_modules =>
      'Bible modules were not found. Update databases or add bible_*.sqlite to the local data folder.';

  @override
  String get bible_previous_chapter => 'Previous chapter';

  @override
  String get bible_next_chapter => 'Next chapter';

  @override
  String get bible_strong_toggle_label => 'Strong';

  @override
  String get bible_module_info => 'Module information';

  @override
  String get bible_module_info_code => 'Code';

  @override
  String get bible_module_info_module_id => 'Module ID';

  @override
  String get bible_module_info_title => 'Title';

  @override
  String get bible_module_info_description => 'Description';

  @override
  String get bible_module_info_language => 'Language';

  @override
  String get bible_module_info_canon => 'Canon';

  @override
  String get bible_module_info_versification => 'Versification';

  @override
  String get bible_module_info_license => 'License';

  @override
  String get bible_module_info_source_summary => 'Source';

  @override
  String get bible_copy_selected_verses => 'Copy selected verses';

  @override
  String get bible_selected_verses_copied =>
      'Selected verses copied to the clipboard.';

  @override
  String get bible_open_parallel_reader => 'Open parallel Bible reader';

  @override
  String get bible_close_parallel_reader => 'Close parallel reader';

  @override
  String get bible_linked_navigation => 'Linked navigation';

  @override
  String get bible_unlinked_navigation => 'Independent navigation';

  @override
  String get revelation_structure_screen => 'Revelation Structure';

  @override
  String get revelation_structure_header =>
      'Book outline and narrative structure';

  @override
  String get historical_background_screen => 'Historical Background';

  @override
  String get historical_background_header =>
      'Key events in church and world history';

  @override
  String get practical_faith_screen => 'Practical Faith';

  @override
  String get practical_faith_header => 'Reflection and application';

  @override
  String planned_feature_message(String featureTitle) {
    return 'The $featureTitle page is planned for a future version.';
  }

  @override
  String get settings_screen => 'Settings';

  @override
  String get settings_header => 'Saving automatically';

  @override
  String get about_screen => 'About';

  @override
  String get about_header => 'General Information About the Application';

  @override
  String get download => 'Download';

  @override
  String get download_header => 'Install the application for your platform';

  @override
  String get download_android => 'Android';

  @override
  String get download_windows => 'Windows';

  @override
  String get download_linux => 'Linux';

  @override
  String get download_google_play => 'Google Play';

  @override
  String get download_microsoft_store => 'Microsoft Store';

  @override
  String get download_snapcraft => 'Snapcraft';

  @override
  String file_saved_at(Object path) {
    return 'Saved: $path';
  }

  @override
  String get error_loading_libraries => 'Error loading libraries';

  @override
  String get error_loading_institutions => 'Error loading institutions';

  @override
  String get error_loading_recommendations => 'Error loading recommendations';

  @override
  String get error_loading_topics => 'Error loading topics';

  @override
  String get error_loading_primary_sources => 'Error loading primary sources';

  @override
  String get changelog => 'Changelog';

  @override
  String get close => 'Close';

  @override
  String get error => 'Error';

  @override
  String get attention => 'Attention';

  @override
  String get info => 'Information';

  @override
  String get more_information => 'More information';

  @override
  String get unable_to_follow_the_link => 'Unable to follow the link';

  @override
  String get language => 'Language';

  @override
  String get color_theme => 'Color theme';

  @override
  String get manuscript_color_theme => 'Manuscript';

  @override
  String get forest_color_theme => 'Forest';

  @override
  String get sky_color_theme => 'Sky';

  @override
  String get grape_color_theme => 'Grape';

  @override
  String get font_size => 'Font size';

  @override
  String get small_font_size => 'Small';

  @override
  String get medium_font_size => 'Medium';

  @override
  String get large_font_size => 'Large';

  @override
  String get sound => 'Sound';

  @override
  String get on => 'On';

  @override
  String get off => 'Off';

  @override
  String get vectors => 'Vectors';

  @override
  String get icons => 'Icons';

  @override
  String get and => 'and';

  @override
  String get by => 'by';

  @override
  String get package => 'Package';

  @override
  String get font => 'Font';

  @override
  String get wikipedia => 'Wikipedia';

  @override
  String get intf => 'INTF';

  @override
  String get image_source => 'Image source';

  @override
  String get topic => 'Topic';

  @override
  String get show_more => 'show more information';

  @override
  String get hide => 'hide';

  @override
  String get full_primary_sources => 'Contain the entire Revelation in full';

  @override
  String get significant_primary_sources =>
      'Contain a significant part of the Revelation';

  @override
  String get fragments_primary_sources =>
      'Contain small fragments of the Revelation';

  @override
  String get verses => 'Quantity of verses';

  @override
  String get choose_page => 'Choose page';

  @override
  String get images_are_missing => 'Images are missing';

  @override
  String get image_not_loaded => 'Image not loaded';

  @override
  String get primary_source_word_source_unavailable =>
      'Primary source unavailable';

  @override
  String get primary_source_word_page_unavailable => 'Page unavailable';

  @override
  String get primary_source_word_word_unavailable => 'Word unavailable';

  @override
  String get primary_source_word_image_unavailable => 'Image unavailable';

  @override
  String get primary_source_words_image_hint =>
      'Tap the image to see the word in the primary source.';

  @override
  String get click_for_info =>
      'Click on the image element you’re interested in to get information about it.';

  @override
  String get low_quality => 'Quality reduced';

  @override
  String get low_quality_message =>
      'A lower-quality image is used in the mobile browser. To view in maximum quality, install the app or open the page on a computer.';

  @override
  String get reload_image => 'Reloading the image';

  @override
  String get zoom_in => 'Zoom in';

  @override
  String get zoom_out => 'Zoom out';

  @override
  String get restore_original_scale => 'Original scale';

  @override
  String get toggle_negative => 'Negative';

  @override
  String get toggle_monochrome => 'Monochrome';

  @override
  String get brightness_contrast => 'Brightness, Contrast';

  @override
  String get brightness => 'Brightness';

  @override
  String get contrast => 'Contrast';

  @override
  String get ok => 'OK';

  @override
  String get cancel => 'Сancel';

  @override
  String get reset => 'Reset';

  @override
  String get area => 'Area';

  @override
  String get size => 'Size';

  @override
  String get not_selected => 'Not selected';

  @override
  String get area_selection => 'Area selection';

  @override
  String get color_replacement => 'Color replacement';

  @override
  String get color_to_replace => 'Color to replace';

  @override
  String get eyedropper => 'Color selection';

  @override
  String get new_color => 'New color';

  @override
  String get palette => 'Palette';

  @override
  String get select_color => 'Select color';

  @override
  String get select_area_header => 'Select an area on the image';

  @override
  String get select_area_description =>
      'Select a rectangular area on the image: touch the starting point, drag, and release. You can zoom in if needed.';

  @override
  String get pick_color_header => 'Select a point on the image';

  @override
  String get pick_color_description =>
      'Click on the area of the image where you want to pick a color. You can zoom in and move the image if needed.';

  @override
  String get tolerance => 'Tolerance';

  @override
  String get replace_color_message =>
      'On the first call, generating the pixel matrix will take some time.';

  @override
  String get page_settings_reset => 'Page settings reset';

  @override
  String get toggle_show_word_separators => 'Word separators';

  @override
  String get toggle_show_strong_numbers => 'Strong\'s numbers';

  @override
  String get toggle_show_verse_numbers => 'Verse numbers';

  @override
  String get strong_number => 'Strong’s number';

  @override
  String get strong_picker_unavailable_numbers =>
      '2717 and 3203-3302 are unavailable';

  @override
  String get strong_dictionary_search => 'Full-text search';

  @override
  String get strong_dictionary_search_hint => '#/word/translation';

  @override
  String get strong_dictionary_no_entries =>
      'Strong’s dictionary entries are unavailable';

  @override
  String get strong_dictionary_no_results => 'No matching entries';

  @override
  String get greek_keyboard_tooltip => 'Greek keyboard';

  @override
  String get strong_pronunciation => 'Pronunciation';

  @override
  String get strong_synonyms => 'Synonyms';

  @override
  String get strong_origin => 'Word analysis';

  @override
  String get strong_usage => 'Usage';

  @override
  String get strong_reference_commentary =>
      'Translation source: https://github.com/openscriptures/strongs';

  @override
  String get strong_origin_tooltip =>
      'Word analysis may include the following elements: derivatives, comparative words, phrases, and related words.';

  @override
  String get strong_part_of_speech => 'Part of speech';

  @override
  String get strong_indeclNumAdj => 'indeclinable numeral (adjective)';

  @override
  String get strong_indeclLetN => 'indeclinable letter (noun)';

  @override
  String get strong_indeclinable => 'indeclinable';

  @override
  String get strong_adj => 'adjective';

  @override
  String get strong_advCor => 'adverb, correlative';

  @override
  String get strong_advInt => 'adverb, interrogative';

  @override
  String get strong_advNeg => 'adverb, negative';

  @override
  String get strong_advSup => 'adverb, superlative';

  @override
  String get strong_adv => 'adverb';

  @override
  String get strong_comp => 'comparative';

  @override
  String get strong_aramaicTransWord => 'aramaic transliterated word';

  @override
  String get strong_hebrewForm => 'hebrew form';

  @override
  String get strong_hebrewNoun => 'hebrew noun';

  @override
  String get strong_hebrew => 'hebrew';

  @override
  String get strong_location => 'location';

  @override
  String get strong_properNoun => 'proper noun';

  @override
  String get strong_noun => 'noun';

  @override
  String get strong_masc => 'masculine';

  @override
  String get strong_fem => 'feminine';

  @override
  String get strong_neut => 'neuter';

  @override
  String get strong_plur => 'plural';

  @override
  String get strong_otherType => 'other Type';

  @override
  String get strong_verbImp => 'verb (imperative)';

  @override
  String get strong_verb => 'verb';

  @override
  String get strong_pronDat => 'pronoun, dative case';

  @override
  String get strong_pronPoss => 'possessive pronoun';

  @override
  String get strong_pronPers => 'personal pronoun';

  @override
  String get strong_pronRecip => 'reciprocal pronoun';

  @override
  String get strong_pronRefl => 'reflexive pronoun';

  @override
  String get strong_pronRel => 'relative pronoun';

  @override
  String get strong_pronCorrel => 'correlative pronoun';

  @override
  String get strong_pronIndef => 'indefinite pronoun';

  @override
  String get strong_pronInterr => 'interrogative pronoun';

  @override
  String get strong_pronDem => 'demonstrative pronoun';

  @override
  String get strong_pron => 'pronoun';

  @override
  String get strong_particleCond => 'conditional particle';

  @override
  String get strong_particleDisj => 'disjunctive particle';

  @override
  String get strong_particleInterr => 'interrogative particle';

  @override
  String get strong_particleNeg => 'negative particle';

  @override
  String get strong_particle => 'particle';

  @override
  String get strong_interj => 'interjection';

  @override
  String get strong_participle => 'participle';

  @override
  String get strong_prefix => 'prefix';

  @override
  String get strong_prep => 'preposition';

  @override
  String get strong_artDef => 'definite article';

  @override
  String get strong_phraseIdi => 'phrase (idiomatic expression)';

  @override
  String get strong_phrase => 'phrase';

  @override
  String get strong_conjNeg => 'negative conjunction';

  @override
  String get strong_conj => 'conjunction';

  @override
  String get strong_or => 'or';

  @override
  String get markdown_unknown_block_title => 'Unsupported content block';

  @override
  String markdown_unknown_block_description(String blockName) {
    return 'This version of the app cannot display the `$blockName` block.';
  }

  @override
  String get markdown_unknown_block_update_hint =>
      'Open the downloads page to install a newer app version for your platform.';

  @override
  String get markdown_unknown_block_update_action => 'Update app';

  @override
  String get markdown_youtube_player_title => 'Embedded YouTube video';

  @override
  String get markdown_youtube_unavailable_title => 'YouTube video unavailable';

  @override
  String get markdown_youtube_unavailable_description =>
      'This YouTube block could not be rendered in the embedded player.';

  @override
  String get markdown_image_loading => 'Loading image...';

  @override
  String get copy_content => 'Copy content';

  @override
  String get export_pdf_content => 'Export to PDF';

  @override
  String get markdown_copied => 'Content copied to the clipboard.';

  @override
  String get markdown_copy_failed => 'Couldn\'t copy the content.';

  @override
  String get markdown_pdf_export_failed => 'Couldn\'t export the PDF.';

  @override
  String get previous_description_item => 'Previous item';

  @override
  String get next_description_item => 'Next item';

  @override
  String get previous_word => 'Previous word';

  @override
  String get next_word => 'Next word';

  @override
  String get previous_verse => 'Previous verse';

  @override
  String get next_verse => 'Next verse';

  @override
  String get previous_dictionary_entry => 'Previous dictionary entry';

  @override
  String get next_dictionary_entry => 'Next dictionary entry';

  @override
  String markdown_images_loading_progress(int loaded, int total) {
    return 'Loading images: $loaded of $total';
  }

  @override
  String get book_code_1 => 'Gen';

  @override
  String get book_name_1 => 'Genesis';

  @override
  String get book_code_2 => 'Exod';

  @override
  String get book_name_2 => 'Exodus';

  @override
  String get book_code_3 => 'Lev';

  @override
  String get book_name_3 => 'Leviticus';

  @override
  String get book_code_4 => 'Num';

  @override
  String get book_name_4 => 'Numbers';

  @override
  String get book_code_5 => 'Deut';

  @override
  String get book_name_5 => 'Deuteronomy';

  @override
  String get book_code_6 => 'Josh';

  @override
  String get book_name_6 => 'Joshua';

  @override
  String get book_code_7 => 'Judg';

  @override
  String get book_name_7 => 'Judges';

  @override
  String get book_code_8 => 'Ruth';

  @override
  String get book_name_8 => 'Ruth';

  @override
  String get book_code_9 => '1Sam';

  @override
  String get book_name_9 => '1 Samuel';

  @override
  String get book_code_10 => '2Sam';

  @override
  String get book_name_10 => '2 Samuel';

  @override
  String get book_code_11 => '1Kgs';

  @override
  String get book_name_11 => '1 Kings';

  @override
  String get book_code_12 => '2Kgs';

  @override
  String get book_name_12 => '2 Kings';

  @override
  String get book_code_13 => '1Chr';

  @override
  String get book_name_13 => '1 Chronicles';

  @override
  String get book_code_14 => '2Chr';

  @override
  String get book_name_14 => '2 Chronicles';

  @override
  String get book_code_15 => 'Ezra';

  @override
  String get book_name_15 => 'Ezra';

  @override
  String get book_code_16 => 'Neh';

  @override
  String get book_name_16 => 'Nehemiah';

  @override
  String get book_code_17 => 'Esth';

  @override
  String get book_name_17 => 'Esther';

  @override
  String get book_code_18 => 'Job';

  @override
  String get book_name_18 => 'Job';

  @override
  String get book_code_19 => 'Ps';

  @override
  String get book_name_19 => 'Psalms';

  @override
  String get book_code_20 => 'Prov';

  @override
  String get book_name_20 => 'Proverbs';

  @override
  String get book_code_21 => 'Eccl';

  @override
  String get book_name_21 => 'Ecclesiastes';

  @override
  String get book_code_22 => 'Song';

  @override
  String get book_name_22 => 'Song of Songs';

  @override
  String get book_code_23 => 'Isa';

  @override
  String get book_name_23 => 'Isaiah';

  @override
  String get book_code_24 => 'Jer';

  @override
  String get book_name_24 => 'Jeremiah';

  @override
  String get book_code_25 => 'Lam';

  @override
  String get book_name_25 => 'Lamentations';

  @override
  String get book_code_26 => 'Ezek';

  @override
  String get book_name_26 => 'Ezekiel';

  @override
  String get book_code_27 => 'Dan';

  @override
  String get book_name_27 => 'Daniel';

  @override
  String get book_code_28 => 'Hos';

  @override
  String get book_name_28 => 'Hosea';

  @override
  String get book_code_29 => 'Joel';

  @override
  String get book_name_29 => 'Joel';

  @override
  String get book_code_30 => 'Amos';

  @override
  String get book_name_30 => 'Amos';

  @override
  String get book_code_31 => 'Obad';

  @override
  String get book_name_31 => 'Obadiah';

  @override
  String get book_code_32 => 'Jonah';

  @override
  String get book_name_32 => 'Jonah';

  @override
  String get book_code_33 => 'Mic';

  @override
  String get book_name_33 => 'Micah';

  @override
  String get book_code_34 => 'Nah';

  @override
  String get book_name_34 => 'Nahum';

  @override
  String get book_code_35 => 'Hab';

  @override
  String get book_name_35 => 'Habakkuk';

  @override
  String get book_code_36 => 'Zeph';

  @override
  String get book_name_36 => 'Zephaniah';

  @override
  String get book_code_37 => 'Hag';

  @override
  String get book_name_37 => 'Haggai';

  @override
  String get book_code_38 => 'Zech';

  @override
  String get book_name_38 => 'Zechariah';

  @override
  String get book_code_39 => 'Mal';

  @override
  String get book_name_39 => 'Malachi';

  @override
  String get book_code_40 => 'Mat';

  @override
  String get book_name_40 => 'Matthew';

  @override
  String get book_code_41 => 'Mark';

  @override
  String get book_name_41 => 'Mark';

  @override
  String get book_code_42 => 'Luke';

  @override
  String get book_name_42 => 'Luke';

  @override
  String get book_code_43 => 'John';

  @override
  String get book_name_43 => 'John';

  @override
  String get book_code_44 => 'Acts';

  @override
  String get book_name_44 => 'Acts';

  @override
  String get book_code_45 => 'Rom';

  @override
  String get book_name_45 => 'Romans';

  @override
  String get book_code_46 => '1Cor';

  @override
  String get book_name_46 => '1 Corinthians';

  @override
  String get book_code_47 => '2Cor';

  @override
  String get book_name_47 => '2 Corinthians';

  @override
  String get book_code_48 => 'Gal';

  @override
  String get book_name_48 => 'Galatians';

  @override
  String get book_code_49 => 'Eph';

  @override
  String get book_name_49 => 'Ephesians';

  @override
  String get book_code_50 => 'Phil';

  @override
  String get book_name_50 => 'Philippians';

  @override
  String get book_code_51 => 'Col';

  @override
  String get book_name_51 => 'Colossians';

  @override
  String get book_code_52 => '1Thess';

  @override
  String get book_name_52 => '1 Thessalonians';

  @override
  String get book_code_53 => '2Thess';

  @override
  String get book_name_53 => '2 Thessalonians';

  @override
  String get book_code_54 => '1Tim';

  @override
  String get book_name_54 => '1 Timothy';

  @override
  String get book_code_55 => '2Tim';

  @override
  String get book_name_55 => '2 Timothy';

  @override
  String get book_code_56 => 'Titus';

  @override
  String get book_name_56 => 'Titus';

  @override
  String get book_code_57 => 'Phlm';

  @override
  String get book_name_57 => 'Philemon';

  @override
  String get book_code_58 => 'Heb';

  @override
  String get book_name_58 => 'Hebrews';

  @override
  String get book_code_59 => 'Jas';

  @override
  String get book_name_59 => 'James';

  @override
  String get book_code_60 => '1Pet';

  @override
  String get book_name_60 => '1 Peter';

  @override
  String get book_code_61 => '2Pet';

  @override
  String get book_name_61 => '2 Peter';

  @override
  String get book_code_62 => '1John';

  @override
  String get book_name_62 => '1 John';

  @override
  String get book_code_63 => '2John';

  @override
  String get book_name_63 => '2 John';

  @override
  String get book_code_64 => '3John';

  @override
  String get book_name_64 => '3 John';

  @override
  String get book_code_65 => 'Jude';

  @override
  String get book_name_65 => 'Jude';

  @override
  String get book_code_66 => 'Rev';

  @override
  String get book_name_66 => 'Revelation';
}
