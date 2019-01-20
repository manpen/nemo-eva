import collections
import csv
import itertools
import math
import multiprocessing
import numpy
import powerlaw
import random
import networkit

import os

from abstract_stage import AbstractStage
from graph_crawler import GraphCrawler
from helpers.print_blocker import PrintBlocker
from helpers.graph_analysis import shrink_to_giant_component, analyze
from helpers.randomizer import randomize_global_curveball

def _execute_one_graph(graph_dict):
    in_path = (
        GraphCrawler()._stagepath +
        graph_dict["Group"] + "/" +
        graph_dict["Path"])
    graph_type = graph_dict["Group"]

    g = None
    try:
        g = networkit.readGraph(
            in_path,
            networkit.Format.EdgeList,
            separator=" ",
            firstNode=0,
            commentPrefix="%",
            continuous=True)
    except Exception as e:
        print(e)
        return []

    if not g:
        print("could not import graph from path", in_path)
        return []

    if g.isWeighted():
        print("graph is weighted which is not supported by randomization", in_path)
        return []

    if g.numberOfNodes() > 0 and g.numberOfEdges() > 0:
        if g.degree(0) == 0:
            g.removeNode(0)

    print("Graph", g.toString())
    g = shrink_to_giant_component(g)
    if g.numberOfNodes() < 100:
        print(
            "Graph is too small (" +
            str(g.numberOfNodes()) +
            " nodes, needs 100): " +
            in_path)
        return []

    model_types = [
        lambda x: [("real-world", "", x)],
        lambda x: randomize_global_curveball(x)
    ]




    outputs = []
    # all_keys = set()
    for model_converter in model_types:
        for model_name, info, model in model_converter(g):
            try:
                output = analyze(model)
            except ZeroDivisionError as e:
                print("Error:", e, "for", model_name, "of", g.getName(), model)
            else:
                output["Graph"] = g.getName()
                output["Type"] = graph_type
                output["Model"] = "real-world"
                output["Info"] = ""

                #self._save_as_csv(output)
                outputs.append(output)
                # all_keys |= set(output.keys())

    # for model_name, info, output in sorted(outputs):
        # for key in all_keys - set(output.keys()):
        #    output[key] = float("nan")
    return outputs


class RandomizedFeatureExtractor(AbstractStage):
    _stage = "2-features"

    def __init__(self, graph_dicts, cores=1, **kwargs):
        super(RandomizedFeatureExtractor, self).__init__()
        self.graph_dicts = graph_dicts
        self.cores = cores
        networkit.engineering.setNumberOfThreads(1)

    def _execute(self):
        #for graph in self.graph_dicts:
        #    self._execute_one_graph(graph)
        count = 0
        total = len(self.graph_dicts)
        pool = multiprocessing.pool.Pool(self.cores)
        for results in pool.imap_unordered(_execute_one_graph, self.graph_dicts):
            for result in results:
                self._save_as_csv(result)
            count += 1
            print("{}/{} graphs done!".format(count, total))
        pool.close()
        pool.join()
