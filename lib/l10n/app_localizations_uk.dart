// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Ukrainian (`uk`).
class AppLocalizationsUk extends AppLocalizations {
  AppLocalizationsUk([String locale = 'uk']) : super(locale);

  @override
  String get app_name => 'Об\'явлення';

  @override
  String get startup_title => 'Запуск застосунку...';

  @override
  String get startup_step_preparing => 'Підготовка застосунку';

  @override
  String get startup_step_loading_settings => 'Завантажуємо ваші налаштування';

  @override
  String get startup_step_initializing_server => 'Підключаємо онлайн-сервіси';

  @override
  String get startup_step_initializing_databases =>
      'Відкриваємо дані застосунку';

  @override
  String get startup_step_configuring_links => 'Підготовка словника Стронга';

  @override
  String startup_progress(int current, int total) {
    return 'Крок $current з $total';
  }

  @override
  String get startup_error => 'Не вдалося запустити застосунок :(';

  @override
  String get startup_retry => 'Спробувати ще раз';

  @override
  String startup_version_build(String version, String build) {
    return 'Версія $version ($build)';
  }

  @override
  String get version => 'Версія застосунку:';

  @override
  String get app_version_from => 'Версія застосунку від';

  @override
  String get common_data_update => 'Версія даних';

  @override
  String localized_data_update(String language) {
    return 'Версія даних $language мовою';
  }

  @override
  String get data_version_from => 'від';

  @override
  String get language_name_en => 'англійською';

  @override
  String get language_name_es => 'іспанською';

  @override
  String get language_name_uk => 'українською';

  @override
  String get language_name_ru => 'російською';

  @override
  String get app_description => 'Додаток для вивчення Об\'явлення.';

  @override
  String get website => 'Revelation.website';

  @override
  String get github_project => 'GitHub проект';

  @override
  String get privacy_policy => 'Політика конфіденційності';

  @override
  String get license => 'Ліцензія';

  @override
  String get support_us => 'Підтримайте нас';

  @override
  String get installation_packages => 'Інсталяційні пакети';

  @override
  String get acknowledgements_title => 'Подяки';

  @override
  String get acknowledgements_description_1 =>
      'Насамперед хочу подякувати Богові за життя; своїй дружині Іринці - за любов і турботу; і мамі - за допомогу та підтримку.\nТакож моя щира вдячність установам за наданий доступ до інформації та безцінних рукописів:';

  @override
  String get acknowledgements_description_2 =>
      'Велика подяка творцям наступного ПЗ та ресурсів:';

  @override
  String get recommended_title => 'Рекомендоване';

  @override
  String get recommended_description =>
      'Рекомендовані ресурси для вивчення Об\'явлення та Біблії загалом:';

  @override
  String get bug_report => 'Повідомити про помилку';

  @override
  String get tools => 'Інструменти';

  @override
  String get refresh_databases => 'Оновити бази даних';

  @override
  String get databases_refreshed => 'Бази даних оновлено';

  @override
  String get databases_up_to_date =>
      'Файли БД актуальні. Оновлення не потрібне.';

  @override
  String get database_size_mismatch =>
      'Розміри деяких файлів БД не відповідають маніфесту. Спробуйте оновити бази даних ще раз.';

  @override
  String get database_refresh_failed => 'Не вдалося оновити бази даних';

  @override
  String get show_local_folder => 'Показати локальну папку';

  @override
  String get local_folder_open_failed => 'Не вдалося відкрити локальну папку';

  @override
  String get clear_cache => 'Очистити кеш';

  @override
  String get cache_cleared => 'Кеш очищено';

  @override
  String get cache_clear_failed => 'Не вдалося очистити кеш';

  @override
  String get log_copied_message =>
      'Логи скопійовано до буфера обміну. Будь ласка, надішліть їх мені:';

  @override
  String get bug_report_wish =>
      'Будь ласка, коротко опишіть помилку та вставте в лист технічну інформацію, яку застосунок щойно автоматично скопіював до буфера обміну (це важливо!). Якщо можливо, додайте до повідомлення знімок екрана. Дякуємо, ви допомагаєте зробити додаток кращим.';

  @override
  String get all_rights_reserved => 'Усі права захищені';

  @override
  String get ad_loading => 'Завантаження реклами...';

  @override
  String get menu => 'Меню';

  @override
  String get close_app => 'Закрити програму';

  @override
  String get todo => 'ЗРОБИТИ';

  @override
  String get primary_sources_screen => 'Першоджерела';

  @override
  String get primary_sources_header => 'Натисніть на зображення щоб відкрити';

  @override
  String get strongs_dictionary_screen => 'Словник Стронґа';

  @override
  String get strongs_dictionary_header =>
      'Значення грецьких слів та їх використання';

  @override
  String get allusion_search_screen => 'Пошук алюзій';

  @override
  String get allusion_search_header => 'Зв\'язки з біблійними текстами';

  @override
  String get bible_screen => 'Біблія';

  @override
  String get bible_header => 'Читання і вивчення Писання';

  @override
  String get bible_module => 'Модуль';

  @override
  String get bible_book => 'Книга';

  @override
  String get bible_chapter => 'Розділ';

  @override
  String get bible_verse => 'Вірш';

  @override
  String get bible_loading => 'Відкриваємо Біблію...';

  @override
  String get bible_loading_chapter => 'Завантажуємо розділ...';

  @override
  String get bible_loading_module => 'Завантажуємо й відкриваємо модуль...';

  @override
  String get bible_no_modules =>
      'Модулі Біблії не знайдено. Оновіть бази даних або додайте bible_*.sqlite до локальної папки даних.';

  @override
  String get bible_previous_chapter => 'Попередній розділ';

  @override
  String get bible_next_chapter => 'Наступний розділ';

  @override
  String get bible_strong_toggle_label => 'Стронґ';

  @override
  String get bible_module_info => 'Інформація про модуль';

  @override
  String get bible_module_info_code => 'Код';

  @override
  String get bible_module_info_module_id => 'ID модуля';

  @override
  String get bible_module_info_title => 'Назва';

  @override
  String get bible_module_info_description => 'Опис';

  @override
  String get bible_module_info_language => 'Мова';

  @override
  String get bible_module_info_canon => 'Канон';

  @override
  String get bible_module_info_versification => 'Версифікація';

  @override
  String get bible_module_info_license => 'Ліцензія';

  @override
  String get bible_module_info_source_summary => 'Джерело';

  @override
  String get bible_copy_selected_verses => 'Копіювати вибрані вірші';

  @override
  String get bible_selected_verses_copied =>
      'Вибрані вірші скопійовано в буфер обміну.';

  @override
  String get revelation_structure_screen => 'Структура Об\'явлення';

  @override
  String get revelation_structure_header => 'План книги та структура оповіді';

  @override
  String get historical_background_screen => 'Історична довідка';

  @override
  String get historical_background_header =>
      'Ключові події з історії церкви та світу';

  @override
  String get practical_faith_screen => 'Практична віра';

  @override
  String get practical_faith_header => 'Роздуми і застосування';

  @override
  String planned_feature_message(String featureTitle) {
    return 'Сторінку «$featureTitle» планується реалізувати в одній із майбутніх версій.';
  }

  @override
  String get settings_screen => 'Налаштування';

  @override
  String get settings_header => 'Зберігаються автоматично';

  @override
  String get about_screen => 'Про програму';

  @override
  String get about_header => 'Загальна інформація про застосунок';

  @override
  String get download => 'Завантажити';

  @override
  String get download_header => 'Встановіть застосунок для вашої платформи';

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
    return 'Збережено: $path';
  }

  @override
  String get error_loading_libraries => 'Помилка завантаження бібліотек';

  @override
  String get error_loading_institutions => 'Помилка завантаження установ';

  @override
  String get error_loading_recommendations =>
      'Помилка завантаження рекомендацій';

  @override
  String get error_loading_topics => 'Помилка завантаження тем';

  @override
  String get error_loading_primary_sources =>
      'Помилка завантаження першоджерел';

  @override
  String get changelog => 'Журнал змін (en)';

  @override
  String get close => 'Закрити';

  @override
  String get error => 'Помилка';

  @override
  String get attention => 'Увага';

  @override
  String get info => 'Інформація';

  @override
  String get more_information => 'Більше інформації';

  @override
  String get unable_to_follow_the_link => 'Неможливо перейти за посиланням';

  @override
  String get language => 'Мова';

  @override
  String get color_theme => 'Кольорова тема';

  @override
  String get manuscript_color_theme => 'Рукопис';

  @override
  String get forest_color_theme => 'Ліс';

  @override
  String get sky_color_theme => 'Небо';

  @override
  String get grape_color_theme => 'Виноград';

  @override
  String get font_size => 'Розмір шрифту';

  @override
  String get small_font_size => 'Маленький';

  @override
  String get medium_font_size => 'Середній';

  @override
  String get large_font_size => 'Великий';

  @override
  String get sound => 'Звук';

  @override
  String get on => 'Увімкнено';

  @override
  String get off => 'Вимкнено';

  @override
  String get vectors => 'Вектори';

  @override
  String get icons => 'Іконки';

  @override
  String get and => 'і';

  @override
  String get by => 'від';

  @override
  String get package => 'Пакет';

  @override
  String get font => 'Шрифт';

  @override
  String get wikipedia => 'Вікіпедія';

  @override
  String get intf => 'INTF';

  @override
  String get image_source => 'Джерело зображень';

  @override
  String get topic => 'Тема';

  @override
  String get show_more => 'показати більше інформації';

  @override
  String get hide => 'приховати';

  @override
  String get full_primary_sources => 'Містять все Об\'явлення повністю';

  @override
  String get significant_primary_sources =>
      'Містять значну частину Об\'явлення';

  @override
  String get fragments_primary_sources =>
      'Містять невеликі фрагменти Об\'явлення';

  @override
  String get verses => 'Кількість віршів';

  @override
  String get choose_page => 'Оберіть стрінку';

  @override
  String get images_are_missing => 'Зображення відсутні';

  @override
  String get image_not_loaded => 'Зображення не завантажено';

  @override
  String get primary_source_word_source_unavailable =>
      'Першоджерело недоступне';

  @override
  String get primary_source_word_page_unavailable => 'Сторінка недоступна';

  @override
  String get primary_source_word_word_unavailable => 'Слово недоступне';

  @override
  String get primary_source_word_image_unavailable => 'Зображення недоступне';

  @override
  String get primary_source_words_image_hint =>
      'Натисніть на зображення, щоб побачити слово в першоджерелі.';

  @override
  String get click_for_info =>
      'Натисніть на потрібний вам елемент зображення, щоб отримати інформацію про нього.';

  @override
  String get low_quality => 'Якість знижено';

  @override
  String get low_quality_message =>
      'У мобільному браузері використовується зображення зниженої якості. Щоб переглянути в максимальній якості, встановіть застосунок або відкрийте сторінку на комп’ютері.';

  @override
  String get reload_image => 'Перезавантаження';

  @override
  String get zoom_in => 'Збільшення';

  @override
  String get zoom_out => 'Зменшення';

  @override
  String get restore_original_scale => 'Початковий масштаб';

  @override
  String get toggle_negative => 'Негатив';

  @override
  String get toggle_monochrome => 'Монохромність';

  @override
  String get brightness_contrast => 'Яскравість, контрастність';

  @override
  String get brightness => 'Яскравість';

  @override
  String get contrast => 'Контрастність';

  @override
  String get ok => 'OK';

  @override
  String get cancel => 'Скасувати';

  @override
  String get reset => 'Скинути';

  @override
  String get area => 'Область';

  @override
  String get size => 'Розмір';

  @override
  String get not_selected => 'Не виділена';

  @override
  String get area_selection => 'Виділення області';

  @override
  String get color_replacement => 'Заміна кольору';

  @override
  String get color_to_replace => 'Колір для заміни';

  @override
  String get eyedropper => 'Обирання кольору';

  @override
  String get new_color => 'Новий колір';

  @override
  String get palette => 'Палітра';

  @override
  String get select_color => 'Виберіть колір';

  @override
  String get select_area_header => 'Виберіть область на зображенні';

  @override
  String get select_area_description =>
      'Виділіть прямокутну область на зображенні: торкніться початкової точки, проведіть і відпустіть. За потреби ви можете збільшити зображення.';

  @override
  String get pick_color_header => 'Виберіть точку на зображенні';

  @override
  String get pick_color_description =>
      'Натисніть на ділянку зображення, з якої ви хочете вибрати колір. За потреби можна збільшити або пересунути зображення.';

  @override
  String get tolerance => 'Допуск';

  @override
  String get replace_color_message =>
      'При першому виклику формування матриці пікселів займе певний час.';

  @override
  String get page_settings_reset => 'Скидання налаштувань';

  @override
  String get toggle_show_word_separators => 'Роздільники слів';

  @override
  String get toggle_show_strong_numbers => 'Номери Стронґа';

  @override
  String get toggle_show_verse_numbers => 'Номери віршів';

  @override
  String get strong_number => 'Номер Стронґа';

  @override
  String get strong_picker_unavailable_numbers => '2717 і 3203-3302 недоступні';

  @override
  String get strong_dictionary_search => 'Повнотекстовий пошук';

  @override
  String get strong_dictionary_search_hint => '#/слово/переклад';

  @override
  String get strong_dictionary_no_entries =>
      'Статті словника Стронґа недоступні';

  @override
  String get strong_dictionary_no_results => 'Немає відповідних статей';

  @override
  String get greek_keyboard_tooltip => 'Грецька клавіатура';

  @override
  String get strong_pronunciation => 'Вимова';

  @override
  String get strong_synonyms => 'Синоніми';

  @override
  String get strong_origin => 'Аналіз слова';

  @override
  String get strong_usage => 'Використання';

  @override
  String get strong_reference_commentary =>
      'Джерело перекладу: здійснено за допомогою ChatGPT';

  @override
  String get strong_origin_tooltip =>
      'Аналіз слова може включати такі посилання: похідні форми, слова для порівняння, словосполучення та пов’язані слова.';

  @override
  String get strong_part_of_speech => 'Частина мови';

  @override
  String get strong_indeclNumAdj =>
      'незмінний числівник (у функції прикметника)';

  @override
  String get strong_indeclLetN => 'незмінна буква (іменник)';

  @override
  String get strong_indeclinable => 'незмінне';

  @override
  String get strong_adj => 'прикметник';

  @override
  String get strong_advCor => 'співвідносний прислівник';

  @override
  String get strong_advInt => 'питальний прислівник';

  @override
  String get strong_advNeg => 'заперечний прислівник';

  @override
  String get strong_advSup => 'прислівник, найвищий ступінь';

  @override
  String get strong_adv => 'прислівник';

  @override
  String get strong_comp => 'ступінь порівняння';

  @override
  String get strong_aramaicTransWord => 'транслитероване арамейське слово';

  @override
  String get strong_hebrewForm => 'форма на івриті';

  @override
  String get strong_hebrewNoun => 'іменник на івриті';

  @override
  String get strong_hebrew => 'іврит';

  @override
  String get strong_location => 'географічна назва';

  @override
  String get strong_properNoun => 'власна назва';

  @override
  String get strong_noun => 'іменник';

  @override
  String get strong_masc => 'чоловічий рід';

  @override
  String get strong_fem => 'жіночий рід';

  @override
  String get strong_neut => 'середній рід';

  @override
  String get strong_plur => 'множина';

  @override
  String get strong_otherType => 'інший тип';

  @override
  String get strong_verbImp => 'дієслово (наказовий спосіб)';

  @override
  String get strong_verb => 'дієслово';

  @override
  String get strong_pronDat => 'займенник, давальний відмінок';

  @override
  String get strong_pronPoss => 'присвійний займенник';

  @override
  String get strong_pronPers => 'особовий займенник';

  @override
  String get strong_pronRecip => 'взаємний займенник';

  @override
  String get strong_pronRefl => 'зворотний займенник';

  @override
  String get strong_pronRel => 'відносний займенник';

  @override
  String get strong_pronCorrel => 'співвідносний займенник';

  @override
  String get strong_pronIndef => 'неозначений займенник';

  @override
  String get strong_pronInterr => 'питальний займенник';

  @override
  String get strong_pronDem => 'вказівний займенник';

  @override
  String get strong_pron => 'займенник';

  @override
  String get strong_particleCond => 'умовна частка';

  @override
  String get strong_particleDisj => 'роздільна частка';

  @override
  String get strong_particleInterr => 'питальна частка';

  @override
  String get strong_particleNeg => 'заперечна частка';

  @override
  String get strong_particle => 'частка';

  @override
  String get strong_interj => 'вигук';

  @override
  String get strong_participle => 'дієприкметник';

  @override
  String get strong_prefix => 'префікс';

  @override
  String get strong_prep => 'прийменник';

  @override
  String get strong_artDef => 'означений артикль';

  @override
  String get strong_phraseIdi => 'фраза (ідіоматичний вираз)';

  @override
  String get strong_phrase => 'фраза';

  @override
  String get strong_conjNeg => 'заперечний сполучник';

  @override
  String get strong_conj => 'сполучник';

  @override
  String get strong_or => 'або';

  @override
  String get markdown_unknown_block_title => 'Непідтримуваний блок вмісту';

  @override
  String markdown_unknown_block_description(String blockName) {
    return 'Ця версія застосунку не вміє відображати блок `$blockName`.';
  }

  @override
  String get markdown_unknown_block_update_hint =>
      'Відкрийте сторінку завантажень, щоб установити новішу версію застосунку для вашої платформи.';

  @override
  String get markdown_unknown_block_update_action => 'Оновити застосунок';

  @override
  String get markdown_youtube_player_title => 'Вбудоване YouTube-відео';

  @override
  String get markdown_youtube_unavailable_title => 'YouTube-відео недоступне';

  @override
  String get markdown_youtube_unavailable_description =>
      'Не вдалося відобразити цей блок YouTube у вбудованому плеєрі.';

  @override
  String get markdown_image_loading => 'Завантаження зображення...';

  @override
  String get copy_content => 'Скопіювати вміст';

  @override
  String get export_pdf_content => 'Експортувати в PDF';

  @override
  String get markdown_copied => 'Вміст скопійовано до буфера обміну.';

  @override
  String get markdown_copy_failed => 'Не вдалося скопіювати вміст.';

  @override
  String get markdown_pdf_export_failed => 'Не вдалося експортувати PDF.';

  @override
  String get previous_description_item => 'Попередній елемент';

  @override
  String get next_description_item => 'Наступний елемент';

  @override
  String get previous_word => 'Попереднє слово';

  @override
  String get next_word => 'Наступне слово';

  @override
  String get previous_verse => 'Попередній вірш';

  @override
  String get next_verse => 'Наступний вірш';

  @override
  String get previous_dictionary_entry => 'Попередня словникова стаття';

  @override
  String get next_dictionary_entry => 'Наступна словникова стаття';

  @override
  String markdown_images_loading_progress(int loaded, int total) {
    return 'Завантаження зображень: $loaded із $total';
  }

  @override
  String get book_code_1 => 'Бут';

  @override
  String get book_name_1 => 'Буття';

  @override
  String get book_code_2 => 'Вих';

  @override
  String get book_name_2 => 'Вихід';

  @override
  String get book_code_3 => 'Лев';

  @override
  String get book_name_3 => 'Левит';

  @override
  String get book_code_4 => 'Чис';

  @override
  String get book_name_4 => 'Числа';

  @override
  String get book_code_5 => 'Втор';

  @override
  String get book_name_5 => 'Повторення Закону';

  @override
  String get book_code_6 => 'Нав';

  @override
  String get book_name_6 => 'Ісус Навин';

  @override
  String get book_code_7 => 'Суд';

  @override
  String get book_name_7 => 'Судді';

  @override
  String get book_code_8 => 'Рут';

  @override
  String get book_name_8 => 'Рут';

  @override
  String get book_code_9 => '1Сам';

  @override
  String get book_name_9 => '1 Самуїла';

  @override
  String get book_code_10 => '2Сам';

  @override
  String get book_name_10 => '2 Самуїла';

  @override
  String get book_code_11 => '1Цар';

  @override
  String get book_name_11 => '1 Царів';

  @override
  String get book_code_12 => '2Цар';

  @override
  String get book_name_12 => '2 Царів';

  @override
  String get book_code_13 => '1Хр';

  @override
  String get book_name_13 => '1 Хронік';

  @override
  String get book_code_14 => '2Хр';

  @override
  String get book_name_14 => '2 Хронік';

  @override
  String get book_code_15 => 'Езд';

  @override
  String get book_name_15 => 'Ездра';

  @override
  String get book_code_16 => 'Неєм';

  @override
  String get book_name_16 => 'Неємія';

  @override
  String get book_code_17 => 'Ест';

  @override
  String get book_name_17 => 'Естер';

  @override
  String get book_code_18 => 'Йов';

  @override
  String get book_name_18 => 'Йов';

  @override
  String get book_code_19 => 'Пс';

  @override
  String get book_name_19 => 'Псалми';

  @override
  String get book_code_20 => 'Прип';

  @override
  String get book_name_20 => 'Приповісті';

  @override
  String get book_code_21 => 'Екл';

  @override
  String get book_name_21 => 'Екклезіяст';

  @override
  String get book_code_22 => 'Пісн';

  @override
  String get book_name_22 => 'Пісня над піснями';

  @override
  String get book_code_23 => 'Іс';

  @override
  String get book_name_23 => 'Ісая';

  @override
  String get book_code_24 => 'Єр';

  @override
  String get book_name_24 => 'Єремія';

  @override
  String get book_code_25 => 'Плач';

  @override
  String get book_name_25 => 'Плач Єремії';

  @override
  String get book_code_26 => 'Єз';

  @override
  String get book_name_26 => 'Єзекіїль';

  @override
  String get book_code_27 => 'Дан';

  @override
  String get book_name_27 => 'Даниїл';

  @override
  String get book_code_28 => 'Ос';

  @override
  String get book_name_28 => 'Осія';

  @override
  String get book_code_29 => 'Йоіл';

  @override
  String get book_name_29 => 'Йоіл';

  @override
  String get book_code_30 => 'Ам';

  @override
  String get book_name_30 => 'Амос';

  @override
  String get book_code_31 => 'Авд';

  @override
  String get book_name_31 => 'Авдій';

  @override
  String get book_code_32 => 'Йона';

  @override
  String get book_name_32 => 'Йона';

  @override
  String get book_code_33 => 'Мих';

  @override
  String get book_name_33 => 'Михей';

  @override
  String get book_code_34 => 'Наум';

  @override
  String get book_name_34 => 'Наум';

  @override
  String get book_code_35 => 'Ав';

  @override
  String get book_name_35 => 'Авакум';

  @override
  String get book_code_36 => 'Соф';

  @override
  String get book_name_36 => 'Софонія';

  @override
  String get book_code_37 => 'Аг';

  @override
  String get book_name_37 => 'Аггей';

  @override
  String get book_code_38 => 'Зах';

  @override
  String get book_name_38 => 'Захарія';

  @override
  String get book_code_39 => 'Мал';

  @override
  String get book_name_39 => 'Малахія';

  @override
  String get book_code_40 => 'Мт';

  @override
  String get book_name_40 => 'Матвій';

  @override
  String get book_code_41 => 'Мк';

  @override
  String get book_name_41 => 'Марк';

  @override
  String get book_code_42 => 'Лк';

  @override
  String get book_name_42 => 'Лука';

  @override
  String get book_code_43 => 'Ів';

  @override
  String get book_name_43 => 'Іван';

  @override
  String get book_code_44 => 'Дії';

  @override
  String get book_name_44 => 'Дії';

  @override
  String get book_code_45 => 'Рим';

  @override
  String get book_name_45 => 'Римлян';

  @override
  String get book_code_46 => '1Кор';

  @override
  String get book_name_46 => '1 Коринтян';

  @override
  String get book_code_47 => '2Кор';

  @override
  String get book_name_47 => '2 Коринтян';

  @override
  String get book_code_48 => 'Гал';

  @override
  String get book_name_48 => 'Галатів';

  @override
  String get book_code_49 => 'Еф';

  @override
  String get book_name_49 => 'Ефесян';

  @override
  String get book_code_50 => 'Флп';

  @override
  String get book_name_50 => 'Филип’ян';

  @override
  String get book_code_51 => 'Кол';

  @override
  String get book_name_51 => 'Колосян';

  @override
  String get book_code_52 => '1Сол';

  @override
  String get book_name_52 => '1 Солунян';

  @override
  String get book_code_53 => '2Сол';

  @override
  String get book_name_53 => '2 Солунян';

  @override
  String get book_code_54 => '1Тим';

  @override
  String get book_name_54 => '1 Тимофію';

  @override
  String get book_code_55 => '2Тим';

  @override
  String get book_name_55 => '2 Тимофію';

  @override
  String get book_code_56 => 'Тит';

  @override
  String get book_name_56 => 'Титу';

  @override
  String get book_code_57 => 'Флм';

  @override
  String get book_name_57 => 'Филимону';

  @override
  String get book_code_58 => 'Євр';

  @override
  String get book_name_58 => 'Євреїв';

  @override
  String get book_code_59 => 'Як';

  @override
  String get book_name_59 => 'Якова';

  @override
  String get book_code_60 => '1Пет';

  @override
  String get book_name_60 => '1 Петра';

  @override
  String get book_code_61 => '2Пет';

  @override
  String get book_name_61 => '2 Петра';

  @override
  String get book_code_62 => '1Ів';

  @override
  String get book_name_62 => '1 Івана';

  @override
  String get book_code_63 => '2Ів';

  @override
  String get book_name_63 => '2 Івана';

  @override
  String get book_code_64 => '3Ів';

  @override
  String get book_name_64 => '3 Івана';

  @override
  String get book_code_65 => 'Юд';

  @override
  String get book_name_65 => 'Юди';

  @override
  String get book_code_66 => 'Об';

  @override
  String get book_name_66 => 'Об’явлення';
}
