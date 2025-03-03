import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import '../models/primary_source.dart';

class PrimarySourcesRepository {
  List<PrimarySource> getFullPrimarySources(BuildContext context) {
    AppLocalizations loc = AppLocalizations.of(context)!;
    final sources = [
      PrimarySource(
          title: loc.uncial_01_title,
          date: loc.uncial_01_date,
          content: loc.uncial_01_content,
          features: loc.uncial_01_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Codex_Sinaiticus',
          preview: 'assets/images/Resources/20001/preview.png',
          images: [
            'assets/images/Resources/20001/20001_02520_Q89_1v_B678_p.jpg',
            'assets/images/Resources/20001/20001_02530_Q89_2r_B679_p.jpg',
            'assets/images/Resources/20001/20001_02540_Q89_2v_B680_p.jpg',
            'assets/images/Resources/20001/20001_02550_Q89_3r_B681_p.jpg',
            'assets/images/Resources/20001/20001_02560_Q89_3v_B682_p.jpg',
            'assets/images/Resources/20001/20001_02570_Q89_4r_B683_p.jpg',
            'assets/images/Resources/20001/20001_02580_Q89_4v_B684_p.jpg',
            'assets/images/Resources/20001/20001_02590_Q89_5r_B685_p.jpg',
            'assets/images/Resources/20001/20001_02600_Q89_5v_B686_p.jpg',
            'assets/images/Resources/20001/20001_02610_Q89_6r_B687_p.jpg',
            'assets/images/Resources/20001/20001_02620_Q89_6v_B688_p.jpg',
            'assets/images/Resources/20001/20001_02630_Q89_7r_B689_p.jpg',
            'assets/images/Resources/20001/20001_02640_Q89_7v_B690_p.jpg',
            'assets/images/Resources/20001/20001_02650_Q89_8r_B691_p.jpg',
            'assets/images/Resources/20001/20001_02660_Q89_8v_B692_p.jpg',
            'assets/images/Resources/20001/20001_02670_Q90_1r_B693_p.jpg',
            'assets/images/Resources/20001/20001_02680_Q90_1v_B694_p.jpg',
            'assets/images/Resources/20001/20001_02690_Q90_2r_B695_p.jpg',
          ]),
      PrimarySource(
          title: loc.uncial_02_title,
          date: loc.uncial_02_date,
          content: loc.uncial_02_content,
          features: loc.uncial_02_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Codex_Alexandrinus',
          preview: 'assets/images/Resources/20002/preview.png',
          images: [
            'assets/images/Resources/20002/GA_02_0128a.jpg',
            'assets/images/Resources/20002/GA_02_0128b.jpg',
            'assets/images/Resources/20002/GA_02_0129a.jpg',
            'assets/images/Resources/20002/GA_02_0129b.jpg',
            'assets/images/Resources/20002/GA_02_0130a.jpg',
            'assets/images/Resources/20002/GA_02_0130b.jpg',
            'assets/images/Resources/20002/GA_02_0131a.jpg',
            'assets/images/Resources/20002/GA_02_0131b.jpg',
            'assets/images/Resources/20002/GA_02_0132a.jpg',
            'assets/images/Resources/20002/GA_02_0132b.jpg',
            'assets/images/Resources/20002/GA_02_0133a.jpg',
            'assets/images/Resources/20002/GA_02_0133b.jpg',
            'assets/images/Resources/20002/GA_02_0134a.jpg',
            'assets/images/Resources/20002/GA_02_0134b.jpg',
            'assets/images/Resources/20002/GA_02_0135a.jpg',
            'assets/images/Resources/20002/GA_02_0135b.jpg',
            'assets/images/Resources/20002/GA_02_0136a.jpg',
            'assets/images/Resources/20002/GA_02_0136b.jpg',
          ]),
      PrimarySource(
          title: loc.uncial_46_title,
          date: loc.uncial_46_date,
          content: loc.uncial_46_content,
          features: loc.uncial_46_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Codex_Vaticanus_2066',
          preview: 'assets/images/Resources/20046/preview.png',
          images: [
            'assets/images/Resources/20046/Vat.gr.2066_0519_fa_0259r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0520_fa_0259v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0521_fa_0260r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0522_fa_0260v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0523_fa_0261r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0524_fa_0261v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0525_fa_0262r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0526_fa_0262v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0527_fa_0263r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0528_fa_0263v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0529_fa_0263r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0530_fa_0263v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0531_fa_0264r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0532_fa_0264v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0533_fa_0265r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0534_fa_0265v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0535_fa_0266r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0536_fa_0266v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0537_fa_0267r_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0538_fa_0267v_m.jpg',
            'assets/images/Resources/20046/Vat.gr.2066_0539_fa_0268r_m.jpg',
          ])
    ];
    return sources;
  }

  List<PrimarySource> getSignificantPrimarySources(BuildContext context) {
    AppLocalizations loc = AppLocalizations.of(context)!;
    final sources = [
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
      PrimarySource(
          title: loc.uncial_04_title,
          date: loc.uncial_04_date,
          content: loc.uncial_04_content,
          features: loc.uncial_04_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Codex_Ephraemi_Rescriptus',
          preview: 'assets/images/Resources/20004/preview.png',
          images: [
            'assets/images/Resources/20004/20004_27_27.01.02-17_f197r.jpeg',
            'assets/images/Resources/20004/20004_27_27.01.17-02.13_f197v.jpeg',
            'assets/images/Resources/20004/20004_27_27.02.13-03.03_f120r.jpeg',
            'assets/images/Resources/20004/20004_27_27.03.03-19_f120v.jpeg',
            'assets/images/Resources/20004/20004_27_27.05.14-06.15_f128r.jpeg',
            'assets/images/Resources/20004/20004_27_27.06.15-07.14_f128v.jpeg',
            'assets/images/Resources/20004/20004_27_27.09.17-10.08_f073v.jpeg',
            'assets/images/Resources/20004/20004_27_27.10.09-11.12_f073r.jpeg',
            'assets/images/Resources/20004/20004_27_27.11.12-12.06_f187r.jpeg',
            'assets/images/Resources/20004/20004_27_27.12.07-13.03_f187v.jpeg',
            'assets/images/Resources/20004/20004_27_27.13.03-14.01_f192r.jpeg',
            'assets/images/Resources/20004/20004_27_27.14.01-14_f192v.jpeg',
            'assets/images/Resources/20004/20004_27_27.14.14-15.07_f066v.jpeg',
            'assets/images/Resources/20004/20004_27_27.15.07-16.13_f066r.jpeg',
            'assets/images/Resources/20004/20004_27_27.18.02-15_f123r.jpeg',
            'assets/images/Resources/20004/20004_27_27.18.15-19.05_f123v.jpeg',
          ]),
      PrimarySource(
          title: loc.uncial_25_title,
          date: loc.uncial_25_date,
          content: loc.uncial_25_content,
          features: loc.uncial_25_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Codex_Porphyrianus',
          preview: 'assets/images/Resources/20025/preview.png',
          images: []),
      PrimarySource(
          title: loc.uncial_51_title,
          date: loc.uncial_51_date,
          content: loc.uncial_51_content,
          features: loc.uncial_51_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Uncial_051',
          preview: 'assets/images/Resources/20051/preview.png',
          images: [
            'assets/images/Resources/20051/preview.jpg',
          ])
    ];
    return sources;
  }

  List<PrimarySource> getFragmentsPrimarySources(BuildContext context) {
    AppLocalizations loc = AppLocalizations.of(context)!;
    final sources = [
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
          title: loc.uncial_169_title,
          date: loc.uncial_169_date,
          content: loc.uncial_169_content,
          features: loc.uncial_169_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Uncial_0169',
          preview: 'assets/images/Resources/20169/preview.png',
          images: [
            'assets/images/Resources/20169/20169x00010.jpg',
            'assets/images/Resources/20169/20169x00020.jpg',
          ]),
      PrimarySource(
          title: loc.uncial_207_title,
          date: loc.uncial_207_date,
          content: loc.uncial_207_content,
          features: loc.uncial_207_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Uncial_0207',
          preview: 'assets/images/Resources/20207/preview.png',
          images: [
            'assets/images/Resources/20207/20207x00010Xa.jpg',
            'assets/images/Resources/20207/20207x00020Xa.jpg',
          ]),
      PrimarySource(
          title: loc.uncial_308_title,
          date: loc.uncial_308_date,
          content: loc.uncial_308_content,
          features: loc.uncial_308_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Uncial_0308',
          preview: 'assets/images/Resources/20308/preview.png',
          images: [
            'assets/images/Resources/20308/Uncial_0308_POxy_4500_recto.jpg',
            'assets/images/Resources/20308/Uncial_0308_hair_side.jpg',
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
          title: loc.uncial_163_title,
          date: loc.uncial_163_date,
          content: loc.uncial_163_content,
          features: loc.uncial_163_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Uncial_0163',
          preview: 'assets/images/Resources/20163/preview.png',
          images: [
            'assets/images/Resources/20163/20163_A.jpg',
            'assets/images/Resources/20163/20163_B.jpg',
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
          title: loc.uncial_229_title,
          date: loc.uncial_229_date,
          content: loc.uncial_229_content,
          features: loc.uncial_229_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Uncial_0229',
          preview: 'assets/images/Resources/20229/preview.png',
          images: [
            'assets/images/Resources/20229/PSI_XIII_1296_a_r.jpg',
            'assets/images/Resources/20229/PSI_XIII_1296_a_v.jpg',
            'assets/images/Resources/20229/PSI_XIII_1296_b_r.jpg',
            'assets/images/Resources/20229/PSI_XIII_1296_b_v.jpg',
          ]),
      PrimarySource(
          title: loc.uncial_52_title,
          date: loc.uncial_52_date,
          content: loc.uncial_52_content,
          features: loc.uncial_52_features,
          linkTitle: loc.wikipedia,
          linkUrl: 'https://en.wikipedia.org/wiki/Uncial_052',
          preview: 'assets/images/Resources/20052/preview.png',
          images: [
            'assets/images/Resources/20052/20052x00090XX_INTF.jpg',
          ])
    ];

    return sources;
  }
}
