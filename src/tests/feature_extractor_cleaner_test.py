from csv import DictReader
from io import StringIO
import numpy
import pytest

from feature_cleaner import FeatureCleaner
from feature_extractor import FeatureExtractor
from graph_crawler import GraphCrawler
from helpers import use_paper_data


class HashDict(dict):
    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


@pytest.mark.second
def test_feature_extractor_and_cleaner():
    groups = ["bio", "inf"]
    with open(GraphCrawler().resultspath) as crawler_results_file:
        crawler_dicts = [
            i for i in DictReader(crawler_results_file)
            if int(i["Edges"]) <= 2000 and i["Group"] in groups
        ]
    print([i["Name"] for i in crawler_dicts])
    extractor = FeatureExtractor(crawler_dicts)
    extractor.execute()
    print("Extractor done!")
    with open(extractor.resultspath) as extractor_results_file:
        extractor_dicts = list(DictReader(extractor_results_file))
    cleaner = FeatureCleaner(extractor_dicts)
    cleaner.execute()

    def get_hash_dicts(file):
        return [HashDict(i) for i in DictReader(file)]

    with open(cleaner.resultspath) as file:
        extracted_features = get_hash_dicts(file)

    with use_paper_data():
        with open(FeatureCleaner.resultspath) as file:
            paper_features = get_hash_dicts(file)

    def get_tuple(x):
        return (x["Graph"], x["Model"])

    paper_tuples = [get_tuple(j) for j in paper_features]
    for i in extracted_features:
        if i["Model"] in ["BA circle", "BA full"]:
            continue
        if get_tuple(i) not in paper_tuples:
            continue

        a = 0
        index = paper_tuples.index(get_tuple(i))
        j = paper_features[index]
        for key in i:
            if key in j:
                try:
                    assert numpy.allclose(float(i[key]), float(j[key]))
                except Exception as e:
                    assert i[key] == j[key]
