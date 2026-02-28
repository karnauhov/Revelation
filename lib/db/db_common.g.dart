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

abstract class _$CommonDB extends GeneratedDatabase {
  _$CommonDB(QueryExecutor e) : super(e);
  $CommonDBManager get managers => $CommonDBManager(this);
  late final $GreekWordsTable greekWords = $GreekWordsTable(this);
  late final $CommonResourcesTable commonResources = $CommonResourcesTable(
    this,
  );
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    greekWords,
    commonResources,
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

class $CommonDBManager {
  final _$CommonDB _db;
  $CommonDBManager(this._db);
  $$GreekWordsTableTableManager get greekWords =>
      $$GreekWordsTableTableManager(_db, _db.greekWords);
  $$CommonResourcesTableTableManager get commonResources =>
      $$CommonResourcesTableTableManager(_db, _db.commonResources);
}
