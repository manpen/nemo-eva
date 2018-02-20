import os
import pytest

from crawler import GraphCrawler


def is_stage_clean(stage):
    path = stage._stagepath
    return not os.path.exists(path) or os.listdir(path) == []


def test_graph_crawler():
    crawler = GraphCrawler()
    assert is_stage_clean(crawler)
