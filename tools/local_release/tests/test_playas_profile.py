"""Keep Playas release notes compatible with its original shell extraction contract."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from local_release.core import ReleaseError
from local_release.profiles import playas


class PlayasMetadataTest(unittest.TestCase):
    def source(self,heading):
        def git(repo,*args):
            if args[0]=='tag':return ''
            if args[-1].endswith('pubspec.yaml'):return 'version: 1.2.1+60'
            if args[-1].endswith('gradle.properties'):return 'android.builtInKotlin=false\nandroid.newDsl=false'
            return heading+'\nCurrent notes\n\n## [1.2.0]\nOlder notes'
        return git

    def test_bracketed_and_plain_headings_extract_the_same_current_section(self):
        for heading in ['## [1.2.1] - 2026-11-01','## 1.2.1 - 2026-11-01']:
            with self.subTest(heading=heading),patch.object(playas,'git',side_effect=self.source(heading)):
                meta=playas.metadata(None,'a'*40,{})
            self.assertIn('Current notes',meta['release_notes'])
            self.assertNotIn('Older notes',meta['release_notes'])
            self.assertEqual(meta['build'],60)

    def test_version_prefix_cannot_publish_another_versions_notes(self):
        with patch.object(playas,'git',side_effect=self.source('## [1.2.10] - 2026-11-01')):
            with self.assertRaises(ReleaseError):playas.metadata(None,'a'*40,{})


if __name__=='__main__':unittest.main()
