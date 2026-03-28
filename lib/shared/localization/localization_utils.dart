import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';

String locLinks(BuildContext context, String key) {
  final localizations = AppLocalizations.of(context)!;
  return locLinksByLocalizations(localizations, key);
}

String locLinksByLocalizations(AppLocalizations localizations, String key) {
  final Map<String, String> translations = _linkTranslations(localizations);
  return translations[key] ?? key;
}

Map<String, String> _linkTranslations(AppLocalizations localizations) {
  final Map<String, String> translations = {
    "@indeclNumAdj": localizations.strong_indeclNumAdj,
    "@indeclLetN": localizations.strong_indeclLetN,
    "@indeclinable": localizations.strong_indeclinable,
    "@adj": localizations.strong_adj,
    "@advCor": localizations.strong_advCor,
    "@advInt": localizations.strong_advInt,
    "@advNeg": localizations.strong_advNeg,
    "@advSup": localizations.strong_advSup,
    "@adv": localizations.strong_adv,
    "@comp": localizations.strong_comp,
    "@aramaicTransWord": localizations.strong_aramaicTransWord,
    "@hebrewForm": localizations.strong_hebrewForm,
    "@hebrewNoun": localizations.strong_hebrewNoun,
    "@hebrew": localizations.strong_hebrew,
    "@location": localizations.strong_location,
    "@properNoun": localizations.strong_properNoun,
    "@noun": localizations.strong_noun,
    "@masc": localizations.strong_masc,
    "@fem": localizations.strong_fem,
    "@neut": localizations.strong_neut,
    "@plur": localizations.strong_plur,
    "@otherType": localizations.strong_otherType,
    "@verbImp": localizations.strong_verbImp,
    "@verb": localizations.strong_verb,
    "@pronDat": localizations.strong_pronDat,
    "@pronPoss": localizations.strong_pronPoss,
    "@pronPers": localizations.strong_pronPers,
    "@pronRecip": localizations.strong_pronRecip,
    "@pronRefl": localizations.strong_pronRefl,
    "@pronRel": localizations.strong_pronRel,
    "@pronCorrel": localizations.strong_pronCorrel,
    "@pronIndef": localizations.strong_pronIndef,
    "@pronInterr": localizations.strong_pronInterr,
    "@pronDem": localizations.strong_pronDem,
    "@pron": localizations.strong_pron,
    "@particleCond": localizations.strong_particleCond,
    "@particleDisj": localizations.strong_particleDisj,
    "@particleInterr": localizations.strong_particleInterr,
    "@particleNeg": localizations.strong_particleNeg,
    "@particle": localizations.strong_particle,
    "@interj": localizations.strong_interj,
    "@participle": localizations.strong_participle,
    "@prefix": localizations.strong_prefix,
    "@prep": localizations.strong_prep,
    "@artDef": localizations.strong_artDef,
    "@phraseIdi": localizations.strong_phraseIdi,
    "@phrase": localizations.strong_phrase,
    "@conjNeg": localizations.strong_conjNeg,
    "@conj": localizations.strong_conj,
    "@or": localizations.strong_or,
  };
  return translations;
}

String locColorThemes(BuildContext context, String key) {
  final localizations = AppLocalizations.of(context);
  final Map<String, String> translations = {
    "manuscript": localizations!.manuscript_color_theme,
    "forest": localizations.forest_color_theme,
    "sky": localizations.sky_color_theme,
    "grape": localizations.grape_color_theme,
  };
  return translations[key] ?? key;
}

String locFontSizes(BuildContext context, String key) {
  final localizations = AppLocalizations.of(context);
  final Map<String, String> translations = {
    "small": localizations!.small_font_size,
    "medium": localizations.medium_font_size,
    "large": localizations.large_font_size,
  };
  return translations[key] ?? key;
}
