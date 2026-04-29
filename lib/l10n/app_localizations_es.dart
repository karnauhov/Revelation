// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Spanish Castilian (`es`).
class AppLocalizationsEs extends AppLocalizations {
  AppLocalizationsEs([String locale = 'es']) : super(locale);

  @override
  String get app_name => 'Apocalipsis';

  @override
  String get startup_title => 'Iniciando la aplicación...';

  @override
  String get startup_step_preparing => 'Preparando la aplicación';

  @override
  String get startup_step_loading_settings => 'Cargando tus ajustes';

  @override
  String get startup_step_initializing_server =>
      'Conectando a servicios en línea';

  @override
  String get startup_step_initializing_databases =>
      'Abriendo los datos de la aplicación';

  @override
  String get startup_step_configuring_links =>
      'Preparando el diccionario de Strong';

  @override
  String startup_progress(int current, int total) {
    return 'Paso $current de $total';
  }

  @override
  String get startup_error => 'No se pudo iniciar la aplicación :(';

  @override
  String get startup_retry => 'Reintentar';

  @override
  String startup_version_build(String version, String build) {
    return 'Versión $version ($build)';
  }

  @override
  String get version => 'Versión de la aplicación:';

  @override
  String get app_version_from => 'Versión de la aplicación del';

  @override
  String get common_data_update => 'Versión de datos';

  @override
  String localized_data_update(String language) {
    return 'Versión de datos en $language';
  }

  @override
  String get data_version_from => 'del';

  @override
  String get language_name_en => 'inglés';

  @override
  String get language_name_es => 'español';

  @override
  String get language_name_uk => 'ucraniano';

  @override
  String get language_name_ru => 'ruso';

  @override
  String get app_description => 'Aplicación para el estudio del Apocalipsis.';

  @override
  String get website => 'Revelation.website';

  @override
  String get github_project => 'Proyecto en GitHub';

  @override
  String get privacy_policy => 'Política de privacidad';

  @override
  String get license => 'Licencia';

  @override
  String get support_us => 'Apóyanos';

  @override
  String get installation_packages => 'Paquetes de instalación';

  @override
  String get acknowledgements_title => 'Agradecimientos';

  @override
  String get acknowledgements_description_1 =>
      'En primer lugar, quiero agradecer a Dios por la vida; a mi esposa Ira por su amor y cuidado; y a mi madre por su ayuda y apoyo.\nTambién, mi sincera gratitud a las instituciones por proporcionar acceso a la información y a los manuscritos invaluables:';

  @override
  String get acknowledgements_description_2 =>
      'Muchas gracias a los creadores del siguiente software y recursos:';

  @override
  String get recommended_title => 'Recomendado';

  @override
  String get recommended_description =>
      'Recursos recomendados para el estudio del Apocalipsis y de la Biblia en general:';

  @override
  String get bug_report => 'Informar de un error';

  @override
  String get log_copied_message =>
      'Los registros se han copiado en el portapapeles. Por favor, envíelos a:';

  @override
  String get bug_report_wish =>
      'Por favor, describa brevemente el error e incluya en el correo electrónico la información técnica que la aplicación acaba de copiar automáticamente al portapapeles (¡esto es importante!). Si es posible, adjunte una captura de pantalla a su mensaje. Gracias, está ayudando a mejorar la aplicación.';

  @override
  String get all_rights_reserved => 'Todos los derechos reservados';

  @override
  String get ad_loading => 'Cargando anuncio...';

  @override
  String get menu => 'Menú';

  @override
  String get close_app => 'Cerrar aplicación';

  @override
  String get todo => 'POR HACER';

  @override
  String get primary_sources_screen => 'Fuentes primarias';

  @override
  String get primary_sources_header => 'Haga clic en la imagen para abrir';

  @override
  String get settings_screen => 'Configuración';

  @override
  String get settings_header => 'Se guardan automáticamente';

  @override
  String get about_screen => 'Acerca de';

  @override
  String get about_header => 'Información general sobre la aplicación';

  @override
  String get download => 'Descargar';

  @override
  String get download_header => 'Instale la aplicación para su plataforma';

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
    return 'Guardado: $path';
  }

  @override
  String get error_loading_libraries => 'Error al cargar bibliotecas';

  @override
  String get error_loading_institutions => 'Error al cargar instituciones';

  @override
  String get error_loading_recommendations => 'Error al cargar recomendaciones';

  @override
  String get error_loading_topics => 'Error al cargar temas';

  @override
  String get error_loading_primary_sources =>
      'Error al cargar fuentes primarias';

  @override
  String get changelog => 'Registro de cambios (en)';

  @override
  String get close => 'Cerrar';

  @override
  String get error => 'Error';

  @override
  String get attention => 'Atención';

  @override
  String get info => 'Información';

  @override
  String get more_information => 'Más información';

  @override
  String get unable_to_follow_the_link => 'No se puede seguir el enlace';

  @override
  String get language => 'Idioma';

  @override
  String get color_theme => 'Tema de color';

  @override
  String get manuscript_color_theme => 'Manuscrito';

  @override
  String get forest_color_theme => 'Bosque';

  @override
  String get sky_color_theme => 'Cielo';

  @override
  String get grape_color_theme => 'Uva';

  @override
  String get font_size => 'Tamaño de fuente';

  @override
  String get small_font_size => 'Pequeño';

  @override
  String get medium_font_size => 'Mediano';

  @override
  String get large_font_size => 'Grande';

  @override
  String get sound => 'Sonido';

  @override
  String get on => 'Encendido';

  @override
  String get off => 'Apagado';

  @override
  String get vectors => 'Vectores';

  @override
  String get icons => 'Iconos';

  @override
  String get and => 'y';

  @override
  String get by => 'por';

  @override
  String get strongsConcordance => 'Concordancia de Strong';

  @override
  String get package => 'Paquete';

  @override
  String get font => 'Fuente';

  @override
  String get wikipedia => 'Wikipedia';

  @override
  String get intf => 'INTF';

  @override
  String get image_source => 'Fuente de imágenes';

  @override
  String get topic => 'Tema';

  @override
  String get show_more => 'mostrar más información';

  @override
  String get hide => 'ocultar';

  @override
  String get full_primary_sources => 'Contienen todo el Apocalipsis completo';

  @override
  String get significant_primary_sources =>
      'Contienen una parte significativa del Apocalipsis';

  @override
  String get fragments_primary_sources =>
      'Contienen pequeños fragmentos del Apocalipsis';

  @override
  String get verses => 'Número de versículos';

  @override
  String get choose_page => 'Seleccione la página';

  @override
  String get images_are_missing => 'Las imágenes no están disponibles';

  @override
  String get image_not_loaded => 'Imagen no cargada';

  @override
  String get click_for_info =>
      'Haga clic en el elemento de la imagen que le interese para obtener información sobre él.';

  @override
  String get low_quality => 'Calidad reducida';

  @override
  String get low_quality_message =>
      'En el navegador móvil se utiliza una imagen de calidad reducida. Para ver en máxima calidad, instale la aplicación o abra la página en una computadora.';

  @override
  String get reload_image => 'Recargar';

  @override
  String get zoom_in => 'Acercar';

  @override
  String get zoom_out => 'Alejar';

  @override
  String get restore_original_scale => 'Escala original';

  @override
  String get toggle_negative => 'Negativo';

  @override
  String get toggle_monochrome => 'Monocromo';

  @override
  String get brightness_contrast => 'Contraste y brillo';

  @override
  String get brightness => 'Brillo';

  @override
  String get contrast => 'Contraste';

  @override
  String get ok => 'OK';

  @override
  String get cancel => 'Cancelar';

  @override
  String get reset => 'Restablecer';

  @override
  String get area => 'Área';

  @override
  String get size => 'Tamaño';

  @override
  String get not_selected => 'No seleccionada';

  @override
  String get area_selection => 'Selección de área';

  @override
  String get color_replacement => 'Reemplazo de color';

  @override
  String get color_to_replace => 'Color a reemplazar';

  @override
  String get eyedropper => 'Selector de color';

  @override
  String get new_color => 'Nuevo color';

  @override
  String get palette => 'Paleta';

  @override
  String get select_color => 'Seleccione color';

  @override
  String get select_area_header => 'Seleccione un área en la imagen';

  @override
  String get select_area_description =>
      'Seleccione un área rectangular en la imagen: toque el punto inicial, arrastre y suelte. Si es necesario, puede ampliar la imagen.';

  @override
  String get pick_color_header => 'Seleccione un punto en la imagen';

  @override
  String get pick_color_description =>
      'Haga clic en el área de la imagen de donde desea seleccionar el color. Si es necesario, puede ampliar o mover la imagen.';

  @override
  String get tolerance => 'Tolerancia';

  @override
  String get replace_color_message =>
      'La primera vez que se invoca, la formación de la matriz de píxeles tomará algún tiempo.';

  @override
  String get page_settings_reset => 'Restablecer configuración';

  @override
  String get toggle_show_word_separators => 'Separadores de palabras';

  @override
  String get toggle_show_strong_numbers => 'Números de Strong';

  @override
  String get toggle_show_verse_numbers => 'Números de versículos';

  @override
  String get strong_number => 'Número de Strong';

  @override
  String get strong_picker_unavailable_numbers =>
      '2717 y 3203-3302 no están disponibles';

  @override
  String get strong_pronunciation => 'Pronunciación';

  @override
  String get strong_synonyms => 'Sinónimos';

  @override
  String get strong_origin => 'Análisis de la palabra';

  @override
  String get strong_usage => 'Uso';

  @override
  String get strong_reference_commentary =>
      'Fuente de la traducción: https://www.logosklogos.com/strongcodes\nEl análisis de una palabra puede incluir las siguientes referencias: formas derivadas, palabras para comparación, combinaciones léxicas y palabras relacionadas.';

  @override
  String get strong_part_of_speech => 'Parte de la oración';

  @override
  String get strong_indeclNumAdj => 'numeral indeclinable (adjetivo)';

  @override
  String get strong_indeclLetN => 'letra indeclinable (sustantivo)';

  @override
  String get strong_indeclinable => 'indeclinable';

  @override
  String get strong_adj => 'adjetivo';

  @override
  String get strong_advCor => 'adverbio correlativo';

  @override
  String get strong_advInt => 'adverbio interrogativo';

  @override
  String get strong_advNeg => 'adverbio negativo';

  @override
  String get strong_advSup => 'adverbio superlativo';

  @override
  String get strong_adv => 'adverbio';

  @override
  String get strong_comp => 'comparativo';

  @override
  String get strong_aramaicTransWord => 'palabra transliterada aramea';

  @override
  String get strong_hebrewForm => 'forma hebrea';

  @override
  String get strong_hebrewNoun => 'sustantivo hebreo';

  @override
  String get strong_hebrew => 'hebreo';

  @override
  String get strong_location => 'ubicación';

  @override
  String get strong_properNoun => 'nombre propio';

  @override
  String get strong_noun => 'sustantivo';

  @override
  String get strong_masc => 'masculino';

  @override
  String get strong_fem => 'femenino';

  @override
  String get strong_neut => 'neutro';

  @override
  String get strong_plur => 'plural';

  @override
  String get strong_otherType => 'otro tipo';

  @override
  String get strong_verbImp => 'verbo (imperativo)';

  @override
  String get strong_verb => 'verbo';

  @override
  String get strong_pronDat => 'pronombre dativo';

  @override
  String get strong_pronPoss => 'pronombre posesivo';

  @override
  String get strong_pronPers => 'pronombre personal';

  @override
  String get strong_pronRecip => 'pronombre recíproco';

  @override
  String get strong_pronRefl => 'pronombre reflexivo';

  @override
  String get strong_pronRel => 'pronombre relativo';

  @override
  String get strong_pronCorrel => 'pronombre correlativo';

  @override
  String get strong_pronIndef => 'pronombre indefinido';

  @override
  String get strong_pronInterr => 'pronombre interrogativo';

  @override
  String get strong_pronDem => 'pronombre demostrativo';

  @override
  String get strong_pron => 'pronombre';

  @override
  String get strong_particleCond => 'partícula condicional';

  @override
  String get strong_particleDisj => 'partícula disyuntiva';

  @override
  String get strong_particleInterr => 'partícula interrogativa';

  @override
  String get strong_particleNeg => 'partícula negativa';

  @override
  String get strong_particle => 'partícula';

  @override
  String get strong_interj => 'interjección';

  @override
  String get strong_participle => 'participio';

  @override
  String get strong_prefix => 'prefijo';

  @override
  String get strong_prep => 'preposición';

  @override
  String get strong_artDef => 'artículo definido';

  @override
  String get strong_phraseIdi => 'frase (expresión idiomática)';

  @override
  String get strong_phrase => 'frase';

  @override
  String get strong_conjNeg => 'conjunción negativa';

  @override
  String get strong_conj => 'conjunción';

  @override
  String get strong_or => 'o';

  @override
  String get markdown_unknown_block_title =>
      'Bloque de contenido no compatible';

  @override
  String markdown_unknown_block_description(String blockName) {
    return 'Esta versión de la aplicación no puede mostrar el bloque `$blockName`.';
  }

  @override
  String get markdown_unknown_block_update_hint =>
      'Abre la página de descargas para instalar una versión más reciente de la aplicación para tu plataforma.';

  @override
  String get markdown_unknown_block_update_action => 'Actualizar aplicación';

  @override
  String get markdown_youtube_player_title => 'Video de YouTube incrustado';

  @override
  String get markdown_youtube_unavailable_title =>
      'Video de YouTube no disponible';

  @override
  String get markdown_youtube_unavailable_description =>
      'No se pudo mostrar este bloque de YouTube en el reproductor incrustado.';

  @override
  String get markdown_image_loading => 'Cargando imagen...';

  @override
  String get copy_content => 'Copiar contenido';

  @override
  String get export_pdf_content => 'Exportar a PDF';

  @override
  String get markdown_copied => 'Contenido copiado al portapapeles.';

  @override
  String get markdown_copy_failed => 'No se pudo copiar el contenido.';

  @override
  String get markdown_pdf_export_failed => 'No se pudo exportar el PDF.';

  @override
  String get previous_description_item => 'Elemento anterior';

  @override
  String get next_description_item => 'Elemento siguiente';

  @override
  String get previous_word => 'Palabra anterior';

  @override
  String get next_word => 'Palabra siguiente';

  @override
  String get previous_verse => 'Versículo anterior';

  @override
  String get next_verse => 'Versículo siguiente';

  @override
  String get previous_dictionary_entry => 'Artículo anterior del diccionario';

  @override
  String get next_dictionary_entry => 'Artículo siguiente del diccionario';

  @override
  String markdown_images_loading_progress(int loaded, int total) {
    return 'Cargando imágenes: $loaded de $total';
  }
}
