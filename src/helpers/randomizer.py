import networkit as nk

def randomize_global_curveball(graph):
    for step in range(1, 20):
        algo = nk.randomization.GlobalCurveball(graph, step)
        algo.run()
        info_map = [
            ("n", graph.numberOfNodes()),
            ("step", step)
        ]
        yield ("gcb-%d" % step, "", algo.getGraph())

