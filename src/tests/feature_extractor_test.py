from csv import DictReader
from io import StringIO
import pytest

from feature_extractor import FeatureExtractor
from graph_crawler import GraphCrawler


class HashDict(dict):
    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


@pytest.mark.second
def test_feature_extractor():
    groups = ["bio", "inf"]
    with open(GraphCrawler().resultspath) as crawler_results_file:
        crawler_dicts = [
            i for i in DictReader(crawler_results_file)
            if int(i["Edges"]) <= 2000 and i["Group"] in groups
        ]
    print([i["Name"] for i in crawler_dicts])
    extractor = FeatureExtractor(crawler_dicts)
    extractor.execute()

    def get_hash_dicts(file):
        keys = ["Graph", "Type", "Model", "Nodes", "Edges"]
        for i in DictReader(file):
            yield HashDict(
                {key: i[key] for key in keys}
            )
    with open(extractor.resultspath) as file:
        extracted_features = set(get_hash_dicts(file))

    stage1_names = [i["Name"] for i in crawler_dicts]
    with open(extractor._stagepath + "../paper-features.csv") as file:
        paper_features = set(
            i for i in get_hash_dicts(file)
            if i["Graph"] in stage1_names
        )

    assert extracted_features >= paper_features
