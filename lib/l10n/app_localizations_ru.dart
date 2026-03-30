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
  String get strongsConcordance => 'Конкорданция Стронга';

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
  String get strong_pronunciation => 'Произношение';

  @override
  String get strong_synonyms => 'Синонимы';

  @override
  String get strong_origin => 'Анализ слова';

  @override
  String get strong_usage => 'Использование';

  @override
  String get strong_reference_commentary =>
      'Источник перевода: https://www.bible.in.ua/underl\nАнализ слова может включать следующие ссылки: производные формы, слова для сравнения, словосочетания и связанные слова.';

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
  String get markdown_image_loading => 'Загрузка изображения...';

  @override
  String markdown_images_loading_progress(int loaded, int total) {
    return 'Загрузка изображений: $loaded из $total';
  }
}
