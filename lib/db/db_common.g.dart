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
  static const VerificationMeta _hebrewMeta = const VerificationMeta('hebrew');
  @override
  late final GeneratedColumn<String> hebrew = GeneratedColumn<String>(
    'hebrew',
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
    hebrew,
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
    if (data.containsKey('hebrew')) {
      context.handle(
        _hebrewMeta,
        hebrew.isAcceptableOrUnknown(data['hebrew']!, _hebrewMeta),
      );
    } else if (isInserting) {
      context.missing(_hebrewMeta);
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
      hebrew: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}hebrew'],
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
  final String hebrew;
  const GreekWord({
    required this.id,
    required this.word,
    required this.category,
    required this.synonyms,
    required this.origin,
    required this.usage,
    required this.hebrew,
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
    map['hebrew'] = Variable<String>(hebrew);
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
      hebrew: Value(hebrew),
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
      hebrew: serializer.fromJson<String>(json['hebrew']),
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
      'hebrew': serializer.toJson<String>(hebrew),
    };
  }

  GreekWord copyWith({
    int? id,
    String? word,
    String? category,
    String? synonyms,
    String? origin,
    String? usage,
    String? hebrew,
  }) => GreekWord(
    id: id ?? this.id,
    word: word ?? this.word,
    category: category ?? this.category,
    synonyms: synonyms ?? this.synonyms,
    origin: origin ?? this.origin,
    usage: usage ?? this.usage,
    hebrew: hebrew ?? this.hebrew,
  );
  GreekWord copyWithCompanion(GreekWordsCompanion data) {
    return GreekWord(
      id: data.id.present ? data.id.value : this.id,
      word: data.word.present ? data.word.value : this.word,
      category: data.category.present ? data.category.value : this.category,
      synonyms: data.synonyms.present ? data.synonyms.value : this.synonyms,
      origin: data.origin.present ? data.origin.value : this.origin,
      usage: data.usage.present ? data.usage.value : this.usage,
      hebrew: data.hebrew.present ? data.hebrew.value : this.hebrew,
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
          ..write('usage: $usage, ')
          ..write('hebrew: $hebrew')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(id, word, category, synonyms, origin, usage, hebrew);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is GreekWord &&
          other.id == this.id &&
          other.word == this.word &&
          other.category == this.category &&
          other.synonyms == this.synonyms &&
          other.origin == this.origin &&
          other.usage == this.usage &&
          other.hebrew == this.hebrew);
}

class GreekWordsCompanion extends UpdateCompanion<GreekWord> {
  final Value<int> id;
  final Value<String> word;
  final Value<String> category;
  final Value<String> synonyms;
  final Value<String> origin;
  final Value<String> usage;
  final Value<String> hebrew;
  const GreekWordsCompanion({
    this.id = const Value.absent(),
    this.word = const Value.absent(),
    this.category = const Value.absent(),
    this.synonyms = const Value.absent(),
    this.origin = const Value.absent(),
    this.usage = const Value.absent(),
    this.hebrew = const Value.absent(),
  });
  GreekWordsCompanion.insert({
    this.id = const Value.absent(),
    required String word,
    required String category,
    required String synonyms,
    required String origin,
    required String usage,
    required String hebrew,
  }) : word = Value(word),
       category = Value(category),
       synonyms = Value(synonyms),
       origin = Value(origin),
       usage = Value(usage),
       hebrew = Value(hebrew);
  static Insertable<GreekWord> custom({
    Expression<int>? id,
    Expression<String>? word,
    Expression<String>? category,
    Expression<String>? synonyms,
    Expression<String>? origin,
    Expression<String>? usage,
    Expression<String>? hebrew,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (word != null) 'word': word,
      if (category != null) 'category': category,
      if (synonyms != null) 'synonyms': synonyms,
      if (origin != null) 'origin': origin,
      if (usage != null) 'usage': usage,
      if (hebrew != null) 'hebrew': hebrew,
    });
  }

  GreekWordsCompanion copyWith({
    Value<int>? id,
    Value<String>? word,
    Value<String>? category,
    Value<String>? synonyms,
    Value<String>? origin,
    Value<String>? usage,
    Value<String>? hebrew,
  }) {
    return GreekWordsCompanion(
      id: id ?? this.id,
      word: word ?? this.word,
      category: category ?? this.category,
      synonyms: synonyms ?? this.synonyms,
      origin: origin ?? this.origin,
      usage: usage ?? this.usage,
      hebrew: hebrew ?? this.hebrew,
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
    if (hebrew.present) {
      map['hebrew'] = Variable<String>(hebrew.value);
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
          ..write('usage: $usage, ')
          ..write('hebrew: $hebrew')
          ..write(')'))
        .toString();
  }
}

abstract class _$CommonDB extends GeneratedDatabase {
  _$CommonDB(QueryExecutor e) : super(e);
  $CommonDBManager get managers => $CommonDBManager(this);
  late final $GreekWordsTable greekWords = $GreekWordsTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [greekWords];
}

typedef $$GreekWordsTableCreateCompanionBuilder =
    GreekWordsCompanion Function({
      Value<int> id,
      required String word,
      required String category,
      required String synonyms,
      required String origin,
      required String usage,
      required String hebrew,
    });
typedef $$GreekWordsTableUpdateCompanionBuilder =
    GreekWordsCompanion Function({
      Value<int> id,
      Value<String> word,
      Value<String> category,
      Value<String> synonyms,
      Value<String> origin,
      Value<String> usage,
      Value<String> hebrew,
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

  ColumnFilters<String> get hebrew => $composableBuilder(
    column: $table.hebrew,
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

  ColumnOrderings<String> get hebrew => $composableBuilder(
    column: $table.hebrew,
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

  GeneratedColumn<String> get hebrew =>
      $composableBuilder(column: $table.hebrew, builder: (column) => column);
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
                Value<String> hebrew = const Value.absent(),
              }) => GreekWordsCompanion(
                id: id,
                word: word,
                category: category,
                synonyms: synonyms,
                origin: origin,
                usage: usage,
                hebrew: hebrew,
              ),
          createCompanionCallback:
              ({
                Value<int> id = const Value.absent(),
                required String word,
                required String category,
                required String synonyms,
                required String origin,
                required String usage,
                required String hebrew,
              }) => GreekWordsCompanion.insert(
                id: id,
                word: word,
                category: category,
                synonyms: synonyms,
                origin: origin,
                usage: usage,
                hebrew: hebrew,
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

class $CommonDBManager {
  final _$CommonDB _db;
  $CommonDBManager(this._db);
  $$GreekWordsTableTableManager get greekWords =>
      $$GreekWordsTableTableManager(_db, _db.greekWords);
}
