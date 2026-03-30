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
  String get strongsConcordance => 'Strong\'s Concordance';

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
  String get strong_pronunciation => 'Pronunciation';

  @override
  String get strong_synonyms => 'Synonyms';

  @override
  String get strong_origin => 'Word analysis';

  @override
  String get strong_usage => 'Usage';

  @override
  String get strong_reference_commentary =>
      'Translation source: https://github.com/openscriptures/strongs\nWord analysis may include the following elements: derivatives, comparative words, phrases, and related words.';

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
  String get markdown_image_loading => 'Loading image...';

  @override
  String markdown_images_loading_progress(int loaded, int total) {
    return 'Loading images: $loaded of $total';
  }
}
