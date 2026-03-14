class TopicInfo {
  final String name;
  final String idIcon;
  final String description;
  final String route;

  TopicInfo({
    required this.name,
    required this.idIcon,
    required this.description,
    required this.route,
  });

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is TopicInfo &&
            runtimeType == other.runtimeType &&
            name == other.name &&
            idIcon == other.idIcon &&
            description == other.description &&
            route == other.route;
  }

  @override
  int get hashCode => Object.hash(name, idIcon, description, route);
}
