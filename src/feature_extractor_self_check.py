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


class NoDaemonProcessPool(multiprocessing.pool.Pool):
    class NoDaemonProcess(multiprocessing.Process):
        def _get_daemon(self):
            return False

        def _set_daemon(self, value):
            pass
        daemon = property(_get_daemon, _set_daemon)

    Process = NoDaemonProcess

def getDeepValue(a_dict, keylist):
    for subkey in keylist:
        a_dict = a_dict[subkey]
    return a_dict

def shrink_to_giant_component(g):
    comp = networkit.components.ConnectedComponents(g)
    comp.run()
    giant_id = max(comp.getPartition().subsetSizeMap().items(),
                   key=lambda x: x[1])
    giant_comp = comp.getPartition().getMembers(giant_id[0])
    for v in g.nodes():
        if v not in giant_comp:
            for u in g.neighbors(v):
                g.removeEdge(v, u)
            g.removeNode(v)
    name = g.getName()
    g = networkit.graph.GraphTools.getCompactedGraph(
      g,
      networkit.graph.GraphTools.getContinuousNodeIds(g)
    )
    g.setName(name)
    return g



def analyze(g):
    originally_weighted = g.isWeighted()
    if originally_weighted:
        g = g.toUnweighted()
    g.removeSelfLoops()
    g = shrink_to_giant_component(g)
    degrees = networkit.centrality.DegreeCentrality(g).run().scores()
    fit = powerlaw.Fit(degrees, fit_method='Likelihood', verbose=False)
    stats = {
        "Originally Weighted": originally_weighted,
        "Degree Distribution": {
            "Powerlaw": {
                "Alpha": fit.alpha,
                "KS Distance": fit.power_law.KS()
            }
        }
    }

    #############

    # possible profiles: minimal, default, complete
    networkit.profiling.Profile.setParallel(1)
    networkit.setSeed(seed=42, useThreadId=False)
    pf = networkit.profiling.Profile.create(g, preset="complete")

    for statname in pf._Profile__measures.keys():
        stats[statname] = pf.getStat(statname)

    stats.update(pf._Profile__properties)

    keys = [[key] for key in stats.keys()]
    output = dict()
    while keys:
        key = keys.pop()
        val = getDeepValue(stats, key)
        if isinstance(val, dict):
            keys += [key + [subkey] for subkey in val]
        elif isinstance(val, int) or isinstance(val, float):
            output[".".join(key)] = val
        elif key == ['Diameter Range']:
            output['Diameter Min'] = val[0]
            output['Diameter Max'] = val[1]
    return output

def binary_search(goal_f, goal, a, b, f_a=None, f_b=None, depth=0):
    if f_a is None:
        f_a = goal_f(a)
    if f_b is None:
        f_b = goal_f(b)
    m = (a + b) / 2
    f_m = goal_f(m)
    if depth < 10 and (f_a <= f_m <= f_b or f_a >= f_m >= f_b):
        if f_a <= goal <= f_m or f_a >= goal >= f_m:
            return binary_search(
                goal_f, goal,
                a, m, f_a, f_m,
                depth=depth+1)
        else:
            return binary_search(
                goal_f, goal,
                m, b, f_m, f_b,
                depth=depth+1)
    return min([(a, f_a), (b, f_b), (m, f_m)], key=lambda x: x[1])

def fit_er(g):
    networkit.setSeed(seed=42, useThreadId=False)
    return networkit.generators.ErdosRenyiGenerator.fit(g).generate()

def fit_ba(g, fully_connected_start):
    random.seed(42, version=2)
    networkit.setSeed(seed=42, useThreadId=False)
    n, m = g.size()
    m_0 = math.ceil(m / n)
    ba = networkit.Graph(n)
    nodes = ba.nodes()
    edges_added = 0
    if fully_connected_start:
        start_connections = itertools.combinations(nodes[:m_0], 2)
    else:  # circle
        start_connections = (
            [(nodes[m_0-1], nodes[0])] +
            [(nodes[i], nodes[i+1]) for i in range(m_0-1)]
        )
    for u, v in start_connections:
        ba.addEdge(u, v)
        edges_added += 1

    for i, v in list(enumerate(nodes))[m_0:]:
        num_new_edges = min(i, int((m-edges_added)/(n-i)))
        really_new_edges = 0
        to_connect = set()
        while len(to_connect) < num_new_edges:
            num_draws = num_new_edges - len(to_connect)
            to_connect_draws = [
                random.choice(ba.randomEdge())
                for i in range(num_draws)
            ]
            to_connect |= set(
                u for u in to_connect_draws if not ba.hasEdge(v, u)
            )
        for u in to_connect:
            ba.addEdge(u, v)
        edges_added += num_new_edges
    return ba

def fit_chung_lu(g):
    networkit.setSeed(seed=42, useThreadId=False)
    return networkit.generators.ChungLuGenerator.fit(g).generate()

def fit_chung_lu_constant(g):
    networkit.setSeed(seed=42, useThreadId=False)
    degrees = networkit.centrality.DegreeCentrality(g).run().scores()
    fit = powerlaw.Fit(degrees, fit_method='Likelihood', verbose=False)
    gamma = max(fit.alpha, 2.1)
    #xmin = int(fit.xmin)
    #xmax = int(fit.xmax) if fit.xmax else max(degrees)

    k = 2 * g.numberOfEdges() / g.numberOfNodes()
    
    generator = networkit.generators.PowerlawDegreeSequence(g)

    generator.setGamma(-(gamma+1))
    generator.setMinimumFromAverageDegree(k)
    
    degree_sequence = generator.run().getDegreeSequence(g.numberOfNodes())
    graph = networkit.generators.ChungLuGenerator(degree_sequence).generate()
    info_map = [
        ("n", g.numberOfNodes()),
        ("gamma", gamma),
        ("k", k)
    ]
    
    info = "|".join([name + "=" + str(val) for name, val in info_map])
    return (info, graph)
        
def fit_hyperbolic(g):
    networkit.setSeed(seed=42, useThreadId=False)
    degrees = networkit.centrality.DegreeCentrality(g).run().scores()
    fit = powerlaw.Fit(degrees, fit_method='Likelihood', verbose=False)
    gamma = max(fit.alpha, 2.1)
    n, m = g.size()
    degree_counts = collections.Counter(degrees)
    n_hyper = n + max(0, 2*degree_counts[1] - degree_counts[2])
    k = 2 * m / (n_hyper-1)
    def criterium(h):
        #networkit.setLogLevel("WARN")
        val = networkit.globals.clustering(h)
        #networkit.setLogLevel("INFO")
        return val
    goal = criterium(g)

    def guess_goal(t):
        hyper_t = networkit.generators.HyperbolicGenerator(
            n_hyper, k, gamma, t).generate()
        hyper_t = shrink_to_giant_component(hyper_t)
        return criterium(hyper_t)
    t, crit_diff = binary_search(guess_goal, goal, 0.01, 0.99)
    hyper = networkit.generators.HyperbolicGenerator(
        n_hyper, k, gamma, t).generate()
    info_map = [
        ("n", n_hyper),
        ("k", k),
        ("gamma", gamma),
        ("t", t)
    ]
    info = "|".join([name + "=" + str(val) for name, val in info_map])
    return (info, hyper)

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
        ("real-world",
            lambda x: ("", x)),
        ("ER",
            lambda x: ("", fit_er(x))),
        ("BA circle",
            lambda x: ("", fit_ba(x, fully_connected_start=False))),
        ("BA full",
            lambda x: ("", fit_ba(x, fully_connected_start=True))),
        ("chung-lu",
            lambda x: ("", fit_chung_lu(x))),
        ("chung-lu constant",
            fit_chung_lu_constant),
        ("hyperbolic",
            fit_hyperbolic)
    ]

    outputs = []
    # all_keys = set()
    for model_name, model_converter in model_types:
        try:
            info1, model1 = model_converter(g)
            output1 = analyze(model1)
            # Retry model based on 
            info2, model2 = model_converter(model1)
            output2 = analyze(model2)
        except ZeroDivisionError as e:
            print("Error:", e, "for", model_name, "of", g.getName())
        else:
            output1["Graph"] = g.getName()
            output1["Type"] = graph_type
            output1["Model"] = model_name
            output1["Info"] = info1
            outputs.append(output1)

            output2["Graph"] = g.getName()
            output2["Type"] = graph_type
            output2["Model"] = model_name + "-second"
            output2["Info"] = info2
            outputs.append(output2)
            # all_keys |= set(output.keys())

    # for model_name, info, output in sorted(outputs):
        # for key in all_keys - set(output.keys()):
        #    output[key] = float("nan")
    return outputs
            
class FeatureExtractorSelfCheck(AbstractStage):
    _stage = "2-features"

    def __init__(self, graph_dicts):
        super(FeatureExtractorSelfCheck, self).__init__()
        self.graph_dicts = graph_dicts
        networkit.engineering.setNumberOfThreads(1)

    def _execute(self):
        #for graph in self.graph_dicts:
        #    self._execute_one_graph(graph)
        count = 0
        total = len(self.graph_dicts)
        pool = multiprocessing.pool.Pool(20)
        for results in pool.imap_unordered(_execute_one_graph, self.graph_dicts):
            for result in results:
                self._save_as_csv(result)
            count += 1
            print("{}/{} graphs done!".format(count, total))
        pool.close()
        pool.join()
