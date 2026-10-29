"""Keep earlier catalog hash contracts scoped to their original subscriptions."""
import json
from pathlib import Path


def before_monagas_expansion(sources):
    path = Path(__file__).resolve().parents[1] / 'sources/monagas-verification.json'
    additions = {row['feed'] for row in json.loads(path.read_text())['sources']}
    # MonagasCatalogTests independently verifies all 311 original records.
    return [source for source in sources if source['url'] not in additions]
