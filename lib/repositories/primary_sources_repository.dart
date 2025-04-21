import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/primary_source.dart';

class PrimarySourcesRepository {
  List<PrimarySource> getFullPrimarySources(BuildContext context) {
    AppLocalizations loc = AppLocalizations.of(context)!;
    final sources = [
      PrimarySource(
          title: loc.uncial_01_title,
          date: loc.uncial_01_date,
          content: loc.uncial_01_content,
          quantity: 404,
          material: loc.uncial_01_material,
          textStyle: loc.uncial_01_textStyle,
          found: loc.uncial_01_found,
          classification: loc.uncial_01_classification,
          currentLocation: loc.uncial_01_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Codex_Sinaiticus',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20001',
          link3Title: loc.image_source,
          link3Url:
              "https://ntvmr.uni-muenster.de/manuscript-workspace?docID=20001",
          preview: 'assets/images/Resources/20001/preview.png',
          maxScale: 3,
          pages: [
            model.Page(
                name: "325v",
                content: "1:1-20; 2:1-7",
                image: "primary_sources/20001/20001_02520_Q89_1v_B678_p.jpg"),
            model.Page(
                name: "326r",
                content: "2:7-29; 3:1-5",
                image: "primary_sources/20001/20001_02530_Q89_2r_B679_p.jpg"),
            model.Page(
                name: "326v",
                content: "3:5-22; 4:1-8",
                image: "primary_sources/20001/20001_02540_Q89_2v_B680_p.jpg"),
            model.Page(
                name: "327r",
                content: "4:8-11; 5:1-14; 6:1-6",
                image: "primary_sources/20001/20001_02550_Q89_3r_B681_p.jpg"),
            model.Page(
                name: "327v",
                content: "6:6-17; 7:1-12",
                image: "primary_sources/20001/20001_02560_Q89_3v_B682_p.jpg"),
            model.Page(
                name: "328r",
                content: "7:12-17; 8:1-13; 9:1-5",
                image: "primary_sources/20001/20001_02570_Q89_4r_B683_p.jpg"),
            model.Page(
                name: "328v",
                content: "9:5-21; 10:1-8",
                image: "primary_sources/20001/20001_02580_Q89_4v_B684_p.jpg"),
            model.Page(
                name: "329r",
                content: "10:8-11; 11:1-19",
                image: "primary_sources/20001/20001_02590_Q89_5r_B685_p.jpg"),
            model.Page(
                name: "329v",
                content: "11:19; 12:1-17; 13:1-4",
                image: "primary_sources/20001/20001_02600_Q89_5v_B686_p.jpg"),
            model.Page(
                name: "330r",
                content: "13:4-18; 14:1-9",
                image: "primary_sources/20001/20001_02610_Q89_6r_B687_p.jpg"),
            model.Page(
                name: "330v",
                content: "14:9-20; 15:1-8; 16:1",
                image: "primary_sources/20001/20001_02620_Q89_6v_B688_p.jpg"),
            model.Page(
                name: "331r",
                content: "16:1-21; 17:1-6",
                image: "primary_sources/20001/20001_02630_Q89_7r_B689_p.jpg"),
            model.Page(
                name: "331v",
                content: "17:6-18; 18:1-11",
                image: "primary_sources/20001/20001_02640_Q89_7v_B690_p.jpg"),
            model.Page(
                name: "332r",
                content: "18:11-24; 19:1-9",
                image: "primary_sources/20001/20001_02650_Q89_8r_B691_p.jpg"),
            model.Page(
                name: "332v",
                content: "19:9-21; 20:1-10",
                image: "primary_sources/20001/20001_02660_Q89_8v_B692_p.jpg"),
            model.Page(
                name: "333r",
                content: "20:10-15; 21:1-20",
                image: "primary_sources/20001/20001_02670_Q90_1r_B693_p.jpg"),
            model.Page(
                name: "333v",
                content: "21:20-27; 22:1-19",
                image: "primary_sources/20001/20001_02680_Q90_1v_B694_p.jpg"),
            model.Page(
                name: "334r",
                content: "22:19-21",
                image: "primary_sources/20001/20001_02690_Q90_2r_B695_p.jpg"),
          ],
          attributes: [
            {"text": "📜 The British Library", "url": "https://www.bl.uk"},
          ]),
      PrimarySource(
          title: loc.uncial_02_title,
          date: loc.uncial_02_date,
          content: loc.uncial_02_content,
          quantity: 404,
          material: loc.uncial_02_material,
          textStyle: loc.uncial_02_textStyle,
          found: loc.uncial_02_found,
          classification: loc.uncial_02_classification,
          currentLocation: loc.uncial_02_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Codex_Alexandrinus',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20002',
          link3Title: loc.image_source,
          link3Url: "https://manuscripts.csntm.org/Manuscript/Group/GA_02",
          preview: 'assets/images/Resources/20002/preview.png',
          maxScale: 3,
          pages: [
            model.Page(
                name: "150r",
                content: "1:1-20; 2:1-7",
                image: "primary_sources/20002/GA_02_0128a.jpg"),
            model.Page(
                name: "150v",
                content: "2:8-29; 3:1-5",
                image: "primary_sources/20002/GA_02_0128b.jpg"),
            model.Page(
                name: "151r",
                content: "3:5-22; 4:1-8",
                image: "primary_sources/20002/GA_02_0129a.jpg"),
            model.Page(
                name: "151v",
                content: "4:8-11; 5:1-14; 6:1-7",
                image: "primary_sources/20002/GA_02_0129b.jpg"),
            model.Page(
                name: "152r",
                content: "6:7-17; 7:1-14",
                image: "primary_sources/20002/GA_02_0130a.jpg"),
            model.Page(
                name: "152v",
                content: "7:14-17; 8:1-13; 9:1-6",
                image: "primary_sources/20002/GA_02_0130b.jpg"),
            model.Page(
                name: "153r",
                content: "9:6-21; 10:1-8",
                image: "primary_sources/20002/GA_02_0131a.jpg"),
            model.Page(
                name: "153v",
                content: "10:8-11; 11:1-19",
                image: "primary_sources/20002/GA_02_0131b.jpg"),
            model.Page(
                name: "154r",
                content: "11:19; 12:1-17; 13:1-4",
                image: "primary_sources/20002/GA_02_0132a.jpg"),
            model.Page(
                name: "154v",
                content: "13:4-18; 14:1-7",
                image: "primary_sources/20002/GA_02_0132b.jpg"),
            model.Page(
                name: "155r",
                content: "14:8-20; 15:1-8",
                image: "primary_sources/20002/GA_02_0133a.jpg"),
            model.Page(
                name: "155v",
                content: "15:8; 16:1-21; 17:1-3",
                image: "primary_sources/20002/GA_02_0133b.jpg"),
            model.Page(
                name: "156r",
                content: "17:3-18; 18:1-8",
                image: "primary_sources/20002/GA_02_0134a.jpg"),
            model.Page(
                name: "156v",
                content: "18:9-24; 19:1-7",
                image: "primary_sources/20002/GA_02_0134b.jpg"),
            model.Page(
                name: "157r",
                content: "19:7-21; 20:1-6",
                image: "primary_sources/20002/GA_02_0135a.jpg"),
            model.Page(
                name: "157v",
                content: "20:7-15; 21:1-14",
                image: "primary_sources/20002/GA_02_0135b.jpg"),
            model.Page(
                name: "158r",
                content: "21:14-27; 22:1-14",
                image: "primary_sources/20002/GA_02_0136a.jpg"),
            model.Page(
                name: "158v",
                content: "22:14-21",
                image: "primary_sources/20002/GA_02_0136b.jpg"),
          ],
          attributes: [
            {"text": "📜 The British Library", "url": "https://www.bl.uk"},
          ]),
      PrimarySource(
          title: loc.uncial_46_title,
          date: loc.uncial_46_date,
          content: loc.uncial_46_content,
          quantity: 405,
          material: loc.uncial_46_material,
          textStyle: loc.uncial_46_textStyle,
          found: loc.uncial_46_found,
          classification: loc.uncial_46_classification,
          currentLocation: loc.uncial_46_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Codex_Vaticanus_2066',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20046',
          link3Title: loc.image_source,
          link3Url: "https://digi.vatlib.it/view/MSS_Vat.gr.2066",
          preview: 'assets/images/Resources/20046/preview.png',
          maxScale: 5,
          pages: [
            model.Page(
                name: "249r",
                content: "1:1-11",
                image: "primary_sources/20046/Vat.gr.2066_0519_fa_0259r_l.jpg"),
            model.Page(
                name: "249v",
                content: "1:11-20; 2:1-2",
                image: "primary_sources/20046/Vat.gr.2066_0520_fa_0259v_l.jpg"),
            model.Page(
                name: "250r",
                content: "2:2-14",
                image: "primary_sources/20046/Vat.gr.2066_0521_fa_0260r_l.jpg"),
            model.Page(
                name: "250v",
                content: "2:14-26",
                image: "primary_sources/20046/Vat.gr.2066_0522_fa_0260v_l.jpg"),
            model.Page(
                name: "251r",
                content: "2:26-29; 3:1-9",
                image: "primary_sources/20046/Vat.gr.2066_0523_fa_0261r_l.jpg"),
            model.Page(
                name: "251v",
                content: "3:9-21",
                image: "primary_sources/20046/Vat.gr.2066_0524_fa_0261v_l.jpg"),
            model.Page(
                name: "252r",
                content: "3:21-22; 4:1-10",
                image: "primary_sources/20046/Vat.gr.2066_0525_fa_0262r_l.jpg"),
            model.Page(
                name: "252v",
                content: "4:10-11; 5:1-9",
                image: "primary_sources/20046/Vat.gr.2066_0526_fa_0262v_l.jpg"),
            model.Page(
                name: "253r",
                content: "5:9-14; 6:1-5",
                image: "primary_sources/20046/Vat.gr.2066_0527_fa_0263r_l.jpg"),
            model.Page(
                name: "253v",
                content: "6:5-15",
                image: "primary_sources/20046/Vat.gr.2066_0528_fa_0263v_l.jpg"),
            model.Page(
                name: "254r",
                content: "6:15-17; 7:1-9",
                image: "primary_sources/20046/Vat.gr.2066_0531_fa_0264r_l.jpg"),
            model.Page(
                name: "254v",
                content: "7:9-17",
                image: "primary_sources/20046/Vat.gr.2066_0532_fa_0264v_l.jpg"),
            model.Page(
                name: "255r",
                content: "7:17; 8:1-11",
                image: "primary_sources/20046/Vat.gr.2066_0533_fa_0265r_l.jpg"),
            model.Page(
                name: "255v",
                content: "8:11-13; 9:1-6",
                image: "primary_sources/20046/Vat.gr.2066_0534_fa_0265v_l.jpg"),
            model.Page(
                name: "256r",
                content: "9:6-17",
                image: "primary_sources/20046/Vat.gr.2066_0535_fa_0266r_l.jpg"),
            model.Page(
                name: "256v",
                content: "9:17-21; 10:1-4",
                image: "primary_sources/20046/Vat.gr.2066_0536_fa_0266v_l.jpg"),
            model.Page(
                name: "257r",
                content: "10:4-11; 11:1-2",
                image: "primary_sources/20046/Vat.gr.2066_0537_fa_0267r_l.jpg"),
            model.Page(
                name: "257v",
                content: "11:2-11",
                image: "primary_sources/20046/Vat.gr.2066_0538_fa_0267v_l.jpg"),
            model.Page(
                name: "258r",
                content: "11:11-19; 12:1",
                image: "primary_sources/20046/Vat.gr.2066_0539_fa_0268r_l.jpg"),
            model.Page(
                name: "258v",
                content: "12:1-11",
                image: "primary_sources/20046/Vat.gr.2066_0540_fa_0268v_l.jpg"),
            model.Page(
                name: "259r",
                content: "12:11-18; 13:1-2",
                image: "primary_sources/20046/Vat.gr.2066_0541_fa_0269r_l.jpg"),
            model.Page(
                name: "259v",
                content: "13:2-12",
                image: "primary_sources/20046/Vat.gr.2066_0542_fa_0269v_l.jpg"),
            model.Page(
                name: "260r",
                content: "13:13-18; 14:1-3",
                image: "primary_sources/20046/Vat.gr.2066_0543_fa_0270r_l.jpg"),
            model.Page(
                name: "260v",
                content: "14:3-11",
                image: "primary_sources/20046/Vat.gr.2066_0544_fa_0270v_l.jpg"),
            model.Page(
                name: "261r",
                content: "14:9-20; 15:1",
                image: "primary_sources/20046/Vat.gr.2066_0545_fa_0271r_l.jpg"),
            model.Page(
                name: "261v",
                content: "15:1-8; 16:1-2",
                image: "primary_sources/20046/Vat.gr.2066_0546_fa_0271v_l.jpg"),
            model.Page(
                name: "262r",
                content: "16:2-13",
                image: "primary_sources/20046/Vat.gr.2066_0547_fa_0272r_l.jpg"),
            model.Page(
                name: "262v",
                content: "16:13-21; 17:1",
                image: "primary_sources/20046/Vat.gr.2066_0548_fa_0272v_l.jpg"),
            model.Page(
                name: "263r",
                content: "17:1-12",
                image: "primary_sources/20046/Vat.gr.2066_0551_fa_0273r_l.jpg"),
            model.Page(
                name: "263v",
                content: "17:12-18; 18:1-5",
                image: "primary_sources/20046/Vat.gr.2066_0552_fa_0273v_l.jpg"),
            model.Page(
                name: "264r",
                content: "18:5-15",
                image: "primary_sources/20046/Vat.gr.2066_0555_fa_0274r_l.jpg"),
            model.Page(
                name: "264v",
                content: "18:15-24; 19:1",
                image: "primary_sources/20046/Vat.gr.2066_0556_fa_0274v_l.jpg"),
            model.Page(
                name: "265r",
                content: "19:1-12",
                image: "primary_sources/20046/Vat.gr.2066_0559_fa_0275r_l.jpg"),
            model.Page(
                name: "265v",
                content: "19:12-21",
                image: "primary_sources/20046/Vat.gr.2066_0560_fa_0275v_l.jpg"),
            model.Page(
                name: "266r",
                content: "20:1-11",
                image: "primary_sources/20046/Vat.gr.2066_0561_fa_0276r_l.jpg"),
            model.Page(
                name: "266v",
                content: "20:11-15; 21:1-8",
                image: "primary_sources/20046/Vat.gr.2066_0562_fa_0276v_l.jpg"),
            model.Page(
                name: "267r",
                content: "21:8-20",
                image: "primary_sources/20046/Vat.gr.2066_0565_fa_0277r_l.jpg"),
            model.Page(
                name: "267v",
                content: "21:20-27; 22:1-7",
                image: "primary_sources/20046/Vat.gr.2066_0566_fa_0277v_l.jpg"),
            model.Page(
                name: "268r",
                content: "22:7-21",
                image: "primary_sources/20046/Vat.gr.2066_0567_fa_0278r_l.jpg"),
          ],
          attributes: [
            {
              "text": "📜 © Biblioteca Apostolica Vaticana",
              "url": "https://www.vaticanlibrary.va"
            },
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
          quantity: 127,
          material: loc.papyrus_47_material,
          textStyle: loc.papyrus_47_textStyle,
          found: loc.papyrus_47_found,
          classification: loc.papyrus_47_classification,
          currentLocation: loc.papyrus_47_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Papyrus_47',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=10047',
          link3Title: loc.image_source,
          link3Url: "https://viewer.cbl.ie/viewer/index",
          preview: 'assets/images/Resources/10047/preview.png',
          maxScale: 5,
          pages: [
            model.Page(
                name: "1r",
                content: "9:10-17",
                image: "primary_sources/10047/BP_03_001a_k.jpg"),
            model.Page(
                name: "1v",
                content: "9:17-21; 10:1",
                image: "primary_sources/10047/BP_03_001b_k.jpg"),
            model.Page(
                name: "2r",
                content: "10:2-8",
                image: "primary_sources/10047/BP_03_002a_k.jpg"),
            model.Page(
                name: "2v",
                content: "10:8-11; 11:1-3",
                image: "primary_sources/10047/BP_03_002b_k.jpg"),
            model.Page(
                name: "3r",
                content: "11:5-9",
                image: "primary_sources/10047/BP_03_003a_k.jpg"),
            model.Page(
                name: "3v",
                content: "11:10-13",
                image: "primary_sources/10047/BP_03_003b_k.jpg"),
            model.Page(
                name: "4r",
                content: "11:13-19",
                image: "primary_sources/10047/BP_03_004a_k.jpg"),
            model.Page(
                name: "4v",
                content: "11:19; 12:1-6",
                image: "primary_sources/10047/BP_03_004b_k.jpg"),
            model.Page(
                name: "5r",
                content: "12:6-12",
                image: "primary_sources/10047/BP_03_005a_k.jpg"),
            model.Page(
                name: "5v",
                content: "12:12-18; 13:1",
                image: "primary_sources/10047/BP_03_005b_k.jpg"),
            model.Page(
                name: "6r",
                content: "13:1-8",
                image: "primary_sources/10047/BP_03_006a_k.jpg"),
            model.Page(
                name: "6v",
                content: "13:9-15",
                image: "primary_sources/10047/BP_03_006b_k.jpg"),
            model.Page(
                name: "7r",
                content: "13:16-18; 14:1-4",
                image: "primary_sources/10047/BP_03_007a_k.jpg"),
            model.Page(
                name: "7v",
                content: "14:4-10",
                image: "primary_sources/10047/BP_03_007b_k.jpg"),
            model.Page(
                name: "8r",
                content: "14:10-15",
                image: "primary_sources/10047/BP_03_008a_k.jpg"),
            model.Page(
                name: "8v",
                content: "14:16-20; 15:1-2",
                image: "primary_sources/10047/BP_03_008b_k.jpg"),
            model.Page(
                name: "9r",
                content: "15:2-8; 16:1",
                image: "primary_sources/10047/BP_03_009a_k.jpg"),
            model.Page(
                name: "9v",
                content: "16:1-9",
                image: "primary_sources/10047/BP_03_009b_k.jpg"),
            model.Page(
                name: "10r",
                content: "16:9-15",
                image: "primary_sources/10047/BP_03_010a_k.jpg"),
            model.Page(
                name: "10v",
                content: "16:17-21; 17:1-2",
                image: "primary_sources/10047/BP_03_010b_k.jpg"),
          ],
          attributes: [
            {
              "text": "📜 The Chester Beatty",
              "url": "https://chesterbeatty.ie"
            },
            {
              "text": "✅ Copyright",
              "url": "https://chesterbeatty.ie/about/copyright-2"
            },
          ]),
      PrimarySource(
          title: loc.uncial_04_title,
          date: loc.uncial_04_date,
          content: loc.uncial_04_content,
          quantity: 241,
          material: loc.uncial_04_material,
          textStyle: loc.uncial_04_textStyle,
          found: loc.uncial_04_found,
          classification: loc.uncial_04_classification,
          currentLocation: loc.uncial_04_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Codex_Ephraemi_Rescriptus',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20004',
          link3Title: loc.image_source,
          link3Url:
              "https://gallica.bnf.fr/ark:/12148/btv1b8470433r.r=Codex%20Ephraemi%20Rescriptus?rk=21459;2",
          preview: 'assets/images/Resources/20004/preview.png',
          maxScale: 5,
          pages: [
            model.Page(
                name: "197r",
                content: "1:2-17",
                image: "primary_sources/20004/20004_27_27.01.02-17_f197r.jpeg"),
            model.Page(
                name: "197v",
                content: "1:17-20; 2:1-13",
                image:
                    "primary_sources/20004/20004_27_27.01.17-02.13_f197v.jpeg"),
            model.Page(
                name: "120r",
                content: "2:13-29; 3:1-3",
                image:
                    "primary_sources/20004/20004_27_27.02.13-03.03_f120r.jpeg"),
            model.Page(
                name: "120v",
                content: "3:3-19",
                image: "primary_sources/20004/20004_27_27.03.03-19_f120v.jpeg"),
            model.Page(
                name: "128r",
                content: "5:14; 6:1-15",
                image:
                    "primary_sources/20004/20004_27_27.05.14-06.15_f128r.jpeg"),
            model.Page(
                name: "128v",
                content: "6:15-17; 7:1-14",
                image:
                    "primary_sources/20004/20004_27_27.06.15-07.14_f128v.jpeg"),
            model.Page(
                name: "73v",
                content: "9:17-21; 10:1-8",
                image:
                    "primary_sources/20004/20004_27_27.09.17-10.08_f073v.jpeg"),
            model.Page(
                name: "73r",
                content: "7:17; 8:1-4; 10:9-10; 11:3-12",
                image:
                    "primary_sources/20004/20004_27_27.10.09-11.12_f073r.jpeg"),
            model.Page(
                name: "187r",
                content: "11:12-19; 12:1-6",
                image:
                    "primary_sources/20004/20004_27_27.11.12-12.06_f187r.jpeg"),
            model.Page(
                name: "187v",
                content: "12:7-18; 13:1-3",
                image:
                    "primary_sources/20004/20004_27_27.12.07-13.03_f187v.jpeg"),
            model.Page(
                name: "192r",
                content: "13:3-18; 14:1",
                image:
                    "primary_sources/20004/20004_27_27.13.03-14.01_f192r.jpeg"),
            model.Page(
                name: "192v",
                content: "14:1-13",
                image: "primary_sources/20004/20004_27_27.14.01-14_f192v.jpeg"),
            model.Page(
                name: "66v",
                content: "14:14-20; 15:1-7",
                image:
                    "primary_sources/20004/20004_27_27.14.14-15.07_f066v.jpeg"),
            model.Page(
                name: "66r",
                content: "15:7-8; 16:1-13",
                image:
                    "primary_sources/20004/20004_27_27.15.07-16.13_f066r.jpeg"),
            model.Page(
                name: "123r",
                content: "18:2-15",
                image: "primary_sources/20004/20004_27_27.18.02-15_f123r.jpeg"),
            model.Page(
                name: "123v",
                content: "18:15-24; 19:1-5",
                image:
                    "primary_sources/20004/20004_27_27.18.15-19.05_f123v.jpeg"),
          ],
          attributes: [
            {
              "text": "📜 Bibliothèque nationale de France",
              "url": "https://www.bnf.fr"
            },
            {
              "text": "📷 Source gallica.bnf.fr / BnF",
              "url": "https://gallica.bnf.fr"
            },
            {
              "text": "✅ Conditions",
              "url":
                  "https://gallica.bnf.fr/accueil/fr/html/conditions-dutilisation-de-gallica"
            },
          ]),
      PrimarySource(
          title: loc.uncial_25_title,
          date: loc.uncial_25_date,
          content: loc.uncial_25_content,
          quantity: 373,
          material: loc.uncial_25_material,
          textStyle: loc.uncial_25_textStyle,
          found: loc.uncial_25_found,
          classification: loc.uncial_25_classification,
          currentLocation: loc.uncial_25_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Codex_Porphyrianus',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20025',
          link3Title: "",
          link3Url: "",
          preview: 'assets/images/Resources/20025/preview.png',
          maxScale: 5,
          pages: [],
          attributes: [
            {
              "text": "📜 Российская национальная библиотека",
              "url": "https://nlr.ru"
            },
          ]),
      PrimarySource(
          title: loc.uncial_51_title,
          date: loc.uncial_51_date,
          content: loc.uncial_51_content,
          quantity: 208,
          material: loc.uncial_51_material,
          textStyle: loc.uncial_51_textStyle,
          found: loc.uncial_51_found,
          classification: loc.uncial_51_classification,
          currentLocation: loc.uncial_51_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Uncial_051',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20051',
          link3Title: loc.image_source,
          link3Url: "https://www.loc.gov/resource/amedmonastery.00271051554-ma",
          preview: 'assets/images/Resources/20051/preview.png',
          maxScale: 3,
          pages: [
            model.Page(
                name: "1",
                content: "11:15-18",
                image: "primary_sources/20051/20051_01.jpg"),
            model.Page(
                name: "2",
                content: "11:18-12:1",
                image: "primary_sources/20051/20051_02.jpg"),
            model.Page(
                name: "3",
                content: "12:2",
                image: "primary_sources/20051/20051_03.jpg"),
            model.Page(
                name: "4",
                content: "12:3",
                image: "primary_sources/20051/20051_04.jpg"),
            model.Page(
                name: "5",
                content: "12:4-5",
                image: "primary_sources/20051/20051_05.jpg"),
            model.Page(
                name: "6",
                content: "12:5-6",
                image: "primary_sources/20051/20051_06.jpg"),
            model.Page(
                name: "7",
                content: "12:7-9",
                image: "primary_sources/20051/20051_07.jpg"),
            model.Page(
                name: "8",
                content: "12:9-10",
                image: "primary_sources/20051/20051_08.jpg"),
            model.Page(
                name: "9",
                content: "12:11-14",
                image: "primary_sources/20051/20051_09.jpg"),
            model.Page(
                name: "10",
                content: "12:15-17",
                image: "primary_sources/20051/20051_10.jpg"),
            model.Page(
                name: "11",
                content: "12:18-13:1,3-6",
                image: "primary_sources/20051/20051_11.jpg"),
            model.Page(
                name: "12",
                content: "13:6-10",
                image: "primary_sources/20051/20051_12.jpg"),
            model.Page(
                name: "13",
                content: "13:11-13",
                image: "primary_sources/20051/20051_13.jpg"),
            model.Page(
                name: "14",
                content: "13:13-17",
                image: "primary_sources/20051/20051_14.jpg"),
            model.Page(
                name: "15",
                content: "13:18",
                image: "primary_sources/20051/20051_15.jpg"),
            model.Page(
                name: "16",
                content: "14:1-3",
                image: "primary_sources/20051/20051_16.jpg"),
            model.Page(
                name: "17",
                content: "14:3-5",
                image: "primary_sources/20051/20051_17.jpg"),
            model.Page(
                name: "18",
                content: "14:6-8",
                image: "primary_sources/20051/20051_18.jpg"),
            model.Page(
                name: "19",
                content: "14:9-11",
                image: "primary_sources/20051/20051_19.jpg"),
            model.Page(
                name: "20",
                content: "14:11-13",
                image: "primary_sources/20051/20051_20.jpg"),
            model.Page(
                name: "21",
                content: "14:14-16",
                image: "primary_sources/20051/20051_21.jpg"),
            model.Page(
                name: "22",
                content: "14:17-19",
                image: "primary_sources/20051/20051_22.jpg"),
            model.Page(
                name: "23",
                content: "14:20",
                image: "primary_sources/20051/20051_23.jpg"),
            model.Page(
                name: "24",
                content: "15:1-2",
                image: "primary_sources/20051/20051_24.jpg"),
            model.Page(
                name: "25",
                content: "15:3-6",
                image: "primary_sources/20051/20051_25.jpg"),
            model.Page(
                name: "26",
                content: "15:7-16:1",
                image: "primary_sources/20051/20051_26.jpg"),
            model.Page(
                name: "27",
                content: "16:2-3",
                image: "primary_sources/20051/20051_27.jpg"),
            model.Page(
                name: "28",
                content: "16:4-6",
                image: "primary_sources/20051/20051_28.jpg"),
            model.Page(
                name: "29",
                content: "16:7",
                image: "primary_sources/20051/20051_29.jpg"),
            model.Page(
                name: "30",
                content: "16:8-9",
                image: "primary_sources/20051/20051_30.jpg"),
            model.Page(
                name: "31",
                content: "16:10-11",
                image: "primary_sources/20051/20051_31.jpg"),
            model.Page(
                name: "32",
                content: "-",
                image: "primary_sources/20051/20051_32.jpg"),
            model.Page(
                name: "33",
                content: "16:12",
                image: "primary_sources/20051/20051_33.jpg"),
            model.Page(
                name: "34",
                content: "16:13-16",
                image: "primary_sources/20051/20051_34.jpg"),
            model.Page(
                name: "35",
                content: "16:17-18",
                image: "primary_sources/20051/20051_35.jpg"),
            model.Page(
                name: "36",
                content: "16:19",
                image: "primary_sources/20051/20051_36.jpg"),
            model.Page(
                name: "37",
                content: "16:20-21",
                image: "primary_sources/20051/20051_37.jpg"),
            model.Page(
                name: "38",
                content: "17:1-3",
                image: "primary_sources/20051/20051_38.jpg"),
            model.Page(
                name: "39",
                content: "17:4-5",
                image: "primary_sources/20051/20051_39.jpg"),
            model.Page(
                name: "40",
                content: "17:6-7",
                image: "primary_sources/20051/20051_40.jpg"),
            model.Page(
                name: "41",
                content: "17:8-9",
                image: "primary_sources/20051/20051_41.jpg"),
            model.Page(
                name: "42",
                content: "-",
                image: "primary_sources/20051/20051_42.jpg"),
            model.Page(
                name: "43",
                content: "17:9-11",
                image: "primary_sources/20051/20051_43.jpg"),
            model.Page(
                name: "44",
                content: "17:12-18",
                image: "primary_sources/20051/20051_44.jpg"),
            model.Page(
                name: "45",
                content: "18:1-2",
                image: "primary_sources/20051/20051_45.jpg"),
            model.Page(
                name: "46",
                content: "18:2-6",
                image: "primary_sources/20051/20051_46.jpg"),
            model.Page(
                name: "47",
                content: "18:6-9",
                image: "primary_sources/20051/20051_47.jpg"),
            model.Page(
                name: "48",
                content: "18:9-14",
                image: "primary_sources/20051/20051_48.jpg"),
            model.Page(
                name: "49",
                content: "18:15-20",
                image: "primary_sources/20051/20051_49.jpg"),
            model.Page(
                name: "50",
                content: "18:21-24",
                image: "primary_sources/20051/20051_50.jpg"),
            model.Page(
                name: "51",
                content: "19:1-4",
                image: "primary_sources/20051/20051_51.jpg"),
            model.Page(
                name: "52",
                content: "19:5-7",
                image: "primary_sources/20051/20051_52.jpg"),
            model.Page(
                name: "53",
                content: "19:7-10",
                image: "primary_sources/20051/20051_53.jpg"),
            model.Page(
                name: "54",
                content: "19:11-12",
                image: "primary_sources/20051/20051_54.jpg"),
            model.Page(
                name: "55",
                content: "19:12-15",
                image: "primary_sources/20051/20051_55.jpg"),
            model.Page(
                name: "56",
                content: "19:16-18",
                image: "primary_sources/20051/20051_56.jpg"),
            model.Page(
                name: "57",
                content: "19:19-20",
                image: "primary_sources/20051/20051_57.jpg"),
            model.Page(
                name: "58",
                content: "19:20-21",
                image: "primary_sources/20051/20051_58.jpg"),
            model.Page(
                name: "59",
                content: "20:1-3",
                image: "primary_sources/20051/20051_59.jpg"),
            model.Page(
                name: "60",
                content: "20:4",
                image: "primary_sources/20051/20051_60.jpg"),
            model.Page(
                name: "61",
                content: "20:4",
                image: "primary_sources/20051/20051_61.jpg"),
            model.Page(
                name: "62",
                content: "20:5-6",
                image: "primary_sources/20051/20051_62.jpg"),
            model.Page(
                name: "63",
                content: "20:7-8",
                image: "primary_sources/20051/20051_63.jpg"),
            model.Page(
                name: "64",
                content: "-",
                image: "primary_sources/20051/20051_64.jpg"),
            model.Page(
                name: "65",
                content: "20:9-10",
                image: "primary_sources/20051/20051_65.jpg"),
            model.Page(
                name: "66",
                content: "-",
                image: "primary_sources/20051/20051_66.jpg"),
            model.Page(
                name: "67",
                content: "20:11",
                image: "primary_sources/20051/20051_67.jpg"),
            model.Page(
                name: "68",
                content: "20:12-13",
                image: "primary_sources/20051/20051_68.jpg"),
            model.Page(
                name: "69",
                content: "20:14-21:1",
                image: "primary_sources/20051/20051_69.jpg"),
            model.Page(
                name: "70",
                content: "21:2",
                image: "primary_sources/20051/20051_70.jpg"),
            model.Page(
                name: "71",
                content: "21:3-6",
                image: "primary_sources/20051/20051_71.jpg"),
            model.Page(
                name: "72",
                content: "21:6-8",
                image: "primary_sources/20051/20051_72.jpg"),
            model.Page(
                name: "73",
                content: "21:9-10",
                image: "primary_sources/20051/20051_73.jpg"),
            model.Page(
                name: "74",
                content: "21:10-12",
                image: "primary_sources/20051/20051_74.jpg"),
            model.Page(
                name: "75",
                content: "21:13-15",
                image: "primary_sources/20051/20051_75.jpg"),
            model.Page(
                name: "76",
                content: "21:16-18",
                image: "primary_sources/20051/20051_76.jpg"),
            model.Page(
                name: "77",
                content: "21:19",
                image: "primary_sources/20051/20051_77.jpg"),
            model.Page(
                name: "78",
                content: "21:20",
                image: "primary_sources/20051/20051_78.jpg"),
            model.Page(
                name: "79",
                content: "21:20-21",
                image: "primary_sources/20051/20051_79.jpg"),
            model.Page(
                name: "80",
                content: "21:21-25",
                image: "primary_sources/20051/20051_80.jpg"),
            model.Page(
                name: "81",
                content: "21:26-22:2",
                image: "primary_sources/20051/20051_81.jpg"),
            model.Page(
                name: "82",
                content: "22:3-4",
                image: "primary_sources/20051/20051_82.jpg"),
            model.Page(
                name: "83",
                content: "22:5-6",
                image: "primary_sources/20051/20051_83.jpg"),
            model.Page(
                name: "84",
                content: "22:7,15-16",
                image: "primary_sources/20051/20051_84.jpg"),
            model.Page(
                name: "85",
                content: "22:17-19",
                image: "primary_sources/20051/20051_85.jpg"),
            model.Page(
                name: "86",
                content: "22:20-21",
                image: "primary_sources/20051/20051_86.jpg"),
            model.Page(
                name: "87",
                content: "-",
                image: "primary_sources/20051/20051_87.jpg"),
            model.Page(
                name: "88",
                content: "-",
                image: "primary_sources/20051/20051_88.jpg"),
            model.Page(
                name: "89",
                content: "-",
                image: "primary_sources/20051/20051_89.jpg"),
            model.Page(
                name: "90",
                content: "-",
                image: "primary_sources/20051/20051_90.jpg"),
            model.Page(
                name: "91",
                content: "-",
                image: "primary_sources/20051/20051_91.jpg"),
            model.Page(
                name: "92",
                content: "-",
                image: "primary_sources/20051/20051_92.jpg"),
            model.Page(
                name: "93",
                content: "-",
                image: "primary_sources/20051/20051_93.jpg"),
          ],
          attributes: [
            {
              "text": "📜 Ιερά Μονή Παντοκράτορος Αγίου Όρους",
              "url": "https://www.pantokrator.gr"
            },
            {
              "text":
                  "📷 Library of Congress Collection of Manuscripts from the Monasteries of Mt. Athos",
              "url":
                  "https://www.loc.gov/collections/manuscripts-from-the-monasteries-of-mount-athos/about-this-collection"
            },
            {
              "text": "✅ Rights & Access",
              "url":
                  "https://www.loc.gov/collections/manuscripts-from-the-monasteries-of-mount-athos/about-this-collection/rights-and-access"
            }
          ])
    ];
    return sources;
  }

  List<PrimarySource> getFragmentsPrimarySources(BuildContext context) {
    AppLocalizations loc = AppLocalizations.of(context)!;
    final sources = [
      PrimarySource(
          title: loc.papyrus_18_title,
          date: loc.papyrus_18_date,
          content: loc.papyrus_18_content,
          quantity: 4,
          material: loc.papyrus_18_material,
          textStyle: loc.papyrus_18_textStyle,
          found: loc.papyrus_18_found,
          classification: loc.papyrus_18_classification,
          currentLocation: loc.papyrus_18_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Papyrus_18',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=10018',
          link3Title: loc.image_source,
          link3Url: "https://4care-skos.mf.no/4care-artefacts/298",
          preview: 'assets/images/Resources/10018/preview.png',
          maxScale: 5,
          pages: [
            model.Page(
                name: "1v",
                content: "1:4-7",
                image: "primary_sources/10018/BL-Papyrus_2053_f001v.jpg")
          ],
          attributes: [
            {"text": "📜 The British Library", "url": "https://www.bl.uk"},
            {
              "text": "📷 Sofia Heim, 2021, 'Artefact ID 298', 4CARE database",
              "url": "https://4care-skos.mf.no/4care-artefacts/298"
            },
          ]),
      PrimarySource(
          title: loc.papyrus_24_title,
          date: loc.papyrus_24_date,
          content: loc.papyrus_24_content,
          quantity: 8,
          material: loc.papyrus_24_material,
          textStyle: loc.papyrus_24_textStyle,
          found: loc.papyrus_24_found,
          classification: loc.papyrus_24_classification,
          currentLocation: loc.papyrus_24_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Papyrus_24',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=10024',
          link3Title: loc.image_source,
          link3Url: "https://collections.library.yale.edu/catalog/17147600",
          preview: 'assets/images/Resources/10024/preview.png',
          maxScale: 5,
          pages: [
            model.Page(
                name: "1r",
                content: "5:5-8",
                image: "primary_sources/10024/32259786.jpg"),
            model.Page(
                name: "1v",
                content: "6:5-8",
                image: "primary_sources/10024/32259790.jpg")
          ],
          attributes: [
            {
              "text": "📜 Special Collections, Yale Divinity Library",
              "url": "https://web.library.yale.edu/divinity/special-collections"
            },
            {
              "text": "✅ Policy",
              "url":
                  "https://lux.collections.yale.edu/content/open-access-policy-2011"
            },
          ]),
      PrimarySource(
          title: loc.papyrus_43_title,
          date: loc.papyrus_43_date,
          content: loc.papyrus_43_content,
          quantity: 5,
          material: loc.papyrus_43_material,
          textStyle: loc.papyrus_43_textStyle,
          found: loc.papyrus_43_found,
          classification: loc.papyrus_43_classification,
          currentLocation: loc.papyrus_43_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Papyrus_43',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=10043',
          link3Title: loc.image_source,
          link3Url: "https://manuscripts.csntm.org/manuscript/View/GA_P43",
          preview: 'assets/images/Resources/10043/preview.png',
          maxScale: 5,
          pages: [
            model.Page(
                name: "1r",
                content: "2:12-13",
                image: "primary_sources/10043/P43_A.jpg"),
            model.Page(
                name: "1v",
                content: "15:8; 16:1-2",
                image: "primary_sources/10043/P43_B.jpg")
          ],
          attributes: [
            {"text": "📜 The British Library", "url": "https://www.bl.uk"},
          ]),
      PrimarySource(
          title: loc.papyrus_85_title,
          date: loc.papyrus_85_date,
          content: loc.papyrus_85_content,
          quantity: 10,
          material: loc.papyrus_85_material,
          textStyle: loc.papyrus_85_textStyle,
          found: loc.papyrus_85_found,
          classification: loc.papyrus_85_classification,
          currentLocation: loc.papyrus_85_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Papyrus_85',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=10085',
          link3Title: loc.image_source,
          link3Url:
              "https://ntvmr.uni-muenster.de/manuscript-workspace?docID=10085",
          preview: 'assets/images/Resources/10085/preview.png',
          maxScale: 5,
          pages: [
            model.Page(
                name: "1r",
                content: "9:19-21; 10:1-2",
                image: "primary_sources/10085/10085x00010Xa_INTF.jpg"),
            model.Page(
                name: "1v",
                content: "10:5-9",
                image: "primary_sources/10085/10085x00020Xa_INTF.jpg")
          ],
          attributes: [
            {
              "text": "📜 Bibliothèque nationale et universitaire",
              "url": "https://www.bnu.fr"
            },
          ]),
      PrimarySource(
          title: loc.papyrus_98_title,
          date: loc.papyrus_98_date,
          content: loc.papyrus_98_content,
          quantity: 9,
          material: loc.papyrus_98_material,
          textStyle: loc.papyrus_98_textStyle,
          found: loc.papyrus_98_found,
          classification: loc.papyrus_98_classification,
          currentLocation: loc.papyrus_98_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Papyrus_98',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=10098',
          link3Title: loc.image_source,
          link3Url:
              "https://www.academia.edu/13166007/Another_Look_at_P.IFAO_II_31_P98_An_Updated_Transcription_and_Textual_Analysis",
          preview: 'assets/images/Resources/10098/preview.png',
          maxScale: 3,
          pages: [
            model.Page(
                name: "1v",
                content: "1:13-20",
                image: "primary_sources/10098/P.IFAO_inv.237b.jpg"),
          ],
          attributes: [
            {
              "text": "📜 Institut français d’archéologie orientale du Caire",
              "url": "https://www.ifao.egnet.net"
            },
          ]),
      PrimarySource(
          title: loc.papyrus_115_title,
          date: loc.papyrus_115_date,
          content: loc.papyrus_115_content,
          quantity: 109,
          material: loc.papyrus_115_material,
          textStyle: loc.papyrus_115_textStyle,
          found: loc.papyrus_115_found,
          classification: loc.papyrus_115_classification,
          currentLocation: loc.papyrus_115_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Papyrus_115',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=10115',
          link3Title: loc.image_source,
          link3Url:
              "https://portal.sds.ox.ac.uk/articles/online_resource/P_Oxy_LXVI_4499_Revelation_II_1-3_13-15_27-29_III_10-12_V_8-9_VI_5-6_VIII_3-8_11-IX_5_7-16_18-X_4_8-XI_5_8-15_18-XII_5_8-10_12-17_XIII_1-3_6-16_18-XIV_3_5-7_10-11_14-15_18-XV_1_4-7/21178999",
          preview: 'assets/images/Resources/10115/preview.png',
          maxScale: 3,
          pages: [
            model.Page(
                name: "1r",
                content: "2:1-3,27-29;5:8-9;8:3-8,11-13",
                image: "primary_sources/10115/4499_a-i1.jpg"),
            model.Page(
                name: "1v",
                content: "2:13-15;3:10-12;6:5-6;9:1-5,7-11",
                image: "primary_sources/10115/4499_a-i2.jpg"),
            model.Page(
                name: "2r",
                content: "9:11-16,18-21;11:1-5,8-12",
                image: "primary_sources/10115/4499_j-o1.jpg"),
            model.Page(
                name: "2v",
                content: "10:1-4,8-11;11:1,13-15,18-19;12:1",
                image: "primary_sources/10115/4499_j-o2.jpg"),
            model.Page(
                name: "3r",
                content: "12:2-5,9-10;13:6-16",
                image: "primary_sources/10115/4499_p-w1.jpg"),
            model.Page(
                name: "3v",
                content: "12:13-17;13:1-3,18;14:1-3,5-7",
                image: "primary_sources/10115/4499_p-w2.jpg"),
            model.Page(
                name: "4r",
                content: "14:10-11,14-15",
                image: "primary_sources/10115/4499_x-z1.jpg"),
            model.Page(
                name: "4v",
                content: "14:18-20;15:1,4-7",
                image: "primary_sources/10115/4499_x-z2.jpg"),
          ],
          attributes: [
            {
              "text": "The Egypt Exploration Society",
              "url": "https://www.ees.ac.uk"
            },
            {
              "text": "Faculty of Classics (📜 University of Oxford)",
              "url": "https://www.classics.ox.ac.uk"
            },
            {
              "text": "✅ License",
              "url": "https://rightsstatements.org/page/InC/1.0/?language=en"
            },
          ]),
      PrimarySource(
          title: loc.uncial_52_title,
          date: loc.uncial_52_date,
          content: loc.uncial_52_content,
          quantity: 14,
          material: loc.uncial_52_material,
          textStyle: loc.uncial_52_textStyle,
          found: loc.uncial_52_found,
          classification: loc.uncial_52_classification,
          currentLocation: loc.uncial_52_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Uncial_052',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20052',
          link3Title: "",
          link3Url: "",
          preview: 'assets/images/Resources/20052/preview.png',
          maxScale: 10,
          pages: [],
          attributes: [
            {
              "text": "📜 Μονή Αγίου Παντελεήμονος",
              "url":
                  "https://www.monastiria.gr/mount-athos-st-panteleimons-russian-monastery/?lang=en"
            },
          ]),
      PrimarySource(
          title: loc.uncial_163_title,
          date: loc.uncial_163_date,
          content: loc.uncial_163_content,
          quantity: 4,
          material: loc.uncial_163_material,
          textStyle: loc.uncial_163_textStyle,
          found: loc.uncial_163_found,
          classification: loc.uncial_163_classification,
          currentLocation: loc.uncial_163_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Uncial_0163',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20163',
          link3Title: loc.image_source,
          link3Url:
              "https://goodspeed.lib.uchicago.edu/view/index.php?doc=9351&obj=001",
          preview: 'assets/images/Resources/20163/preview.png',
          maxScale: 3,
          pages: [
            model.Page(
                name: "1",
                content: "16:17-18",
                image:
                    "primary_sources/20163/ark_61001_b25p3r42st00_00000001.jpg"),
            model.Page(
                name: "2",
                content: "16:19-20",
                image:
                    "primary_sources/20163/ark_61001_b25p3r42st00_00000002.jpg"),
          ],
          attributes: [
            {
              "text":
                  "📜 The University of Chicago Library (Goodspeed Manuscript Collection)",
              "url":
                  "https://www.lib.uchicago.edu/collex/collections/goodspeed-manuscript-collection"
            },
            {
              "text": "✅ License",
              "url": "https://creativecommons.org/licenses/by-nc/4.0"
            },
          ]),
      PrimarySource(
          title: loc.uncial_169_title,
          date: loc.uncial_169_date,
          content: loc.uncial_169_content,
          quantity: 7,
          material: loc.uncial_169_material,
          textStyle: loc.uncial_169_textStyle,
          found: loc.uncial_169_found,
          classification: loc.uncial_169_classification,
          currentLocation: loc.uncial_169_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Uncial_0169',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20169',
          link3Title: loc.image_source,
          link3Url: "https://papyri.info/apis/pts.apis.5",
          preview: 'assets/images/Resources/20169/preview.png',
          maxScale: 3,
          pages: [
            model.Page(
                name: "1r",
                content: "3:19-22; 4:1",
                image:
                    "primary_sources/20169/pts.apis.5.f.0.600_3000x3407.jpg"),
            model.Page(
                name: "1v",
                content: "4:1-3",
                image:
                    "primary_sources/20169/pts.apis.5.b.0.600_3000x3578.jpg"),
          ],
          attributes: [
            {
              "text":
                  "📜 Papyrus Collection, Special Collections, Wright Library, Princeton Theological Seminary",
              "url": "https://ptsem.edu/library/collections/special/art/papyrus"
            },
            {
              "text": "📷 Digital Corpus of Literary Papyri",
              "url": "https://papyri.info"
            },
            {
              "text": "✅ License",
              "url": "https://creativecommons.org/licenses/by/3.0"
            },
          ]),
      PrimarySource(
          title: loc.uncial_207_title,
          date: loc.uncial_207_date,
          content: loc.uncial_207_content,
          quantity: 14,
          material: loc.uncial_207_material,
          textStyle: loc.uncial_207_textStyle,
          found: loc.uncial_207_found,
          classification: loc.uncial_207_classification,
          currentLocation: loc.uncial_207_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Uncial_0207',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20207',
          link3Title: loc.image_source,
          link3Url: "https://manuscripts.csntm.org/manuscript/View/GA_0207",
          preview: 'assets/images/Resources/20207/preview.png',
          maxScale: 2,
          pages: [
            model.Page(
                name: "1",
                content: "9:7-15",
                image: "primary_sources/20207/GA_0207_0001a.jpg"),
            model.Page(
                name: "2",
                content: "9:2-7",
                image: "primary_sources/20207/GA_0207_0001b.jpg"),
          ],
          attributes: [
            {
              "text": "📜 Biblioteca Medicea Laurenziana",
              "url": "https://www.bmlonline.it"
            },
          ]),
      PrimarySource(
          title: loc.uncial_229_title,
          date: loc.uncial_229_date,
          content: loc.uncial_229_content,
          quantity: 5,
          material: loc.uncial_229_material,
          textStyle: loc.uncial_229_textStyle,
          found: loc.uncial_229_found,
          classification: loc.uncial_229_classification,
          currentLocation: loc.uncial_229_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Uncial_0229',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20229',
          link3Title: loc.image_source,
          link3Url: "https://psi-online.it/documents/psi;13;1296",
          preview: 'assets/images/Resources/20229/preview.png',
          maxScale: 5,
          pages: [
            model.Page(
                name: "1r",
                content: "-",
                image: "primary_sources/20229/PSI_XIII_1296_a_r.jpg"),
            model.Page(
                name: "1v",
                content: "18:16-17",
                image: "primary_sources/20229/PSI_XIII_1296_a_v.jpg"),
            model.Page(
                name: "2r",
                content: "19:4-6",
                image: "primary_sources/20229/PSI_XIII_1296_b_r.jpg"),
            model.Page(
                name: "2v",
                content: "-",
                image: "primary_sources/20229/PSI_XIII_1296_b_v.jpg"),
          ],
          attributes: [
            {
              "text": "📜 Istituto Papirologico “Girolamo Vitelli”",
              "url": "https://www.istitutopapirologico.unifi.it"
            },
          ]),
      PrimarySource(
          title: loc.uncial_308_title,
          date: loc.uncial_308_date,
          content: loc.uncial_308_content,
          quantity: 4,
          material: loc.uncial_308_material,
          textStyle: loc.uncial_308_textStyle,
          found: loc.uncial_308_found,
          classification: loc.uncial_308_classification,
          currentLocation: loc.uncial_308_currentLocation,
          link1Title: loc.wikipedia,
          link1Url: 'https://en.wikipedia.org/wiki/Uncial_0308',
          link2Title: loc.intf,
          link2Url:
              'https://ntvmr.uni-muenster.de/manuscript-catalog?docID=20308',
          link3Title: loc.image_source,
          link3Url:
              "https://portal.sds.ox.ac.uk/articles/online_resource/P_Oxy_LXVI_4500_Revelation_XI_15-16_17-18/21179002",
          preview: 'assets/images/Resources/20308/preview.png',
          maxScale: 5,
          pages: [
            model.Page(
                name: "1r",
                content: "11:15-16",
                image:
                    "primary_sources/20308/POxy.v0066.n4500.a.flesh.hires.jpg"),
            model.Page(
                name: "1v",
                content: "11:17-18",
                image:
                    "primary_sources/20308/POxy.v0066.n4500.a.hair.hires.jpg"),
          ],
          attributes: [
            {
              "text": "The Egypt Exploration Society",
              "url": "https://www.ees.ac.uk"
            },
            {
              "text": "Faculty of Classics (📜 University of Oxford)",
              "url": "https://www.classics.ox.ac.uk"
            },
            {
              "text": "✅ License",
              "url": "https://rightsstatements.org/page/InC/1.0/?language=en"
            },
          ]),
    ];

    return sources;
  }
}
