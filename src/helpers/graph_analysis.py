import networkit

from helpers.powerlaw_estimation import powerlaw_fit

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
    powerlaw_alpha = powerlaw_fit(degrees)
    stats = {
        "Originally Weighted": originally_weighted,
        "Degree Distribution": {
            "Powerlaw": {
                "Alpha": powerlaw_alpha
                #"KS Distance": fit.power_law.KS()
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