"""Offline integrity and geography contracts for the expanded public catalog."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from collect import parse_opml
from audit_feeds import audit


class ExpandedCatalogTests(unittest.TestCase):
    def setUp(self):
        self.sources = parse_opml(ROOT / 'sources/feeds.opml')

    def test_new_folders_have_local_and_international_channels(self):
        self.assertEqual(len(self.sources), 226)
        self.assertEqual(sum(s['category'] == '08 - Maturín / Monagas' for s in self.sources), 6)
        self.assertEqual(sum(s['category'] == '09 - Cultura y entretenimiento internacional' for s in self.sources), 9)
        self.assertEqual(audit(ROOT / 'sources/feeds.opml')['problem_count'], 0)

    def test_original_211_entries_are_unchanged(self):
        originals = [s for s in self.sources if s['category'][:2] in {'01','02','03','04','05','06','07'}]
        digest = hashlib.sha256(json.dumps(originals, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.assertEqual(digest, '2e34363f0a62c2e6d348850216a19bf1921db26eb7c4b1ec83b513093b6f303c')

    def test_discovery_records_are_explicitly_unverified_and_match_catalog(self):
        records = json.loads((ROOT / 'sources/discovery-verification.json').read_text())['sources']
        new = [s for s in self.sources if s['category'].startswith(('08 -', '09 -'))]
        self.assertEqual({s['url'] for s in new}, {r['feed'] for r in records})
        self.assertEqual(len(records), 15)
        for record in records:
            self.assertEqual(record['status'], 'pendiente_conectividad')
            self.assertIsNone(record['entries_observed'])
            self.assertIsNone(record['last_published_at'])
            url = urlsplit(record['feed'])
            self.assertEqual(url.hostname, 'news.google.com')
            query = parse_qs(url.query)['q'][0]
            self.assertEqual(query, record['query'])
            self.assertNotIn('gl=CL', record['feed'])

    def test_generated_catalog_matches_opml(self):
        data = json.loads((ROOT / 'web/data/sources.json').read_text())
        self.assertEqual(data['sources'], self.sources)
        self.assertEqual(len(data['categories']), 9)

    def test_monagas_is_venezuelan_and_culture_is_not_a_geographic_subset(self):
        script = """
const fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('web/v12.js','utf8');
const categories=JSON.parse(fs.readFileSync('web/data/sources.json')).categories;
const context=vm.createContext({state:{categories},window:{},localStorage:{getItem:()=>null}});
vm.runInContext(source.slice(0,source.indexOf('  const display ='))+
 '\\nwindow.inGeo=inGeo;window.geoCats=geoCats;})();',context);
console.log(JSON.stringify({venezuela:context.window.geoCats('venezuela'),latam:context.window.geoCats('latam'),
 local:context.window.inGeo({categories:['08 - Maturín / Monagas']},'venezuela'),
 culture:context.window.inGeo({categories:['09 - Cultura y entretenimiento internacional']},'latam')}));
"""
        result = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertEqual(data['venezuela'], ['05 - Venezuela', '08 - Maturín / Monagas'])
        self.assertIn('08 - Maturín / Monagas', data['latam'])
        self.assertNotIn('09 - Cultura y entretenimiento internacional', data['latam'])
        self.assertTrue(data['local'])
        self.assertFalse(data['culture'])
