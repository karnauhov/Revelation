import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';

void main() {
  test(
    'initial state uses first page when source has permissions and pages',
    () {
      final source = _buildSource(
        pages: [
          model.Page(name: 'P1', content: 'C1', image: 'p1.png'),
          model.Page(name: 'P2', content: 'C2', image: 'p2.png'),
        ],
        permissionsReceived: true,
      );
      final cubit = PrimarySourceSessionCubit(source: source);
      addTearDown(cubit.close);

      expect(cubit.state.source.id, source.id);
      expect(cubit.state.selectedPage?.name, 'P1');
      expect(cubit.state.imageName, isEmpty);
      expect(cubit.state.isMenuOpen, isFalse);
    },
  );

  test(
    'initial state has null selectedPage when source has no permissions',
    () {
      final source = _buildSource(
        pages: [model.Page(name: 'P1', content: 'C1', image: 'p1.png')],
        permissionsReceived: false,
      );
      final cubit = PrimarySourceSessionCubit(source: source);
      addTearDown(cubit.close);

      expect(cubit.state.selectedPage, isNull);
    },
  );

  test('setters update selectedPage, imageName and menu state', () {
    final page = model.Page(name: 'P2', content: 'C2', image: 'p2.png');
    final source = _buildSource(
      pages: [model.Page(name: 'P1', content: 'C1', image: 'p1.png')],
      permissionsReceived: true,
    );
    final cubit = PrimarySourceSessionCubit(source: source);
    addTearDown(cubit.close);

    cubit.setSelectedPage(page);
    cubit.setImageName('p2.png');
    cubit.setMenuOpen(true);

    expect(cubit.state.selectedPage, page);
    expect(cubit.state.imageName, 'p2.png');
    expect(cubit.state.isMenuOpen, isTrue);
  });
}

PrimarySource _buildSource({
  required List<model.Page> pages,
  required bool permissionsReceived,
}) {
  return PrimarySource(
    id: 'source-1',
    title: 'Source',
    date: '',
    content: '',
    quantity: 0,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    link1Title: '',
    link1Url: '',
    link2Title: '',
    link2Url: '',
    link3Title: '',
    link3Url: '',
    preview: '',
    maxScale: 1,
    isMonochrome: false,
    pages: pages,
    attributes: const [],
    permissionsReceived: permissionsReceived,
  );
}
