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
  static const VerificationMeta _translitMeta = const VerificationMeta(
    'translit',
  );
  @override
  late final GeneratedColumn<String> translit = GeneratedColumn<String>(
    'translit',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [id, word, translit];
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
    if (data.containsKey('translit')) {
      context.handle(
        _translitMeta,
        translit.isAcceptableOrUnknown(data['translit']!, _translitMeta),
      );
    } else if (isInserting) {
      context.missing(_translitMeta);
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
      translit: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}translit'],
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
  final String translit;
  const GreekWord({
    required this.id,
    required this.word,
    required this.translit,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['word'] = Variable<String>(word);
    map['translit'] = Variable<String>(translit);
    return map;
  }

  GreekWordsCompanion toCompanion(bool nullToAbsent) {
    return GreekWordsCompanion(
      id: Value(id),
      word: Value(word),
      translit: Value(translit),
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
      translit: serializer.fromJson<String>(json['translit']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'word': serializer.toJson<String>(word),
      'translit': serializer.toJson<String>(translit),
    };
  }

  GreekWord copyWith({int? id, String? word, String? translit}) => GreekWord(
    id: id ?? this.id,
    word: word ?? this.word,
    translit: translit ?? this.translit,
  );
  GreekWord copyWithCompanion(GreekWordsCompanion data) {
    return GreekWord(
      id: data.id.present ? data.id.value : this.id,
      word: data.word.present ? data.word.value : this.word,
      translit: data.translit.present ? data.translit.value : this.translit,
    );
  }

  @override
  String toString() {
    return (StringBuffer('GreekWord(')
          ..write('id: $id, ')
          ..write('word: $word, ')
          ..write('translit: $translit')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, word, translit);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is GreekWord &&
          other.id == this.id &&
          other.word == this.word &&
          other.translit == this.translit);
}

class GreekWordsCompanion extends UpdateCompanion<GreekWord> {
  final Value<int> id;
  final Value<String> word;
  final Value<String> translit;
  const GreekWordsCompanion({
    this.id = const Value.absent(),
    this.word = const Value.absent(),
    this.translit = const Value.absent(),
  });
  GreekWordsCompanion.insert({
    this.id = const Value.absent(),
    required String word,
    required String translit,
  }) : word = Value(word),
       translit = Value(translit);
  static Insertable<GreekWord> custom({
    Expression<int>? id,
    Expression<String>? word,
    Expression<String>? translit,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (word != null) 'word': word,
      if (translit != null) 'translit': translit,
    });
  }

  GreekWordsCompanion copyWith({
    Value<int>? id,
    Value<String>? word,
    Value<String>? translit,
  }) {
    return GreekWordsCompanion(
      id: id ?? this.id,
      word: word ?? this.word,
      translit: translit ?? this.translit,
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
    if (translit.present) {
      map['translit'] = Variable<String>(translit.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('GreekWordsCompanion(')
          ..write('id: $id, ')
          ..write('word: $word, ')
          ..write('translit: $translit')
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
      required String translit,
    });
typedef $$GreekWordsTableUpdateCompanionBuilder =
    GreekWordsCompanion Function({
      Value<int> id,
      Value<String> word,
      Value<String> translit,
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

  ColumnFilters<String> get translit => $composableBuilder(
    column: $table.translit,
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

  ColumnOrderings<String> get translit => $composableBuilder(
    column: $table.translit,
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

  GeneratedColumn<String> get translit =>
      $composableBuilder(column: $table.translit, builder: (column) => column);
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
                Value<String> translit = const Value.absent(),
              }) => GreekWordsCompanion(id: id, word: word, translit: translit),
          createCompanionCallback:
              ({
                Value<int> id = const Value.absent(),
                required String word,
                required String translit,
              }) => GreekWordsCompanion.insert(
                id: id,
                word: word,
                translit: translit,
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
