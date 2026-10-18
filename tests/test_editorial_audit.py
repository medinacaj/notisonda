"""No network needed to test editorial quality diagnostics."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_editorial import inspect, markdown

class EditorialAuditTests(unittest.TestCase):
    def test_distinguishes_duplicate_rss_from_multiple_feeds_of_same_outlet(self):
        sources=[
          {"id":"one","name":"A Tecnología","url":"https://a.test/tech"},
          {"id":"two","name":"A Deportes","url":"https://a.test/sports"},
          {"id":"three","name":"A copia","url":"https://a.test/tech/"}]
        data=inspect(sources,[],[])
        self.assertEqual(len(data["duplicate_feed_urls"]),1)
        self.assertEqual(len(data["duplicate_feed_urls"][0]),2)

    def test_flags_different_ids_with_same_title_without_deleting_articles(self):
        title="La ciudad inaugura nueva conexión de transporte público"
        articles=[{"id":"1","title":title,"publisher":"Diario A","source_ids":["one"]},
                  {"id":"2","title":title,"publisher":"Diario B","source_ids":["two"]}]
        sources=[{"id":x,"url":"https://example.com/"+x} for x in ("one","two")]
        result=inspect(sources,[],articles)
        self.assertEqual(result["possible_duplicate_total"],1)
        self.assertEqual(result["orphaned_article_sources"],0)
        self.assertIn("revisión humana",markdown(result))
        self.assertEqual(len(articles),2)

    def test_orphaned_sources_and_outage_are_diagnostic_not_blocking(self):
        result=inspect([{"id":"live","url":"https://example.com"}],
            [{"state":"error","name":"Enlace RSS temporalmente fallido"}],
            [{"id":"1","title":"Título","source_ids":["legacy"],"is_radar":True}])
        self.assertEqual(result["orphaned_article_sources"],1)
        self.assertEqual(result["radar_without_credit"],1)
        self.assertEqual(result["unavailable_total"],1)

    def test_different_titles_do_not_trigger_false_duplicate(self):
        result=inspect([],[],[{"id":"1","title":"Noticia uno"},
                              {"id":"2","title":"Noticia dos"}])
        self.assertEqual(result["possible_duplicate_total"],0)

if __name__=="__main__":
    unittest.main()
