import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_state.dart';

void main() {
  test('initial is loading and contains empty topic payload', () {
    final state = TopicContentState.initial();

    expect(state.route, isEmpty);
    expect(state.language, isEmpty);
    expect(state.name, isEmpty);
    expect(state.description, isEmpty);
    expect(state.markdown, isEmpty);
    expect(state.isLoading, isTrue);
    expect(state.failure, isNull);
  });

  test('copyWith updates requested fields and clears failure on demand', () {
    final initial = TopicContentState.initial().copyWith(
      route: 'intro',
      language: 'en',
      name: 'Topic',
      description: 'Description',
      markdown: '# Intro',
      isLoading: false,
      failure: const AppFailure.dataSource('failed'),
    );

    final updated = initial.copyWith(language: 'ru', markdown: '# RU');
    final cleared = updated.copyWith(clearFailure: true);

    expect(updated.route, 'intro');
    expect(updated.language, 'ru');
    expect(updated.markdown, '# RU');
    expect(updated.failure, const AppFailure.dataSource('failed'));
    expect(cleared.failure, isNull);
  });

  test('value equality includes all state fields', () {
    final a = TopicContentState(
      route: 'intro',
      language: 'en',
      name: 'Name',
      description: 'Desc',
      markdown: '# Body',
      isLoading: false,
      failure: const AppFailure.validation('bad'),
    );
    final b = TopicContentState(
      route: 'intro',
      language: 'en',
      name: 'Name',
      description: 'Desc',
      markdown: '# Body',
      isLoading: false,
      failure: const AppFailure.validation('bad'),
    );
    final c = b.copyWith(isLoading: true);

    expect(a, b);
    expect(a.hashCode, b.hashCode);
    expect(a, isNot(c));
  });
}
