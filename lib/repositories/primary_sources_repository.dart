import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import '../models/primary_source.dart';

class PrimarySourcesRepository {
  List<PrimarySource> getPrimarySources(BuildContext context) {
    AppLocalizations loc = AppLocalizations.of(context)!;
    final sources = [
      PrimarySource(
          title: loc.papyrus_18_title,
          date: loc.papyrus_18_date,
          content: loc.papyrus_18_content,
          features: loc.papyrus_18_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Papyrus_18',
          preview: 'assets/images/Resources/10018/preview.png',
          images: ['assets/images/Resources/10018/P18.jpg']),
      PrimarySource(
          title: loc.papyrus_24_title,
          date: loc.papyrus_24_date,
          content: loc.papyrus_24_content,
          features: loc.papyrus_24_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Papyrus_24',
          preview: 'assets/images/Resources/10024/preview.png',
          images: [
            'assets/images/Resources/10024/P24_A.jpg',
            'assets/images/Resources/10024/P24_B.jpg'
          ]),
      PrimarySource(
          title: loc.papyrus_43_title,
          date: loc.papyrus_43_date,
          content: loc.papyrus_43_content,
          features: loc.papyrus_43_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Papyrus_43',
          preview: 'assets/images/Resources/10043/preview.png',
          images: [
            'assets/images/Resources/10043/P43_A.jpg',
            'assets/images/Resources/10043/P43_B.jpg'
          ]),
      PrimarySource(
          title: loc.papyrus_47_title,
          date: loc.papyrus_47_date,
          content: loc.papyrus_47_content,
          features: loc.papyrus_47_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Papyrus_47',
          preview: 'assets/images/Resources/10047/preview.png',
          images: [
            'assets/images/Resources/10047/T0004403.jpg',
            'assets/images/Resources/10047/T0004404a.jpg',
            'assets/images/Resources/10047/T0004405b_a.jpg',
            'assets/images/Resources/10047/T0005405.jpg',
            'assets/images/Resources/10047/T0005406.jpg',
            'assets/images/Resources/10047/T0005407.jpg',
            'assets/images/Resources/10047/T0005408.jpg',
            'assets/images/Resources/10047/T0005409.jpg',
            'assets/images/Resources/10047/T0005410.jpg',
            'assets/images/Resources/10047/T0005411.jpg',
            'assets/images/Resources/10047/T0005412.jpg',
            'assets/images/Resources/10047/T0005413.jpg',
            'assets/images/Resources/10047/T0005416.jpg',
            'assets/images/Resources/10047/T0005417.jpg',
            'assets/images/Resources/10047/T0005418.jpg',
            'assets/images/Resources/10047/T0005419.jpg',
            'assets/images/Resources/10047/T0005420.jpg',
            'assets/images/Resources/10047/T0005421.jpg',
            'assets/images/Resources/10047/T0005494.jpg',
            'assets/images/Resources/10047/T0005495.jpg',
          ]),
      PrimarySource(
          title: loc.papyrus_85_title,
          date: loc.papyrus_85_date,
          content: loc.papyrus_85_content,
          features: loc.papyrus_85_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Papyrus_85',
          preview: 'assets/images/Resources/10085/preview.png',
          images: [
            'assets/images/Resources/10085/10085x00010Xa_INTF.jpg',
            'assets/images/Resources/10085/10085x00020Xa_INTF.jpg'
          ]),
      PrimarySource(
          title: loc.papyrus_98_title,
          date: loc.papyrus_98_date,
          content: loc.papyrus_98_content,
          features: loc.papyrus_98_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Papyrus_98',
          preview: 'assets/images/Resources/10098/preview.png',
          images: [
            'assets/images/Resources/10098/P98.jpg',
          ]),
      PrimarySource(
          title: loc.papyrus_115_title,
          date: loc.papyrus_115_date,
          content: loc.papyrus_115_content,
          features: loc.papyrus_115_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Papyrus_115',
          preview: 'assets/images/Resources/10115/preview.png',
          images: [
            'assets/images/Resources/10115/10115x00020XX_INTF.jpg',
            'assets/images/Resources/10115/10115x00040XX_INTF.jpg',
          ]),
    ];

    return sources;
  }
}
