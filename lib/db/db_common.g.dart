// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'db_common.dart';

// ignore_for_file: type=lint
class $GreekWordsTable extends GreekWords
    with TableInfo<$GreekWordsTable, GreekWord> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $GreekWordsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
    'id',
    aliasedName,
    false,
    hasAutoIncrement: true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'PRIMARY KEY AUTOINCREMENT',
    ),
  );
  static const VerificationMeta _wordMeta = const VerificationMeta('word');
  @override
  late final GeneratedColumn<String> word = GeneratedColumn<String>(
    'word',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _categoryMeta = const VerificationMeta(
    'category',
  );
  @override
  late final GeneratedColumn<String> category = GeneratedColumn<String>(
    'category',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _synonymsMeta = const VerificationMeta(
    'synonyms',
  );
  @override
  late final GeneratedColumn<String> synonyms = GeneratedColumn<String>(
    'synonyms',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _originMeta = const VerificationMeta('origin');
  @override
  late final GeneratedColumn<String> origin = GeneratedColumn<String>(
    'origin',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _usageMeta = const VerificationMeta('usage');
  @override
  late final GeneratedColumn<String> usage = GeneratedColumn<String>(
    'usage',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    word,
    category,
    synonyms,
    origin,
    usage,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'greek_words';
  @override
  VerificationContext validateIntegrity(
    Insertable<GreekWord> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('word')) {
      context.handle(
        _wordMeta,
        word.isAcceptableOrUnknown(data['word']!, _wordMeta),
      );
    } else if (isInserting) {
      context.missing(_wordMeta);
    }
    if (data.containsKey('category')) {
      context.handle(
        _categoryMeta,
        category.isAcceptableOrUnknown(data['category']!, _categoryMeta),
      );
    } else if (isInserting) {
      context.missing(_categoryMeta);
    }
    if (data.containsKey('synonyms')) {
      context.handle(
        _synonymsMeta,
        synonyms.isAcceptableOrUnknown(data['synonyms']!, _synonymsMeta),
      );
    } else if (isInserting) {
      context.missing(_synonymsMeta);
    }
    if (data.containsKey('origin')) {
      context.handle(
        _originMeta,
        origin.isAcceptableOrUnknown(data['origin']!, _originMeta),
      );
    } else if (isInserting) {
      context.missing(_originMeta);
    }
    if (data.containsKey('usage')) {
      context.handle(
        _usageMeta,
        usage.isAcceptableOrUnknown(data['usage']!, _usageMeta),
      );
    } else if (isInserting) {
      context.missing(_usageMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  GreekWord map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return GreekWord(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}id'],
      )!,
      word: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}word'],
      )!,
      category: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}category'],
      )!,
      synonyms: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}synonyms'],
      )!,
      origin: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}origin'],
      )!,
      usage: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}usage'],
      )!,
    );
  }

  @override
  $GreekWordsTable createAlias(String alias) {
    return $GreekWordsTable(attachedDatabase, alias);
  }
}

class GreekWord extends DataClass implements Insertable<GreekWord> {
  final int id;
  final String word;
  final String category;
  final String synonyms;
  final String origin;
  final String usage;
  const GreekWord({
    required this.id,
    required this.word,
    required this.category,
    required this.synonyms,
    required this.origin,
    required this.usage,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['word'] = Variable<String>(word);
    map['category'] = Variable<String>(category);
    map['synonyms'] = Variable<String>(synonyms);
    map['origin'] = Variable<String>(origin);
    map['usage'] = Variable<String>(usage);
    return map;
  }

  GreekWordsCompanion toCompanion(bool nullToAbsent) {
    return GreekWordsCompanion(
      id: Value(id),
      word: Value(word),
      category: Value(category),
      synonyms: Value(synonyms),
      origin: Value(origin),
      usage: Value(usage),
    );
  }

  factory GreekWord.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return GreekWord(
      id: serializer.fromJson<int>(json['id']),
      word: serializer.fromJson<String>(json['word']),
      category: serializer.fromJson<String>(json['category']),
      synonyms: serializer.fromJson<String>(json['synonyms']),
      origin: serializer.fromJson<String>(json['origin']),
      usage: serializer.fromJson<String>(json['usage']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'word': serializer.toJson<String>(word),
      'category': serializer.toJson<String>(category),
      'synonyms': serializer.toJson<String>(synonyms),
      'origin': serializer.toJson<String>(origin),
      'usage': serializer.toJson<String>(usage),
    };
  }

  GreekWord copyWith({
    int? id,
    String? word,
    String? category,
    String? synonyms,
    String? origin,
    String? usage,
  }) => GreekWord(
    id: id ?? this.id,
    word: word ?? this.word,
    category: category ?? this.category,
    synonyms: synonyms ?? this.synonyms,
    origin: origin ?? this.origin,
    usage: usage ?? this.usage,
  );
  GreekWord copyWithCompanion(GreekWordsCompanion data) {
    return GreekWord(
      id: data.id.present ? data.id.value : this.id,
      word: data.word.present ? data.word.value : this.word,
      category: data.category.present ? data.category.value : this.category,
      synonyms: data.synonyms.present ? data.synonyms.value : this.synonyms,
      origin: data.origin.present ? data.origin.value : this.origin,
      usage: data.usage.present ? data.usage.value : this.usage,
    );
  }

  @override
  String toString() {
    return (StringBuffer('GreekWord(')
          ..write('id: $id, ')
          ..write('word: $word, ')
          ..write('category: $category, ')
          ..write('synonyms: $synonyms, ')
          ..write('origin: $origin, ')
          ..write('usage: $usage')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, word, category, synonyms, origin, usage);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is GreekWord &&
          other.id == this.id &&
          other.word == this.word &&
          other.category == this.category &&
          other.synonyms == this.synonyms &&
          other.origin == this.origin &&
          other.usage == this.usage);
}

class GreekWordsCompanion extends UpdateCompanion<GreekWord> {
  final Value<int> id;
  final Value<String> word;
  final Value<String> category;
  final Value<String> synonyms;
  final Value<String> origin;
  final Value<String> usage;
  const GreekWordsCompanion({
    this.id = const Value.absent(),
    this.word = const Value.absent(),
    this.category = const Value.absent(),
    this.synonyms = const Value.absent(),
    this.origin = const Value.absent(),
    this.usage = const Value.absent(),
  });
  GreekWordsCompanion.insert({
    this.id = const Value.absent(),
    required String word,
    required String category,
    required String synonyms,
    required String origin,
    required String usage,
  }) : word = Value(word),
       category = Value(category),
       synonyms = Value(synonyms),
       origin = Value(origin),
       usage = Value(usage);
  static Insertable<GreekWord> custom({
    Expression<int>? id,
    Expression<String>? word,
    Expression<String>? category,
    Expression<String>? synonyms,
    Expression<String>? origin,
    Expression<String>? usage,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (word != null) 'word': word,
      if (category != null) 'category': category,
      if (synonyms != null) 'synonyms': synonyms,
      if (origin != null) 'origin': origin,
      if (usage != null) 'usage': usage,
    });
  }

  GreekWordsCompanion copyWith({
    Value<int>? id,
    Value<String>? word,
    Value<String>? category,
    Value<String>? synonyms,
    Value<String>? origin,
    Value<String>? usage,
  }) {
    return GreekWordsCompanion(
      id: id ?? this.id,
      word: word ?? this.word,
      category: category ?? this.category,
      synonyms: synonyms ?? this.synonyms,
      origin: origin ?? this.origin,
      usage: usage ?? this.usage,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (word.present) {
      map['word'] = Variable<String>(word.value);
    }
    if (category.present) {
      map['category'] = Variable<String>(category.value);
    }
    if (synonyms.present) {
      map['synonyms'] = Variable<String>(synonyms.value);
    }
    if (origin.present) {
      map['origin'] = Variable<String>(origin.value);
    }
    if (usage.present) {
      map['usage'] = Variable<String>(usage.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('GreekWordsCompanion(')
          ..write('id: $id, ')
          ..write('word: $word, ')
          ..write('category: $category, ')
          ..write('synonyms: $synonyms, ')
          ..write('origin: $origin, ')
          ..write('usage: $usage')
          ..write(')'))
        .toString();
  }
}

class $CommonResourcesTable extends CommonResources
    with TableInfo<$CommonResourcesTable, CommonResource> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CommonResourcesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _keyMeta = const VerificationMeta('key');
  @override
  late final GeneratedColumn<String> key = GeneratedColumn<String>(
    'key',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _fileNameMeta = const VerificationMeta(
    'fileName',
  );
  @override
  late final GeneratedColumn<String> fileName = GeneratedColumn<String>(
    'file_name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _mimeTypeMeta = const VerificationMeta(
    'mimeType',
  );
  @override
  late final GeneratedColumn<String> mimeType = GeneratedColumn<String>(
    'mime_type',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _dataMeta = const VerificationMeta('data');
  @override
  late final GeneratedColumn<Uint8List> data = GeneratedColumn<Uint8List>(
    'data',
    aliasedName,
    false,
    type: DriftSqlType.blob,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [key, fileName, mimeType, data];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'common_resources';
  @override
  VerificationContext validateIntegrity(
    Insertable<CommonResource> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('key')) {
      context.handle(
        _keyMeta,
        key.isAcceptableOrUnknown(data['key']!, _keyMeta),
      );
    } else if (isInserting) {
      context.missing(_keyMeta);
    }
    if (data.containsKey('file_name')) {
      context.handle(
        _fileNameMeta,
        fileName.isAcceptableOrUnknown(data['file_name']!, _fileNameMeta),
      );
    } else if (isInserting) {
      context.missing(_fileNameMeta);
    }
    if (data.containsKey('mime_type')) {
      context.handle(
        _mimeTypeMeta,
        mimeType.isAcceptableOrUnknown(data['mime_type']!, _mimeTypeMeta),
      );
    } else if (isInserting) {
      context.missing(_mimeTypeMeta);
    }
    if (data.containsKey('data')) {
      context.handle(
        _dataMeta,
        this.data.isAcceptableOrUnknown(data['data']!, _dataMeta),
      );
    } else if (isInserting) {
      context.missing(_dataMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {key};
  @override
  CommonResource map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CommonResource(
      key: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}key'],
      )!,
      fileName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}file_name'],
      )!,
      mimeType: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}mime_type'],
      )!,
      data: attachedDatabase.typeMapping.read(
        DriftSqlType.blob,
        data['${effectivePrefix}data'],
      )!,
    );
  }

  @override
  $CommonResourcesTable createAlias(String alias) {
    return $CommonResourcesTable(attachedDatabase, alias);
  }
}

class CommonResource extends DataClass implements Insertable<CommonResource> {
  final String key;
  final String fileName;
  final String mimeType;
  final Uint8List data;
  const CommonResource({
    required this.key,
    required this.fileName,
    required this.mimeType,
    required this.data,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['key'] = Variable<String>(key);
    map['file_name'] = Variable<String>(fileName);
    map['mime_type'] = Variable<String>(mimeType);
    map['data'] = Variable<Uint8List>(data);
    return map;
  }

  CommonResourcesCompanion toCompanion(bool nullToAbsent) {
    return CommonResourcesCompanion(
      key: Value(key),
      fileName: Value(fileName),
      mimeType: Value(mimeType),
      data: Value(data),
    );
  }

  factory CommonResource.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CommonResource(
      key: serializer.fromJson<String>(json['key']),
      fileName: serializer.fromJson<String>(json['fileName']),
      mimeType: serializer.fromJson<String>(json['mimeType']),
      data: serializer.fromJson<Uint8List>(json['data']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'key': serializer.toJson<String>(key),
      'fileName': serializer.toJson<String>(fileName),
      'mimeType': serializer.toJson<String>(mimeType),
      'data': serializer.toJson<Uint8List>(data),
    };
  }

  CommonResource copyWith({
    String? key,
    String? fileName,
    String? mimeType,
    Uint8List? data,
  }) => CommonResource(
    key: key ?? this.key,
    fileName: fileName ?? this.fileName,
    mimeType: mimeType ?? this.mimeType,
    data: data ?? this.data,
  );
  CommonResource copyWithCompanion(CommonResourcesCompanion data) {
    return CommonResource(
      key: data.key.present ? data.key.value : this.key,
      fileName: data.fileName.present ? data.fileName.value : this.fileName,
      mimeType: data.mimeType.present ? data.mimeType.value : this.mimeType,
      data: data.data.present ? data.data.value : this.data,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CommonResource(')
          ..write('key: $key, ')
          ..write('fileName: $fileName, ')
          ..write('mimeType: $mimeType, ')
          ..write('data: $data')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(key, fileName, mimeType, $driftBlobEquality.hash(data));
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CommonResource &&
          other.key == this.key &&
          other.fileName == this.fileName &&
          other.mimeType == this.mimeType &&
          $driftBlobEquality.equals(other.data, this.data));
}

class CommonResourcesCompanion extends UpdateCompanion<CommonResource> {
  final Value<String> key;
  final Value<String> fileName;
  final Value<String> mimeType;
  final Value<Uint8List> data;
  final Value<int> rowid;
  const CommonResourcesCompanion({
    this.key = const Value.absent(),
    this.fileName = const Value.absent(),
    this.mimeType = const Value.absent(),
    this.data = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CommonResourcesCompanion.insert({
    required String key,
    required String fileName,
    required String mimeType,
    required Uint8List data,
    this.rowid = const Value.absent(),
  }) : key = Value(key),
       fileName = Value(fileName),
       mimeType = Value(mimeType),
       data = Value(data);
  static Insertable<CommonResource> custom({
    Expression<String>? key,
    Expression<String>? fileName,
    Expression<String>? mimeType,
    Expression<Uint8List>? data,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (key != null) 'key': key,
      if (fileName != null) 'file_name': fileName,
      if (mimeType != null) 'mime_type': mimeType,
      if (data != null) 'data': data,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CommonResourcesCompanion copyWith({
    Value<String>? key,
    Value<String>? fileName,
    Value<String>? mimeType,
    Value<Uint8List>? data,
    Value<int>? rowid,
  }) {
    return CommonResourcesCompanion(
      key: key ?? this.key,
      fileName: fileName ?? this.fileName,
      mimeType: mimeType ?? this.mimeType,
      data: data ?? this.data,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (key.present) {
      map['key'] = Variable<String>(key.value);
    }
    if (fileName.present) {
      map['file_name'] = Variable<String>(fileName.value);
    }
    if (mimeType.present) {
      map['mime_type'] = Variable<String>(mimeType.value);
    }
    if (data.present) {
      map['data'] = Variable<Uint8List>(data.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CommonResourcesCompanion(')
          ..write('key: $key, ')
          ..write('fileName: $fileName, ')
          ..write('mimeType: $mimeType, ')
          ..write('data: $data, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PrimarySourcesTable extends PrimarySources
    with TableInfo<$PrimarySourcesTable, PrimarySource> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PrimarySourcesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _familyMeta = const VerificationMeta('family');
  @override
  late final GeneratedColumn<String> family = GeneratedColumn<String>(
    'family',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _numberMeta = const VerificationMeta('number');
  @override
  late final GeneratedColumn<int> number = GeneratedColumn<int>(
    'number',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _groupKindMeta = const VerificationMeta(
    'groupKind',
  );
  @override
  late final GeneratedColumn<String> groupKind = GeneratedColumn<String>(
    'group_kind',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _sortOrderMeta = const VerificationMeta(
    'sortOrder',
  );
  @override
  late final GeneratedColumn<int> sortOrder = GeneratedColumn<int>(
    'sort_order',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _versesCountMeta = const VerificationMeta(
    'versesCount',
  );
  @override
  late final GeneratedColumn<int> versesCount = GeneratedColumn<int>(
    'verses_count',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _previewResourceKeyMeta =
      const VerificationMeta('previewResourceKey');
  @override
  late final GeneratedColumn<String> previewResourceKey =
      GeneratedColumn<String>(
        'preview_resource_key',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: true,
      );
  static const VerificationMeta _defaultMaxScaleMeta = const VerificationMeta(
    'defaultMaxScale',
  );
  @override
  late final GeneratedColumn<double> defaultMaxScale = GeneratedColumn<double>(
    'default_max_scale',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
    defaultValue: const Constant(3.0),
  );
  static const VerificationMeta _canShowImagesMeta = const VerificationMeta(
    'canShowImages',
  );
  @override
  late final GeneratedColumn<bool> canShowImages = GeneratedColumn<bool>(
    'can_show_images',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("can_show_images" IN (0, 1))',
    ),
    defaultValue: const Constant(true),
  );
  static const VerificationMeta _imagesAreMonochromeMeta =
      const VerificationMeta('imagesAreMonochrome');
  @override
  late final GeneratedColumn<bool> imagesAreMonochrome = GeneratedColumn<bool>(
    'images_are_monochrome',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("images_are_monochrome" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _notesMeta = const VerificationMeta('notes');
  @override
  late final GeneratedColumn<String> notes = GeneratedColumn<String>(
    'notes',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    family,
    number,
    groupKind,
    sortOrder,
    versesCount,
    previewResourceKey,
    defaultMaxScale,
    canShowImages,
    imagesAreMonochrome,
    notes,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'primary_sources';
  @override
  VerificationContext validateIntegrity(
    Insertable<PrimarySource> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('family')) {
      context.handle(
        _familyMeta,
        family.isAcceptableOrUnknown(data['family']!, _familyMeta),
      );
    } else if (isInserting) {
      context.missing(_familyMeta);
    }
    if (data.containsKey('number')) {
      context.handle(
        _numberMeta,
        number.isAcceptableOrUnknown(data['number']!, _numberMeta),
      );
    } else if (isInserting) {
      context.missing(_numberMeta);
    }
    if (data.containsKey('group_kind')) {
      context.handle(
        _groupKindMeta,
        groupKind.isAcceptableOrUnknown(data['group_kind']!, _groupKindMeta),
      );
    } else if (isInserting) {
      context.missing(_groupKindMeta);
    }
    if (data.containsKey('sort_order')) {
      context.handle(
        _sortOrderMeta,
        sortOrder.isAcceptableOrUnknown(data['sort_order']!, _sortOrderMeta),
      );
    }
    if (data.containsKey('verses_count')) {
      context.handle(
        _versesCountMeta,
        versesCount.isAcceptableOrUnknown(
          data['verses_count']!,
          _versesCountMeta,
        ),
      );
    }
    if (data.containsKey('preview_resource_key')) {
      context.handle(
        _previewResourceKeyMeta,
        previewResourceKey.isAcceptableOrUnknown(
          data['preview_resource_key']!,
          _previewResourceKeyMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_previewResourceKeyMeta);
    }
    if (data.containsKey('default_max_scale')) {
      context.handle(
        _defaultMaxScaleMeta,
        defaultMaxScale.isAcceptableOrUnknown(
          data['default_max_scale']!,
          _defaultMaxScaleMeta,
        ),
      );
    }
    if (data.containsKey('can_show_images')) {
      context.handle(
        _canShowImagesMeta,
        canShowImages.isAcceptableOrUnknown(
          data['can_show_images']!,
          _canShowImagesMeta,
        ),
      );
    }
    if (data.containsKey('images_are_monochrome')) {
      context.handle(
        _imagesAreMonochromeMeta,
        imagesAreMonochrome.isAcceptableOrUnknown(
          data['images_are_monochrome']!,
          _imagesAreMonochromeMeta,
        ),
      );
    }
    if (data.containsKey('notes')) {
      context.handle(
        _notesMeta,
        notes.isAcceptableOrUnknown(data['notes']!, _notesMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  PrimarySource map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PrimarySource(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      family: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}family'],
      )!,
      number: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}number'],
      )!,
      groupKind: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}group_kind'],
      )!,
      sortOrder: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}sort_order'],
      )!,
      versesCount: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}verses_count'],
      )!,
      previewResourceKey: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}preview_resource_key'],
      )!,
      defaultMaxScale: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}default_max_scale'],
      )!,
      canShowImages: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}can_show_images'],
      )!,
      imagesAreMonochrome: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}images_are_monochrome'],
      )!,
      notes: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}notes'],
      )!,
    );
  }

  @override
  $PrimarySourcesTable createAlias(String alias) {
    return $PrimarySourcesTable(attachedDatabase, alias);
  }
}

class PrimarySource extends DataClass implements Insertable<PrimarySource> {
  final String id;
  final String family;
  final int number;
  final String groupKind;
  final int sortOrder;
  final int versesCount;
  final String previewResourceKey;
  final double defaultMaxScale;
  final bool canShowImages;
  final bool imagesAreMonochrome;
  final String notes;
  const PrimarySource({
    required this.id,
    required this.family,
    required this.number,
    required this.groupKind,
    required this.sortOrder,
    required this.versesCount,
    required this.previewResourceKey,
    required this.defaultMaxScale,
    required this.canShowImages,
    required this.imagesAreMonochrome,
    required this.notes,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['family'] = Variable<String>(family);
    map['number'] = Variable<int>(number);
    map['group_kind'] = Variable<String>(groupKind);
    map['sort_order'] = Variable<int>(sortOrder);
    map['verses_count'] = Variable<int>(versesCount);
    map['preview_resource_key'] = Variable<String>(previewResourceKey);
    map['default_max_scale'] = Variable<double>(defaultMaxScale);
    map['can_show_images'] = Variable<bool>(canShowImages);
    map['images_are_monochrome'] = Variable<bool>(imagesAreMonochrome);
    map['notes'] = Variable<String>(notes);
    return map;
  }

  PrimarySourcesCompanion toCompanion(bool nullToAbsent) {
    return PrimarySourcesCompanion(
      id: Value(id),
      family: Value(family),
      number: Value(number),
      groupKind: Value(groupKind),
      sortOrder: Value(sortOrder),
      versesCount: Value(versesCount),
      previewResourceKey: Value(previewResourceKey),
      defaultMaxScale: Value(defaultMaxScale),
      canShowImages: Value(canShowImages),
      imagesAreMonochrome: Value(imagesAreMonochrome),
      notes: Value(notes),
    );
  }

  factory PrimarySource.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PrimarySource(
      id: serializer.fromJson<String>(json['id']),
      family: serializer.fromJson<String>(json['family']),
      number: serializer.fromJson<int>(json['number']),
      groupKind: serializer.fromJson<String>(json['groupKind']),
      sortOrder: serializer.fromJson<int>(json['sortOrder']),
      versesCount: serializer.fromJson<int>(json['versesCount']),
      previewResourceKey: serializer.fromJson<String>(
        json['previewResourceKey'],
      ),
      defaultMaxScale: serializer.fromJson<double>(json['defaultMaxScale']),
      canShowImages: serializer.fromJson<bool>(json['canShowImages']),
      imagesAreMonochrome: serializer.fromJson<bool>(
        json['imagesAreMonochrome'],
      ),
      notes: serializer.fromJson<String>(json['notes']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'family': serializer.toJson<String>(family),
      'number': serializer.toJson<int>(number),
      'groupKind': serializer.toJson<String>(groupKind),
      'sortOrder': serializer.toJson<int>(sortOrder),
      'versesCount': serializer.toJson<int>(versesCount),
      'previewResourceKey': serializer.toJson<String>(previewResourceKey),
      'defaultMaxScale': serializer.toJson<double>(defaultMaxScale),
      'canShowImages': serializer.toJson<bool>(canShowImages),
      'imagesAreMonochrome': serializer.toJson<bool>(imagesAreMonochrome),
      'notes': serializer.toJson<String>(notes),
    };
  }

  PrimarySource copyWith({
    String? id,
    String? family,
    int? number,
    String? groupKind,
    int? sortOrder,
    int? versesCount,
    String? previewResourceKey,
    double? defaultMaxScale,
    bool? canShowImages,
    bool? imagesAreMonochrome,
    String? notes,
  }) => PrimarySource(
    id: id ?? this.id,
    family: family ?? this.family,
    number: number ?? this.number,
    groupKind: groupKind ?? this.groupKind,
    sortOrder: sortOrder ?? this.sortOrder,
    versesCount: versesCount ?? this.versesCount,
    previewResourceKey: previewResourceKey ?? this.previewResourceKey,
    defaultMaxScale: defaultMaxScale ?? this.defaultMaxScale,
    canShowImages: canShowImages ?? this.canShowImages,
    imagesAreMonochrome: imagesAreMonochrome ?? this.imagesAreMonochrome,
    notes: notes ?? this.notes,
  );
  PrimarySource copyWithCompanion(PrimarySourcesCompanion data) {
    return PrimarySource(
      id: data.id.present ? data.id.value : this.id,
      family: data.family.present ? data.family.value : this.family,
      number: data.number.present ? data.number.value : this.number,
      groupKind: data.groupKind.present ? data.groupKind.value : this.groupKind,
      sortOrder: data.sortOrder.present ? data.sortOrder.value : this.sortOrder,
      versesCount: data.versesCount.present
          ? data.versesCount.value
          : this.versesCount,
      previewResourceKey: data.previewResourceKey.present
          ? data.previewResourceKey.value
          : this.previewResourceKey,
      defaultMaxScale: data.defaultMaxScale.present
          ? data.defaultMaxScale.value
          : this.defaultMaxScale,
      canShowImages: data.canShowImages.present
          ? data.canShowImages.value
          : this.canShowImages,
      imagesAreMonochrome: data.imagesAreMonochrome.present
          ? data.imagesAreMonochrome.value
          : this.imagesAreMonochrome,
      notes: data.notes.present ? data.notes.value : this.notes,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySource(')
          ..write('id: $id, ')
          ..write('family: $family, ')
          ..write('number: $number, ')
          ..write('groupKind: $groupKind, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('versesCount: $versesCount, ')
          ..write('previewResourceKey: $previewResourceKey, ')
          ..write('defaultMaxScale: $defaultMaxScale, ')
          ..write('canShowImages: $canShowImages, ')
          ..write('imagesAreMonochrome: $imagesAreMonochrome, ')
          ..write('notes: $notes')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    family,
    number,
    groupKind,
    sortOrder,
    versesCount,
    previewResourceKey,
    defaultMaxScale,
    canShowImages,
    imagesAreMonochrome,
    notes,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PrimarySource &&
          other.id == this.id &&
          other.family == this.family &&
          other.number == this.number &&
          other.groupKind == this.groupKind &&
          other.sortOrder == this.sortOrder &&
          other.versesCount == this.versesCount &&
          other.previewResourceKey == this.previewResourceKey &&
          other.defaultMaxScale == this.defaultMaxScale &&
          other.canShowImages == this.canShowImages &&
          other.imagesAreMonochrome == this.imagesAreMonochrome &&
          other.notes == this.notes);
}

class PrimarySourcesCompanion extends UpdateCompanion<PrimarySource> {
  final Value<String> id;
  final Value<String> family;
  final Value<int> number;
  final Value<String> groupKind;
  final Value<int> sortOrder;
  final Value<int> versesCount;
  final Value<String> previewResourceKey;
  final Value<double> defaultMaxScale;
  final Value<bool> canShowImages;
  final Value<bool> imagesAreMonochrome;
  final Value<String> notes;
  final Value<int> rowid;
  const PrimarySourcesCompanion({
    this.id = const Value.absent(),
    this.family = const Value.absent(),
    this.number = const Value.absent(),
    this.groupKind = const Value.absent(),
    this.sortOrder = const Value.absent(),
    this.versesCount = const Value.absent(),
    this.previewResourceKey = const Value.absent(),
    this.defaultMaxScale = const Value.absent(),
    this.canShowImages = const Value.absent(),
    this.imagesAreMonochrome = const Value.absent(),
    this.notes = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PrimarySourcesCompanion.insert({
    required String id,
    required String family,
    required int number,
    required String groupKind,
    this.sortOrder = const Value.absent(),
    this.versesCount = const Value.absent(),
    required String previewResourceKey,
    this.defaultMaxScale = const Value.absent(),
    this.canShowImages = const Value.absent(),
    this.imagesAreMonochrome = const Value.absent(),
    this.notes = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       family = Value(family),
       number = Value(number),
       groupKind = Value(groupKind),
       previewResourceKey = Value(previewResourceKey);
  static Insertable<PrimarySource> custom({
    Expression<String>? id,
    Expression<String>? family,
    Expression<int>? number,
    Expression<String>? groupKind,
    Expression<int>? sortOrder,
    Expression<int>? versesCount,
    Expression<String>? previewResourceKey,
    Expression<double>? defaultMaxScale,
    Expression<bool>? canShowImages,
    Expression<bool>? imagesAreMonochrome,
    Expression<String>? notes,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (family != null) 'family': family,
      if (number != null) 'number': number,
      if (groupKind != null) 'group_kind': groupKind,
      if (sortOrder != null) 'sort_order': sortOrder,
      if (versesCount != null) 'verses_count': versesCount,
      if (previewResourceKey != null)
        'preview_resource_key': previewResourceKey,
      if (defaultMaxScale != null) 'default_max_scale': defaultMaxScale,
      if (canShowImages != null) 'can_show_images': canShowImages,
      if (imagesAreMonochrome != null)
        'images_are_monochrome': imagesAreMonochrome,
      if (notes != null) 'notes': notes,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PrimarySourcesCompanion copyWith({
    Value<String>? id,
    Value<String>? family,
    Value<int>? number,
    Value<String>? groupKind,
    Value<int>? sortOrder,
    Value<int>? versesCount,
    Value<String>? previewResourceKey,
    Value<double>? defaultMaxScale,
    Value<bool>? canShowImages,
    Value<bool>? imagesAreMonochrome,
    Value<String>? notes,
    Value<int>? rowid,
  }) {
    return PrimarySourcesCompanion(
      id: id ?? this.id,
      family: family ?? this.family,
      number: number ?? this.number,
      groupKind: groupKind ?? this.groupKind,
      sortOrder: sortOrder ?? this.sortOrder,
      versesCount: versesCount ?? this.versesCount,
      previewResourceKey: previewResourceKey ?? this.previewResourceKey,
      defaultMaxScale: defaultMaxScale ?? this.defaultMaxScale,
      canShowImages: canShowImages ?? this.canShowImages,
      imagesAreMonochrome: imagesAreMonochrome ?? this.imagesAreMonochrome,
      notes: notes ?? this.notes,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (family.present) {
      map['family'] = Variable<String>(family.value);
    }
    if (number.present) {
      map['number'] = Variable<int>(number.value);
    }
    if (groupKind.present) {
      map['group_kind'] = Variable<String>(groupKind.value);
    }
    if (sortOrder.present) {
      map['sort_order'] = Variable<int>(sortOrder.value);
    }
    if (versesCount.present) {
      map['verses_count'] = Variable<int>(versesCount.value);
    }
    if (previewResourceKey.present) {
      map['preview_resource_key'] = Variable<String>(previewResourceKey.value);
    }
    if (defaultMaxScale.present) {
      map['default_max_scale'] = Variable<double>(defaultMaxScale.value);
    }
    if (canShowImages.present) {
      map['can_show_images'] = Variable<bool>(canShowImages.value);
    }
    if (imagesAreMonochrome.present) {
      map['images_are_monochrome'] = Variable<bool>(imagesAreMonochrome.value);
    }
    if (notes.present) {
      map['notes'] = Variable<String>(notes.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourcesCompanion(')
          ..write('id: $id, ')
          ..write('family: $family, ')
          ..write('number: $number, ')
          ..write('groupKind: $groupKind, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('versesCount: $versesCount, ')
          ..write('previewResourceKey: $previewResourceKey, ')
          ..write('defaultMaxScale: $defaultMaxScale, ')
          ..write('canShowImages: $canShowImages, ')
          ..write('imagesAreMonochrome: $imagesAreMonochrome, ')
          ..write('notes: $notes, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PrimarySourceLinksTable extends PrimarySourceLinks
    with TableInfo<$PrimarySourceLinksTable, PrimarySourceLink> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PrimarySourceLinksTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _sourceIdMeta = const VerificationMeta(
    'sourceId',
  );
  @override
  late final GeneratedColumn<String> sourceId = GeneratedColumn<String>(
    'source_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _linkIdMeta = const VerificationMeta('linkId');
  @override
  late final GeneratedColumn<String> linkId = GeneratedColumn<String>(
    'link_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _sortOrderMeta = const VerificationMeta(
    'sortOrder',
  );
  @override
  late final GeneratedColumn<int> sortOrder = GeneratedColumn<int>(
    'sort_order',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _linkRoleMeta = const VerificationMeta(
    'linkRole',
  );
  @override
  late final GeneratedColumn<String> linkRole = GeneratedColumn<String>(
    'link_role',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _urlMeta = const VerificationMeta('url');
  @override
  late final GeneratedColumn<String> url = GeneratedColumn<String>(
    'url',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [
    sourceId,
    linkId,
    sortOrder,
    linkRole,
    url,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'primary_source_links';
  @override
  VerificationContext validateIntegrity(
    Insertable<PrimarySourceLink> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('source_id')) {
      context.handle(
        _sourceIdMeta,
        sourceId.isAcceptableOrUnknown(data['source_id']!, _sourceIdMeta),
      );
    } else if (isInserting) {
      context.missing(_sourceIdMeta);
    }
    if (data.containsKey('link_id')) {
      context.handle(
        _linkIdMeta,
        linkId.isAcceptableOrUnknown(data['link_id']!, _linkIdMeta),
      );
    } else if (isInserting) {
      context.missing(_linkIdMeta);
    }
    if (data.containsKey('sort_order')) {
      context.handle(
        _sortOrderMeta,
        sortOrder.isAcceptableOrUnknown(data['sort_order']!, _sortOrderMeta),
      );
    }
    if (data.containsKey('link_role')) {
      context.handle(
        _linkRoleMeta,
        linkRole.isAcceptableOrUnknown(data['link_role']!, _linkRoleMeta),
      );
    } else if (isInserting) {
      context.missing(_linkRoleMeta);
    }
    if (data.containsKey('url')) {
      context.handle(
        _urlMeta,
        url.isAcceptableOrUnknown(data['url']!, _urlMeta),
      );
    } else if (isInserting) {
      context.missing(_urlMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {sourceId, linkId};
  @override
  PrimarySourceLink map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PrimarySourceLink(
      sourceId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}source_id'],
      )!,
      linkId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}link_id'],
      )!,
      sortOrder: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}sort_order'],
      )!,
      linkRole: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}link_role'],
      )!,
      url: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}url'],
      )!,
    );
  }

  @override
  $PrimarySourceLinksTable createAlias(String alias) {
    return $PrimarySourceLinksTable(attachedDatabase, alias);
  }
}

class PrimarySourceLink extends DataClass
    implements Insertable<PrimarySourceLink> {
  final String sourceId;
  final String linkId;
  final int sortOrder;
  final String linkRole;
  final String url;
  const PrimarySourceLink({
    required this.sourceId,
    required this.linkId,
    required this.sortOrder,
    required this.linkRole,
    required this.url,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['source_id'] = Variable<String>(sourceId);
    map['link_id'] = Variable<String>(linkId);
    map['sort_order'] = Variable<int>(sortOrder);
    map['link_role'] = Variable<String>(linkRole);
    map['url'] = Variable<String>(url);
    return map;
  }

  PrimarySourceLinksCompanion toCompanion(bool nullToAbsent) {
    return PrimarySourceLinksCompanion(
      sourceId: Value(sourceId),
      linkId: Value(linkId),
      sortOrder: Value(sortOrder),
      linkRole: Value(linkRole),
      url: Value(url),
    );
  }

  factory PrimarySourceLink.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PrimarySourceLink(
      sourceId: serializer.fromJson<String>(json['sourceId']),
      linkId: serializer.fromJson<String>(json['linkId']),
      sortOrder: serializer.fromJson<int>(json['sortOrder']),
      linkRole: serializer.fromJson<String>(json['linkRole']),
      url: serializer.fromJson<String>(json['url']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'sourceId': serializer.toJson<String>(sourceId),
      'linkId': serializer.toJson<String>(linkId),
      'sortOrder': serializer.toJson<int>(sortOrder),
      'linkRole': serializer.toJson<String>(linkRole),
      'url': serializer.toJson<String>(url),
    };
  }

  PrimarySourceLink copyWith({
    String? sourceId,
    String? linkId,
    int? sortOrder,
    String? linkRole,
    String? url,
  }) => PrimarySourceLink(
    sourceId: sourceId ?? this.sourceId,
    linkId: linkId ?? this.linkId,
    sortOrder: sortOrder ?? this.sortOrder,
    linkRole: linkRole ?? this.linkRole,
    url: url ?? this.url,
  );
  PrimarySourceLink copyWithCompanion(PrimarySourceLinksCompanion data) {
    return PrimarySourceLink(
      sourceId: data.sourceId.present ? data.sourceId.value : this.sourceId,
      linkId: data.linkId.present ? data.linkId.value : this.linkId,
      sortOrder: data.sortOrder.present ? data.sortOrder.value : this.sortOrder,
      linkRole: data.linkRole.present ? data.linkRole.value : this.linkRole,
      url: data.url.present ? data.url.value : this.url,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceLink(')
          ..write('sourceId: $sourceId, ')
          ..write('linkId: $linkId, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('linkRole: $linkRole, ')
          ..write('url: $url')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(sourceId, linkId, sortOrder, linkRole, url);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PrimarySourceLink &&
          other.sourceId == this.sourceId &&
          other.linkId == this.linkId &&
          other.sortOrder == this.sortOrder &&
          other.linkRole == this.linkRole &&
          other.url == this.url);
}

class PrimarySourceLinksCompanion extends UpdateCompanion<PrimarySourceLink> {
  final Value<String> sourceId;
  final Value<String> linkId;
  final Value<int> sortOrder;
  final Value<String> linkRole;
  final Value<String> url;
  final Value<int> rowid;
  const PrimarySourceLinksCompanion({
    this.sourceId = const Value.absent(),
    this.linkId = const Value.absent(),
    this.sortOrder = const Value.absent(),
    this.linkRole = const Value.absent(),
    this.url = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PrimarySourceLinksCompanion.insert({
    required String sourceId,
    required String linkId,
    this.sortOrder = const Value.absent(),
    required String linkRole,
    required String url,
    this.rowid = const Value.absent(),
  }) : sourceId = Value(sourceId),
       linkId = Value(linkId),
       linkRole = Value(linkRole),
       url = Value(url);
  static Insertable<PrimarySourceLink> custom({
    Expression<String>? sourceId,
    Expression<String>? linkId,
    Expression<int>? sortOrder,
    Expression<String>? linkRole,
    Expression<String>? url,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (sourceId != null) 'source_id': sourceId,
      if (linkId != null) 'link_id': linkId,
      if (sortOrder != null) 'sort_order': sortOrder,
      if (linkRole != null) 'link_role': linkRole,
      if (url != null) 'url': url,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PrimarySourceLinksCompanion copyWith({
    Value<String>? sourceId,
    Value<String>? linkId,
    Value<int>? sortOrder,
    Value<String>? linkRole,
    Value<String>? url,
    Value<int>? rowid,
  }) {
    return PrimarySourceLinksCompanion(
      sourceId: sourceId ?? this.sourceId,
      linkId: linkId ?? this.linkId,
      sortOrder: sortOrder ?? this.sortOrder,
      linkRole: linkRole ?? this.linkRole,
      url: url ?? this.url,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (sourceId.present) {
      map['source_id'] = Variable<String>(sourceId.value);
    }
    if (linkId.present) {
      map['link_id'] = Variable<String>(linkId.value);
    }
    if (sortOrder.present) {
      map['sort_order'] = Variable<int>(sortOrder.value);
    }
    if (linkRole.present) {
      map['link_role'] = Variable<String>(linkRole.value);
    }
    if (url.present) {
      map['url'] = Variable<String>(url.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceLinksCompanion(')
          ..write('sourceId: $sourceId, ')
          ..write('linkId: $linkId, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('linkRole: $linkRole, ')
          ..write('url: $url, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PrimarySourceAttributionsTable extends PrimarySourceAttributions
    with TableInfo<$PrimarySourceAttributionsTable, PrimarySourceAttribution> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PrimarySourceAttributionsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _sourceIdMeta = const VerificationMeta(
    'sourceId',
  );
  @override
  late final GeneratedColumn<String> sourceId = GeneratedColumn<String>(
    'source_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _attributionIdMeta = const VerificationMeta(
    'attributionId',
  );
  @override
  late final GeneratedColumn<String> attributionId = GeneratedColumn<String>(
    'attribution_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _sortOrderMeta = const VerificationMeta(
    'sortOrder',
  );
  @override
  late final GeneratedColumn<int> sortOrder = GeneratedColumn<int>(
    'sort_order',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _displayTextMeta = const VerificationMeta(
    'displayText',
  );
  @override
  late final GeneratedColumn<String> displayText = GeneratedColumn<String>(
    'text',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _urlMeta = const VerificationMeta('url');
  @override
  late final GeneratedColumn<String> url = GeneratedColumn<String>(
    'url',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [
    sourceId,
    attributionId,
    sortOrder,
    displayText,
    url,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'primary_source_attributions';
  @override
  VerificationContext validateIntegrity(
    Insertable<PrimarySourceAttribution> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('source_id')) {
      context.handle(
        _sourceIdMeta,
        sourceId.isAcceptableOrUnknown(data['source_id']!, _sourceIdMeta),
      );
    } else if (isInserting) {
      context.missing(_sourceIdMeta);
    }
    if (data.containsKey('attribution_id')) {
      context.handle(
        _attributionIdMeta,
        attributionId.isAcceptableOrUnknown(
          data['attribution_id']!,
          _attributionIdMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_attributionIdMeta);
    }
    if (data.containsKey('sort_order')) {
      context.handle(
        _sortOrderMeta,
        sortOrder.isAcceptableOrUnknown(data['sort_order']!, _sortOrderMeta),
      );
    }
    if (data.containsKey('text')) {
      context.handle(
        _displayTextMeta,
        displayText.isAcceptableOrUnknown(data['text']!, _displayTextMeta),
      );
    } else if (isInserting) {
      context.missing(_displayTextMeta);
    }
    if (data.containsKey('url')) {
      context.handle(
        _urlMeta,
        url.isAcceptableOrUnknown(data['url']!, _urlMeta),
      );
    } else if (isInserting) {
      context.missing(_urlMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {sourceId, attributionId};
  @override
  PrimarySourceAttribution map(
    Map<String, dynamic> data, {
    String? tablePrefix,
  }) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PrimarySourceAttribution(
      sourceId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}source_id'],
      )!,
      attributionId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}attribution_id'],
      )!,
      sortOrder: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}sort_order'],
      )!,
      displayText: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}text'],
      )!,
      url: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}url'],
      )!,
    );
  }

  @override
  $PrimarySourceAttributionsTable createAlias(String alias) {
    return $PrimarySourceAttributionsTable(attachedDatabase, alias);
  }
}

class PrimarySourceAttribution extends DataClass
    implements Insertable<PrimarySourceAttribution> {
  final String sourceId;
  final String attributionId;
  final int sortOrder;
  final String displayText;
  final String url;
  const PrimarySourceAttribution({
    required this.sourceId,
    required this.attributionId,
    required this.sortOrder,
    required this.displayText,
    required this.url,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['source_id'] = Variable<String>(sourceId);
    map['attribution_id'] = Variable<String>(attributionId);
    map['sort_order'] = Variable<int>(sortOrder);
    map['text'] = Variable<String>(displayText);
    map['url'] = Variable<String>(url);
    return map;
  }

  PrimarySourceAttributionsCompanion toCompanion(bool nullToAbsent) {
    return PrimarySourceAttributionsCompanion(
      sourceId: Value(sourceId),
      attributionId: Value(attributionId),
      sortOrder: Value(sortOrder),
      displayText: Value(displayText),
      url: Value(url),
    );
  }

  factory PrimarySourceAttribution.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PrimarySourceAttribution(
      sourceId: serializer.fromJson<String>(json['sourceId']),
      attributionId: serializer.fromJson<String>(json['attributionId']),
      sortOrder: serializer.fromJson<int>(json['sortOrder']),
      displayText: serializer.fromJson<String>(json['displayText']),
      url: serializer.fromJson<String>(json['url']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'sourceId': serializer.toJson<String>(sourceId),
      'attributionId': serializer.toJson<String>(attributionId),
      'sortOrder': serializer.toJson<int>(sortOrder),
      'displayText': serializer.toJson<String>(displayText),
      'url': serializer.toJson<String>(url),
    };
  }

  PrimarySourceAttribution copyWith({
    String? sourceId,
    String? attributionId,
    int? sortOrder,
    String? displayText,
    String? url,
  }) => PrimarySourceAttribution(
    sourceId: sourceId ?? this.sourceId,
    attributionId: attributionId ?? this.attributionId,
    sortOrder: sortOrder ?? this.sortOrder,
    displayText: displayText ?? this.displayText,
    url: url ?? this.url,
  );
  PrimarySourceAttribution copyWithCompanion(
    PrimarySourceAttributionsCompanion data,
  ) {
    return PrimarySourceAttribution(
      sourceId: data.sourceId.present ? data.sourceId.value : this.sourceId,
      attributionId: data.attributionId.present
          ? data.attributionId.value
          : this.attributionId,
      sortOrder: data.sortOrder.present ? data.sortOrder.value : this.sortOrder,
      displayText: data.displayText.present
          ? data.displayText.value
          : this.displayText,
      url: data.url.present ? data.url.value : this.url,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceAttribution(')
          ..write('sourceId: $sourceId, ')
          ..write('attributionId: $attributionId, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('displayText: $displayText, ')
          ..write('url: $url')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(sourceId, attributionId, sortOrder, displayText, url);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PrimarySourceAttribution &&
          other.sourceId == this.sourceId &&
          other.attributionId == this.attributionId &&
          other.sortOrder == this.sortOrder &&
          other.displayText == this.displayText &&
          other.url == this.url);
}

class PrimarySourceAttributionsCompanion
    extends UpdateCompanion<PrimarySourceAttribution> {
  final Value<String> sourceId;
  final Value<String> attributionId;
  final Value<int> sortOrder;
  final Value<String> displayText;
  final Value<String> url;
  final Value<int> rowid;
  const PrimarySourceAttributionsCompanion({
    this.sourceId = const Value.absent(),
    this.attributionId = const Value.absent(),
    this.sortOrder = const Value.absent(),
    this.displayText = const Value.absent(),
    this.url = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PrimarySourceAttributionsCompanion.insert({
    required String sourceId,
    required String attributionId,
    this.sortOrder = const Value.absent(),
    required String displayText,
    required String url,
    this.rowid = const Value.absent(),
  }) : sourceId = Value(sourceId),
       attributionId = Value(attributionId),
       displayText = Value(displayText),
       url = Value(url);
  static Insertable<PrimarySourceAttribution> custom({
    Expression<String>? sourceId,
    Expression<String>? attributionId,
    Expression<int>? sortOrder,
    Expression<String>? displayText,
    Expression<String>? url,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (sourceId != null) 'source_id': sourceId,
      if (attributionId != null) 'attribution_id': attributionId,
      if (sortOrder != null) 'sort_order': sortOrder,
      if (displayText != null) 'text': displayText,
      if (url != null) 'url': url,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PrimarySourceAttributionsCompanion copyWith({
    Value<String>? sourceId,
    Value<String>? attributionId,
    Value<int>? sortOrder,
    Value<String>? displayText,
    Value<String>? url,
    Value<int>? rowid,
  }) {
    return PrimarySourceAttributionsCompanion(
      sourceId: sourceId ?? this.sourceId,
      attributionId: attributionId ?? this.attributionId,
      sortOrder: sortOrder ?? this.sortOrder,
      displayText: displayText ?? this.displayText,
      url: url ?? this.url,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (sourceId.present) {
      map['source_id'] = Variable<String>(sourceId.value);
    }
    if (attributionId.present) {
      map['attribution_id'] = Variable<String>(attributionId.value);
    }
    if (sortOrder.present) {
      map['sort_order'] = Variable<int>(sortOrder.value);
    }
    if (displayText.present) {
      map['text'] = Variable<String>(displayText.value);
    }
    if (url.present) {
      map['url'] = Variable<String>(url.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceAttributionsCompanion(')
          ..write('sourceId: $sourceId, ')
          ..write('attributionId: $attributionId, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('displayText: $displayText, ')
          ..write('url: $url, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PrimarySourcePagesTable extends PrimarySourcePages
    with TableInfo<$PrimarySourcePagesTable, PrimarySourcePage> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PrimarySourcePagesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _sourceIdMeta = const VerificationMeta(
    'sourceId',
  );
  @override
  late final GeneratedColumn<String> sourceId = GeneratedColumn<String>(
    'source_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _pageNameMeta = const VerificationMeta(
    'pageName',
  );
  @override
  late final GeneratedColumn<String> pageName = GeneratedColumn<String>(
    'page_name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _sortOrderMeta = const VerificationMeta(
    'sortOrder',
  );
  @override
  late final GeneratedColumn<int> sortOrder = GeneratedColumn<int>(
    'sort_order',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _contentRefMeta = const VerificationMeta(
    'contentRef',
  );
  @override
  late final GeneratedColumn<String> contentRef = GeneratedColumn<String>(
    'content_ref',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _imagePathMeta = const VerificationMeta(
    'imagePath',
  );
  @override
  late final GeneratedColumn<String> imagePath = GeneratedColumn<String>(
    'image_path',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _mobileImagePathMeta = const VerificationMeta(
    'mobileImagePath',
  );
  @override
  late final GeneratedColumn<String> mobileImagePath = GeneratedColumn<String>(
    'mobile_image_path',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    sourceId,
    pageName,
    sortOrder,
    contentRef,
    imagePath,
    mobileImagePath,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'primary_source_pages';
  @override
  VerificationContext validateIntegrity(
    Insertable<PrimarySourcePage> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('source_id')) {
      context.handle(
        _sourceIdMeta,
        sourceId.isAcceptableOrUnknown(data['source_id']!, _sourceIdMeta),
      );
    } else if (isInserting) {
      context.missing(_sourceIdMeta);
    }
    if (data.containsKey('page_name')) {
      context.handle(
        _pageNameMeta,
        pageName.isAcceptableOrUnknown(data['page_name']!, _pageNameMeta),
      );
    } else if (isInserting) {
      context.missing(_pageNameMeta);
    }
    if (data.containsKey('sort_order')) {
      context.handle(
        _sortOrderMeta,
        sortOrder.isAcceptableOrUnknown(data['sort_order']!, _sortOrderMeta),
      );
    }
    if (data.containsKey('content_ref')) {
      context.handle(
        _contentRefMeta,
        contentRef.isAcceptableOrUnknown(data['content_ref']!, _contentRefMeta),
      );
    } else if (isInserting) {
      context.missing(_contentRefMeta);
    }
    if (data.containsKey('image_path')) {
      context.handle(
        _imagePathMeta,
        imagePath.isAcceptableOrUnknown(data['image_path']!, _imagePathMeta),
      );
    } else if (isInserting) {
      context.missing(_imagePathMeta);
    }
    if (data.containsKey('mobile_image_path')) {
      context.handle(
        _mobileImagePathMeta,
        mobileImagePath.isAcceptableOrUnknown(
          data['mobile_image_path']!,
          _mobileImagePathMeta,
        ),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {sourceId, pageName};
  @override
  PrimarySourcePage map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PrimarySourcePage(
      sourceId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}source_id'],
      )!,
      pageName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}page_name'],
      )!,
      sortOrder: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}sort_order'],
      )!,
      contentRef: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}content_ref'],
      )!,
      imagePath: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}image_path'],
      )!,
      mobileImagePath: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}mobile_image_path'],
      ),
    );
  }

  @override
  $PrimarySourcePagesTable createAlias(String alias) {
    return $PrimarySourcePagesTable(attachedDatabase, alias);
  }
}

class PrimarySourcePage extends DataClass
    implements Insertable<PrimarySourcePage> {
  final String sourceId;
  final String pageName;
  final int sortOrder;
  final String contentRef;
  final String imagePath;
  final String? mobileImagePath;
  const PrimarySourcePage({
    required this.sourceId,
    required this.pageName,
    required this.sortOrder,
    required this.contentRef,
    required this.imagePath,
    this.mobileImagePath,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['source_id'] = Variable<String>(sourceId);
    map['page_name'] = Variable<String>(pageName);
    map['sort_order'] = Variable<int>(sortOrder);
    map['content_ref'] = Variable<String>(contentRef);
    map['image_path'] = Variable<String>(imagePath);
    if (!nullToAbsent || mobileImagePath != null) {
      map['mobile_image_path'] = Variable<String>(mobileImagePath);
    }
    return map;
  }

  PrimarySourcePagesCompanion toCompanion(bool nullToAbsent) {
    return PrimarySourcePagesCompanion(
      sourceId: Value(sourceId),
      pageName: Value(pageName),
      sortOrder: Value(sortOrder),
      contentRef: Value(contentRef),
      imagePath: Value(imagePath),
      mobileImagePath: mobileImagePath == null && nullToAbsent
          ? const Value.absent()
          : Value(mobileImagePath),
    );
  }

  factory PrimarySourcePage.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PrimarySourcePage(
      sourceId: serializer.fromJson<String>(json['sourceId']),
      pageName: serializer.fromJson<String>(json['pageName']),
      sortOrder: serializer.fromJson<int>(json['sortOrder']),
      contentRef: serializer.fromJson<String>(json['contentRef']),
      imagePath: serializer.fromJson<String>(json['imagePath']),
      mobileImagePath: serializer.fromJson<String?>(json['mobileImagePath']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'sourceId': serializer.toJson<String>(sourceId),
      'pageName': serializer.toJson<String>(pageName),
      'sortOrder': serializer.toJson<int>(sortOrder),
      'contentRef': serializer.toJson<String>(contentRef),
      'imagePath': serializer.toJson<String>(imagePath),
      'mobileImagePath': serializer.toJson<String?>(mobileImagePath),
    };
  }

  PrimarySourcePage copyWith({
    String? sourceId,
    String? pageName,
    int? sortOrder,
    String? contentRef,
    String? imagePath,
    Value<String?> mobileImagePath = const Value.absent(),
  }) => PrimarySourcePage(
    sourceId: sourceId ?? this.sourceId,
    pageName: pageName ?? this.pageName,
    sortOrder: sortOrder ?? this.sortOrder,
    contentRef: contentRef ?? this.contentRef,
    imagePath: imagePath ?? this.imagePath,
    mobileImagePath: mobileImagePath.present
        ? mobileImagePath.value
        : this.mobileImagePath,
  );
  PrimarySourcePage copyWithCompanion(PrimarySourcePagesCompanion data) {
    return PrimarySourcePage(
      sourceId: data.sourceId.present ? data.sourceId.value : this.sourceId,
      pageName: data.pageName.present ? data.pageName.value : this.pageName,
      sortOrder: data.sortOrder.present ? data.sortOrder.value : this.sortOrder,
      contentRef: data.contentRef.present
          ? data.contentRef.value
          : this.contentRef,
      imagePath: data.imagePath.present ? data.imagePath.value : this.imagePath,
      mobileImagePath: data.mobileImagePath.present
          ? data.mobileImagePath.value
          : this.mobileImagePath,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourcePage(')
          ..write('sourceId: $sourceId, ')
          ..write('pageName: $pageName, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('contentRef: $contentRef, ')
          ..write('imagePath: $imagePath, ')
          ..write('mobileImagePath: $mobileImagePath')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    sourceId,
    pageName,
    sortOrder,
    contentRef,
    imagePath,
    mobileImagePath,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PrimarySourcePage &&
          other.sourceId == this.sourceId &&
          other.pageName == this.pageName &&
          other.sortOrder == this.sortOrder &&
          other.contentRef == this.contentRef &&
          other.imagePath == this.imagePath &&
          other.mobileImagePath == this.mobileImagePath);
}

class PrimarySourcePagesCompanion extends UpdateCompanion<PrimarySourcePage> {
  final Value<String> sourceId;
  final Value<String> pageName;
  final Value<int> sortOrder;
  final Value<String> contentRef;
  final Value<String> imagePath;
  final Value<String?> mobileImagePath;
  final Value<int> rowid;
  const PrimarySourcePagesCompanion({
    this.sourceId = const Value.absent(),
    this.pageName = const Value.absent(),
    this.sortOrder = const Value.absent(),
    this.contentRef = const Value.absent(),
    this.imagePath = const Value.absent(),
    this.mobileImagePath = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PrimarySourcePagesCompanion.insert({
    required String sourceId,
    required String pageName,
    this.sortOrder = const Value.absent(),
    required String contentRef,
    required String imagePath,
    this.mobileImagePath = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : sourceId = Value(sourceId),
       pageName = Value(pageName),
       contentRef = Value(contentRef),
       imagePath = Value(imagePath);
  static Insertable<PrimarySourcePage> custom({
    Expression<String>? sourceId,
    Expression<String>? pageName,
    Expression<int>? sortOrder,
    Expression<String>? contentRef,
    Expression<String>? imagePath,
    Expression<String>? mobileImagePath,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (sourceId != null) 'source_id': sourceId,
      if (pageName != null) 'page_name': pageName,
      if (sortOrder != null) 'sort_order': sortOrder,
      if (contentRef != null) 'content_ref': contentRef,
      if (imagePath != null) 'image_path': imagePath,
      if (mobileImagePath != null) 'mobile_image_path': mobileImagePath,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PrimarySourcePagesCompanion copyWith({
    Value<String>? sourceId,
    Value<String>? pageName,
    Value<int>? sortOrder,
    Value<String>? contentRef,
    Value<String>? imagePath,
    Value<String?>? mobileImagePath,
    Value<int>? rowid,
  }) {
    return PrimarySourcePagesCompanion(
      sourceId: sourceId ?? this.sourceId,
      pageName: pageName ?? this.pageName,
      sortOrder: sortOrder ?? this.sortOrder,
      contentRef: contentRef ?? this.contentRef,
      imagePath: imagePath ?? this.imagePath,
      mobileImagePath: mobileImagePath ?? this.mobileImagePath,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (sourceId.present) {
      map['source_id'] = Variable<String>(sourceId.value);
    }
    if (pageName.present) {
      map['page_name'] = Variable<String>(pageName.value);
    }
    if (sortOrder.present) {
      map['sort_order'] = Variable<int>(sortOrder.value);
    }
    if (contentRef.present) {
      map['content_ref'] = Variable<String>(contentRef.value);
    }
    if (imagePath.present) {
      map['image_path'] = Variable<String>(imagePath.value);
    }
    if (mobileImagePath.present) {
      map['mobile_image_path'] = Variable<String>(mobileImagePath.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourcePagesCompanion(')
          ..write('sourceId: $sourceId, ')
          ..write('pageName: $pageName, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('contentRef: $contentRef, ')
          ..write('imagePath: $imagePath, ')
          ..write('mobileImagePath: $mobileImagePath, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PrimarySourceWordsTable extends PrimarySourceWords
    with TableInfo<$PrimarySourceWordsTable, PrimarySourceWord> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PrimarySourceWordsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _sourceIdMeta = const VerificationMeta(
    'sourceId',
  );
  @override
  late final GeneratedColumn<String> sourceId = GeneratedColumn<String>(
    'source_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _pageNameMeta = const VerificationMeta(
    'pageName',
  );
  @override
  late final GeneratedColumn<String> pageName = GeneratedColumn<String>(
    'page_name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _wordIndexMeta = const VerificationMeta(
    'wordIndex',
  );
  @override
  late final GeneratedColumn<int> wordIndex = GeneratedColumn<int>(
    'word_index',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _wordTextMeta = const VerificationMeta(
    'wordText',
  );
  @override
  late final GeneratedColumn<String> wordText = GeneratedColumn<String>(
    'text',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _strongNumberMeta = const VerificationMeta(
    'strongNumber',
  );
  @override
  late final GeneratedColumn<int> strongNumber = GeneratedColumn<int>(
    'strong_number',
    aliasedName,
    true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _strongPronounceMeta = const VerificationMeta(
    'strongPronounce',
  );
  @override
  late final GeneratedColumn<bool> strongPronounce = GeneratedColumn<bool>(
    'strong_pronounce',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("strong_pronounce" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _strongXShiftMeta = const VerificationMeta(
    'strongXShift',
  );
  @override
  late final GeneratedColumn<double> strongXShift = GeneratedColumn<double>(
    'strong_x_shift',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
    defaultValue: const Constant(0.0),
  );
  static const VerificationMeta _missingCharIndexesJsonMeta =
      const VerificationMeta('missingCharIndexesJson');
  @override
  late final GeneratedColumn<String> missingCharIndexesJson =
      GeneratedColumn<String>(
        'missing_char_indexes_json',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: false,
        defaultValue: const Constant('[]'),
      );
  static const VerificationMeta _rectanglesJsonMeta = const VerificationMeta(
    'rectanglesJson',
  );
  @override
  late final GeneratedColumn<String> rectanglesJson = GeneratedColumn<String>(
    'rectangles_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('[]'),
  );
  @override
  List<GeneratedColumn> get $columns => [
    sourceId,
    pageName,
    wordIndex,
    wordText,
    strongNumber,
    strongPronounce,
    strongXShift,
    missingCharIndexesJson,
    rectanglesJson,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'primary_source_words';
  @override
  VerificationContext validateIntegrity(
    Insertable<PrimarySourceWord> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('source_id')) {
      context.handle(
        _sourceIdMeta,
        sourceId.isAcceptableOrUnknown(data['source_id']!, _sourceIdMeta),
      );
    } else if (isInserting) {
      context.missing(_sourceIdMeta);
    }
    if (data.containsKey('page_name')) {
      context.handle(
        _pageNameMeta,
        pageName.isAcceptableOrUnknown(data['page_name']!, _pageNameMeta),
      );
    } else if (isInserting) {
      context.missing(_pageNameMeta);
    }
    if (data.containsKey('word_index')) {
      context.handle(
        _wordIndexMeta,
        wordIndex.isAcceptableOrUnknown(data['word_index']!, _wordIndexMeta),
      );
    } else if (isInserting) {
      context.missing(_wordIndexMeta);
    }
    if (data.containsKey('text')) {
      context.handle(
        _wordTextMeta,
        wordText.isAcceptableOrUnknown(data['text']!, _wordTextMeta),
      );
    } else if (isInserting) {
      context.missing(_wordTextMeta);
    }
    if (data.containsKey('strong_number')) {
      context.handle(
        _strongNumberMeta,
        strongNumber.isAcceptableOrUnknown(
          data['strong_number']!,
          _strongNumberMeta,
        ),
      );
    }
    if (data.containsKey('strong_pronounce')) {
      context.handle(
        _strongPronounceMeta,
        strongPronounce.isAcceptableOrUnknown(
          data['strong_pronounce']!,
          _strongPronounceMeta,
        ),
      );
    }
    if (data.containsKey('strong_x_shift')) {
      context.handle(
        _strongXShiftMeta,
        strongXShift.isAcceptableOrUnknown(
          data['strong_x_shift']!,
          _strongXShiftMeta,
        ),
      );
    }
    if (data.containsKey('missing_char_indexes_json')) {
      context.handle(
        _missingCharIndexesJsonMeta,
        missingCharIndexesJson.isAcceptableOrUnknown(
          data['missing_char_indexes_json']!,
          _missingCharIndexesJsonMeta,
        ),
      );
    }
    if (data.containsKey('rectangles_json')) {
      context.handle(
        _rectanglesJsonMeta,
        rectanglesJson.isAcceptableOrUnknown(
          data['rectangles_json']!,
          _rectanglesJsonMeta,
        ),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {sourceId, pageName, wordIndex};
  @override
  PrimarySourceWord map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PrimarySourceWord(
      sourceId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}source_id'],
      )!,
      pageName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}page_name'],
      )!,
      wordIndex: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}word_index'],
      )!,
      wordText: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}text'],
      )!,
      strongNumber: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}strong_number'],
      ),
      strongPronounce: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}strong_pronounce'],
      )!,
      strongXShift: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}strong_x_shift'],
      )!,
      missingCharIndexesJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}missing_char_indexes_json'],
      )!,
      rectanglesJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}rectangles_json'],
      )!,
    );
  }

  @override
  $PrimarySourceWordsTable createAlias(String alias) {
    return $PrimarySourceWordsTable(attachedDatabase, alias);
  }
}

class PrimarySourceWord extends DataClass
    implements Insertable<PrimarySourceWord> {
  final String sourceId;
  final String pageName;
  final int wordIndex;
  final String wordText;
  final int? strongNumber;
  final bool strongPronounce;
  final double strongXShift;
  final String missingCharIndexesJson;
  final String rectanglesJson;
  const PrimarySourceWord({
    required this.sourceId,
    required this.pageName,
    required this.wordIndex,
    required this.wordText,
    this.strongNumber,
    required this.strongPronounce,
    required this.strongXShift,
    required this.missingCharIndexesJson,
    required this.rectanglesJson,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['source_id'] = Variable<String>(sourceId);
    map['page_name'] = Variable<String>(pageName);
    map['word_index'] = Variable<int>(wordIndex);
    map['text'] = Variable<String>(wordText);
    if (!nullToAbsent || strongNumber != null) {
      map['strong_number'] = Variable<int>(strongNumber);
    }
    map['strong_pronounce'] = Variable<bool>(strongPronounce);
    map['strong_x_shift'] = Variable<double>(strongXShift);
    map['missing_char_indexes_json'] = Variable<String>(missingCharIndexesJson);
    map['rectangles_json'] = Variable<String>(rectanglesJson);
    return map;
  }

  PrimarySourceWordsCompanion toCompanion(bool nullToAbsent) {
    return PrimarySourceWordsCompanion(
      sourceId: Value(sourceId),
      pageName: Value(pageName),
      wordIndex: Value(wordIndex),
      wordText: Value(wordText),
      strongNumber: strongNumber == null && nullToAbsent
          ? const Value.absent()
          : Value(strongNumber),
      strongPronounce: Value(strongPronounce),
      strongXShift: Value(strongXShift),
      missingCharIndexesJson: Value(missingCharIndexesJson),
      rectanglesJson: Value(rectanglesJson),
    );
  }

  factory PrimarySourceWord.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PrimarySourceWord(
      sourceId: serializer.fromJson<String>(json['sourceId']),
      pageName: serializer.fromJson<String>(json['pageName']),
      wordIndex: serializer.fromJson<int>(json['wordIndex']),
      wordText: serializer.fromJson<String>(json['wordText']),
      strongNumber: serializer.fromJson<int?>(json['strongNumber']),
      strongPronounce: serializer.fromJson<bool>(json['strongPronounce']),
      strongXShift: serializer.fromJson<double>(json['strongXShift']),
      missingCharIndexesJson: serializer.fromJson<String>(
        json['missingCharIndexesJson'],
      ),
      rectanglesJson: serializer.fromJson<String>(json['rectanglesJson']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'sourceId': serializer.toJson<String>(sourceId),
      'pageName': serializer.toJson<String>(pageName),
      'wordIndex': serializer.toJson<int>(wordIndex),
      'wordText': serializer.toJson<String>(wordText),
      'strongNumber': serializer.toJson<int?>(strongNumber),
      'strongPronounce': serializer.toJson<bool>(strongPronounce),
      'strongXShift': serializer.toJson<double>(strongXShift),
      'missingCharIndexesJson': serializer.toJson<String>(
        missingCharIndexesJson,
      ),
      'rectanglesJson': serializer.toJson<String>(rectanglesJson),
    };
  }

  PrimarySourceWord copyWith({
    String? sourceId,
    String? pageName,
    int? wordIndex,
    String? wordText,
    Value<int?> strongNumber = const Value.absent(),
    bool? strongPronounce,
    double? strongXShift,
    String? missingCharIndexesJson,
    String? rectanglesJson,
  }) => PrimarySourceWord(
    sourceId: sourceId ?? this.sourceId,
    pageName: pageName ?? this.pageName,
    wordIndex: wordIndex ?? this.wordIndex,
    wordText: wordText ?? this.wordText,
    strongNumber: strongNumber.present ? strongNumber.value : this.strongNumber,
    strongPronounce: strongPronounce ?? this.strongPronounce,
    strongXShift: strongXShift ?? this.strongXShift,
    missingCharIndexesJson:
        missingCharIndexesJson ?? this.missingCharIndexesJson,
    rectanglesJson: rectanglesJson ?? this.rectanglesJson,
  );
  PrimarySourceWord copyWithCompanion(PrimarySourceWordsCompanion data) {
    return PrimarySourceWord(
      sourceId: data.sourceId.present ? data.sourceId.value : this.sourceId,
      pageName: data.pageName.present ? data.pageName.value : this.pageName,
      wordIndex: data.wordIndex.present ? data.wordIndex.value : this.wordIndex,
      wordText: data.wordText.present ? data.wordText.value : this.wordText,
      strongNumber: data.strongNumber.present
          ? data.strongNumber.value
          : this.strongNumber,
      strongPronounce: data.strongPronounce.present
          ? data.strongPronounce.value
          : this.strongPronounce,
      strongXShift: data.strongXShift.present
          ? data.strongXShift.value
          : this.strongXShift,
      missingCharIndexesJson: data.missingCharIndexesJson.present
          ? data.missingCharIndexesJson.value
          : this.missingCharIndexesJson,
      rectanglesJson: data.rectanglesJson.present
          ? data.rectanglesJson.value
          : this.rectanglesJson,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceWord(')
          ..write('sourceId: $sourceId, ')
          ..write('pageName: $pageName, ')
          ..write('wordIndex: $wordIndex, ')
          ..write('wordText: $wordText, ')
          ..write('strongNumber: $strongNumber, ')
          ..write('strongPronounce: $strongPronounce, ')
          ..write('strongXShift: $strongXShift, ')
          ..write('missingCharIndexesJson: $missingCharIndexesJson, ')
          ..write('rectanglesJson: $rectanglesJson')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    sourceId,
    pageName,
    wordIndex,
    wordText,
    strongNumber,
    strongPronounce,
    strongXShift,
    missingCharIndexesJson,
    rectanglesJson,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PrimarySourceWord &&
          other.sourceId == this.sourceId &&
          other.pageName == this.pageName &&
          other.wordIndex == this.wordIndex &&
          other.wordText == this.wordText &&
          other.strongNumber == this.strongNumber &&
          other.strongPronounce == this.strongPronounce &&
          other.strongXShift == this.strongXShift &&
          other.missingCharIndexesJson == this.missingCharIndexesJson &&
          other.rectanglesJson == this.rectanglesJson);
}

class PrimarySourceWordsCompanion extends UpdateCompanion<PrimarySourceWord> {
  final Value<String> sourceId;
  final Value<String> pageName;
  final Value<int> wordIndex;
  final Value<String> wordText;
  final Value<int?> strongNumber;
  final Value<bool> strongPronounce;
  final Value<double> strongXShift;
  final Value<String> missingCharIndexesJson;
  final Value<String> rectanglesJson;
  final Value<int> rowid;
  const PrimarySourceWordsCompanion({
    this.sourceId = const Value.absent(),
    this.pageName = const Value.absent(),
    this.wordIndex = const Value.absent(),
    this.wordText = const Value.absent(),
    this.strongNumber = const Value.absent(),
    this.strongPronounce = const Value.absent(),
    this.strongXShift = const Value.absent(),
    this.missingCharIndexesJson = const Value.absent(),
    this.rectanglesJson = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PrimarySourceWordsCompanion.insert({
    required String sourceId,
    required String pageName,
    required int wordIndex,
    required String wordText,
    this.strongNumber = const Value.absent(),
    this.strongPronounce = const Value.absent(),
    this.strongXShift = const Value.absent(),
    this.missingCharIndexesJson = const Value.absent(),
    this.rectanglesJson = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : sourceId = Value(sourceId),
       pageName = Value(pageName),
       wordIndex = Value(wordIndex),
       wordText = Value(wordText);
  static Insertable<PrimarySourceWord> custom({
    Expression<String>? sourceId,
    Expression<String>? pageName,
    Expression<int>? wordIndex,
    Expression<String>? wordText,
    Expression<int>? strongNumber,
    Expression<bool>? strongPronounce,
    Expression<double>? strongXShift,
    Expression<String>? missingCharIndexesJson,
    Expression<String>? rectanglesJson,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (sourceId != null) 'source_id': sourceId,
      if (pageName != null) 'page_name': pageName,
      if (wordIndex != null) 'word_index': wordIndex,
      if (wordText != null) 'text': wordText,
      if (strongNumber != null) 'strong_number': strongNumber,
      if (strongPronounce != null) 'strong_pronounce': strongPronounce,
      if (strongXShift != null) 'strong_x_shift': strongXShift,
      if (missingCharIndexesJson != null)
        'missing_char_indexes_json': missingCharIndexesJson,
      if (rectanglesJson != null) 'rectangles_json': rectanglesJson,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PrimarySourceWordsCompanion copyWith({
    Value<String>? sourceId,
    Value<String>? pageName,
    Value<int>? wordIndex,
    Value<String>? wordText,
    Value<int?>? strongNumber,
    Value<bool>? strongPronounce,
    Value<double>? strongXShift,
    Value<String>? missingCharIndexesJson,
    Value<String>? rectanglesJson,
    Value<int>? rowid,
  }) {
    return PrimarySourceWordsCompanion(
      sourceId: sourceId ?? this.sourceId,
      pageName: pageName ?? this.pageName,
      wordIndex: wordIndex ?? this.wordIndex,
      wordText: wordText ?? this.wordText,
      strongNumber: strongNumber ?? this.strongNumber,
      strongPronounce: strongPronounce ?? this.strongPronounce,
      strongXShift: strongXShift ?? this.strongXShift,
      missingCharIndexesJson:
          missingCharIndexesJson ?? this.missingCharIndexesJson,
      rectanglesJson: rectanglesJson ?? this.rectanglesJson,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (sourceId.present) {
      map['source_id'] = Variable<String>(sourceId.value);
    }
    if (pageName.present) {
      map['page_name'] = Variable<String>(pageName.value);
    }
    if (wordIndex.present) {
      map['word_index'] = Variable<int>(wordIndex.value);
    }
    if (wordText.present) {
      map['text'] = Variable<String>(wordText.value);
    }
    if (strongNumber.present) {
      map['strong_number'] = Variable<int>(strongNumber.value);
    }
    if (strongPronounce.present) {
      map['strong_pronounce'] = Variable<bool>(strongPronounce.value);
    }
    if (strongXShift.present) {
      map['strong_x_shift'] = Variable<double>(strongXShift.value);
    }
    if (missingCharIndexesJson.present) {
      map['missing_char_indexes_json'] = Variable<String>(
        missingCharIndexesJson.value,
      );
    }
    if (rectanglesJson.present) {
      map['rectangles_json'] = Variable<String>(rectanglesJson.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceWordsCompanion(')
          ..write('sourceId: $sourceId, ')
          ..write('pageName: $pageName, ')
          ..write('wordIndex: $wordIndex, ')
          ..write('wordText: $wordText, ')
          ..write('strongNumber: $strongNumber, ')
          ..write('strongPronounce: $strongPronounce, ')
          ..write('strongXShift: $strongXShift, ')
          ..write('missingCharIndexesJson: $missingCharIndexesJson, ')
          ..write('rectanglesJson: $rectanglesJson, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PrimarySourceVersesTable extends PrimarySourceVerses
    with TableInfo<$PrimarySourceVersesTable, PrimarySourceVerse> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PrimarySourceVersesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _sourceIdMeta = const VerificationMeta(
    'sourceId',
  );
  @override
  late final GeneratedColumn<String> sourceId = GeneratedColumn<String>(
    'source_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _pageNameMeta = const VerificationMeta(
    'pageName',
  );
  @override
  late final GeneratedColumn<String> pageName = GeneratedColumn<String>(
    'page_name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _verseIndexMeta = const VerificationMeta(
    'verseIndex',
  );
  @override
  late final GeneratedColumn<int> verseIndex = GeneratedColumn<int>(
    'verse_index',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _chapterNumberMeta = const VerificationMeta(
    'chapterNumber',
  );
  @override
  late final GeneratedColumn<int> chapterNumber = GeneratedColumn<int>(
    'chapter_number',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _verseNumberMeta = const VerificationMeta(
    'verseNumber',
  );
  @override
  late final GeneratedColumn<int> verseNumber = GeneratedColumn<int>(
    'verse_number',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _labelXMeta = const VerificationMeta('labelX');
  @override
  late final GeneratedColumn<double> labelX = GeneratedColumn<double>(
    'label_x',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _labelYMeta = const VerificationMeta('labelY');
  @override
  late final GeneratedColumn<double> labelY = GeneratedColumn<double>(
    'label_y',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _wordIndexesJsonMeta = const VerificationMeta(
    'wordIndexesJson',
  );
  @override
  late final GeneratedColumn<String> wordIndexesJson = GeneratedColumn<String>(
    'word_indexes_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('[]'),
  );
  static const VerificationMeta _contoursJsonMeta = const VerificationMeta(
    'contoursJson',
  );
  @override
  late final GeneratedColumn<String> contoursJson = GeneratedColumn<String>(
    'contours_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('[]'),
  );
  @override
  List<GeneratedColumn> get $columns => [
    sourceId,
    pageName,
    verseIndex,
    chapterNumber,
    verseNumber,
    labelX,
    labelY,
    wordIndexesJson,
    contoursJson,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'primary_source_verses';
  @override
  VerificationContext validateIntegrity(
    Insertable<PrimarySourceVerse> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('source_id')) {
      context.handle(
        _sourceIdMeta,
        sourceId.isAcceptableOrUnknown(data['source_id']!, _sourceIdMeta),
      );
    } else if (isInserting) {
      context.missing(_sourceIdMeta);
    }
    if (data.containsKey('page_name')) {
      context.handle(
        _pageNameMeta,
        pageName.isAcceptableOrUnknown(data['page_name']!, _pageNameMeta),
      );
    } else if (isInserting) {
      context.missing(_pageNameMeta);
    }
    if (data.containsKey('verse_index')) {
      context.handle(
        _verseIndexMeta,
        verseIndex.isAcceptableOrUnknown(data['verse_index']!, _verseIndexMeta),
      );
    } else if (isInserting) {
      context.missing(_verseIndexMeta);
    }
    if (data.containsKey('chapter_number')) {
      context.handle(
        _chapterNumberMeta,
        chapterNumber.isAcceptableOrUnknown(
          data['chapter_number']!,
          _chapterNumberMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_chapterNumberMeta);
    }
    if (data.containsKey('verse_number')) {
      context.handle(
        _verseNumberMeta,
        verseNumber.isAcceptableOrUnknown(
          data['verse_number']!,
          _verseNumberMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_verseNumberMeta);
    }
    if (data.containsKey('label_x')) {
      context.handle(
        _labelXMeta,
        labelX.isAcceptableOrUnknown(data['label_x']!, _labelXMeta),
      );
    } else if (isInserting) {
      context.missing(_labelXMeta);
    }
    if (data.containsKey('label_y')) {
      context.handle(
        _labelYMeta,
        labelY.isAcceptableOrUnknown(data['label_y']!, _labelYMeta),
      );
    } else if (isInserting) {
      context.missing(_labelYMeta);
    }
    if (data.containsKey('word_indexes_json')) {
      context.handle(
        _wordIndexesJsonMeta,
        wordIndexesJson.isAcceptableOrUnknown(
          data['word_indexes_json']!,
          _wordIndexesJsonMeta,
        ),
      );
    }
    if (data.containsKey('contours_json')) {
      context.handle(
        _contoursJsonMeta,
        contoursJson.isAcceptableOrUnknown(
          data['contours_json']!,
          _contoursJsonMeta,
        ),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {sourceId, pageName, verseIndex};
  @override
  PrimarySourceVerse map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PrimarySourceVerse(
      sourceId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}source_id'],
      )!,
      pageName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}page_name'],
      )!,
      verseIndex: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}verse_index'],
      )!,
      chapterNumber: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}chapter_number'],
      )!,
      verseNumber: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}verse_number'],
      )!,
      labelX: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}label_x'],
      )!,
      labelY: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}label_y'],
      )!,
      wordIndexesJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}word_indexes_json'],
      )!,
      contoursJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}contours_json'],
      )!,
    );
  }

  @override
  $PrimarySourceVersesTable createAlias(String alias) {
    return $PrimarySourceVersesTable(attachedDatabase, alias);
  }
}

class PrimarySourceVerse extends DataClass
    implements Insertable<PrimarySourceVerse> {
  final String sourceId;
  final String pageName;
  final int verseIndex;
  final int chapterNumber;
  final int verseNumber;
  final double labelX;
  final double labelY;
  final String wordIndexesJson;
  final String contoursJson;
  const PrimarySourceVerse({
    required this.sourceId,
    required this.pageName,
    required this.verseIndex,
    required this.chapterNumber,
    required this.verseNumber,
    required this.labelX,
    required this.labelY,
    required this.wordIndexesJson,
    required this.contoursJson,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['source_id'] = Variable<String>(sourceId);
    map['page_name'] = Variable<String>(pageName);
    map['verse_index'] = Variable<int>(verseIndex);
    map['chapter_number'] = Variable<int>(chapterNumber);
    map['verse_number'] = Variable<int>(verseNumber);
    map['label_x'] = Variable<double>(labelX);
    map['label_y'] = Variable<double>(labelY);
    map['word_indexes_json'] = Variable<String>(wordIndexesJson);
    map['contours_json'] = Variable<String>(contoursJson);
    return map;
  }

  PrimarySourceVersesCompanion toCompanion(bool nullToAbsent) {
    return PrimarySourceVersesCompanion(
      sourceId: Value(sourceId),
      pageName: Value(pageName),
      verseIndex: Value(verseIndex),
      chapterNumber: Value(chapterNumber),
      verseNumber: Value(verseNumber),
      labelX: Value(labelX),
      labelY: Value(labelY),
      wordIndexesJson: Value(wordIndexesJson),
      contoursJson: Value(contoursJson),
    );
  }

  factory PrimarySourceVerse.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PrimarySourceVerse(
      sourceId: serializer.fromJson<String>(json['sourceId']),
      pageName: serializer.fromJson<String>(json['pageName']),
      verseIndex: serializer.fromJson<int>(json['verseIndex']),
      chapterNumber: serializer.fromJson<int>(json['chapterNumber']),
      verseNumber: serializer.fromJson<int>(json['verseNumber']),
      labelX: serializer.fromJson<double>(json['labelX']),
      labelY: serializer.fromJson<double>(json['labelY']),
      wordIndexesJson: serializer.fromJson<String>(json['wordIndexesJson']),
      contoursJson: serializer.fromJson<String>(json['contoursJson']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'sourceId': serializer.toJson<String>(sourceId),
      'pageName': serializer.toJson<String>(pageName),
      'verseIndex': serializer.toJson<int>(verseIndex),
      'chapterNumber': serializer.toJson<int>(chapterNumber),
      'verseNumber': serializer.toJson<int>(verseNumber),
      'labelX': serializer.toJson<double>(labelX),
      'labelY': serializer.toJson<double>(labelY),
      'wordIndexesJson': serializer.toJson<String>(wordIndexesJson),
      'contoursJson': serializer.toJson<String>(contoursJson),
    };
  }

  PrimarySourceVerse copyWith({
    String? sourceId,
    String? pageName,
    int? verseIndex,
    int? chapterNumber,
    int? verseNumber,
    double? labelX,
    double? labelY,
    String? wordIndexesJson,
    String? contoursJson,
  }) => PrimarySourceVerse(
    sourceId: sourceId ?? this.sourceId,
    pageName: pageName ?? this.pageName,
    verseIndex: verseIndex ?? this.verseIndex,
    chapterNumber: chapterNumber ?? this.chapterNumber,
    verseNumber: verseNumber ?? this.verseNumber,
    labelX: labelX ?? this.labelX,
    labelY: labelY ?? this.labelY,
    wordIndexesJson: wordIndexesJson ?? this.wordIndexesJson,
    contoursJson: contoursJson ?? this.contoursJson,
  );
  PrimarySourceVerse copyWithCompanion(PrimarySourceVersesCompanion data) {
    return PrimarySourceVerse(
      sourceId: data.sourceId.present ? data.sourceId.value : this.sourceId,
      pageName: data.pageName.present ? data.pageName.value : this.pageName,
      verseIndex: data.verseIndex.present
          ? data.verseIndex.value
          : this.verseIndex,
      chapterNumber: data.chapterNumber.present
          ? data.chapterNumber.value
          : this.chapterNumber,
      verseNumber: data.verseNumber.present
          ? data.verseNumber.value
          : this.verseNumber,
      labelX: data.labelX.present ? data.labelX.value : this.labelX,
      labelY: data.labelY.present ? data.labelY.value : this.labelY,
      wordIndexesJson: data.wordIndexesJson.present
          ? data.wordIndexesJson.value
          : this.wordIndexesJson,
      contoursJson: data.contoursJson.present
          ? data.contoursJson.value
          : this.contoursJson,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceVerse(')
          ..write('sourceId: $sourceId, ')
          ..write('pageName: $pageName, ')
          ..write('verseIndex: $verseIndex, ')
          ..write('chapterNumber: $chapterNumber, ')
          ..write('verseNumber: $verseNumber, ')
          ..write('labelX: $labelX, ')
          ..write('labelY: $labelY, ')
          ..write('wordIndexesJson: $wordIndexesJson, ')
          ..write('contoursJson: $contoursJson')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    sourceId,
    pageName,
    verseIndex,
    chapterNumber,
    verseNumber,
    labelX,
    labelY,
    wordIndexesJson,
    contoursJson,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PrimarySourceVerse &&
          other.sourceId == this.sourceId &&
          other.pageName == this.pageName &&
          other.verseIndex == this.verseIndex &&
          other.chapterNumber == this.chapterNumber &&
          other.verseNumber == this.verseNumber &&
          other.labelX == this.labelX &&
          other.labelY == this.labelY &&
          other.wordIndexesJson == this.wordIndexesJson &&
          other.contoursJson == this.contoursJson);
}

class PrimarySourceVersesCompanion extends UpdateCompanion<PrimarySourceVerse> {
  final Value<String> sourceId;
  final Value<String> pageName;
  final Value<int> verseIndex;
  final Value<int> chapterNumber;
  final Value<int> verseNumber;
  final Value<double> labelX;
  final Value<double> labelY;
  final Value<String> wordIndexesJson;
  final Value<String> contoursJson;
  final Value<int> rowid;
  const PrimarySourceVersesCompanion({
    this.sourceId = const Value.absent(),
    this.pageName = const Value.absent(),
    this.verseIndex = const Value.absent(),
    this.chapterNumber = const Value.absent(),
    this.verseNumber = const Value.absent(),
    this.labelX = const Value.absent(),
    this.labelY = const Value.absent(),
    this.wordIndexesJson = const Value.absent(),
    this.contoursJson = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PrimarySourceVersesCompanion.insert({
    required String sourceId,
    required String pageName,
    required int verseIndex,
    required int chapterNumber,
    required int verseNumber,
    required double labelX,
    required double labelY,
    this.wordIndexesJson = const Value.absent(),
    this.contoursJson = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : sourceId = Value(sourceId),
       pageName = Value(pageName),
       verseIndex = Value(verseIndex),
       chapterNumber = Value(chapterNumber),
       verseNumber = Value(verseNumber),
       labelX = Value(labelX),
       labelY = Value(labelY);
  static Insertable<PrimarySourceVerse> custom({
    Expression<String>? sourceId,
    Expression<String>? pageName,
    Expression<int>? verseIndex,
    Expression<int>? chapterNumber,
    Expression<int>? verseNumber,
    Expression<double>? labelX,
    Expression<double>? labelY,
    Expression<String>? wordIndexesJson,
    Expression<String>? contoursJson,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (sourceId != null) 'source_id': sourceId,
      if (pageName != null) 'page_name': pageName,
      if (verseIndex != null) 'verse_index': verseIndex,
      if (chapterNumber != null) 'chapter_number': chapterNumber,
      if (verseNumber != null) 'verse_number': verseNumber,
      if (labelX != null) 'label_x': labelX,
      if (labelY != null) 'label_y': labelY,
      if (wordIndexesJson != null) 'word_indexes_json': wordIndexesJson,
      if (contoursJson != null) 'contours_json': contoursJson,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PrimarySourceVersesCompanion copyWith({
    Value<String>? sourceId,
    Value<String>? pageName,
    Value<int>? verseIndex,
    Value<int>? chapterNumber,
    Value<int>? verseNumber,
    Value<double>? labelX,
    Value<double>? labelY,
    Value<String>? wordIndexesJson,
    Value<String>? contoursJson,
    Value<int>? rowid,
  }) {
    return PrimarySourceVersesCompanion(
      sourceId: sourceId ?? this.sourceId,
      pageName: pageName ?? this.pageName,
      verseIndex: verseIndex ?? this.verseIndex,
      chapterNumber: chapterNumber ?? this.chapterNumber,
      verseNumber: verseNumber ?? this.verseNumber,
      labelX: labelX ?? this.labelX,
      labelY: labelY ?? this.labelY,
      wordIndexesJson: wordIndexesJson ?? this.wordIndexesJson,
      contoursJson: contoursJson ?? this.contoursJson,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (sourceId.present) {
      map['source_id'] = Variable<String>(sourceId.value);
    }
    if (pageName.present) {
      map['page_name'] = Variable<String>(pageName.value);
    }
    if (verseIndex.present) {
      map['verse_index'] = Variable<int>(verseIndex.value);
    }
    if (chapterNumber.present) {
      map['chapter_number'] = Variable<int>(chapterNumber.value);
    }
    if (verseNumber.present) {
      map['verse_number'] = Variable<int>(verseNumber.value);
    }
    if (labelX.present) {
      map['label_x'] = Variable<double>(labelX.value);
    }
    if (labelY.present) {
      map['label_y'] = Variable<double>(labelY.value);
    }
    if (wordIndexesJson.present) {
      map['word_indexes_json'] = Variable<String>(wordIndexesJson.value);
    }
    if (contoursJson.present) {
      map['contours_json'] = Variable<String>(contoursJson.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceVersesCompanion(')
          ..write('sourceId: $sourceId, ')
          ..write('pageName: $pageName, ')
          ..write('verseIndex: $verseIndex, ')
          ..write('chapterNumber: $chapterNumber, ')
          ..write('verseNumber: $verseNumber, ')
          ..write('labelX: $labelX, ')
          ..write('labelY: $labelY, ')
          ..write('wordIndexesJson: $wordIndexesJson, ')
          ..write('contoursJson: $contoursJson, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$CommonDB extends GeneratedDatabase {
  _$CommonDB(QueryExecutor e) : super(e);
  $CommonDBManager get managers => $CommonDBManager(this);
  late final $GreekWordsTable greekWords = $GreekWordsTable(this);
  late final $CommonResourcesTable commonResources = $CommonResourcesTable(
    this,
  );
  late final $PrimarySourcesTable primarySources = $PrimarySourcesTable(this);
  late final $PrimarySourceLinksTable primarySourceLinks =
      $PrimarySourceLinksTable(this);
  late final $PrimarySourceAttributionsTable primarySourceAttributions =
      $PrimarySourceAttributionsTable(this);
  late final $PrimarySourcePagesTable primarySourcePages =
      $PrimarySourcePagesTable(this);
  late final $PrimarySourceWordsTable primarySourceWords =
      $PrimarySourceWordsTable(this);
  late final $PrimarySourceVersesTable primarySourceVerses =
      $PrimarySourceVersesTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    greekWords,
    commonResources,
    primarySources,
    primarySourceLinks,
    primarySourceAttributions,
    primarySourcePages,
    primarySourceWords,
    primarySourceVerses,
  ];
}

typedef $$GreekWordsTableCreateCompanionBuilder =
    GreekWordsCompanion Function({
      Value<int> id,
      required String word,
      required String category,
      required String synonyms,
      required String origin,
      required String usage,
    });
typedef $$GreekWordsTableUpdateCompanionBuilder =
    GreekWordsCompanion Function({
      Value<int> id,
      Value<String> word,
      Value<String> category,
      Value<String> synonyms,
      Value<String> origin,
      Value<String> usage,
    });

class $$GreekWordsTableFilterComposer
    extends Composer<_$CommonDB, $GreekWordsTable> {
  $$GreekWordsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get word => $composableBuilder(
    column: $table.word,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get category => $composableBuilder(
    column: $table.category,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get synonyms => $composableBuilder(
    column: $table.synonyms,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get origin => $composableBuilder(
    column: $table.origin,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get usage => $composableBuilder(
    column: $table.usage,
    builder: (column) => ColumnFilters(column),
  );
}

class $$GreekWordsTableOrderingComposer
    extends Composer<_$CommonDB, $GreekWordsTable> {
  $$GreekWordsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get word => $composableBuilder(
    column: $table.word,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get category => $composableBuilder(
    column: $table.category,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get synonyms => $composableBuilder(
    column: $table.synonyms,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get origin => $composableBuilder(
    column: $table.origin,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get usage => $composableBuilder(
    column: $table.usage,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$GreekWordsTableAnnotationComposer
    extends Composer<_$CommonDB, $GreekWordsTable> {
  $$GreekWordsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get word =>
      $composableBuilder(column: $table.word, builder: (column) => column);

  GeneratedColumn<String> get category =>
      $composableBuilder(column: $table.category, builder: (column) => column);

  GeneratedColumn<String> get synonyms =>
      $composableBuilder(column: $table.synonyms, builder: (column) => column);

  GeneratedColumn<String> get origin =>
      $composableBuilder(column: $table.origin, builder: (column) => column);

  GeneratedColumn<String> get usage =>
      $composableBuilder(column: $table.usage, builder: (column) => column);
}

class $$GreekWordsTableTableManager
    extends
        RootTableManager<
          _$CommonDB,
          $GreekWordsTable,
          GreekWord,
          $$GreekWordsTableFilterComposer,
          $$GreekWordsTableOrderingComposer,
          $$GreekWordsTableAnnotationComposer,
          $$GreekWordsTableCreateCompanionBuilder,
          $$GreekWordsTableUpdateCompanionBuilder,
          (GreekWord, BaseReferences<_$CommonDB, $GreekWordsTable, GreekWord>),
          GreekWord,
          PrefetchHooks Function()
        > {
  $$GreekWordsTableTableManager(_$CommonDB db, $GreekWordsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$GreekWordsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$GreekWordsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$GreekWordsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<int> id = const Value.absent(),
                Value<String> word = const Value.absent(),
                Value<String> category = const Value.absent(),
                Value<String> synonyms = const Value.absent(),
                Value<String> origin = const Value.absent(),
                Value<String> usage = const Value.absent(),
              }) => GreekWordsCompanion(
                id: id,
                word: word,
                category: category,
                synonyms: synonyms,
                origin: origin,
                usage: usage,
              ),
          createCompanionCallback:
              ({
                Value<int> id = const Value.absent(),
                required String word,
                required String category,
                required String synonyms,
                required String origin,
                required String usage,
              }) => GreekWordsCompanion.insert(
                id: id,
                word: word,
                category: category,
                synonyms: synonyms,
                origin: origin,
                usage: usage,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$GreekWordsTableProcessedTableManager =
    ProcessedTableManager<
      _$CommonDB,
      $GreekWordsTable,
      GreekWord,
      $$GreekWordsTableFilterComposer,
      $$GreekWordsTableOrderingComposer,
      $$GreekWordsTableAnnotationComposer,
      $$GreekWordsTableCreateCompanionBuilder,
      $$GreekWordsTableUpdateCompanionBuilder,
      (GreekWord, BaseReferences<_$CommonDB, $GreekWordsTable, GreekWord>),
      GreekWord,
      PrefetchHooks Function()
    >;
typedef $$CommonResourcesTableCreateCompanionBuilder =
    CommonResourcesCompanion Function({
      required String key,
      required String fileName,
      required String mimeType,
      required Uint8List data,
      Value<int> rowid,
    });
typedef $$CommonResourcesTableUpdateCompanionBuilder =
    CommonResourcesCompanion Function({
      Value<String> key,
      Value<String> fileName,
      Value<String> mimeType,
      Value<Uint8List> data,
      Value<int> rowid,
    });

class $$CommonResourcesTableFilterComposer
    extends Composer<_$CommonDB, $CommonResourcesTable> {
  $$CommonResourcesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get key => $composableBuilder(
    column: $table.key,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get fileName => $composableBuilder(
    column: $table.fileName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get mimeType => $composableBuilder(
    column: $table.mimeType,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<Uint8List> get data => $composableBuilder(
    column: $table.data,
    builder: (column) => ColumnFilters(column),
  );
}

class $$CommonResourcesTableOrderingComposer
    extends Composer<_$CommonDB, $CommonResourcesTable> {
  $$CommonResourcesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get key => $composableBuilder(
    column: $table.key,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get fileName => $composableBuilder(
    column: $table.fileName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get mimeType => $composableBuilder(
    column: $table.mimeType,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<Uint8List> get data => $composableBuilder(
    column: $table.data,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$CommonResourcesTableAnnotationComposer
    extends Composer<_$CommonDB, $CommonResourcesTable> {
  $$CommonResourcesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get key =>
      $composableBuilder(column: $table.key, builder: (column) => column);

  GeneratedColumn<String> get fileName =>
      $composableBuilder(column: $table.fileName, builder: (column) => column);

  GeneratedColumn<String> get mimeType =>
      $composableBuilder(column: $table.mimeType, builder: (column) => column);

  GeneratedColumn<Uint8List> get data =>
      $composableBuilder(column: $table.data, builder: (column) => column);
}

class $$CommonResourcesTableTableManager
    extends
        RootTableManager<
          _$CommonDB,
          $CommonResourcesTable,
          CommonResource,
          $$CommonResourcesTableFilterComposer,
          $$CommonResourcesTableOrderingComposer,
          $$CommonResourcesTableAnnotationComposer,
          $$CommonResourcesTableCreateCompanionBuilder,
          $$CommonResourcesTableUpdateCompanionBuilder,
          (
            CommonResource,
            BaseReferences<_$CommonDB, $CommonResourcesTable, CommonResource>,
          ),
          CommonResource,
          PrefetchHooks Function()
        > {
  $$CommonResourcesTableTableManager(_$CommonDB db, $CommonResourcesTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CommonResourcesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CommonResourcesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CommonResourcesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> key = const Value.absent(),
                Value<String> fileName = const Value.absent(),
                Value<String> mimeType = const Value.absent(),
                Value<Uint8List> data = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => CommonResourcesCompanion(
                key: key,
                fileName: fileName,
                mimeType: mimeType,
                data: data,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String key,
                required String fileName,
                required String mimeType,
                required Uint8List data,
                Value<int> rowid = const Value.absent(),
              }) => CommonResourcesCompanion.insert(
                key: key,
                fileName: fileName,
                mimeType: mimeType,
                data: data,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$CommonResourcesTableProcessedTableManager =
    ProcessedTableManager<
      _$CommonDB,
      $CommonResourcesTable,
      CommonResource,
      $$CommonResourcesTableFilterComposer,
      $$CommonResourcesTableOrderingComposer,
      $$CommonResourcesTableAnnotationComposer,
      $$CommonResourcesTableCreateCompanionBuilder,
      $$CommonResourcesTableUpdateCompanionBuilder,
      (
        CommonResource,
        BaseReferences<_$CommonDB, $CommonResourcesTable, CommonResource>,
      ),
      CommonResource,
      PrefetchHooks Function()
    >;
typedef $$PrimarySourcesTableCreateCompanionBuilder =
    PrimarySourcesCompanion Function({
      required String id,
      required String family,
      required int number,
      required String groupKind,
      Value<int> sortOrder,
      Value<int> versesCount,
      required String previewResourceKey,
      Value<double> defaultMaxScale,
      Value<bool> canShowImages,
      Value<bool> imagesAreMonochrome,
      Value<String> notes,
      Value<int> rowid,
    });
typedef $$PrimarySourcesTableUpdateCompanionBuilder =
    PrimarySourcesCompanion Function({
      Value<String> id,
      Value<String> family,
      Value<int> number,
      Value<String> groupKind,
      Value<int> sortOrder,
      Value<int> versesCount,
      Value<String> previewResourceKey,
      Value<double> defaultMaxScale,
      Value<bool> canShowImages,
      Value<bool> imagesAreMonochrome,
      Value<String> notes,
      Value<int> rowid,
    });

class $$PrimarySourcesTableFilterComposer
    extends Composer<_$CommonDB, $PrimarySourcesTable> {
  $$PrimarySourcesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get family => $composableBuilder(
    column: $table.family,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get number => $composableBuilder(
    column: $table.number,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get groupKind => $composableBuilder(
    column: $table.groupKind,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get versesCount => $composableBuilder(
    column: $table.versesCount,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get previewResourceKey => $composableBuilder(
    column: $table.previewResourceKey,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get defaultMaxScale => $composableBuilder(
    column: $table.defaultMaxScale,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get canShowImages => $composableBuilder(
    column: $table.canShowImages,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get imagesAreMonochrome => $composableBuilder(
    column: $table.imagesAreMonochrome,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get notes => $composableBuilder(
    column: $table.notes,
    builder: (column) => ColumnFilters(column),
  );
}

class $$PrimarySourcesTableOrderingComposer
    extends Composer<_$CommonDB, $PrimarySourcesTable> {
  $$PrimarySourcesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get family => $composableBuilder(
    column: $table.family,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get number => $composableBuilder(
    column: $table.number,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get groupKind => $composableBuilder(
    column: $table.groupKind,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get versesCount => $composableBuilder(
    column: $table.versesCount,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get previewResourceKey => $composableBuilder(
    column: $table.previewResourceKey,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get defaultMaxScale => $composableBuilder(
    column: $table.defaultMaxScale,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get canShowImages => $composableBuilder(
    column: $table.canShowImages,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get imagesAreMonochrome => $composableBuilder(
    column: $table.imagesAreMonochrome,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get notes => $composableBuilder(
    column: $table.notes,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$PrimarySourcesTableAnnotationComposer
    extends Composer<_$CommonDB, $PrimarySourcesTable> {
  $$PrimarySourcesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get family =>
      $composableBuilder(column: $table.family, builder: (column) => column);

  GeneratedColumn<int> get number =>
      $composableBuilder(column: $table.number, builder: (column) => column);

  GeneratedColumn<String> get groupKind =>
      $composableBuilder(column: $table.groupKind, builder: (column) => column);

  GeneratedColumn<int> get sortOrder =>
      $composableBuilder(column: $table.sortOrder, builder: (column) => column);

  GeneratedColumn<int> get versesCount => $composableBuilder(
    column: $table.versesCount,
    builder: (column) => column,
  );

  GeneratedColumn<String> get previewResourceKey => $composableBuilder(
    column: $table.previewResourceKey,
    builder: (column) => column,
  );

  GeneratedColumn<double> get defaultMaxScale => $composableBuilder(
    column: $table.defaultMaxScale,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get canShowImages => $composableBuilder(
    column: $table.canShowImages,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get imagesAreMonochrome => $composableBuilder(
    column: $table.imagesAreMonochrome,
    builder: (column) => column,
  );

  GeneratedColumn<String> get notes =>
      $composableBuilder(column: $table.notes, builder: (column) => column);
}

class $$PrimarySourcesTableTableManager
    extends
        RootTableManager<
          _$CommonDB,
          $PrimarySourcesTable,
          PrimarySource,
          $$PrimarySourcesTableFilterComposer,
          $$PrimarySourcesTableOrderingComposer,
          $$PrimarySourcesTableAnnotationComposer,
          $$PrimarySourcesTableCreateCompanionBuilder,
          $$PrimarySourcesTableUpdateCompanionBuilder,
          (
            PrimarySource,
            BaseReferences<_$CommonDB, $PrimarySourcesTable, PrimarySource>,
          ),
          PrimarySource,
          PrefetchHooks Function()
        > {
  $$PrimarySourcesTableTableManager(_$CommonDB db, $PrimarySourcesTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PrimarySourcesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PrimarySourcesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PrimarySourcesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> family = const Value.absent(),
                Value<int> number = const Value.absent(),
                Value<String> groupKind = const Value.absent(),
                Value<int> sortOrder = const Value.absent(),
                Value<int> versesCount = const Value.absent(),
                Value<String> previewResourceKey = const Value.absent(),
                Value<double> defaultMaxScale = const Value.absent(),
                Value<bool> canShowImages = const Value.absent(),
                Value<bool> imagesAreMonochrome = const Value.absent(),
                Value<String> notes = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourcesCompanion(
                id: id,
                family: family,
                number: number,
                groupKind: groupKind,
                sortOrder: sortOrder,
                versesCount: versesCount,
                previewResourceKey: previewResourceKey,
                defaultMaxScale: defaultMaxScale,
                canShowImages: canShowImages,
                imagesAreMonochrome: imagesAreMonochrome,
                notes: notes,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                required String family,
                required int number,
                required String groupKind,
                Value<int> sortOrder = const Value.absent(),
                Value<int> versesCount = const Value.absent(),
                required String previewResourceKey,
                Value<double> defaultMaxScale = const Value.absent(),
                Value<bool> canShowImages = const Value.absent(),
                Value<bool> imagesAreMonochrome = const Value.absent(),
                Value<String> notes = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourcesCompanion.insert(
                id: id,
                family: family,
                number: number,
                groupKind: groupKind,
                sortOrder: sortOrder,
                versesCount: versesCount,
                previewResourceKey: previewResourceKey,
                defaultMaxScale: defaultMaxScale,
                canShowImages: canShowImages,
                imagesAreMonochrome: imagesAreMonochrome,
                notes: notes,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$PrimarySourcesTableProcessedTableManager =
    ProcessedTableManager<
      _$CommonDB,
      $PrimarySourcesTable,
      PrimarySource,
      $$PrimarySourcesTableFilterComposer,
      $$PrimarySourcesTableOrderingComposer,
      $$PrimarySourcesTableAnnotationComposer,
      $$PrimarySourcesTableCreateCompanionBuilder,
      $$PrimarySourcesTableUpdateCompanionBuilder,
      (
        PrimarySource,
        BaseReferences<_$CommonDB, $PrimarySourcesTable, PrimarySource>,
      ),
      PrimarySource,
      PrefetchHooks Function()
    >;
typedef $$PrimarySourceLinksTableCreateCompanionBuilder =
    PrimarySourceLinksCompanion Function({
      required String sourceId,
      required String linkId,
      Value<int> sortOrder,
      required String linkRole,
      required String url,
      Value<int> rowid,
    });
typedef $$PrimarySourceLinksTableUpdateCompanionBuilder =
    PrimarySourceLinksCompanion Function({
      Value<String> sourceId,
      Value<String> linkId,
      Value<int> sortOrder,
      Value<String> linkRole,
      Value<String> url,
      Value<int> rowid,
    });

class $$PrimarySourceLinksTableFilterComposer
    extends Composer<_$CommonDB, $PrimarySourceLinksTable> {
  $$PrimarySourceLinksTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get linkId => $composableBuilder(
    column: $table.linkId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get linkRole => $composableBuilder(
    column: $table.linkRole,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get url => $composableBuilder(
    column: $table.url,
    builder: (column) => ColumnFilters(column),
  );
}

class $$PrimarySourceLinksTableOrderingComposer
    extends Composer<_$CommonDB, $PrimarySourceLinksTable> {
  $$PrimarySourceLinksTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get linkId => $composableBuilder(
    column: $table.linkId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get linkRole => $composableBuilder(
    column: $table.linkRole,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get url => $composableBuilder(
    column: $table.url,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$PrimarySourceLinksTableAnnotationComposer
    extends Composer<_$CommonDB, $PrimarySourceLinksTable> {
  $$PrimarySourceLinksTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get sourceId =>
      $composableBuilder(column: $table.sourceId, builder: (column) => column);

  GeneratedColumn<String> get linkId =>
      $composableBuilder(column: $table.linkId, builder: (column) => column);

  GeneratedColumn<int> get sortOrder =>
      $composableBuilder(column: $table.sortOrder, builder: (column) => column);

  GeneratedColumn<String> get linkRole =>
      $composableBuilder(column: $table.linkRole, builder: (column) => column);

  GeneratedColumn<String> get url =>
      $composableBuilder(column: $table.url, builder: (column) => column);
}

class $$PrimarySourceLinksTableTableManager
    extends
        RootTableManager<
          _$CommonDB,
          $PrimarySourceLinksTable,
          PrimarySourceLink,
          $$PrimarySourceLinksTableFilterComposer,
          $$PrimarySourceLinksTableOrderingComposer,
          $$PrimarySourceLinksTableAnnotationComposer,
          $$PrimarySourceLinksTableCreateCompanionBuilder,
          $$PrimarySourceLinksTableUpdateCompanionBuilder,
          (
            PrimarySourceLink,
            BaseReferences<
              _$CommonDB,
              $PrimarySourceLinksTable,
              PrimarySourceLink
            >,
          ),
          PrimarySourceLink,
          PrefetchHooks Function()
        > {
  $$PrimarySourceLinksTableTableManager(
    _$CommonDB db,
    $PrimarySourceLinksTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PrimarySourceLinksTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PrimarySourceLinksTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PrimarySourceLinksTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> sourceId = const Value.absent(),
                Value<String> linkId = const Value.absent(),
                Value<int> sortOrder = const Value.absent(),
                Value<String> linkRole = const Value.absent(),
                Value<String> url = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceLinksCompanion(
                sourceId: sourceId,
                linkId: linkId,
                sortOrder: sortOrder,
                linkRole: linkRole,
                url: url,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String sourceId,
                required String linkId,
                Value<int> sortOrder = const Value.absent(),
                required String linkRole,
                required String url,
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceLinksCompanion.insert(
                sourceId: sourceId,
                linkId: linkId,
                sortOrder: sortOrder,
                linkRole: linkRole,
                url: url,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$PrimarySourceLinksTableProcessedTableManager =
    ProcessedTableManager<
      _$CommonDB,
      $PrimarySourceLinksTable,
      PrimarySourceLink,
      $$PrimarySourceLinksTableFilterComposer,
      $$PrimarySourceLinksTableOrderingComposer,
      $$PrimarySourceLinksTableAnnotationComposer,
      $$PrimarySourceLinksTableCreateCompanionBuilder,
      $$PrimarySourceLinksTableUpdateCompanionBuilder,
      (
        PrimarySourceLink,
        BaseReferences<_$CommonDB, $PrimarySourceLinksTable, PrimarySourceLink>,
      ),
      PrimarySourceLink,
      PrefetchHooks Function()
    >;
typedef $$PrimarySourceAttributionsTableCreateCompanionBuilder =
    PrimarySourceAttributionsCompanion Function({
      required String sourceId,
      required String attributionId,
      Value<int> sortOrder,
      required String displayText,
      required String url,
      Value<int> rowid,
    });
typedef $$PrimarySourceAttributionsTableUpdateCompanionBuilder =
    PrimarySourceAttributionsCompanion Function({
      Value<String> sourceId,
      Value<String> attributionId,
      Value<int> sortOrder,
      Value<String> displayText,
      Value<String> url,
      Value<int> rowid,
    });

class $$PrimarySourceAttributionsTableFilterComposer
    extends Composer<_$CommonDB, $PrimarySourceAttributionsTable> {
  $$PrimarySourceAttributionsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get attributionId => $composableBuilder(
    column: $table.attributionId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get displayText => $composableBuilder(
    column: $table.displayText,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get url => $composableBuilder(
    column: $table.url,
    builder: (column) => ColumnFilters(column),
  );
}

class $$PrimarySourceAttributionsTableOrderingComposer
    extends Composer<_$CommonDB, $PrimarySourceAttributionsTable> {
  $$PrimarySourceAttributionsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get attributionId => $composableBuilder(
    column: $table.attributionId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get displayText => $composableBuilder(
    column: $table.displayText,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get url => $composableBuilder(
    column: $table.url,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$PrimarySourceAttributionsTableAnnotationComposer
    extends Composer<_$CommonDB, $PrimarySourceAttributionsTable> {
  $$PrimarySourceAttributionsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get sourceId =>
      $composableBuilder(column: $table.sourceId, builder: (column) => column);

  GeneratedColumn<String> get attributionId => $composableBuilder(
    column: $table.attributionId,
    builder: (column) => column,
  );

  GeneratedColumn<int> get sortOrder =>
      $composableBuilder(column: $table.sortOrder, builder: (column) => column);

  GeneratedColumn<String> get displayText => $composableBuilder(
    column: $table.displayText,
    builder: (column) => column,
  );

  GeneratedColumn<String> get url =>
      $composableBuilder(column: $table.url, builder: (column) => column);
}

class $$PrimarySourceAttributionsTableTableManager
    extends
        RootTableManager<
          _$CommonDB,
          $PrimarySourceAttributionsTable,
          PrimarySourceAttribution,
          $$PrimarySourceAttributionsTableFilterComposer,
          $$PrimarySourceAttributionsTableOrderingComposer,
          $$PrimarySourceAttributionsTableAnnotationComposer,
          $$PrimarySourceAttributionsTableCreateCompanionBuilder,
          $$PrimarySourceAttributionsTableUpdateCompanionBuilder,
          (
            PrimarySourceAttribution,
            BaseReferences<
              _$CommonDB,
              $PrimarySourceAttributionsTable,
              PrimarySourceAttribution
            >,
          ),
          PrimarySourceAttribution,
          PrefetchHooks Function()
        > {
  $$PrimarySourceAttributionsTableTableManager(
    _$CommonDB db,
    $PrimarySourceAttributionsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PrimarySourceAttributionsTableFilterComposer(
                $db: db,
                $table: table,
              ),
          createOrderingComposer: () =>
              $$PrimarySourceAttributionsTableOrderingComposer(
                $db: db,
                $table: table,
              ),
          createComputedFieldComposer: () =>
              $$PrimarySourceAttributionsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> sourceId = const Value.absent(),
                Value<String> attributionId = const Value.absent(),
                Value<int> sortOrder = const Value.absent(),
                Value<String> displayText = const Value.absent(),
                Value<String> url = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceAttributionsCompanion(
                sourceId: sourceId,
                attributionId: attributionId,
                sortOrder: sortOrder,
                displayText: displayText,
                url: url,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String sourceId,
                required String attributionId,
                Value<int> sortOrder = const Value.absent(),
                required String displayText,
                required String url,
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceAttributionsCompanion.insert(
                sourceId: sourceId,
                attributionId: attributionId,
                sortOrder: sortOrder,
                displayText: displayText,
                url: url,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$PrimarySourceAttributionsTableProcessedTableManager =
    ProcessedTableManager<
      _$CommonDB,
      $PrimarySourceAttributionsTable,
      PrimarySourceAttribution,
      $$PrimarySourceAttributionsTableFilterComposer,
      $$PrimarySourceAttributionsTableOrderingComposer,
      $$PrimarySourceAttributionsTableAnnotationComposer,
      $$PrimarySourceAttributionsTableCreateCompanionBuilder,
      $$PrimarySourceAttributionsTableUpdateCompanionBuilder,
      (
        PrimarySourceAttribution,
        BaseReferences<
          _$CommonDB,
          $PrimarySourceAttributionsTable,
          PrimarySourceAttribution
        >,
      ),
      PrimarySourceAttribution,
      PrefetchHooks Function()
    >;
typedef $$PrimarySourcePagesTableCreateCompanionBuilder =
    PrimarySourcePagesCompanion Function({
      required String sourceId,
      required String pageName,
      Value<int> sortOrder,
      required String contentRef,
      required String imagePath,
      Value<String?> mobileImagePath,
      Value<int> rowid,
    });
typedef $$PrimarySourcePagesTableUpdateCompanionBuilder =
    PrimarySourcePagesCompanion Function({
      Value<String> sourceId,
      Value<String> pageName,
      Value<int> sortOrder,
      Value<String> contentRef,
      Value<String> imagePath,
      Value<String?> mobileImagePath,
      Value<int> rowid,
    });

class $$PrimarySourcePagesTableFilterComposer
    extends Composer<_$CommonDB, $PrimarySourcePagesTable> {
  $$PrimarySourcePagesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get pageName => $composableBuilder(
    column: $table.pageName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get contentRef => $composableBuilder(
    column: $table.contentRef,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get imagePath => $composableBuilder(
    column: $table.imagePath,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get mobileImagePath => $composableBuilder(
    column: $table.mobileImagePath,
    builder: (column) => ColumnFilters(column),
  );
}

class $$PrimarySourcePagesTableOrderingComposer
    extends Composer<_$CommonDB, $PrimarySourcePagesTable> {
  $$PrimarySourcePagesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get pageName => $composableBuilder(
    column: $table.pageName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get contentRef => $composableBuilder(
    column: $table.contentRef,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get imagePath => $composableBuilder(
    column: $table.imagePath,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get mobileImagePath => $composableBuilder(
    column: $table.mobileImagePath,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$PrimarySourcePagesTableAnnotationComposer
    extends Composer<_$CommonDB, $PrimarySourcePagesTable> {
  $$PrimarySourcePagesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get sourceId =>
      $composableBuilder(column: $table.sourceId, builder: (column) => column);

  GeneratedColumn<String> get pageName =>
      $composableBuilder(column: $table.pageName, builder: (column) => column);

  GeneratedColumn<int> get sortOrder =>
      $composableBuilder(column: $table.sortOrder, builder: (column) => column);

  GeneratedColumn<String> get contentRef => $composableBuilder(
    column: $table.contentRef,
    builder: (column) => column,
  );

  GeneratedColumn<String> get imagePath =>
      $composableBuilder(column: $table.imagePath, builder: (column) => column);

  GeneratedColumn<String> get mobileImagePath => $composableBuilder(
    column: $table.mobileImagePath,
    builder: (column) => column,
  );
}

class $$PrimarySourcePagesTableTableManager
    extends
        RootTableManager<
          _$CommonDB,
          $PrimarySourcePagesTable,
          PrimarySourcePage,
          $$PrimarySourcePagesTableFilterComposer,
          $$PrimarySourcePagesTableOrderingComposer,
          $$PrimarySourcePagesTableAnnotationComposer,
          $$PrimarySourcePagesTableCreateCompanionBuilder,
          $$PrimarySourcePagesTableUpdateCompanionBuilder,
          (
            PrimarySourcePage,
            BaseReferences<
              _$CommonDB,
              $PrimarySourcePagesTable,
              PrimarySourcePage
            >,
          ),
          PrimarySourcePage,
          PrefetchHooks Function()
        > {
  $$PrimarySourcePagesTableTableManager(
    _$CommonDB db,
    $PrimarySourcePagesTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PrimarySourcePagesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PrimarySourcePagesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PrimarySourcePagesTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> sourceId = const Value.absent(),
                Value<String> pageName = const Value.absent(),
                Value<int> sortOrder = const Value.absent(),
                Value<String> contentRef = const Value.absent(),
                Value<String> imagePath = const Value.absent(),
                Value<String?> mobileImagePath = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourcePagesCompanion(
                sourceId: sourceId,
                pageName: pageName,
                sortOrder: sortOrder,
                contentRef: contentRef,
                imagePath: imagePath,
                mobileImagePath: mobileImagePath,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String sourceId,
                required String pageName,
                Value<int> sortOrder = const Value.absent(),
                required String contentRef,
                required String imagePath,
                Value<String?> mobileImagePath = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourcePagesCompanion.insert(
                sourceId: sourceId,
                pageName: pageName,
                sortOrder: sortOrder,
                contentRef: contentRef,
                imagePath: imagePath,
                mobileImagePath: mobileImagePath,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$PrimarySourcePagesTableProcessedTableManager =
    ProcessedTableManager<
      _$CommonDB,
      $PrimarySourcePagesTable,
      PrimarySourcePage,
      $$PrimarySourcePagesTableFilterComposer,
      $$PrimarySourcePagesTableOrderingComposer,
      $$PrimarySourcePagesTableAnnotationComposer,
      $$PrimarySourcePagesTableCreateCompanionBuilder,
      $$PrimarySourcePagesTableUpdateCompanionBuilder,
      (
        PrimarySourcePage,
        BaseReferences<_$CommonDB, $PrimarySourcePagesTable, PrimarySourcePage>,
      ),
      PrimarySourcePage,
      PrefetchHooks Function()
    >;
typedef $$PrimarySourceWordsTableCreateCompanionBuilder =
    PrimarySourceWordsCompanion Function({
      required String sourceId,
      required String pageName,
      required int wordIndex,
      required String wordText,
      Value<int?> strongNumber,
      Value<bool> strongPronounce,
      Value<double> strongXShift,
      Value<String> missingCharIndexesJson,
      Value<String> rectanglesJson,
      Value<int> rowid,
    });
typedef $$PrimarySourceWordsTableUpdateCompanionBuilder =
    PrimarySourceWordsCompanion Function({
      Value<String> sourceId,
      Value<String> pageName,
      Value<int> wordIndex,
      Value<String> wordText,
      Value<int?> strongNumber,
      Value<bool> strongPronounce,
      Value<double> strongXShift,
      Value<String> missingCharIndexesJson,
      Value<String> rectanglesJson,
      Value<int> rowid,
    });

class $$PrimarySourceWordsTableFilterComposer
    extends Composer<_$CommonDB, $PrimarySourceWordsTable> {
  $$PrimarySourceWordsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get pageName => $composableBuilder(
    column: $table.pageName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get wordIndex => $composableBuilder(
    column: $table.wordIndex,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get wordText => $composableBuilder(
    column: $table.wordText,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get strongNumber => $composableBuilder(
    column: $table.strongNumber,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get strongPronounce => $composableBuilder(
    column: $table.strongPronounce,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get strongXShift => $composableBuilder(
    column: $table.strongXShift,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get missingCharIndexesJson => $composableBuilder(
    column: $table.missingCharIndexesJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get rectanglesJson => $composableBuilder(
    column: $table.rectanglesJson,
    builder: (column) => ColumnFilters(column),
  );
}

class $$PrimarySourceWordsTableOrderingComposer
    extends Composer<_$CommonDB, $PrimarySourceWordsTable> {
  $$PrimarySourceWordsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get pageName => $composableBuilder(
    column: $table.pageName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get wordIndex => $composableBuilder(
    column: $table.wordIndex,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get wordText => $composableBuilder(
    column: $table.wordText,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get strongNumber => $composableBuilder(
    column: $table.strongNumber,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get strongPronounce => $composableBuilder(
    column: $table.strongPronounce,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get strongXShift => $composableBuilder(
    column: $table.strongXShift,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get missingCharIndexesJson => $composableBuilder(
    column: $table.missingCharIndexesJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get rectanglesJson => $composableBuilder(
    column: $table.rectanglesJson,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$PrimarySourceWordsTableAnnotationComposer
    extends Composer<_$CommonDB, $PrimarySourceWordsTable> {
  $$PrimarySourceWordsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get sourceId =>
      $composableBuilder(column: $table.sourceId, builder: (column) => column);

  GeneratedColumn<String> get pageName =>
      $composableBuilder(column: $table.pageName, builder: (column) => column);

  GeneratedColumn<int> get wordIndex =>
      $composableBuilder(column: $table.wordIndex, builder: (column) => column);

  GeneratedColumn<String> get wordText =>
      $composableBuilder(column: $table.wordText, builder: (column) => column);

  GeneratedColumn<int> get strongNumber => $composableBuilder(
    column: $table.strongNumber,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get strongPronounce => $composableBuilder(
    column: $table.strongPronounce,
    builder: (column) => column,
  );

  GeneratedColumn<double> get strongXShift => $composableBuilder(
    column: $table.strongXShift,
    builder: (column) => column,
  );

  GeneratedColumn<String> get missingCharIndexesJson => $composableBuilder(
    column: $table.missingCharIndexesJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get rectanglesJson => $composableBuilder(
    column: $table.rectanglesJson,
    builder: (column) => column,
  );
}

class $$PrimarySourceWordsTableTableManager
    extends
        RootTableManager<
          _$CommonDB,
          $PrimarySourceWordsTable,
          PrimarySourceWord,
          $$PrimarySourceWordsTableFilterComposer,
          $$PrimarySourceWordsTableOrderingComposer,
          $$PrimarySourceWordsTableAnnotationComposer,
          $$PrimarySourceWordsTableCreateCompanionBuilder,
          $$PrimarySourceWordsTableUpdateCompanionBuilder,
          (
            PrimarySourceWord,
            BaseReferences<
              _$CommonDB,
              $PrimarySourceWordsTable,
              PrimarySourceWord
            >,
          ),
          PrimarySourceWord,
          PrefetchHooks Function()
        > {
  $$PrimarySourceWordsTableTableManager(
    _$CommonDB db,
    $PrimarySourceWordsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PrimarySourceWordsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PrimarySourceWordsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PrimarySourceWordsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> sourceId = const Value.absent(),
                Value<String> pageName = const Value.absent(),
                Value<int> wordIndex = const Value.absent(),
                Value<String> wordText = const Value.absent(),
                Value<int?> strongNumber = const Value.absent(),
                Value<bool> strongPronounce = const Value.absent(),
                Value<double> strongXShift = const Value.absent(),
                Value<String> missingCharIndexesJson = const Value.absent(),
                Value<String> rectanglesJson = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceWordsCompanion(
                sourceId: sourceId,
                pageName: pageName,
                wordIndex: wordIndex,
                wordText: wordText,
                strongNumber: strongNumber,
                strongPronounce: strongPronounce,
                strongXShift: strongXShift,
                missingCharIndexesJson: missingCharIndexesJson,
                rectanglesJson: rectanglesJson,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String sourceId,
                required String pageName,
                required int wordIndex,
                required String wordText,
                Value<int?> strongNumber = const Value.absent(),
                Value<bool> strongPronounce = const Value.absent(),
                Value<double> strongXShift = const Value.absent(),
                Value<String> missingCharIndexesJson = const Value.absent(),
                Value<String> rectanglesJson = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceWordsCompanion.insert(
                sourceId: sourceId,
                pageName: pageName,
                wordIndex: wordIndex,
                wordText: wordText,
                strongNumber: strongNumber,
                strongPronounce: strongPronounce,
                strongXShift: strongXShift,
                missingCharIndexesJson: missingCharIndexesJson,
                rectanglesJson: rectanglesJson,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$PrimarySourceWordsTableProcessedTableManager =
    ProcessedTableManager<
      _$CommonDB,
      $PrimarySourceWordsTable,
      PrimarySourceWord,
      $$PrimarySourceWordsTableFilterComposer,
      $$PrimarySourceWordsTableOrderingComposer,
      $$PrimarySourceWordsTableAnnotationComposer,
      $$PrimarySourceWordsTableCreateCompanionBuilder,
      $$PrimarySourceWordsTableUpdateCompanionBuilder,
      (
        PrimarySourceWord,
        BaseReferences<_$CommonDB, $PrimarySourceWordsTable, PrimarySourceWord>,
      ),
      PrimarySourceWord,
      PrefetchHooks Function()
    >;
typedef $$PrimarySourceVersesTableCreateCompanionBuilder =
    PrimarySourceVersesCompanion Function({
      required String sourceId,
      required String pageName,
      required int verseIndex,
      required int chapterNumber,
      required int verseNumber,
      required double labelX,
      required double labelY,
      Value<String> wordIndexesJson,
      Value<String> contoursJson,
      Value<int> rowid,
    });
typedef $$PrimarySourceVersesTableUpdateCompanionBuilder =
    PrimarySourceVersesCompanion Function({
      Value<String> sourceId,
      Value<String> pageName,
      Value<int> verseIndex,
      Value<int> chapterNumber,
      Value<int> verseNumber,
      Value<double> labelX,
      Value<double> labelY,
      Value<String> wordIndexesJson,
      Value<String> contoursJson,
      Value<int> rowid,
    });

class $$PrimarySourceVersesTableFilterComposer
    extends Composer<_$CommonDB, $PrimarySourceVersesTable> {
  $$PrimarySourceVersesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get pageName => $composableBuilder(
    column: $table.pageName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get verseIndex => $composableBuilder(
    column: $table.verseIndex,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get chapterNumber => $composableBuilder(
    column: $table.chapterNumber,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get verseNumber => $composableBuilder(
    column: $table.verseNumber,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get labelX => $composableBuilder(
    column: $table.labelX,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get labelY => $composableBuilder(
    column: $table.labelY,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get wordIndexesJson => $composableBuilder(
    column: $table.wordIndexesJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get contoursJson => $composableBuilder(
    column: $table.contoursJson,
    builder: (column) => ColumnFilters(column),
  );
}

class $$PrimarySourceVersesTableOrderingComposer
    extends Composer<_$CommonDB, $PrimarySourceVersesTable> {
  $$PrimarySourceVersesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get sourceId => $composableBuilder(
    column: $table.sourceId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get pageName => $composableBuilder(
    column: $table.pageName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get verseIndex => $composableBuilder(
    column: $table.verseIndex,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get chapterNumber => $composableBuilder(
    column: $table.chapterNumber,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get verseNumber => $composableBuilder(
    column: $table.verseNumber,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get labelX => $composableBuilder(
    column: $table.labelX,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get labelY => $composableBuilder(
    column: $table.labelY,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get wordIndexesJson => $composableBuilder(
    column: $table.wordIndexesJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get contoursJson => $composableBuilder(
    column: $table.contoursJson,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$PrimarySourceVersesTableAnnotationComposer
    extends Composer<_$CommonDB, $PrimarySourceVersesTable> {
  $$PrimarySourceVersesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get sourceId =>
      $composableBuilder(column: $table.sourceId, builder: (column) => column);

  GeneratedColumn<String> get pageName =>
      $composableBuilder(column: $table.pageName, builder: (column) => column);

  GeneratedColumn<int> get verseIndex => $composableBuilder(
    column: $table.verseIndex,
    builder: (column) => column,
  );

  GeneratedColumn<int> get chapterNumber => $composableBuilder(
    column: $table.chapterNumber,
    builder: (column) => column,
  );

  GeneratedColumn<int> get verseNumber => $composableBuilder(
    column: $table.verseNumber,
    builder: (column) => column,
  );

  GeneratedColumn<double> get labelX =>
      $composableBuilder(column: $table.labelX, builder: (column) => column);

  GeneratedColumn<double> get labelY =>
      $composableBuilder(column: $table.labelY, builder: (column) => column);

  GeneratedColumn<String> get wordIndexesJson => $composableBuilder(
    column: $table.wordIndexesJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get contoursJson => $composableBuilder(
    column: $table.contoursJson,
    builder: (column) => column,
  );
}

class $$PrimarySourceVersesTableTableManager
    extends
        RootTableManager<
          _$CommonDB,
          $PrimarySourceVersesTable,
          PrimarySourceVerse,
          $$PrimarySourceVersesTableFilterComposer,
          $$PrimarySourceVersesTableOrderingComposer,
          $$PrimarySourceVersesTableAnnotationComposer,
          $$PrimarySourceVersesTableCreateCompanionBuilder,
          $$PrimarySourceVersesTableUpdateCompanionBuilder,
          (
            PrimarySourceVerse,
            BaseReferences<
              _$CommonDB,
              $PrimarySourceVersesTable,
              PrimarySourceVerse
            >,
          ),
          PrimarySourceVerse,
          PrefetchHooks Function()
        > {
  $$PrimarySourceVersesTableTableManager(
    _$CommonDB db,
    $PrimarySourceVersesTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PrimarySourceVersesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PrimarySourceVersesTableOrderingComposer(
                $db: db,
                $table: table,
              ),
          createComputedFieldComposer: () =>
              $$PrimarySourceVersesTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> sourceId = const Value.absent(),
                Value<String> pageName = const Value.absent(),
                Value<int> verseIndex = const Value.absent(),
                Value<int> chapterNumber = const Value.absent(),
                Value<int> verseNumber = const Value.absent(),
                Value<double> labelX = const Value.absent(),
                Value<double> labelY = const Value.absent(),
                Value<String> wordIndexesJson = const Value.absent(),
                Value<String> contoursJson = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceVersesCompanion(
                sourceId: sourceId,
                pageName: pageName,
                verseIndex: verseIndex,
                chapterNumber: chapterNumber,
                verseNumber: verseNumber,
                labelX: labelX,
                labelY: labelY,
                wordIndexesJson: wordIndexesJson,
                contoursJson: contoursJson,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String sourceId,
                required String pageName,
                required int verseIndex,
                required int chapterNumber,
                required int verseNumber,
                required double labelX,
                required double labelY,
                Value<String> wordIndexesJson = const Value.absent(),
                Value<String> contoursJson = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceVersesCompanion.insert(
                sourceId: sourceId,
                pageName: pageName,
                verseIndex: verseIndex,
                chapterNumber: chapterNumber,
                verseNumber: verseNumber,
                labelX: labelX,
                labelY: labelY,
                wordIndexesJson: wordIndexesJson,
                contoursJson: contoursJson,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$PrimarySourceVersesTableProcessedTableManager =
    ProcessedTableManager<
      _$CommonDB,
      $PrimarySourceVersesTable,
      PrimarySourceVerse,
      $$PrimarySourceVersesTableFilterComposer,
      $$PrimarySourceVersesTableOrderingComposer,
      $$PrimarySourceVersesTableAnnotationComposer,
      $$PrimarySourceVersesTableCreateCompanionBuilder,
      $$PrimarySourceVersesTableUpdateCompanionBuilder,
      (
        PrimarySourceVerse,
        BaseReferences<
          _$CommonDB,
          $PrimarySourceVersesTable,
          PrimarySourceVerse
        >,
      ),
      PrimarySourceVerse,
      PrefetchHooks Function()
    >;

class $CommonDBManager {
  final _$CommonDB _db;
  $CommonDBManager(this._db);
  $$GreekWordsTableTableManager get greekWords =>
      $$GreekWordsTableTableManager(_db, _db.greekWords);
  $$CommonResourcesTableTableManager get commonResources =>
      $$CommonResourcesTableTableManager(_db, _db.commonResources);
  $$PrimarySourcesTableTableManager get primarySources =>
      $$PrimarySourcesTableTableManager(_db, _db.primarySources);
  $$PrimarySourceLinksTableTableManager get primarySourceLinks =>
      $$PrimarySourceLinksTableTableManager(_db, _db.primarySourceLinks);
  $$PrimarySourceAttributionsTableTableManager get primarySourceAttributions =>
      $$PrimarySourceAttributionsTableTableManager(
        _db,
        _db.primarySourceAttributions,
      );
  $$PrimarySourcePagesTableTableManager get primarySourcePages =>
      $$PrimarySourcePagesTableTableManager(_db, _db.primarySourcePages);
  $$PrimarySourceWordsTableTableManager get primarySourceWords =>
      $$PrimarySourceWordsTableTableManager(_db, _db.primarySourceWords);
  $$PrimarySourceVersesTableTableManager get primarySourceVerses =>
      $$PrimarySourceVersesTableTableManager(_db, _db.primarySourceVerses);
}
