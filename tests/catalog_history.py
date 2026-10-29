"""Keep historical catalog contracts scoped to the subscriptions they describe."""
import json
from pathlib import Path


def before_business_expansion(sources):
    record = Path(__file__).resolve().parents[1] / 'sources/business-sources-verification.json'
    additions = {row['feed'] for row in json.loads(record.read_text())['sources']}
    # BusinessCatalogTests independently checks the exact hash of these 311 records.
    return [source for source in sources if source['url'] not in additions]
