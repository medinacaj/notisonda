import sys
import unittest
import json
from datetime import datetime,timezone,timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collect import group_related_articles,publish_partitioned

class RelatedTests(unittest.TestCase):
    def item(self,i,source,title,at=0):
        return {'id':str(i),'url':'https://'+source+'.example/'+str(i),
                'title':title,'source':source,'publisher':source,'source_ids':[source],
                'categories':['Test'],'published_at':(datetime(2026,10,17,tzinfo=timezone.utc)+timedelta(hours=at)).isoformat()}
    def test_group_with_alternatives(self):
        title='Gobierno anuncia nuevas medidas para mejorar la red del transporte público'
        records=[self.item(1,'uno',title),self.item(2,'dos',title,2)]
        grouped=group_related_articles(records)
        self.assertEqual(len(grouped),1)
        self.assertEqual(grouped[0]['source_ids'],['uno','dos'])
        self.assertEqual(grouped[0]['also_in'][0]['url'],records[1]['url'])
    def test_no_merge_short_or_old(self):
        title='Gobierno anuncia nuevas medidas para mejorar la red del transporte público'
        self.assertEqual(len(group_related_articles([self.item(1,'uno',title),self.item(2,'dos',title,25)])),2)
        self.assertEqual(len(group_related_articles([self.item(1,'uno','Chile anuncia medidas'),self.item(2,'dos','Chile anuncia medidas')])),2)
    def test_split_consistency(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            records=[self.item(i,'one','Noticia titular número '+str(i)) for i in range(725)]
            publish_partitioned(root,records,'2026-10-17T10:00:00Z')
            meta=json.loads((root/'meta.json').read_text())
            all_items=json.loads((root/'latest.json').read_text())['items']
            for name in meta['archive_files']:
                all_items.extend(json.loads((root/name).read_text())['items'])
            self.assertEqual([x['id'] for x in all_items],[x['id'] for x in records])
            self.assertEqual(len(meta['archive_files']),2)
