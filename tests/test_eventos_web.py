import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eventos"))
import publicar_web  # noqa: E402


def snapshot(stamp, events):
    return {"generated_at": stamp, "summary": {"sources_attempted": 3, "sources_ok": 2, "sources_failed": 1},
            "events": events, "runs": []}


def event(**kw):
    base = {"title": "Concierto", "date": "2030-05-10", "time": "19:00", "commune": "Concepción",
            "category": "Cultura", "price_status": "free", "status": "Confirmado", "source": "Teatro",
            "source_url": "https://teatro.example/concierto", "official": True,
            "sources": [{"name": "Teatro", "url": "https://teatro.example/concierto"}], "changes": []}
    base.update(kw)
    return base


class EventosWebTests(unittest.TestCase):
    """Puente recolector → web estática, sin red."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data = self.root / "data"
        self.data.mkdir()
        self.out = self.root / "web"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, doc):
        (self.data / name).write_text(json.dumps(doc), encoding="utf-8")

    def test_export_keeps_current_events_and_drops_unsafe_urls(self):
        self.write("crawled_events.json", snapshot("2030-05-01T10:00:00", [
            event(),
            event(title="Feria pasada", date="2020-01-01"),
            event(title="Enlace raro", source_url="javascript:alert(1)", image_url="data:x"),
        ]))
        self.write("national_events.json", snapshot("2030-05-01T11:00:00", [
            event(title="Ópera", commune="Santiago", region="Metropolitana")]))
        counts = publicar_web.export(str(self.out), data_dir=str(self.data), today="2030-05-01",
                                     now="2030-05-01T12:00:00")
        self.assertEqual(counts, {"biobio": 2, "nacional": 1})
        doc = json.loads((self.out / "eventos.json").read_text(encoding="utf-8"))
        titles = [e["title"] for e in doc["events"]]
        self.assertNotIn("Feria pasada", titles)
        odd = next(e for e in doc["events"] if e["title"] == "Enlace raro")
        self.assertIsNone(odd["source_url"])
        self.assertIsNone(odd["image_url"])
        bio = next(e for e in doc["events"] if e["title"] == "Concierto")
        self.assertEqual((bio["scope"], bio["province"], bio["region"]), ("biobio", "Concepción", "Biobío"))
        self.assertEqual(len(doc["communes"]["biobio"]), 33)
        # Los snapshots completos se publican para dar continuidad al próximo rastreo.
        self.assertTrue((self.out / "eventos" / "biobio.json").exists())
        self.assertTrue((self.out / "eventos" / "nacional.json").exists())

    def test_export_without_snapshots_is_empty_not_invented(self):
        counts = publicar_web.export(str(self.out), data_dir=str(self.data), today="2030-05-01")
        self.assertEqual(counts, {"biobio": 0, "nacional": 0})
        doc = json.loads((self.out / "eventos.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["events"], [])
        self.assertIsNone(doc["scopes"]["biobio"]["generated_at"])

    def test_recover_picks_newest_snapshot(self):
        self.write("crawled_events.json", snapshot("2030-05-01T10:00:00", [event()]))
        art = self.root / "artefacto"
        art.mkdir()
        (art / "crawled_events.json").write_text(json.dumps(snapshot("2030-05-02T10:00:00", [])), encoding="utf-8")
        published = {"nacional": snapshot("2030-05-03T10:00:00", [event(title="Ópera")])}

        def fetcher(url):
            scope = url.rsplit("/", 1)[-1][:-5]
            if scope not in published:
                raise OSError("sin publicación")
            return published[scope]

        chosen = publicar_web.recover(from_dir=str(art), from_url="https://example.invalid/",
                                      fetcher=fetcher, data_dir=str(self.data), log=lambda *_: None)
        self.assertEqual(chosen, {"biobio": "artefacto", "nacional": "pages"})
        bio = json.loads((self.data / "crawled_events.json").read_text(encoding="utf-8"))
        self.assertEqual(bio["generated_at"], "2030-05-02T10:00:00")

    def test_recover_ignores_invalid_published_json(self):
        self.write("crawled_events.json", snapshot("2030-05-01T10:00:00", [event()]))
        chosen = publicar_web.recover(from_url="https://example.invalid/", fetcher=lambda url: {"events": "no"},
                                      data_dir=str(self.data), log=lambda *_: None)
        self.assertEqual(chosen["biobio"], "repositorio")
        self.assertIsNone(chosen["nacional"])


class EventosFrontendContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web/index.html").read_text(encoding="utf8")
        cls.js = (ROOT / "web/eventos.js").read_text(encoding="utf8")
        cls.sw = (ROOT / "web/sw.js").read_text(encoding="utf8")
        cls.deploy = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf8")
        cls.crawl = (ROOT / ".github/workflows/eventos.yml").read_text(encoding="utf8")

    def test_events_view_is_wired(self):
        for marker in ('id="eventsView"', 'id="eventDialog"', 'id="eventsFilters"', 'eventos.css?v=', 'eventos.js?v='):
            self.assertIn(marker, self.html)
        self.assertLess(self.html.index("v13.js?v="), self.html.index("eventos.js?v="))
        self.assertIn("'./eventos.js'", self.sw)
        self.assertIn("'./data/eventos.json'", self.sw)

    def test_dom_is_built_without_html_strings(self):
        # Los datos vienen de sitios de terceros: nunca se interpretan como HTML.
        self.assertNotIn("innerHTML", self.js)
        self.assertNotIn("insertAdjacentHTML", self.js)
        self.assertIn("safeURL(", self.js)

    def test_events_never_block_news_publication(self):
        step = self.deploy[self.deploy.index("Incorporar eventos"):]
        self.assertIn("continue-on-error: true", step.split("- name:")[0])
        self.assertIn("python -m unittest discover -s eventos/tests -t eventos", self.deploy)
        self.assertNotIn("contents: write", self.crawl)
        self.assertIn("check_snapshot.py", self.crawl)


if __name__ == "__main__":
    unittest.main()
