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

class $TopicTextsTable extends TopicTexts
    with TableInfo<$TopicTextsTable, TopicText> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $TopicTextsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _routeMeta = const VerificationMeta('route');
  @override
  late final GeneratedColumn<String> route = GeneratedColumn<String>(
    'route',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _markdownMeta = const VerificationMeta(
    'markdown',
  );
  @override
  late final GeneratedColumn<String> markdown = GeneratedColumn<String>(
    'markdown',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [route, markdown];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'topic_texts';
  @override
  VerificationContext validateIntegrity(
    Insertable<TopicText> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('route')) {
      context.handle(
        _routeMeta,
        route.isAcceptableOrUnknown(data['route']!, _routeMeta),
      );
    } else if (isInserting) {
      context.missing(_routeMeta);
    }
    if (data.containsKey('markdown')) {
      context.handle(
        _markdownMeta,
        markdown.isAcceptableOrUnknown(data['markdown']!, _markdownMeta),
      );
    } else if (isInserting) {
      context.missing(_markdownMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {route};
  @override
  TopicText map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return TopicText(
      route: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}route'],
      )!,
      markdown: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}markdown'],
      )!,
    );
  }

  @override
  $TopicTextsTable createAlias(String alias) {
    return $TopicTextsTable(attachedDatabase, alias);
  }
}

class TopicText extends DataClass implements Insertable<TopicText> {
  final String route;
  final String markdown;
  const TopicText({required this.route, required this.markdown});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['route'] = Variable<String>(route);
    map['markdown'] = Variable<String>(markdown);
    return map;
  }

  TopicTextsCompanion toCompanion(bool nullToAbsent) {
    return TopicTextsCompanion(route: Value(route), markdown: Value(markdown));
  }

  factory TopicText.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return TopicText(
      route: serializer.fromJson<String>(json['route']),
      markdown: serializer.fromJson<String>(json['markdown']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'route': serializer.toJson<String>(route),
      'markdown': serializer.toJson<String>(markdown),
    };
  }

  TopicText copyWith({String? route, String? markdown}) => TopicText(
    route: route ?? this.route,
    markdown: markdown ?? this.markdown,
  );
  TopicText copyWithCompanion(TopicTextsCompanion data) {
    return TopicText(
      route: data.route.present ? data.route.value : this.route,
      markdown: data.markdown.present ? data.markdown.value : this.markdown,
    );
  }

  @override
  String toString() {
    return (StringBuffer('TopicText(')
          ..write('route: $route, ')
          ..write('markdown: $markdown')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(route, markdown);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is TopicText &&
          other.route == this.route &&
          other.markdown == this.markdown);
}

class TopicTextsCompanion extends UpdateCompanion<TopicText> {
  final Value<String> route;
  final Value<String> markdown;
  final Value<int> rowid;
  const TopicTextsCompanion({
    this.route = const Value.absent(),
    this.markdown = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  TopicTextsCompanion.insert({
    required String route,
    required String markdown,
    this.rowid = const Value.absent(),
  }) : route = Value(route),
       markdown = Value(markdown);
  static Insertable<TopicText> custom({
    Expression<String>? route,
    Expression<String>? markdown,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (route != null) 'route': route,
      if (markdown != null) 'markdown': markdown,
      if (rowid != null) 'rowid': rowid,
    });
  }

  TopicTextsCompanion copyWith({
    Value<String>? route,
    Value<String>? markdown,
    Value<int>? rowid,
  }) {
    return TopicTextsCompanion(
      route: route ?? this.route,
      markdown: markdown ?? this.markdown,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (route.present) {
      map['route'] = Variable<String>(route.value);
    }
    if (markdown.present) {
      map['markdown'] = Variable<String>(markdown.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TopicTextsCompanion(')
          ..write('route: $route, ')
          ..write('markdown: $markdown, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $TopicsTable extends Topics with TableInfo<$TopicsTable, Topic> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $TopicsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _routeMeta = const VerificationMeta('route');
  @override
  late final GeneratedColumn<String> route = GeneratedColumn<String>(
    'route',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _nameMeta = const VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name = GeneratedColumn<String>(
    'name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _descriptionMeta = const VerificationMeta(
    'description',
  );
  @override
  late final GeneratedColumn<String> description = GeneratedColumn<String>(
    'description',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _idIconMeta = const VerificationMeta('idIcon');
  @override
  late final GeneratedColumn<String> idIcon = GeneratedColumn<String>(
    'id_icon',
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
  static const VerificationMeta _isVisibleMeta = const VerificationMeta(
    'isVisible',
  );
  @override
  late final GeneratedColumn<bool> isVisible = GeneratedColumn<bool>(
    'is_visible',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("is_visible" IN (0, 1))',
    ),
    defaultValue: const Constant(true),
  );
  @override
  List<GeneratedColumn> get $columns => [
    route,
    name,
    description,
    idIcon,
    sortOrder,
    isVisible,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'topics';
  @override
  VerificationContext validateIntegrity(
    Insertable<Topic> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('route')) {
      context.handle(
        _routeMeta,
        route.isAcceptableOrUnknown(data['route']!, _routeMeta),
      );
    } else if (isInserting) {
      context.missing(_routeMeta);
    }
    if (data.containsKey('name')) {
      context.handle(
        _nameMeta,
        name.isAcceptableOrUnknown(data['name']!, _nameMeta),
      );
    } else if (isInserting) {
      context.missing(_nameMeta);
    }
    if (data.containsKey('description')) {
      context.handle(
        _descriptionMeta,
        description.isAcceptableOrUnknown(
          data['description']!,
          _descriptionMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_descriptionMeta);
    }
    if (data.containsKey('id_icon')) {
      context.handle(
        _idIconMeta,
        idIcon.isAcceptableOrUnknown(data['id_icon']!, _idIconMeta),
      );
    } else if (isInserting) {
      context.missing(_idIconMeta);
    }
    if (data.containsKey('sort_order')) {
      context.handle(
        _sortOrderMeta,
        sortOrder.isAcceptableOrUnknown(data['sort_order']!, _sortOrderMeta),
      );
    }
    if (data.containsKey('is_visible')) {
      context.handle(
        _isVisibleMeta,
        isVisible.isAcceptableOrUnknown(data['is_visible']!, _isVisibleMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {route};
  @override
  Topic map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Topic(
      route: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}route'],
      )!,
      name: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}name'],
      )!,
      description: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}description'],
      )!,
      idIcon: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id_icon'],
      )!,
      sortOrder: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}sort_order'],
      )!,
      isVisible: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}is_visible'],
      )!,
    );
  }

  @override
  $TopicsTable createAlias(String alias) {
    return $TopicsTable(attachedDatabase, alias);
  }
}

class Topic extends DataClass implements Insertable<Topic> {
  final String route;
  final String name;
  final String description;
  final String idIcon;
  final int sortOrder;
  final bool isVisible;
  const Topic({
    required this.route,
    required this.name,
    required this.description,
    required this.idIcon,
    required this.sortOrder,
    required this.isVisible,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['route'] = Variable<String>(route);
    map['name'] = Variable<String>(name);
    map['description'] = Variable<String>(description);
    map['id_icon'] = Variable<String>(idIcon);
    map['sort_order'] = Variable<int>(sortOrder);
    map['is_visible'] = Variable<bool>(isVisible);
    return map;
  }

  TopicsCompanion toCompanion(bool nullToAbsent) {
    return TopicsCompanion(
      route: Value(route),
      name: Value(name),
      description: Value(description),
      idIcon: Value(idIcon),
      sortOrder: Value(sortOrder),
      isVisible: Value(isVisible),
    );
  }

  factory Topic.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Topic(
      route: serializer.fromJson<String>(json['route']),
      name: serializer.fromJson<String>(json['name']),
      description: serializer.fromJson<String>(json['description']),
      idIcon: serializer.fromJson<String>(json['idIcon']),
      sortOrder: serializer.fromJson<int>(json['sortOrder']),
      isVisible: serializer.fromJson<bool>(json['isVisible']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'route': serializer.toJson<String>(route),
      'name': serializer.toJson<String>(name),
      'description': serializer.toJson<String>(description),
      'idIcon': serializer.toJson<String>(idIcon),
      'sortOrder': serializer.toJson<int>(sortOrder),
      'isVisible': serializer.toJson<bool>(isVisible),
    };
  }

  Topic copyWith({
    String? route,
    String? name,
    String? description,
    String? idIcon,
    int? sortOrder,
    bool? isVisible,
  }) => Topic(
    route: route ?? this.route,
    name: name ?? this.name,
    description: description ?? this.description,
    idIcon: idIcon ?? this.idIcon,
    sortOrder: sortOrder ?? this.sortOrder,
    isVisible: isVisible ?? this.isVisible,
  );
  Topic copyWithCompanion(TopicsCompanion data) {
    return Topic(
      route: data.route.present ? data.route.value : this.route,
      name: data.name.present ? data.name.value : this.name,
      description: data.description.present
          ? data.description.value
          : this.description,
      idIcon: data.idIcon.present ? data.idIcon.value : this.idIcon,
      sortOrder: data.sortOrder.present ? data.sortOrder.value : this.sortOrder,
      isVisible: data.isVisible.present ? data.isVisible.value : this.isVisible,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Topic(')
          ..write('route: $route, ')
          ..write('name: $name, ')
          ..write('description: $description, ')
          ..write('idIcon: $idIcon, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('isVisible: $isVisible')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(route, name, description, idIcon, sortOrder, isVisible);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Topic &&
          other.route == this.route &&
          other.name == this.name &&
          other.description == this.description &&
          other.idIcon == this.idIcon &&
          other.sortOrder == this.sortOrder &&
          other.isVisible == this.isVisible);
}

class TopicsCompanion extends UpdateCompanion<Topic> {
  final Value<String> route;
  final Value<String> name;
  final Value<String> description;
  final Value<String> idIcon;
  final Value<int> sortOrder;
  final Value<bool> isVisible;
  final Value<int> rowid;
  const TopicsCompanion({
    this.route = const Value.absent(),
    this.name = const Value.absent(),
    this.description = const Value.absent(),
    this.idIcon = const Value.absent(),
    this.sortOrder = const Value.absent(),
    this.isVisible = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  TopicsCompanion.insert({
    required String route,
    required String name,
    required String description,
    required String idIcon,
    this.sortOrder = const Value.absent(),
    this.isVisible = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : route = Value(route),
       name = Value(name),
       description = Value(description),
       idIcon = Value(idIcon);
  static Insertable<Topic> custom({
    Expression<String>? route,
    Expression<String>? name,
    Expression<String>? description,
    Expression<String>? idIcon,
    Expression<int>? sortOrder,
    Expression<bool>? isVisible,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (route != null) 'route': route,
      if (name != null) 'name': name,
      if (description != null) 'description': description,
      if (idIcon != null) 'id_icon': idIcon,
      if (sortOrder != null) 'sort_order': sortOrder,
      if (isVisible != null) 'is_visible': isVisible,
      if (rowid != null) 'rowid': rowid,
    });
  }

  TopicsCompanion copyWith({
    Value<String>? route,
    Value<String>? name,
    Value<String>? description,
    Value<String>? idIcon,
    Value<int>? sortOrder,
    Value<bool>? isVisible,
    Value<int>? rowid,
  }) {
    return TopicsCompanion(
      route: route ?? this.route,
      name: name ?? this.name,
      description: description ?? this.description,
      idIcon: idIcon ?? this.idIcon,
      sortOrder: sortOrder ?? this.sortOrder,
      isVisible: isVisible ?? this.isVisible,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (route.present) {
      map['route'] = Variable<String>(route.value);
    }
    if (name.present) {
      map['name'] = Variable<String>(name.value);
    }
    if (description.present) {
      map['description'] = Variable<String>(description.value);
    }
    if (idIcon.present) {
      map['id_icon'] = Variable<String>(idIcon.value);
    }
    if (sortOrder.present) {
      map['sort_order'] = Variable<int>(sortOrder.value);
    }
    if (isVisible.present) {
      map['is_visible'] = Variable<bool>(isVisible.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('TopicsCompanion(')
          ..write('route: $route, ')
          ..write('name: $name, ')
          ..write('description: $description, ')
          ..write('idIcon: $idIcon, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('isVisible: $isVisible, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$LocalizedDB extends GeneratedDatabase {
  _$LocalizedDB(QueryExecutor e) : super(e);
  $LocalizedDBManager get managers => $LocalizedDBManager(this);
  late final $GreekDescsTable greekDescs = $GreekDescsTable(this);
  late final $TopicTextsTable topicTexts = $TopicTextsTable(this);
  late final $TopicsTable topics = $TopicsTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    greekDescs,
    topicTexts,
    topics,
  ];
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
typedef $$TopicTextsTableCreateCompanionBuilder =
    TopicTextsCompanion Function({
      required String route,
      required String markdown,
      Value<int> rowid,
    });
typedef $$TopicTextsTableUpdateCompanionBuilder =
    TopicTextsCompanion Function({
      Value<String> route,
      Value<String> markdown,
      Value<int> rowid,
    });

class $$TopicTextsTableFilterComposer
    extends Composer<_$LocalizedDB, $TopicTextsTable> {
  $$TopicTextsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get route => $composableBuilder(
    column: $table.route,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get markdown => $composableBuilder(
    column: $table.markdown,
    builder: (column) => ColumnFilters(column),
  );
}

class $$TopicTextsTableOrderingComposer
    extends Composer<_$LocalizedDB, $TopicTextsTable> {
  $$TopicTextsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get route => $composableBuilder(
    column: $table.route,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get markdown => $composableBuilder(
    column: $table.markdown,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$TopicTextsTableAnnotationComposer
    extends Composer<_$LocalizedDB, $TopicTextsTable> {
  $$TopicTextsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get route =>
      $composableBuilder(column: $table.route, builder: (column) => column);

  GeneratedColumn<String> get markdown =>
      $composableBuilder(column: $table.markdown, builder: (column) => column);
}

class $$TopicTextsTableTableManager
    extends
        RootTableManager<
          _$LocalizedDB,
          $TopicTextsTable,
          TopicText,
          $$TopicTextsTableFilterComposer,
          $$TopicTextsTableOrderingComposer,
          $$TopicTextsTableAnnotationComposer,
          $$TopicTextsTableCreateCompanionBuilder,
          $$TopicTextsTableUpdateCompanionBuilder,
          (
            TopicText,
            BaseReferences<_$LocalizedDB, $TopicTextsTable, TopicText>,
          ),
          TopicText,
          PrefetchHooks Function()
        > {
  $$TopicTextsTableTableManager(_$LocalizedDB db, $TopicTextsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$TopicTextsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$TopicTextsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$TopicTextsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> route = const Value.absent(),
                Value<String> markdown = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => TopicTextsCompanion(
                route: route,
                markdown: markdown,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String route,
                required String markdown,
                Value<int> rowid = const Value.absent(),
              }) => TopicTextsCompanion.insert(
                route: route,
                markdown: markdown,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$TopicTextsTableProcessedTableManager =
    ProcessedTableManager<
      _$LocalizedDB,
      $TopicTextsTable,
      TopicText,
      $$TopicTextsTableFilterComposer,
      $$TopicTextsTableOrderingComposer,
      $$TopicTextsTableAnnotationComposer,
      $$TopicTextsTableCreateCompanionBuilder,
      $$TopicTextsTableUpdateCompanionBuilder,
      (TopicText, BaseReferences<_$LocalizedDB, $TopicTextsTable, TopicText>),
      TopicText,
      PrefetchHooks Function()
    >;
typedef $$TopicsTableCreateCompanionBuilder =
    TopicsCompanion Function({
      required String route,
      required String name,
      required String description,
      required String idIcon,
      Value<int> sortOrder,
      Value<bool> isVisible,
      Value<int> rowid,
    });
typedef $$TopicsTableUpdateCompanionBuilder =
    TopicsCompanion Function({
      Value<String> route,
      Value<String> name,
      Value<String> description,
      Value<String> idIcon,
      Value<int> sortOrder,
      Value<bool> isVisible,
      Value<int> rowid,
    });

class $$TopicsTableFilterComposer
    extends Composer<_$LocalizedDB, $TopicsTable> {
  $$TopicsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get route => $composableBuilder(
    column: $table.route,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get description => $composableBuilder(
    column: $table.description,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get idIcon => $composableBuilder(
    column: $table.idIcon,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get isVisible => $composableBuilder(
    column: $table.isVisible,
    builder: (column) => ColumnFilters(column),
  );
}

class $$TopicsTableOrderingComposer
    extends Composer<_$LocalizedDB, $TopicsTable> {
  $$TopicsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get route => $composableBuilder(
    column: $table.route,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get description => $composableBuilder(
    column: $table.description,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get idIcon => $composableBuilder(
    column: $table.idIcon,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get sortOrder => $composableBuilder(
    column: $table.sortOrder,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get isVisible => $composableBuilder(
    column: $table.isVisible,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$TopicsTableAnnotationComposer
    extends Composer<_$LocalizedDB, $TopicsTable> {
  $$TopicsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get route =>
      $composableBuilder(column: $table.route, builder: (column) => column);

  GeneratedColumn<String> get name =>
      $composableBuilder(column: $table.name, builder: (column) => column);

  GeneratedColumn<String> get description => $composableBuilder(
    column: $table.description,
    builder: (column) => column,
  );

  GeneratedColumn<String> get idIcon =>
      $composableBuilder(column: $table.idIcon, builder: (column) => column);

  GeneratedColumn<int> get sortOrder =>
      $composableBuilder(column: $table.sortOrder, builder: (column) => column);

  GeneratedColumn<bool> get isVisible =>
      $composableBuilder(column: $table.isVisible, builder: (column) => column);
}

class $$TopicsTableTableManager
    extends
        RootTableManager<
          _$LocalizedDB,
          $TopicsTable,
          Topic,
          $$TopicsTableFilterComposer,
          $$TopicsTableOrderingComposer,
          $$TopicsTableAnnotationComposer,
          $$TopicsTableCreateCompanionBuilder,
          $$TopicsTableUpdateCompanionBuilder,
          (Topic, BaseReferences<_$LocalizedDB, $TopicsTable, Topic>),
          Topic,
          PrefetchHooks Function()
        > {
  $$TopicsTableTableManager(_$LocalizedDB db, $TopicsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$TopicsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$TopicsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$TopicsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> route = const Value.absent(),
                Value<String> name = const Value.absent(),
                Value<String> description = const Value.absent(),
                Value<String> idIcon = const Value.absent(),
                Value<int> sortOrder = const Value.absent(),
                Value<bool> isVisible = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => TopicsCompanion(
                route: route,
                name: name,
                description: description,
                idIcon: idIcon,
                sortOrder: sortOrder,
                isVisible: isVisible,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String route,
                required String name,
                required String description,
                required String idIcon,
                Value<int> sortOrder = const Value.absent(),
                Value<bool> isVisible = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => TopicsCompanion.insert(
                route: route,
                name: name,
                description: description,
                idIcon: idIcon,
                sortOrder: sortOrder,
                isVisible: isVisible,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$TopicsTableProcessedTableManager =
    ProcessedTableManager<
      _$LocalizedDB,
      $TopicsTable,
      Topic,
      $$TopicsTableFilterComposer,
      $$TopicsTableOrderingComposer,
      $$TopicsTableAnnotationComposer,
      $$TopicsTableCreateCompanionBuilder,
      $$TopicsTableUpdateCompanionBuilder,
      (Topic, BaseReferences<_$LocalizedDB, $TopicsTable, Topic>),
      Topic,
      PrefetchHooks Function()
    >;

class $LocalizedDBManager {
  final _$LocalizedDB _db;
  $LocalizedDBManager(this._db);
  $$GreekDescsTableTableManager get greekDescs =>
      $$GreekDescsTableTableManager(_db, _db.greekDescs);
  $$TopicTextsTableTableManager get topicTexts =>
      $$TopicTextsTableTableManager(_db, _db.topicTexts);
  $$TopicsTableTableManager get topics =>
      $$TopicsTableTableManager(_db, _db.topics);
}
