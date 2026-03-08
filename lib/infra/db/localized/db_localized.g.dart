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

class $ArticlesTable extends Articles with TableInfo<$ArticlesTable, Article> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ArticlesTable(this.attachedDatabase, [this._alias]);
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
  List<GeneratedColumn> get $columns => [
    route,
    name,
    description,
    idIcon,
    sortOrder,
    isVisible,
    markdown,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'articles';
  @override
  VerificationContext validateIntegrity(
    Insertable<Article> instance, {
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
  Article map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Article(
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
      markdown: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}markdown'],
      )!,
    );
  }

  @override
  $ArticlesTable createAlias(String alias) {
    return $ArticlesTable(attachedDatabase, alias);
  }
}

class Article extends DataClass implements Insertable<Article> {
  final String route;
  final String name;
  final String description;
  final String idIcon;
  final int sortOrder;
  final bool isVisible;
  final String markdown;
  const Article({
    required this.route,
    required this.name,
    required this.description,
    required this.idIcon,
    required this.sortOrder,
    required this.isVisible,
    required this.markdown,
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
    map['markdown'] = Variable<String>(markdown);
    return map;
  }

  ArticlesCompanion toCompanion(bool nullToAbsent) {
    return ArticlesCompanion(
      route: Value(route),
      name: Value(name),
      description: Value(description),
      idIcon: Value(idIcon),
      sortOrder: Value(sortOrder),
      isVisible: Value(isVisible),
      markdown: Value(markdown),
    );
  }

  factory Article.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Article(
      route: serializer.fromJson<String>(json['route']),
      name: serializer.fromJson<String>(json['name']),
      description: serializer.fromJson<String>(json['description']),
      idIcon: serializer.fromJson<String>(json['idIcon']),
      sortOrder: serializer.fromJson<int>(json['sortOrder']),
      isVisible: serializer.fromJson<bool>(json['isVisible']),
      markdown: serializer.fromJson<String>(json['markdown']),
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
      'markdown': serializer.toJson<String>(markdown),
    };
  }

  Article copyWith({
    String? route,
    String? name,
    String? description,
    String? idIcon,
    int? sortOrder,
    bool? isVisible,
    String? markdown,
  }) => Article(
    route: route ?? this.route,
    name: name ?? this.name,
    description: description ?? this.description,
    idIcon: idIcon ?? this.idIcon,
    sortOrder: sortOrder ?? this.sortOrder,
    isVisible: isVisible ?? this.isVisible,
    markdown: markdown ?? this.markdown,
  );
  Article copyWithCompanion(ArticlesCompanion data) {
    return Article(
      route: data.route.present ? data.route.value : this.route,
      name: data.name.present ? data.name.value : this.name,
      description: data.description.present
          ? data.description.value
          : this.description,
      idIcon: data.idIcon.present ? data.idIcon.value : this.idIcon,
      sortOrder: data.sortOrder.present ? data.sortOrder.value : this.sortOrder,
      isVisible: data.isVisible.present ? data.isVisible.value : this.isVisible,
      markdown: data.markdown.present ? data.markdown.value : this.markdown,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Article(')
          ..write('route: $route, ')
          ..write('name: $name, ')
          ..write('description: $description, ')
          ..write('idIcon: $idIcon, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('isVisible: $isVisible, ')
          ..write('markdown: $markdown')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    route,
    name,
    description,
    idIcon,
    sortOrder,
    isVisible,
    markdown,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Article &&
          other.route == this.route &&
          other.name == this.name &&
          other.description == this.description &&
          other.idIcon == this.idIcon &&
          other.sortOrder == this.sortOrder &&
          other.isVisible == this.isVisible &&
          other.markdown == this.markdown);
}

class ArticlesCompanion extends UpdateCompanion<Article> {
  final Value<String> route;
  final Value<String> name;
  final Value<String> description;
  final Value<String> idIcon;
  final Value<int> sortOrder;
  final Value<bool> isVisible;
  final Value<String> markdown;
  final Value<int> rowid;
  const ArticlesCompanion({
    this.route = const Value.absent(),
    this.name = const Value.absent(),
    this.description = const Value.absent(),
    this.idIcon = const Value.absent(),
    this.sortOrder = const Value.absent(),
    this.isVisible = const Value.absent(),
    this.markdown = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ArticlesCompanion.insert({
    required String route,
    required String name,
    required String description,
    required String idIcon,
    this.sortOrder = const Value.absent(),
    this.isVisible = const Value.absent(),
    required String markdown,
    this.rowid = const Value.absent(),
  }) : route = Value(route),
       name = Value(name),
       description = Value(description),
       idIcon = Value(idIcon),
       markdown = Value(markdown);
  static Insertable<Article> custom({
    Expression<String>? route,
    Expression<String>? name,
    Expression<String>? description,
    Expression<String>? idIcon,
    Expression<int>? sortOrder,
    Expression<bool>? isVisible,
    Expression<String>? markdown,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (route != null) 'route': route,
      if (name != null) 'name': name,
      if (description != null) 'description': description,
      if (idIcon != null) 'id_icon': idIcon,
      if (sortOrder != null) 'sort_order': sortOrder,
      if (isVisible != null) 'is_visible': isVisible,
      if (markdown != null) 'markdown': markdown,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ArticlesCompanion copyWith({
    Value<String>? route,
    Value<String>? name,
    Value<String>? description,
    Value<String>? idIcon,
    Value<int>? sortOrder,
    Value<bool>? isVisible,
    Value<String>? markdown,
    Value<int>? rowid,
  }) {
    return ArticlesCompanion(
      route: route ?? this.route,
      name: name ?? this.name,
      description: description ?? this.description,
      idIcon: idIcon ?? this.idIcon,
      sortOrder: sortOrder ?? this.sortOrder,
      isVisible: isVisible ?? this.isVisible,
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
    return (StringBuffer('ArticlesCompanion(')
          ..write('route: $route, ')
          ..write('name: $name, ')
          ..write('description: $description, ')
          ..write('idIcon: $idIcon, ')
          ..write('sortOrder: $sortOrder, ')
          ..write('isVisible: $isVisible, ')
          ..write('markdown: $markdown, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PrimarySourceTextsTable extends PrimarySourceTexts
    with TableInfo<$PrimarySourceTextsTable, PrimarySourceText> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PrimarySourceTextsTable(this.attachedDatabase, [this._alias]);
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
  static const VerificationMeta _titleMarkupMeta = const VerificationMeta(
    'titleMarkup',
  );
  @override
  late final GeneratedColumn<String> titleMarkup = GeneratedColumn<String>(
    'title_markup',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _dateLabelMeta = const VerificationMeta(
    'dateLabel',
  );
  @override
  late final GeneratedColumn<String> dateLabel = GeneratedColumn<String>(
    'date_label',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _contentLabelMeta = const VerificationMeta(
    'contentLabel',
  );
  @override
  late final GeneratedColumn<String> contentLabel = GeneratedColumn<String>(
    'content_label',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _materialTextMeta = const VerificationMeta(
    'materialText',
  );
  @override
  late final GeneratedColumn<String> materialText = GeneratedColumn<String>(
    'material_text',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _textStyleTextMeta = const VerificationMeta(
    'textStyleText',
  );
  @override
  late final GeneratedColumn<String> textStyleText = GeneratedColumn<String>(
    'text_style_text',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _foundTextMeta = const VerificationMeta(
    'foundText',
  );
  @override
  late final GeneratedColumn<String> foundText = GeneratedColumn<String>(
    'found_text',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _classificationTextMeta =
      const VerificationMeta('classificationText');
  @override
  late final GeneratedColumn<String> classificationText =
      GeneratedColumn<String>(
        'classification_text',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: true,
      );
  static const VerificationMeta _currentLocationTextMeta =
      const VerificationMeta('currentLocationText');
  @override
  late final GeneratedColumn<String> currentLocationText =
      GeneratedColumn<String>(
        'current_location_text',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: true,
      );
  @override
  List<GeneratedColumn> get $columns => [
    sourceId,
    titleMarkup,
    dateLabel,
    contentLabel,
    materialText,
    textStyleText,
    foundText,
    classificationText,
    currentLocationText,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'primary_source_texts';
  @override
  VerificationContext validateIntegrity(
    Insertable<PrimarySourceText> instance, {
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
    if (data.containsKey('title_markup')) {
      context.handle(
        _titleMarkupMeta,
        titleMarkup.isAcceptableOrUnknown(
          data['title_markup']!,
          _titleMarkupMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_titleMarkupMeta);
    }
    if (data.containsKey('date_label')) {
      context.handle(
        _dateLabelMeta,
        dateLabel.isAcceptableOrUnknown(data['date_label']!, _dateLabelMeta),
      );
    } else if (isInserting) {
      context.missing(_dateLabelMeta);
    }
    if (data.containsKey('content_label')) {
      context.handle(
        _contentLabelMeta,
        contentLabel.isAcceptableOrUnknown(
          data['content_label']!,
          _contentLabelMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_contentLabelMeta);
    }
    if (data.containsKey('material_text')) {
      context.handle(
        _materialTextMeta,
        materialText.isAcceptableOrUnknown(
          data['material_text']!,
          _materialTextMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_materialTextMeta);
    }
    if (data.containsKey('text_style_text')) {
      context.handle(
        _textStyleTextMeta,
        textStyleText.isAcceptableOrUnknown(
          data['text_style_text']!,
          _textStyleTextMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_textStyleTextMeta);
    }
    if (data.containsKey('found_text')) {
      context.handle(
        _foundTextMeta,
        foundText.isAcceptableOrUnknown(data['found_text']!, _foundTextMeta),
      );
    } else if (isInserting) {
      context.missing(_foundTextMeta);
    }
    if (data.containsKey('classification_text')) {
      context.handle(
        _classificationTextMeta,
        classificationText.isAcceptableOrUnknown(
          data['classification_text']!,
          _classificationTextMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_classificationTextMeta);
    }
    if (data.containsKey('current_location_text')) {
      context.handle(
        _currentLocationTextMeta,
        currentLocationText.isAcceptableOrUnknown(
          data['current_location_text']!,
          _currentLocationTextMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_currentLocationTextMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {sourceId};
  @override
  PrimarySourceText map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PrimarySourceText(
      sourceId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}source_id'],
      )!,
      titleMarkup: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}title_markup'],
      )!,
      dateLabel: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}date_label'],
      )!,
      contentLabel: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}content_label'],
      )!,
      materialText: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}material_text'],
      )!,
      textStyleText: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}text_style_text'],
      )!,
      foundText: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}found_text'],
      )!,
      classificationText: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}classification_text'],
      )!,
      currentLocationText: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}current_location_text'],
      )!,
    );
  }

  @override
  $PrimarySourceTextsTable createAlias(String alias) {
    return $PrimarySourceTextsTable(attachedDatabase, alias);
  }
}

class PrimarySourceText extends DataClass
    implements Insertable<PrimarySourceText> {
  final String sourceId;
  final String titleMarkup;
  final String dateLabel;
  final String contentLabel;
  final String materialText;
  final String textStyleText;
  final String foundText;
  final String classificationText;
  final String currentLocationText;
  const PrimarySourceText({
    required this.sourceId,
    required this.titleMarkup,
    required this.dateLabel,
    required this.contentLabel,
    required this.materialText,
    required this.textStyleText,
    required this.foundText,
    required this.classificationText,
    required this.currentLocationText,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['source_id'] = Variable<String>(sourceId);
    map['title_markup'] = Variable<String>(titleMarkup);
    map['date_label'] = Variable<String>(dateLabel);
    map['content_label'] = Variable<String>(contentLabel);
    map['material_text'] = Variable<String>(materialText);
    map['text_style_text'] = Variable<String>(textStyleText);
    map['found_text'] = Variable<String>(foundText);
    map['classification_text'] = Variable<String>(classificationText);
    map['current_location_text'] = Variable<String>(currentLocationText);
    return map;
  }

  PrimarySourceTextsCompanion toCompanion(bool nullToAbsent) {
    return PrimarySourceTextsCompanion(
      sourceId: Value(sourceId),
      titleMarkup: Value(titleMarkup),
      dateLabel: Value(dateLabel),
      contentLabel: Value(contentLabel),
      materialText: Value(materialText),
      textStyleText: Value(textStyleText),
      foundText: Value(foundText),
      classificationText: Value(classificationText),
      currentLocationText: Value(currentLocationText),
    );
  }

  factory PrimarySourceText.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PrimarySourceText(
      sourceId: serializer.fromJson<String>(json['sourceId']),
      titleMarkup: serializer.fromJson<String>(json['titleMarkup']),
      dateLabel: serializer.fromJson<String>(json['dateLabel']),
      contentLabel: serializer.fromJson<String>(json['contentLabel']),
      materialText: serializer.fromJson<String>(json['materialText']),
      textStyleText: serializer.fromJson<String>(json['textStyleText']),
      foundText: serializer.fromJson<String>(json['foundText']),
      classificationText: serializer.fromJson<String>(
        json['classificationText'],
      ),
      currentLocationText: serializer.fromJson<String>(
        json['currentLocationText'],
      ),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'sourceId': serializer.toJson<String>(sourceId),
      'titleMarkup': serializer.toJson<String>(titleMarkup),
      'dateLabel': serializer.toJson<String>(dateLabel),
      'contentLabel': serializer.toJson<String>(contentLabel),
      'materialText': serializer.toJson<String>(materialText),
      'textStyleText': serializer.toJson<String>(textStyleText),
      'foundText': serializer.toJson<String>(foundText),
      'classificationText': serializer.toJson<String>(classificationText),
      'currentLocationText': serializer.toJson<String>(currentLocationText),
    };
  }

  PrimarySourceText copyWith({
    String? sourceId,
    String? titleMarkup,
    String? dateLabel,
    String? contentLabel,
    String? materialText,
    String? textStyleText,
    String? foundText,
    String? classificationText,
    String? currentLocationText,
  }) => PrimarySourceText(
    sourceId: sourceId ?? this.sourceId,
    titleMarkup: titleMarkup ?? this.titleMarkup,
    dateLabel: dateLabel ?? this.dateLabel,
    contentLabel: contentLabel ?? this.contentLabel,
    materialText: materialText ?? this.materialText,
    textStyleText: textStyleText ?? this.textStyleText,
    foundText: foundText ?? this.foundText,
    classificationText: classificationText ?? this.classificationText,
    currentLocationText: currentLocationText ?? this.currentLocationText,
  );
  PrimarySourceText copyWithCompanion(PrimarySourceTextsCompanion data) {
    return PrimarySourceText(
      sourceId: data.sourceId.present ? data.sourceId.value : this.sourceId,
      titleMarkup: data.titleMarkup.present
          ? data.titleMarkup.value
          : this.titleMarkup,
      dateLabel: data.dateLabel.present ? data.dateLabel.value : this.dateLabel,
      contentLabel: data.contentLabel.present
          ? data.contentLabel.value
          : this.contentLabel,
      materialText: data.materialText.present
          ? data.materialText.value
          : this.materialText,
      textStyleText: data.textStyleText.present
          ? data.textStyleText.value
          : this.textStyleText,
      foundText: data.foundText.present ? data.foundText.value : this.foundText,
      classificationText: data.classificationText.present
          ? data.classificationText.value
          : this.classificationText,
      currentLocationText: data.currentLocationText.present
          ? data.currentLocationText.value
          : this.currentLocationText,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceText(')
          ..write('sourceId: $sourceId, ')
          ..write('titleMarkup: $titleMarkup, ')
          ..write('dateLabel: $dateLabel, ')
          ..write('contentLabel: $contentLabel, ')
          ..write('materialText: $materialText, ')
          ..write('textStyleText: $textStyleText, ')
          ..write('foundText: $foundText, ')
          ..write('classificationText: $classificationText, ')
          ..write('currentLocationText: $currentLocationText')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    sourceId,
    titleMarkup,
    dateLabel,
    contentLabel,
    materialText,
    textStyleText,
    foundText,
    classificationText,
    currentLocationText,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PrimarySourceText &&
          other.sourceId == this.sourceId &&
          other.titleMarkup == this.titleMarkup &&
          other.dateLabel == this.dateLabel &&
          other.contentLabel == this.contentLabel &&
          other.materialText == this.materialText &&
          other.textStyleText == this.textStyleText &&
          other.foundText == this.foundText &&
          other.classificationText == this.classificationText &&
          other.currentLocationText == this.currentLocationText);
}

class PrimarySourceTextsCompanion extends UpdateCompanion<PrimarySourceText> {
  final Value<String> sourceId;
  final Value<String> titleMarkup;
  final Value<String> dateLabel;
  final Value<String> contentLabel;
  final Value<String> materialText;
  final Value<String> textStyleText;
  final Value<String> foundText;
  final Value<String> classificationText;
  final Value<String> currentLocationText;
  final Value<int> rowid;
  const PrimarySourceTextsCompanion({
    this.sourceId = const Value.absent(),
    this.titleMarkup = const Value.absent(),
    this.dateLabel = const Value.absent(),
    this.contentLabel = const Value.absent(),
    this.materialText = const Value.absent(),
    this.textStyleText = const Value.absent(),
    this.foundText = const Value.absent(),
    this.classificationText = const Value.absent(),
    this.currentLocationText = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PrimarySourceTextsCompanion.insert({
    required String sourceId,
    required String titleMarkup,
    required String dateLabel,
    required String contentLabel,
    required String materialText,
    required String textStyleText,
    required String foundText,
    required String classificationText,
    required String currentLocationText,
    this.rowid = const Value.absent(),
  }) : sourceId = Value(sourceId),
       titleMarkup = Value(titleMarkup),
       dateLabel = Value(dateLabel),
       contentLabel = Value(contentLabel),
       materialText = Value(materialText),
       textStyleText = Value(textStyleText),
       foundText = Value(foundText),
       classificationText = Value(classificationText),
       currentLocationText = Value(currentLocationText);
  static Insertable<PrimarySourceText> custom({
    Expression<String>? sourceId,
    Expression<String>? titleMarkup,
    Expression<String>? dateLabel,
    Expression<String>? contentLabel,
    Expression<String>? materialText,
    Expression<String>? textStyleText,
    Expression<String>? foundText,
    Expression<String>? classificationText,
    Expression<String>? currentLocationText,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (sourceId != null) 'source_id': sourceId,
      if (titleMarkup != null) 'title_markup': titleMarkup,
      if (dateLabel != null) 'date_label': dateLabel,
      if (contentLabel != null) 'content_label': contentLabel,
      if (materialText != null) 'material_text': materialText,
      if (textStyleText != null) 'text_style_text': textStyleText,
      if (foundText != null) 'found_text': foundText,
      if (classificationText != null) 'classification_text': classificationText,
      if (currentLocationText != null)
        'current_location_text': currentLocationText,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PrimarySourceTextsCompanion copyWith({
    Value<String>? sourceId,
    Value<String>? titleMarkup,
    Value<String>? dateLabel,
    Value<String>? contentLabel,
    Value<String>? materialText,
    Value<String>? textStyleText,
    Value<String>? foundText,
    Value<String>? classificationText,
    Value<String>? currentLocationText,
    Value<int>? rowid,
  }) {
    return PrimarySourceTextsCompanion(
      sourceId: sourceId ?? this.sourceId,
      titleMarkup: titleMarkup ?? this.titleMarkup,
      dateLabel: dateLabel ?? this.dateLabel,
      contentLabel: contentLabel ?? this.contentLabel,
      materialText: materialText ?? this.materialText,
      textStyleText: textStyleText ?? this.textStyleText,
      foundText: foundText ?? this.foundText,
      classificationText: classificationText ?? this.classificationText,
      currentLocationText: currentLocationText ?? this.currentLocationText,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (sourceId.present) {
      map['source_id'] = Variable<String>(sourceId.value);
    }
    if (titleMarkup.present) {
      map['title_markup'] = Variable<String>(titleMarkup.value);
    }
    if (dateLabel.present) {
      map['date_label'] = Variable<String>(dateLabel.value);
    }
    if (contentLabel.present) {
      map['content_label'] = Variable<String>(contentLabel.value);
    }
    if (materialText.present) {
      map['material_text'] = Variable<String>(materialText.value);
    }
    if (textStyleText.present) {
      map['text_style_text'] = Variable<String>(textStyleText.value);
    }
    if (foundText.present) {
      map['found_text'] = Variable<String>(foundText.value);
    }
    if (classificationText.present) {
      map['classification_text'] = Variable<String>(classificationText.value);
    }
    if (currentLocationText.present) {
      map['current_location_text'] = Variable<String>(
        currentLocationText.value,
      );
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceTextsCompanion(')
          ..write('sourceId: $sourceId, ')
          ..write('titleMarkup: $titleMarkup, ')
          ..write('dateLabel: $dateLabel, ')
          ..write('contentLabel: $contentLabel, ')
          ..write('materialText: $materialText, ')
          ..write('textStyleText: $textStyleText, ')
          ..write('foundText: $foundText, ')
          ..write('classificationText: $classificationText, ')
          ..write('currentLocationText: $currentLocationText, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PrimarySourceLinkTextsTable extends PrimarySourceLinkTexts
    with TableInfo<$PrimarySourceLinkTextsTable, PrimarySourceLinkText> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PrimarySourceLinkTextsTable(this.attachedDatabase, [this._alias]);
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
  static const VerificationMeta _titleMeta = const VerificationMeta('title');
  @override
  late final GeneratedColumn<String> title = GeneratedColumn<String>(
    'title',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [sourceId, linkId, title];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'primary_source_link_texts';
  @override
  VerificationContext validateIntegrity(
    Insertable<PrimarySourceLinkText> instance, {
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
    if (data.containsKey('title')) {
      context.handle(
        _titleMeta,
        title.isAcceptableOrUnknown(data['title']!, _titleMeta),
      );
    } else if (isInserting) {
      context.missing(_titleMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {sourceId, linkId};
  @override
  PrimarySourceLinkText map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return PrimarySourceLinkText(
      sourceId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}source_id'],
      )!,
      linkId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}link_id'],
      )!,
      title: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}title'],
      )!,
    );
  }

  @override
  $PrimarySourceLinkTextsTable createAlias(String alias) {
    return $PrimarySourceLinkTextsTable(attachedDatabase, alias);
  }
}

class PrimarySourceLinkText extends DataClass
    implements Insertable<PrimarySourceLinkText> {
  final String sourceId;
  final String linkId;
  final String title;
  const PrimarySourceLinkText({
    required this.sourceId,
    required this.linkId,
    required this.title,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['source_id'] = Variable<String>(sourceId);
    map['link_id'] = Variable<String>(linkId);
    map['title'] = Variable<String>(title);
    return map;
  }

  PrimarySourceLinkTextsCompanion toCompanion(bool nullToAbsent) {
    return PrimarySourceLinkTextsCompanion(
      sourceId: Value(sourceId),
      linkId: Value(linkId),
      title: Value(title),
    );
  }

  factory PrimarySourceLinkText.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return PrimarySourceLinkText(
      sourceId: serializer.fromJson<String>(json['sourceId']),
      linkId: serializer.fromJson<String>(json['linkId']),
      title: serializer.fromJson<String>(json['title']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'sourceId': serializer.toJson<String>(sourceId),
      'linkId': serializer.toJson<String>(linkId),
      'title': serializer.toJson<String>(title),
    };
  }

  PrimarySourceLinkText copyWith({
    String? sourceId,
    String? linkId,
    String? title,
  }) => PrimarySourceLinkText(
    sourceId: sourceId ?? this.sourceId,
    linkId: linkId ?? this.linkId,
    title: title ?? this.title,
  );
  PrimarySourceLinkText copyWithCompanion(
    PrimarySourceLinkTextsCompanion data,
  ) {
    return PrimarySourceLinkText(
      sourceId: data.sourceId.present ? data.sourceId.value : this.sourceId,
      linkId: data.linkId.present ? data.linkId.value : this.linkId,
      title: data.title.present ? data.title.value : this.title,
    );
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceLinkText(')
          ..write('sourceId: $sourceId, ')
          ..write('linkId: $linkId, ')
          ..write('title: $title')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(sourceId, linkId, title);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is PrimarySourceLinkText &&
          other.sourceId == this.sourceId &&
          other.linkId == this.linkId &&
          other.title == this.title);
}

class PrimarySourceLinkTextsCompanion
    extends UpdateCompanion<PrimarySourceLinkText> {
  final Value<String> sourceId;
  final Value<String> linkId;
  final Value<String> title;
  final Value<int> rowid;
  const PrimarySourceLinkTextsCompanion({
    this.sourceId = const Value.absent(),
    this.linkId = const Value.absent(),
    this.title = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PrimarySourceLinkTextsCompanion.insert({
    required String sourceId,
    required String linkId,
    required String title,
    this.rowid = const Value.absent(),
  }) : sourceId = Value(sourceId),
       linkId = Value(linkId),
       title = Value(title);
  static Insertable<PrimarySourceLinkText> custom({
    Expression<String>? sourceId,
    Expression<String>? linkId,
    Expression<String>? title,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (sourceId != null) 'source_id': sourceId,
      if (linkId != null) 'link_id': linkId,
      if (title != null) 'title': title,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PrimarySourceLinkTextsCompanion copyWith({
    Value<String>? sourceId,
    Value<String>? linkId,
    Value<String>? title,
    Value<int>? rowid,
  }) {
    return PrimarySourceLinkTextsCompanion(
      sourceId: sourceId ?? this.sourceId,
      linkId: linkId ?? this.linkId,
      title: title ?? this.title,
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
    if (title.present) {
      map['title'] = Variable<String>(title.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PrimarySourceLinkTextsCompanion(')
          ..write('sourceId: $sourceId, ')
          ..write('linkId: $linkId, ')
          ..write('title: $title, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$LocalizedDB extends GeneratedDatabase {
  _$LocalizedDB(QueryExecutor e) : super(e);
  $LocalizedDBManager get managers => $LocalizedDBManager(this);
  late final $GreekDescsTable greekDescs = $GreekDescsTable(this);
  late final $ArticlesTable articles = $ArticlesTable(this);
  late final $PrimarySourceTextsTable primarySourceTexts =
      $PrimarySourceTextsTable(this);
  late final $PrimarySourceLinkTextsTable primarySourceLinkTexts =
      $PrimarySourceLinkTextsTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    greekDescs,
    articles,
    primarySourceTexts,
    primarySourceLinkTexts,
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
typedef $$ArticlesTableCreateCompanionBuilder =
    ArticlesCompanion Function({
      required String route,
      required String name,
      required String description,
      required String idIcon,
      Value<int> sortOrder,
      Value<bool> isVisible,
      required String markdown,
      Value<int> rowid,
    });
typedef $$ArticlesTableUpdateCompanionBuilder =
    ArticlesCompanion Function({
      Value<String> route,
      Value<String> name,
      Value<String> description,
      Value<String> idIcon,
      Value<int> sortOrder,
      Value<bool> isVisible,
      Value<String> markdown,
      Value<int> rowid,
    });

class $$ArticlesTableFilterComposer
    extends Composer<_$LocalizedDB, $ArticlesTable> {
  $$ArticlesTableFilterComposer({
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

  ColumnFilters<String> get markdown => $composableBuilder(
    column: $table.markdown,
    builder: (column) => ColumnFilters(column),
  );
}

class $$ArticlesTableOrderingComposer
    extends Composer<_$LocalizedDB, $ArticlesTable> {
  $$ArticlesTableOrderingComposer({
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

  ColumnOrderings<String> get markdown => $composableBuilder(
    column: $table.markdown,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$ArticlesTableAnnotationComposer
    extends Composer<_$LocalizedDB, $ArticlesTable> {
  $$ArticlesTableAnnotationComposer({
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

  GeneratedColumn<String> get markdown =>
      $composableBuilder(column: $table.markdown, builder: (column) => column);
}

class $$ArticlesTableTableManager
    extends
        RootTableManager<
          _$LocalizedDB,
          $ArticlesTable,
          Article,
          $$ArticlesTableFilterComposer,
          $$ArticlesTableOrderingComposer,
          $$ArticlesTableAnnotationComposer,
          $$ArticlesTableCreateCompanionBuilder,
          $$ArticlesTableUpdateCompanionBuilder,
          (Article, BaseReferences<_$LocalizedDB, $ArticlesTable, Article>),
          Article,
          PrefetchHooks Function()
        > {
  $$ArticlesTableTableManager(_$LocalizedDB db, $ArticlesTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ArticlesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ArticlesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ArticlesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> route = const Value.absent(),
                Value<String> name = const Value.absent(),
                Value<String> description = const Value.absent(),
                Value<String> idIcon = const Value.absent(),
                Value<int> sortOrder = const Value.absent(),
                Value<bool> isVisible = const Value.absent(),
                Value<String> markdown = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ArticlesCompanion(
                route: route,
                name: name,
                description: description,
                idIcon: idIcon,
                sortOrder: sortOrder,
                isVisible: isVisible,
                markdown: markdown,
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
                required String markdown,
                Value<int> rowid = const Value.absent(),
              }) => ArticlesCompanion.insert(
                route: route,
                name: name,
                description: description,
                idIcon: idIcon,
                sortOrder: sortOrder,
                isVisible: isVisible,
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

typedef $$ArticlesTableProcessedTableManager =
    ProcessedTableManager<
      _$LocalizedDB,
      $ArticlesTable,
      Article,
      $$ArticlesTableFilterComposer,
      $$ArticlesTableOrderingComposer,
      $$ArticlesTableAnnotationComposer,
      $$ArticlesTableCreateCompanionBuilder,
      $$ArticlesTableUpdateCompanionBuilder,
      (Article, BaseReferences<_$LocalizedDB, $ArticlesTable, Article>),
      Article,
      PrefetchHooks Function()
    >;
typedef $$PrimarySourceTextsTableCreateCompanionBuilder =
    PrimarySourceTextsCompanion Function({
      required String sourceId,
      required String titleMarkup,
      required String dateLabel,
      required String contentLabel,
      required String materialText,
      required String textStyleText,
      required String foundText,
      required String classificationText,
      required String currentLocationText,
      Value<int> rowid,
    });
typedef $$PrimarySourceTextsTableUpdateCompanionBuilder =
    PrimarySourceTextsCompanion Function({
      Value<String> sourceId,
      Value<String> titleMarkup,
      Value<String> dateLabel,
      Value<String> contentLabel,
      Value<String> materialText,
      Value<String> textStyleText,
      Value<String> foundText,
      Value<String> classificationText,
      Value<String> currentLocationText,
      Value<int> rowid,
    });

class $$PrimarySourceTextsTableFilterComposer
    extends Composer<_$LocalizedDB, $PrimarySourceTextsTable> {
  $$PrimarySourceTextsTableFilterComposer({
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

  ColumnFilters<String> get titleMarkup => $composableBuilder(
    column: $table.titleMarkup,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get dateLabel => $composableBuilder(
    column: $table.dateLabel,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get contentLabel => $composableBuilder(
    column: $table.contentLabel,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get materialText => $composableBuilder(
    column: $table.materialText,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get textStyleText => $composableBuilder(
    column: $table.textStyleText,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get foundText => $composableBuilder(
    column: $table.foundText,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get classificationText => $composableBuilder(
    column: $table.classificationText,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get currentLocationText => $composableBuilder(
    column: $table.currentLocationText,
    builder: (column) => ColumnFilters(column),
  );
}

class $$PrimarySourceTextsTableOrderingComposer
    extends Composer<_$LocalizedDB, $PrimarySourceTextsTable> {
  $$PrimarySourceTextsTableOrderingComposer({
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

  ColumnOrderings<String> get titleMarkup => $composableBuilder(
    column: $table.titleMarkup,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get dateLabel => $composableBuilder(
    column: $table.dateLabel,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get contentLabel => $composableBuilder(
    column: $table.contentLabel,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get materialText => $composableBuilder(
    column: $table.materialText,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get textStyleText => $composableBuilder(
    column: $table.textStyleText,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get foundText => $composableBuilder(
    column: $table.foundText,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get classificationText => $composableBuilder(
    column: $table.classificationText,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get currentLocationText => $composableBuilder(
    column: $table.currentLocationText,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$PrimarySourceTextsTableAnnotationComposer
    extends Composer<_$LocalizedDB, $PrimarySourceTextsTable> {
  $$PrimarySourceTextsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get sourceId =>
      $composableBuilder(column: $table.sourceId, builder: (column) => column);

  GeneratedColumn<String> get titleMarkup => $composableBuilder(
    column: $table.titleMarkup,
    builder: (column) => column,
  );

  GeneratedColumn<String> get dateLabel =>
      $composableBuilder(column: $table.dateLabel, builder: (column) => column);

  GeneratedColumn<String> get contentLabel => $composableBuilder(
    column: $table.contentLabel,
    builder: (column) => column,
  );

  GeneratedColumn<String> get materialText => $composableBuilder(
    column: $table.materialText,
    builder: (column) => column,
  );

  GeneratedColumn<String> get textStyleText => $composableBuilder(
    column: $table.textStyleText,
    builder: (column) => column,
  );

  GeneratedColumn<String> get foundText =>
      $composableBuilder(column: $table.foundText, builder: (column) => column);

  GeneratedColumn<String> get classificationText => $composableBuilder(
    column: $table.classificationText,
    builder: (column) => column,
  );

  GeneratedColumn<String> get currentLocationText => $composableBuilder(
    column: $table.currentLocationText,
    builder: (column) => column,
  );
}

class $$PrimarySourceTextsTableTableManager
    extends
        RootTableManager<
          _$LocalizedDB,
          $PrimarySourceTextsTable,
          PrimarySourceText,
          $$PrimarySourceTextsTableFilterComposer,
          $$PrimarySourceTextsTableOrderingComposer,
          $$PrimarySourceTextsTableAnnotationComposer,
          $$PrimarySourceTextsTableCreateCompanionBuilder,
          $$PrimarySourceTextsTableUpdateCompanionBuilder,
          (
            PrimarySourceText,
            BaseReferences<
              _$LocalizedDB,
              $PrimarySourceTextsTable,
              PrimarySourceText
            >,
          ),
          PrimarySourceText,
          PrefetchHooks Function()
        > {
  $$PrimarySourceTextsTableTableManager(
    _$LocalizedDB db,
    $PrimarySourceTextsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PrimarySourceTextsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PrimarySourceTextsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PrimarySourceTextsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> sourceId = const Value.absent(),
                Value<String> titleMarkup = const Value.absent(),
                Value<String> dateLabel = const Value.absent(),
                Value<String> contentLabel = const Value.absent(),
                Value<String> materialText = const Value.absent(),
                Value<String> textStyleText = const Value.absent(),
                Value<String> foundText = const Value.absent(),
                Value<String> classificationText = const Value.absent(),
                Value<String> currentLocationText = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceTextsCompanion(
                sourceId: sourceId,
                titleMarkup: titleMarkup,
                dateLabel: dateLabel,
                contentLabel: contentLabel,
                materialText: materialText,
                textStyleText: textStyleText,
                foundText: foundText,
                classificationText: classificationText,
                currentLocationText: currentLocationText,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String sourceId,
                required String titleMarkup,
                required String dateLabel,
                required String contentLabel,
                required String materialText,
                required String textStyleText,
                required String foundText,
                required String classificationText,
                required String currentLocationText,
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceTextsCompanion.insert(
                sourceId: sourceId,
                titleMarkup: titleMarkup,
                dateLabel: dateLabel,
                contentLabel: contentLabel,
                materialText: materialText,
                textStyleText: textStyleText,
                foundText: foundText,
                classificationText: classificationText,
                currentLocationText: currentLocationText,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$PrimarySourceTextsTableProcessedTableManager =
    ProcessedTableManager<
      _$LocalizedDB,
      $PrimarySourceTextsTable,
      PrimarySourceText,
      $$PrimarySourceTextsTableFilterComposer,
      $$PrimarySourceTextsTableOrderingComposer,
      $$PrimarySourceTextsTableAnnotationComposer,
      $$PrimarySourceTextsTableCreateCompanionBuilder,
      $$PrimarySourceTextsTableUpdateCompanionBuilder,
      (
        PrimarySourceText,
        BaseReferences<
          _$LocalizedDB,
          $PrimarySourceTextsTable,
          PrimarySourceText
        >,
      ),
      PrimarySourceText,
      PrefetchHooks Function()
    >;
typedef $$PrimarySourceLinkTextsTableCreateCompanionBuilder =
    PrimarySourceLinkTextsCompanion Function({
      required String sourceId,
      required String linkId,
      required String title,
      Value<int> rowid,
    });
typedef $$PrimarySourceLinkTextsTableUpdateCompanionBuilder =
    PrimarySourceLinkTextsCompanion Function({
      Value<String> sourceId,
      Value<String> linkId,
      Value<String> title,
      Value<int> rowid,
    });

class $$PrimarySourceLinkTextsTableFilterComposer
    extends Composer<_$LocalizedDB, $PrimarySourceLinkTextsTable> {
  $$PrimarySourceLinkTextsTableFilterComposer({
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

  ColumnFilters<String> get title => $composableBuilder(
    column: $table.title,
    builder: (column) => ColumnFilters(column),
  );
}

class $$PrimarySourceLinkTextsTableOrderingComposer
    extends Composer<_$LocalizedDB, $PrimarySourceLinkTextsTable> {
  $$PrimarySourceLinkTextsTableOrderingComposer({
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

  ColumnOrderings<String> get title => $composableBuilder(
    column: $table.title,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$PrimarySourceLinkTextsTableAnnotationComposer
    extends Composer<_$LocalizedDB, $PrimarySourceLinkTextsTable> {
  $$PrimarySourceLinkTextsTableAnnotationComposer({
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

  GeneratedColumn<String> get title =>
      $composableBuilder(column: $table.title, builder: (column) => column);
}

class $$PrimarySourceLinkTextsTableTableManager
    extends
        RootTableManager<
          _$LocalizedDB,
          $PrimarySourceLinkTextsTable,
          PrimarySourceLinkText,
          $$PrimarySourceLinkTextsTableFilterComposer,
          $$PrimarySourceLinkTextsTableOrderingComposer,
          $$PrimarySourceLinkTextsTableAnnotationComposer,
          $$PrimarySourceLinkTextsTableCreateCompanionBuilder,
          $$PrimarySourceLinkTextsTableUpdateCompanionBuilder,
          (
            PrimarySourceLinkText,
            BaseReferences<
              _$LocalizedDB,
              $PrimarySourceLinkTextsTable,
              PrimarySourceLinkText
            >,
          ),
          PrimarySourceLinkText,
          PrefetchHooks Function()
        > {
  $$PrimarySourceLinkTextsTableTableManager(
    _$LocalizedDB db,
    $PrimarySourceLinkTextsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PrimarySourceLinkTextsTableFilterComposer(
                $db: db,
                $table: table,
              ),
          createOrderingComposer: () =>
              $$PrimarySourceLinkTextsTableOrderingComposer(
                $db: db,
                $table: table,
              ),
          createComputedFieldComposer: () =>
              $$PrimarySourceLinkTextsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> sourceId = const Value.absent(),
                Value<String> linkId = const Value.absent(),
                Value<String> title = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceLinkTextsCompanion(
                sourceId: sourceId,
                linkId: linkId,
                title: title,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String sourceId,
                required String linkId,
                required String title,
                Value<int> rowid = const Value.absent(),
              }) => PrimarySourceLinkTextsCompanion.insert(
                sourceId: sourceId,
                linkId: linkId,
                title: title,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$PrimarySourceLinkTextsTableProcessedTableManager =
    ProcessedTableManager<
      _$LocalizedDB,
      $PrimarySourceLinkTextsTable,
      PrimarySourceLinkText,
      $$PrimarySourceLinkTextsTableFilterComposer,
      $$PrimarySourceLinkTextsTableOrderingComposer,
      $$PrimarySourceLinkTextsTableAnnotationComposer,
      $$PrimarySourceLinkTextsTableCreateCompanionBuilder,
      $$PrimarySourceLinkTextsTableUpdateCompanionBuilder,
      (
        PrimarySourceLinkText,
        BaseReferences<
          _$LocalizedDB,
          $PrimarySourceLinkTextsTable,
          PrimarySourceLinkText
        >,
      ),
      PrimarySourceLinkText,
      PrefetchHooks Function()
    >;

class $LocalizedDBManager {
  final _$LocalizedDB _db;
  $LocalizedDBManager(this._db);
  $$GreekDescsTableTableManager get greekDescs =>
      $$GreekDescsTableTableManager(_db, _db.greekDescs);
  $$ArticlesTableTableManager get articles =>
      $$ArticlesTableTableManager(_db, _db.articles);
  $$PrimarySourceTextsTableTableManager get primarySourceTexts =>
      $$PrimarySourceTextsTableTableManager(_db, _db.primarySourceTexts);
  $$PrimarySourceLinkTextsTableTableManager get primarySourceLinkTexts =>
      $$PrimarySourceLinkTextsTableTableManager(
        _db,
        _db.primarySourceLinkTexts,
      );
}
