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
    assert is_stage_clean(crawler)

    def graph_filter_func(graph_properties):
        return int(graph_properties["Nodes"]) < 10000
    crawler = GraphCrawler(graph_filter_func=graph_filter_func)
    crawler.execute()

    with open(results_path(crawler)) as crawl_results:
        crawled_graphs = [
            i["Graph"] for i in DictReader(crawl_results)
        ]
    print(crawled_graphs)

    with open("../data/paper-features.csv") as paper_features:
        filtered_paper_graphs = [
            i["Graph"] for i in DictReader(paper_features)
            if graph_filter_func(i)
        ]
    print(filtered_paper_graphs)

    assert set(crawled_graphs) >= set(filtered_paper_graphs)
