import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/infra/db/connectors/bible_module_connector.dart';
import 'package:revelation/shared/config/app_constants.dart';

abstract class BibleModuleDataSource {
  Future<List<String>> listModuleFiles({required String defaultModuleFile});

  BibleModuleDB openModule(String moduleFile);
}

class LocalBibleModuleDataSource implements BibleModuleDataSource {
  const LocalBibleModuleDataSource();

  @override
  Future<List<String>> listModuleFiles({required String defaultModuleFile}) {
    return listLocalBibleModuleFiles(defaultModuleFile: defaultModuleFile);
  }

  @override
  BibleModuleDB openModule(String moduleFile) {
    return BibleModuleDB(openBibleModuleExecutor(moduleFile));
  }
}

String defaultBibleModuleFileForLanguage(String languageCode) {
  switch (languageCode.trim().toLowerCase()) {
    case 'en':
    case 'es':
    case 'uk':
    case 'ru':
    default:
      return AppConstants.defaultBibleModuleDB;
  }
}
