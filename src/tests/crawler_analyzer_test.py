import os
import pytest

from graph_crawler import GraphCrawler


def is_stage_clean(stage):
    path = stage._stagepath
    return not os.path.exists(path) or os.listdir(path) == []


@pytest.mark.first
def test_graph_crawler():
    crawler = GraphCrawler()
    assert is_stage_clean(crawler)
    crawler.execute(graph_filter_func=lambda x: x["nodes"] < 100000)
