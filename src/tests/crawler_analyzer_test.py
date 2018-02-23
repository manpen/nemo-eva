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
    groups = ["bio", "inf", "ca"]

    def graph_filter_func(graph_properties):
        return (
            int(graph_properties["Nodes"]) < 10000 and
            int(graph_properties["Edges"]) < 1000000)
    crawler = GraphCrawler(groups=groups, graph_filter_func=graph_filter_func)
    assert is_stage_clean(crawler)
    crawler.execute()

    with open(results_path(crawler)) as crawl_results:
        crawled_graphs = [
            i["Name"] for i in DictReader(crawl_results)
        ]

    with open("../data/paper-features.csv") as paper_features:
        filtered_paper_graphs = [
            i["Graph"] for i in DictReader(paper_features)
            if graph_filter_func(i) and
            i["Model"] == "real-world" and
            any(i["Graph"].startswith(group) for group in groups)
        ]

    assert set(crawled_graphs) >= set(filtered_paper_graphs)
