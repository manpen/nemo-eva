from csv import DictReader
import os
import pytest

from graph_crawler import GraphCrawler


def is_stage_clean(stage):
    path = stage._stagepath
    return not os.path.exists(path) or os.listdir(path) == []


def results_path(stage):
    path = stage._stagepath
    return path + "results.csv"


@pytest.mark.first
def test_graph_crawler():
    def graph_filter_func(graph_properties):
        return (
            int(graph_properties["Nodes"]) < 10000 and
            int(graph_properties["Edges"]) < 100000)
    crawler = GraphCrawler(graph_filter_func=graph_filter_func)
    assert is_stage_clean(crawler)
    crawler.execute()

    with open(results_path(crawler)) as crawl_results:
        crawled_graphs = set(
            i["Name"] for i in DictReader(crawl_results)
        )

    with open("../data/paper-features.csv") as paper_features:
        filtered_paper_graphs = set(
            i["Graph"] for i in DictReader(paper_features)
            if graph_filter_func(i) and
            i["Model"] == "real-world"
        )

    wrong_names = ["bn-fly-drosophila_medulla_1", "bn-macaque-rhesus_brain_1"]
    paper_features = [
        i.replace("_", "-") if i in wrong_names
        else i
        for i in paper_features
    ]

    print("More:", filtered_paper_graphs - crawled_graphs)
    print("Missing:", filtered_paper_graphs - crawled_graphs)
    assert crawled_graphs >= filtered_paper_graphs
