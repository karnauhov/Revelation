// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Russian (`ru`).
class AppLocalizationsRu extends AppLocalizations {
  AppLocalizationsRu([String locale = 'ru']) : super(locale);

  @override
  String get app_name => 'Откровение';

  @override
  String get startup_title => 'Запуск приложения...';

  @override
  String get startup_step_preparing => 'Подготавливаем приложение';

  @override
  String get startup_step_loading_settings => 'Загружаем ваши настройки';

  @override
  String get startup_step_initializing_server => 'Подключаем онлайн-сервисы';

  @override
  String get startup_step_initializing_databases =>
      'Открываем данные приложения';

  @override
  String get startup_step_configuring_links => 'Подготавливаем словарь Стронга';

  @override
  String startup_progress(int current, int total) {
    return 'Шаг $current из $total';
  }

  @override
  String get startup_error => 'Не удалось запустить :(';

  @override
  String get startup_retry => 'Повторить';

  @override
  String startup_version_build(String version, String build) {
    return 'Версия $version ($build)';
  }

  @override
  String get version => 'Версия приложения:';

  @override
  String get app_version_from => 'Версия приложения от';

  @override
  String get common_data_update => 'Версия данных';

  @override
  String localized_data_update(String language) {
    return 'Версия данных на $language языке';
  }

  @override
  String get data_version_from => 'от';

  @override
  String get language_name_en => 'английском';

  @override
  String get language_name_es => 'испанском';

  @override
  String get language_name_uk => 'украинском';

  @override
  String get language_name_ru => 'русском';

  @override
  String get app_description => 'Приложение для изучения Откровения.';

  @override
  String get website => 'Revelation.website';

  @override
  String get github_project => 'GitHub проект';

  @override
  String get privacy_policy => 'Политика конфиденциальности';

  @override
  String get license => 'Лицензия';

  @override
  String get support_us => 'Поддержите нас';

  @override
  String get installation_packages => 'Установочные пакеты';

  @override
  String get acknowledgements_title => 'Благодарности';

  @override
  String get acknowledgements_description_1 =>
      'В первую очередь хочу поблагодарить Бога за жизнь; свою жену Иру - за любовь и заботу; и маму - за помощь и поддержку.\nТакже моя искренняя признательность учреждениям за предоставленный доступ к информации и бесценным рукописям:';

  @override
  String get acknowledgements_description_2 =>
      'Огромное спасибо создателям следующего ПО и ресурсов:';

  @override
  String get recommended_title => 'Рекомендуемое';

  @override
  String get recommended_description =>
      'Рекомендуемые ресурсы для изучения Откровения и Библии в целом:';

  @override
  String get bug_report => 'Сообщить об ошибке';

  @override
  String get tools => 'Инструменты';

  @override
  String get refresh_databases => 'Обновить базы данных';

  @override
  String get databases_refreshed => 'Базы данных обновлены';

  @override
  String get databases_up_to_date =>
      'Файлы БД актуальны. Обновление не требуется.';

  @override
  String get database_size_mismatch =>
      'Размеры некоторых файлов БД не соответствуют манифесту. Попробуйте обновить базы данных ещё раз.';

  @override
  String get database_refresh_failed => 'Не удалось обновить базы данных';

  @override
  String get show_local_folder => 'Показать локальную папку';

  @override
  String get local_folder_open_failed => 'Не удалось открыть локальную папку';

  @override
  String get clear_cache => 'Очистить кэш';

  @override
  String get cache_cleared => 'Кэш очищен';

  @override
  String get cache_clear_failed => 'Не удалось очистить кэш';

  @override
  String get log_copied_message =>
      'Логи скопированы в буфер обмена. Пожалуйста, отправьте их мне:';

  @override
  String get bug_report_wish =>
      'Пожалуйста, кратко опишите ошибку и вставьте в письмо техническую информацию, которую приложение только что автоматически скопировало в буфер обмена (это важно!). По возможности приложите скриншот экрана к сообщению. Спасибо, вы помогаете сделать приложение лучше.';

  @override
  String get all_rights_reserved => 'Все права защищены';

  @override
  String get ad_loading => 'Загрузка рекламы...';

  @override
  String get menu => 'Меню';

  @override
  String get close_app => 'Закрыть приложение';

  @override
  String get todo => 'СДЕЛАТЬ';

  @override
  String get primary_sources_screen => 'Первоисточники';

  @override
  String get primary_sources_header => 'Нажмите на изображение, чтобы открыть';

  @override
  String get strongs_dictionary_screen => 'Словарь Стронга';

  @override
  String get strongs_dictionary_header =>
      'Значения греческих слов и их использование';

  @override
  String get allusion_search_screen => 'Поиск аллюзий';

  @override
  String get allusion_search_header => 'Связи с библейскими текстами';

  @override
  String get bible_screen => 'Библия';

  @override
  String get bible_header => 'Чтение и изучение Писания';

  @override
  String get bible_module => 'Модуль';

  @override
  String get bible_book => 'Книга';

  @override
  String get bible_chapter => 'Глава';

  @override
  String get bible_verse => 'Стих';

  @override
  String get bible_loading => 'Открываем Библию...';

  @override
  String get bible_loading_chapter => 'Загружаем главу...';

  @override
  String get bible_loading_module => 'Скачиваем и открываем модуль...';

  @override
  String get bible_no_modules =>
      'Модули Библии не найдены. Обновите базы данных или добавьте bible_*.sqlite в локальную папку данных.';

  @override
  String get bible_previous_chapter => 'Предыдущая глава';

  @override
  String get bible_next_chapter => 'Следующая глава';

  @override
  String get bible_strong_toggle_label => 'Стронг';

  @override
  String get revelation_structure_screen => 'Структура Откровения';

  @override
  String get revelation_structure_header =>
      'План книги и структура повествования';

  @override
  String get historical_background_screen => 'Историческая справка';

  @override
  String get historical_background_header =>
      'Ключевые события из истории церкви и мира';

  @override
  String get practical_faith_screen => 'Практическая вера';

  @override
  String get practical_faith_header => 'Размышление и применение';

  @override
  String planned_feature_message(String featureTitle) {
    return 'Страница «$featureTitle» планируется к реализации в одной из будущих версий.';
  }

  @override
  String get settings_screen => 'Настройки';

  @override
  String get settings_header => 'Сохраняются автоматически';

  @override
  String get about_screen => 'О программе';

  @override
  String get about_header => 'Общая информация о приложении';

  @override
  String get download => 'Скачать';

  @override
  String get download_header => 'Установите приложение для вашей платформы';

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
    return 'Сохранено: $path';
  }

  @override
  String get error_loading_libraries => 'Ошибка загрузки библиотек';

  @override
  String get error_loading_institutions => 'Ошибка загрузки учреждений';

  @override
  String get error_loading_recommendations => 'Ошибка загрузки рекомендаций';

  @override
  String get error_loading_topics => 'Ошибка загрузки тем';

  @override
  String get error_loading_primary_sources => 'Ошибка загрузки первоисточников';

  @override
  String get changelog => 'Журнал изменений (en)';

  @override
  String get close => 'Закрыть';

  @override
  String get error => 'Ошибка';

  @override
  String get attention => 'Внимание';

  @override
  String get info => 'Информация';

  @override
  String get more_information => 'Больше информации';

  @override
  String get unable_to_follow_the_link => 'Невозможно перейти по ссылке';

  @override
  String get language => 'Язык';

  @override
  String get color_theme => 'Цветовая тема';

  @override
  String get manuscript_color_theme => 'Рукопись';

  @override
  String get forest_color_theme => 'Лес';

  @override
  String get sky_color_theme => 'Небо';

  @override
  String get grape_color_theme => 'Виноград';

  @override
  String get font_size => 'Размер шрифта';

  @override
  String get small_font_size => 'Маленький';

  @override
  String get medium_font_size => 'Средний';

  @override
  String get large_font_size => 'Большой';

  @override
  String get sound => 'Звук';

  @override
  String get on => 'Включен';

  @override
  String get off => 'Выключен';

  @override
  String get vectors => 'Векторы';

  @override
  String get icons => 'Иконки';

  @override
  String get and => 'и';

  @override
  String get by => 'от';

  @override
  String get package => 'Пакет';

  @override
  String get font => 'Шрифт';

  @override
  String get wikipedia => 'Википедия';

  @override
  String get intf => 'INTF';

  @override
  String get image_source => 'Источник изображений';

  @override
  String get topic => 'Тема';

  @override
  String get show_more => 'показать больше информации';

  @override
  String get hide => 'скрыть';

  @override
  String get full_primary_sources => 'Содержат все Откровение целиком';

  @override
  String get significant_primary_sources =>
      'Содержат значительную часть Откровения';

  @override
  String get fragments_primary_sources =>
      'Содержат небольшие фрагменты Откровения';

  @override
  String get verses => 'Количество стихов';

  @override
  String get choose_page => 'Выберите страницу';

  @override
  String get images_are_missing => 'Изображения отсутствуют';

  @override
  String get image_not_loaded => 'Изображение не загружено';

  @override
  String get primary_source_word_source_unavailable =>
      'Первоисточник недоступен';

  @override
  String get primary_source_word_page_unavailable => 'Страница недоступна';

  @override
  String get primary_source_word_word_unavailable => 'Слово недоступно';

  @override
  String get primary_source_word_image_unavailable => 'Изображение недоступно';

  @override
  String get primary_source_words_image_hint =>
      'Нажмите на изображение чтоб увидеть слово в первоисточнике';

  @override
  String get click_for_info =>
      'Кликните на интересующий вас элемент изображения, чтобы получить о нем информацию.';

  @override
  String get low_quality => 'Качество снижено';

  @override
  String get low_quality_message =>
      'В мобильном браузере используется изображение сниженного качества. Для просмотра в максимальном качестве установите приложение или откройте страницу на компьютере.';

  @override
  String get reload_image => 'Перезагрузка';

  @override
  String get zoom_in => 'Увеличение';

  @override
  String get zoom_out => 'Уменьшение';

  @override
  String get restore_original_scale => 'Начальный масштаб';

  @override
  String get toggle_negative => 'Негатив';

  @override
  String get toggle_monochrome => 'Монохромность';

  @override
  String get brightness_contrast => 'Яркость, контрастность';

  @override
  String get brightness => 'Яркость';

  @override
  String get contrast => 'Контрастность';

  @override
  String get ok => 'OK';

  @override
  String get cancel => 'Отменить';

  @override
  String get reset => 'Сбросить';

  @override
  String get area => 'Область';

  @override
  String get size => 'Размер';

  @override
  String get not_selected => 'Не выделена';

  @override
  String get area_selection => 'Выделение области';

  @override
  String get color_replacement => 'Замена цвета';

  @override
  String get color_to_replace => 'Цвет для замены';

  @override
  String get eyedropper => 'Выбор цвета';

  @override
  String get new_color => 'Новый цвет';

  @override
  String get palette => 'Палитра';

  @override
  String get select_color => 'Выберите цвет';

  @override
  String get select_area_header => 'Выберите область на изображении';

  @override
  String get select_area_description =>
      'Выделите прямоугольную область на изображении: коснитесь начальной точки, проведите и отпустите. При необходимости вы можете увеличить изображение.';

  @override
  String get pick_color_header => 'Выберите точку на изображении';

  @override
  String get pick_color_description =>
      'Нажмите на область изображения, откуда вы хотите выбрать цвет. При необходимости вы можете увеличить или передвинуть изображение.';

  @override
  String get tolerance => 'Допуск';

  @override
  String get replace_color_message =>
      'При первом вызове формирование матрицы пикселей займёт некоторое время.';

  @override
  String get page_settings_reset => 'Сброс настроек';

  @override
  String get toggle_show_word_separators => 'Разделители слов';

  @override
  String get toggle_show_strong_numbers => 'Номера Стронга';

  @override
  String get toggle_show_verse_numbers => 'Номера стихов';

  @override
  String get strong_number => 'Номер Стронга';

  @override
  String get strong_picker_unavailable_numbers => '2717 и 3203-3302 недоступны';

  @override
  String get strong_dictionary_search => 'Полнотекстовый поиск';

  @override
  String get strong_dictionary_search_hint => '#/слово/перевод';

  @override
  String get strong_dictionary_no_entries =>
      'Статьи словаря Стронга недоступны';

  @override
  String get strong_dictionary_no_results => 'Нет подходящих статей';

  @override
  String get greek_keyboard_tooltip => 'Греческая клавиатура';

  @override
  String get strong_pronunciation => 'Произношение';

  @override
  String get strong_synonyms => 'Синонимы';

  @override
  String get strong_origin => 'Анализ слова';

  @override
  String get strong_usage => 'Использование';

  @override
  String get strong_reference_commentary =>
      'Источник перевода: https://www.bible.in.ua/underl';

  @override
  String get strong_origin_tooltip =>
      'Анализ слова может включать следующие ссылки: производные формы, слова для сравнения, словосочетания и связанные слова.';

  @override
  String get strong_part_of_speech => 'Часть речи';

  @override
  String get strong_indeclNumAdj =>
      'неизменяемое числительное (в функции прилагательного)';

  @override
  String get strong_indeclLetN => 'неизменяемая буква (существительное)';

  @override
  String get strong_indeclinable => 'неизменяемое';

  @override
  String get strong_adj => 'прилагательное';

  @override
  String get strong_advCor => 'соотносительное наречие';

  @override
  String get strong_advInt => 'вопросительное наречие';

  @override
  String get strong_advNeg => 'отрицательное наречие';

  @override
  String get strong_advSup => 'наречие, превосходная степень';

  @override
  String get strong_adv => 'наречие';

  @override
  String get strong_comp => 'сравнительная степень';

  @override
  String get strong_aramaicTransWord => 'транслитерированное арамейское слово';

  @override
  String get strong_hebrewForm => 'форма на иврите';

  @override
  String get strong_hebrewNoun => 'существительное на иврите';

  @override
  String get strong_hebrew => 'иврит';

  @override
  String get strong_location => 'географическое название';

  @override
  String get strong_properNoun => 'имя собственное';

  @override
  String get strong_noun => 'существительное';

  @override
  String get strong_masc => 'мужской род';

  @override
  String get strong_fem => 'женский род';

  @override
  String get strong_neut => 'средний род';

  @override
  String get strong_plur => 'множественное число';

  @override
  String get strong_otherType => 'другой тип';

  @override
  String get strong_verbImp => 'глагол (повелительное наклонение)';

  @override
  String get strong_verb => 'глагол';

  @override
  String get strong_pronDat => 'Местоимение, дательный падеж';

  @override
  String get strong_pronPoss => 'притяжательное местоимение';

  @override
  String get strong_pronPers => 'личное местоимение';

  @override
  String get strong_pronRecip => 'взаимное местоимение';

  @override
  String get strong_pronRefl => 'возвратное местоимение';

  @override
  String get strong_pronRel => 'относительное местоимение';

  @override
  String get strong_pronCorrel => 'соотносительное местоимение';

  @override
  String get strong_pronIndef => 'неопределённое местоимение';

  @override
  String get strong_pronInterr => 'вопросительное местоимение';

  @override
  String get strong_pronDem => 'указательное местоимение';

  @override
  String get strong_pron => 'местоимение';

  @override
  String get strong_particleCond => 'условная частица';

  @override
  String get strong_particleDisj => 'разделительная частица';

  @override
  String get strong_particleInterr => 'вопросительная частица';

  @override
  String get strong_particleNeg => 'отрицательная частица';

  @override
  String get strong_particle => 'частица';

  @override
  String get strong_interj => 'междометие';

  @override
  String get strong_participle => 'причастие';

  @override
  String get strong_prefix => 'префикс';

  @override
  String get strong_prep => 'предлог';

  @override
  String get strong_artDef => 'определённый артикль';

  @override
  String get strong_phraseIdi => 'фраза (идиоматическое выражение)';

  @override
  String get strong_phrase => 'фраза';

  @override
  String get strong_conjNeg => 'отрицательный союз';

  @override
  String get strong_conj => 'союз';

  @override
  String get strong_or => 'или';

  @override
  String get markdown_unknown_block_title =>
      'Неподдерживаемый блок содержимого';

  @override
  String markdown_unknown_block_description(String blockName) {
    return 'Эта версия приложения не умеет отображать блок `$blockName`.';
  }

  @override
  String get markdown_unknown_block_update_hint =>
      'Откройте страницу загрузок, чтобы установить более новую версию приложения для вашей платформы.';

  @override
  String get markdown_unknown_block_update_action => 'Обновить приложение';

  @override
  String get markdown_youtube_player_title => 'Встроенное YouTube-видео';

  @override
  String get markdown_youtube_unavailable_title => 'YouTube-видео недоступно';

  @override
  String get markdown_youtube_unavailable_description =>
      'Этот YouTube-блок не удалось отобразить во встроенном плеере.';

  @override
  String get markdown_image_loading => 'Загрузка изображения...';

  @override
  String get copy_content => 'Скопировать содержимое';

  @override
  String get export_pdf_content => 'Экспортировать в PDF';

  @override
  String get markdown_copied => 'Содержимое скопировано в буфер обмена.';

  @override
  String get markdown_copy_failed => 'Не удалось скопировать содержимое.';

  @override
  String get markdown_pdf_export_failed => 'Не удалось экспортировать PDF.';

  @override
  String get previous_description_item => 'Предыдущий элемент';

  @override
  String get next_description_item => 'Следующий элемент';

  @override
  String get previous_word => 'Предыдущее слово';

  @override
  String get next_word => 'Следующее слово';

  @override
  String get previous_verse => 'Предыдущий стих';

  @override
  String get next_verse => 'Следующий стих';

  @override
  String get previous_dictionary_entry => 'Предыдущая словарная статья';

  @override
  String get next_dictionary_entry => 'Следующая словарная статья';

  @override
  String markdown_images_loading_progress(int loaded, int total) {
    return 'Загрузка изображений: $loaded из $total';
  }

  @override
  String get book_code_1 => 'Быт';

  @override
  String get book_name_1 => 'Бытие';

  @override
  String get book_code_2 => 'Исх';

  @override
  String get book_name_2 => 'Исход';

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
  String get book_name_5 => 'Второзаконие';

  @override
  String get book_code_6 => 'Нав';

  @override
  String get book_name_6 => 'Иисус Навин';

  @override
  String get book_code_7 => 'Суд';

  @override
  String get book_name_7 => 'Судьи';

  @override
  String get book_code_8 => 'Руф';

  @override
  String get book_name_8 => 'Руфь';

  @override
  String get book_code_9 => '1Цар';

  @override
  String get book_name_9 => '1 Царств';

  @override
  String get book_code_10 => '2Цар';

  @override
  String get book_name_10 => '2 Царств';

  @override
  String get book_code_11 => '3Цар';

  @override
  String get book_name_11 => '3 Царств';

  @override
  String get book_code_12 => '4Цар';

  @override
  String get book_name_12 => '4 Царств';

  @override
  String get book_code_13 => '1Пар';

  @override
  String get book_name_13 => '1 Паралипоменон';

  @override
  String get book_code_14 => '2Пар';

  @override
  String get book_name_14 => '2 Паралипоменон';

  @override
  String get book_code_15 => 'Езд';

  @override
  String get book_name_15 => 'Ездра';

  @override
  String get book_code_16 => 'Неем';

  @override
  String get book_name_16 => 'Неемия';

  @override
  String get book_code_17 => 'Есф';

  @override
  String get book_name_17 => 'Есфирь';

  @override
  String get book_code_18 => 'Иов';

  @override
  String get book_name_18 => 'Иов';

  @override
  String get book_code_19 => 'Пс';

  @override
  String get book_name_19 => 'Псалтирь';

  @override
  String get book_code_20 => 'Прит';

  @override
  String get book_name_20 => 'Притчи';

  @override
  String get book_code_21 => 'Еккл';

  @override
  String get book_name_21 => 'Екклесиаст';

  @override
  String get book_code_22 => 'Песн';

  @override
  String get book_name_22 => 'Песнь Песней';

  @override
  String get book_code_23 => 'Ис';

  @override
  String get book_name_23 => 'Исаия';

  @override
  String get book_code_24 => 'Иер';

  @override
  String get book_name_24 => 'Иеремия';

  @override
  String get book_code_25 => 'Плач';

  @override
  String get book_name_25 => 'Плач Иеремии';

  @override
  String get book_code_26 => 'Иез';

  @override
  String get book_name_26 => 'Иезекииль';

  @override
  String get book_code_27 => 'Дан';

  @override
  String get book_name_27 => 'Даниил';

  @override
  String get book_code_28 => 'Ос';

  @override
  String get book_name_28 => 'Осия';

  @override
  String get book_code_29 => 'Иоил';

  @override
  String get book_name_29 => 'Иоиль';

  @override
  String get book_code_30 => 'Ам';

  @override
  String get book_name_30 => 'Амос';

  @override
  String get book_code_31 => 'Авд';

  @override
  String get book_name_31 => 'Авдий';

  @override
  String get book_code_32 => 'Иона';

  @override
  String get book_name_32 => 'Иона';

  @override
  String get book_code_33 => 'Мих';

  @override
  String get book_name_33 => 'Михей';

  @override
  String get book_code_34 => 'Наум';

  @override
  String get book_name_34 => 'Наум';

  @override
  String get book_code_35 => 'Авв';

  @override
  String get book_name_35 => 'Аввакум';

  @override
  String get book_code_36 => 'Соф';

  @override
  String get book_name_36 => 'Софония';

  @override
  String get book_code_37 => 'Агг';

  @override
  String get book_name_37 => 'Аггей';

  @override
  String get book_code_38 => 'Зах';

  @override
  String get book_name_38 => 'Захария';

  @override
  String get book_code_39 => 'Мал';

  @override
  String get book_name_39 => 'Малахия';

  @override
  String get book_code_40 => 'Мф';

  @override
  String get book_name_40 => 'Матфей';

  @override
  String get book_code_41 => 'Мк';

  @override
  String get book_name_41 => 'Марк';

  @override
  String get book_code_42 => 'Лк';

  @override
  String get book_name_42 => 'Лука';

  @override
  String get book_code_43 => 'Ин';

  @override
  String get book_name_43 => 'Иоанн';

  @override
  String get book_code_44 => 'Деян';

  @override
  String get book_name_44 => 'Деяния';

  @override
  String get book_code_45 => 'Рим';

  @override
  String get book_name_45 => 'Римлянам';

  @override
  String get book_code_46 => '1Кор';

  @override
  String get book_name_46 => '1 Коринфянам';

  @override
  String get book_code_47 => '2Кор';

  @override
  String get book_name_47 => '2 Коринфянам';

  @override
  String get book_code_48 => 'Гал';

  @override
  String get book_name_48 => 'Галатам';

  @override
  String get book_code_49 => 'Еф';

  @override
  String get book_name_49 => 'Ефесянам';

  @override
  String get book_code_50 => 'Флп';

  @override
  String get book_name_50 => 'Филиппийцам';

  @override
  String get book_code_51 => 'Кол';

  @override
  String get book_name_51 => 'Колоссянам';

  @override
  String get book_code_52 => '1Фес';

  @override
  String get book_name_52 => '1 Фессалоникийцам';

  @override
  String get book_code_53 => '2Фес';

  @override
  String get book_name_53 => '2 Фессалоникийцам';

  @override
  String get book_code_54 => '1Тим';

  @override
  String get book_name_54 => '1 Тимофею';

  @override
  String get book_code_55 => '2Тим';

  @override
  String get book_name_55 => '2 Тимофею';

  @override
  String get book_code_56 => 'Тит';

  @override
  String get book_name_56 => 'Титу';

  @override
  String get book_code_57 => 'Флм';

  @override
  String get book_name_57 => 'Филимону';

  @override
  String get book_code_58 => 'Евр';

  @override
  String get book_name_58 => 'Евреям';

  @override
  String get book_code_59 => 'Иак';

  @override
  String get book_name_59 => 'Иакова';

  @override
  String get book_code_60 => '1Пет';

  @override
  String get book_name_60 => '1 Петра';

  @override
  String get book_code_61 => '2Пет';

  @override
  String get book_name_61 => '2 Петра';

  @override
  String get book_code_62 => '1Ин';

  @override
  String get book_name_62 => '1 Иоанна';

  @override
  String get book_code_63 => '2Ин';

  @override
  String get book_name_63 => '2 Иоанна';

  @override
  String get book_code_64 => '3Ин';

  @override
  String get book_name_64 => '3 Иоанна';

  @override
  String get book_code_65 => 'Иуд';

  @override
  String get book_name_65 => 'Иуды';

  @override
  String get book_code_66 => 'Откр';

  @override
  String get book_name_66 => 'Откровение';
}
