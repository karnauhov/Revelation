// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'db_localized.dart';

// ignore_for_file: type=lint
class $GreekDescsTable extends GreekDescs
    with TableInfo<$GreekDescsTable, GreekDesc> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $GreekDescsTable(this.attachedDatabase, [this._alias]);
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
  static const VerificationMeta _descMeta = const VerificationMeta('desc');
  @override
  late final GeneratedColumn<String> desc = GeneratedColumn<String>(
    'desc',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [id, desc];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'greek_descs';
  @override
  VerificationContext validateIntegrity(
    Insertable<GreekDesc> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('desc')) {
      context.handle(
        _descMeta,
        desc.isAcceptableOrUnknown(data['desc']!, _descMeta),
      );
    } else if (isInserting) {
      context.missing(_descMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  GreekDesc map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return GreekDesc(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}id'],
      )!,
      desc: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}desc'],
      )!,
    );
  }

  @override
  $GreekDescsTable createAlias(String alias) {
    return $GreekDescsTable(attachedDatabase, alias);
  }
}

class GreekDesc extends DataClass implements Insertable<GreekDesc> {
  final int id;
  final String desc;
  const GreekDesc({required this.id, required this.desc});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['desc'] = Variable<String>(desc);
    return map;
  }

  GreekDescsCompanion toCompanion(bool nullToAbsent) {
    return GreekDescsCompanion(id: Value(id), desc: Value(desc));
  }

  factory GreekDesc.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return GreekDesc(
      id: serializer.fromJson<int>(json['id']),
      desc: serializer.fromJson<String>(json['desc']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'desc': serializer.toJson<String>(desc),
    };
  }

  GreekDesc copyWith({int? id, String? desc}) =>
      GreekDesc(id: id ?? this.id, desc: desc ?? this.desc);
  GreekDesc copyWithCompanion(GreekDescsCompanion data) {
    return GreekDesc(
      id: data.id.present ? data.id.value : this.id,
      desc: data.desc.present ? data.desc.value : this.desc,
    );
  }

  @override
  String toString() {
    return (StringBuffer('GreekDesc(')
          ..write('id: $id, ')
          ..write('desc: $desc')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, desc);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is GreekDesc && other.id == this.id && other.desc == this.desc);
}

class GreekDescsCompanion extends UpdateCompanion<GreekDesc> {
  final Value<int> id;
  final Value<String> desc;
  const GreekDescsCompanion({
    this.id = const Value.absent(),
    this.desc = const Value.absent(),
  });
  GreekDescsCompanion.insert({
    this.id = const Value.absent(),
    required String desc,
  }) : desc = Value(desc);
  static Insertable<GreekDesc> custom({
    Expression<int>? id,
    Expression<String>? desc,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (desc != null) 'desc': desc,
    });
  }

  GreekDescsCompanion copyWith({Value<int>? id, Value<String>? desc}) {
    return GreekDescsCompanion(id: id ?? this.id, desc: desc ?? this.desc);
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (desc.present) {
      map['desc'] = Variable<String>(desc.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('GreekDescsCompanion(')
          ..write('id: $id, ')
          ..write('desc: $desc')
          ..write(')'))
        .toString();
  }
}

abstract class _$LocalizedDB extends GeneratedDatabase {
  _$LocalizedDB(QueryExecutor e) : super(e);
  $LocalizedDBManager get managers => $LocalizedDBManager(this);
  late final $GreekDescsTable greekDescs = $GreekDescsTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [greekDescs];
}

typedef $$GreekDescsTableCreateCompanionBuilder =
    GreekDescsCompanion Function({Value<int> id, required String desc});
typedef $$GreekDescsTableUpdateCompanionBuilder =
    GreekDescsCompanion Function({Value<int> id, Value<String> desc});

class $$GreekDescsTableFilterComposer
    extends Composer<_$LocalizedDB, $GreekDescsTable> {
  $$GreekDescsTableFilterComposer({
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

  ColumnFilters<String> get desc => $composableBuilder(
    column: $table.desc,
    builder: (column) => ColumnFilters(column),
  );
}

class $$GreekDescsTableOrderingComposer
    extends Composer<_$LocalizedDB, $GreekDescsTable> {
  $$GreekDescsTableOrderingComposer({
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

  ColumnOrderings<String> get desc => $composableBuilder(
    column: $table.desc,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$GreekDescsTableAnnotationComposer
    extends Composer<_$LocalizedDB, $GreekDescsTable> {
  $$GreekDescsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get desc =>
      $composableBuilder(column: $table.desc, builder: (column) => column);
}

class $$GreekDescsTableTableManager
    extends
        RootTableManager<
          _$LocalizedDB,
          $GreekDescsTable,
          GreekDesc,
          $$GreekDescsTableFilterComposer,
          $$GreekDescsTableOrderingComposer,
          $$GreekDescsTableAnnotationComposer,
          $$GreekDescsTableCreateCompanionBuilder,
          $$GreekDescsTableUpdateCompanionBuilder,
          (
            GreekDesc,
            BaseReferences<_$LocalizedDB, $GreekDescsTable, GreekDesc>,
          ),
          GreekDesc,
          PrefetchHooks Function()
        > {
  $$GreekDescsTableTableManager(_$LocalizedDB db, $GreekDescsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$GreekDescsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$GreekDescsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$GreekDescsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<int> id = const Value.absent(),
                Value<String> desc = const Value.absent(),
              }) => GreekDescsCompanion(id: id, desc: desc),
          createCompanionCallback:
              ({Value<int> id = const Value.absent(), required String desc}) =>
                  GreekDescsCompanion.insert(id: id, desc: desc),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$GreekDescsTableProcessedTableManager =
    ProcessedTableManager<
      _$LocalizedDB,
      $GreekDescsTable,
      GreekDesc,
      $$GreekDescsTableFilterComposer,
      $$GreekDescsTableOrderingComposer,
      $$GreekDescsTableAnnotationComposer,
      $$GreekDescsTableCreateCompanionBuilder,
      $$GreekDescsTableUpdateCompanionBuilder,
      (GreekDesc, BaseReferences<_$LocalizedDB, $GreekDescsTable, GreekDesc>),
      GreekDesc,
      PrefetchHooks Function()
    >;

class $LocalizedDBManager {
  final _$LocalizedDB _db;
  $LocalizedDBManager(this._db);
  $$GreekDescsTableTableManager get greekDescs =>
      $$GreekDescsTableTableManager(_db, _db.greekDescs);
}
