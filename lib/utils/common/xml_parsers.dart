import 'package:flutter/services.dart';
import 'package:revelation/models/institution_info.dart';
import 'package:revelation/models/library_info.dart';
import 'package:revelation/models/recommended_info.dart';
import 'package:xml/xml.dart';

Future<List<LibraryInfo>> parseLibraries(
  AssetBundle bundle,
  String xmlPath,
) async {
  try {
    final xmlString = await bundle.loadString(xmlPath);
    final document = XmlDocument.parse(xmlString);
    final libraries = <LibraryInfo>[];

    for (var element in document.findAllElements('library')) {
      final name = element.getElement('name')?.innerText;
      final idIcon = element.getElement('idIcon')?.innerText;
      final license = element.getElement('license')?.innerText;
      final officialSite = element.getElement('officialSite')?.innerText;
      final licenseLink = element.getElement('licenseLink')?.innerText;

      if (name == null ||
          idIcon == null ||
          license == null ||
          officialSite == null ||
          licenseLink == null) {
        throw Exception('Missing required tags in library element');
      }

      libraries.add(
        LibraryInfo(
          name: name,
          idIcon: idIcon,
          license: license,
          officialSite: officialSite,
          licenseLink: licenseLink,
        ),
      );
    }

    return libraries;
  } on XmlException {
    rethrow;
  } on PlatformException {
    rethrow;
  } catch (e) {
    throw Exception('Unknown error: $e');
  }
}

Future<List<InstitutionInfo>> parseInstitutions(
  AssetBundle bundle,
  String xmlPath,
) async {
  try {
    final xmlString = await bundle.loadString(xmlPath);
    final document = XmlDocument.parse(xmlString);
    final institutions = <InstitutionInfo>[];

    for (var element in document.findAllElements('institution')) {
      final name = element.getElement('name')?.innerText;
      final idIcon = element.getElement('idIcon')?.innerText;
      final officialSite = element.getElement('officialSite')?.innerText;

      if (name == null || idIcon == null || officialSite == null) {
        throw Exception('Missing required tags in institution element');
      }
      final sourcesElement = element.getElement('sources');
      final sources = <String, String>{};

      if (sourcesElement != null) {
        for (var source in sourcesElement.findElements('source')) {
          final text = source.getElement('text')?.innerText ?? '';
          final link = source.getElement('link')?.innerText ?? '';
          sources[text] = link;
        }
      }

      institutions.add(
        InstitutionInfo(
          name: name,
          idIcon: idIcon,
          officialSite: officialSite,
          sources: sources,
        ),
      );
    }

    return institutions;
  } on XmlException {
    rethrow;
  } on PlatformException {
    rethrow;
  } catch (e) {
    throw Exception('Unknown error: $e');
  }
}

Future<List<RecommendedInfo>> parseRecommended(
  AssetBundle bundle,
  String xmlPath,
) async {
  try {
    final xmlString = await bundle.loadString(xmlPath);
    final document = XmlDocument.parse(xmlString);
    final recommendations = <RecommendedInfo>[];

    for (var element in document.findAllElements('recommendation')) {
      final name = element.getElement('name')?.innerText;
      final idIcon = element.getElement('idIcon')?.innerText;
      final officialSite = element.getElement('officialSite')?.innerText;

      if (name == null || idIcon == null || officialSite == null) {
        throw Exception('Missing required tags in recommendation element');
      }

      recommendations.add(
        RecommendedInfo(name: name, idIcon: idIcon, officialSite: officialSite),
      );
    }

    return recommendations;
  } on XmlException {
    rethrow;
  } on PlatformException {
    rethrow;
  } catch (e) {
    throw Exception('Unknown error: $e');
  }
}
