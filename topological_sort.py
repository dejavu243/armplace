"""Применение топологической сортировки для расстановки мест в турнире

    Algorithm
    1. Set first 3 (or 4) places
    2. Find all target nodes
    3. Find mean level player loose and max wins in winners
    4. Set places in ascending order. If there are two identical mean, then compare by max wins
    5. Delete targets
    6. If there are no nodes unvisited than exit, else go to 2.
"""
import matplotlib.pyplot as plt
import networkx
import networkx as nx

import data.left_hand_75kg.left_hand_75kg as lh75
import data.right_hand_70kg.right_hand_70kg as rh70
import data.left_hand_80kg.left_hand_80kg as lh80
from grinev_algorithm import TournamentGraphConstructor

# names, pairs = lh75.names, lh75.pairs
names, pairs = lh80.names, lh80.pairs
# names, pairs = rh70.names, rh70.pairs

plt.rcParams["figure.figsize"] = (20, 10)


def get_tournament_dict(_graph: networkx.Graph) -> dict:
    tournament = {}
    for node in _graph.nodes():
        level = _graph.out_degree(node) - _graph.in_degree(node) + 2
        losses = _graph.in_degree(node)
        wins = _graph.out_degree(node)
        # print(node, level)
        for node_adj in _graph.nodes():
            if (node, node_adj) in _graph.edges():
                # weight = _graph.get_edge_data(node, node_adj)['weight']
                weight = 1
                level += (weight - 1)
                wins += (weight - 1)
                # print(node, node_adj, weight)
            elif (node_adj, node) in _graph.edges():
                # weight = _graph.get_edge_data(node_adj, node)['weight']
                weight = 1
                level -= (weight - 1)
                losses += (weight - 1)
                # print(node_adj, node, weight)
        tournament[node] = {"level": level, "losses": losses, "wins": wins}

    return tournament


def get_target_points_sorted(target_points, keys=None, reverse=None):
    # return sorted  list by some key
    if not isinstance(keys, list):
        return sorted(target_points.items(), key=lambda item: item[1][keys], reverse=reverse)
    else:
        if reverse is None:
            order_list = [-1] * len(keys)
        elif isinstance(reverse, list):
            order_list = [1 if x == True else -1 for x in reverse]
        elif reverse is not None:
            direction = 1 if reverse == True else -1
            order_list = [direction] * len(keys)

        if len(keys) == 2:
            return sorted(target_points.items(), key=lambda item: (
                order_list[0] * item[1][keys[0]], order_list[1] * item[1][keys[1]]))
        elif len(keys) == 3:
            return sorted(target_points.items(),
                          key=lambda item: (
                              order_list[0] * item[1][keys[0]], order_list[1] * item[1][keys[1]],
                              order_list[2] * item[1][keys[2]]))
        elif len(keys) == 4:
            return sorted(target_points.items(),
                          key=lambda item: (
                              order_list[0] * item[1][keys[0]], order_list[1] * item[1][keys[1]],
                              order_list[2] * item[1][keys[2]], order_list[3] * item[1][keys[3]]))


# example topological sort
alg = TournamentGraphConstructor(names, pairs)
graph = alg.make_graph()
top_sort = list(nx.topological_sort(graph))

tour = get_tournament_dict(graph)
print(get_tournament_dict(graph))


# for k, v in sorted(tournament.items(), key = lambda x: x[1]['place']):
#    print("PLACE:", v["place"], "\t", k, "\tLEVEL:", v["level"], "\tW/L:", v["wins"], v["losses"])


def get_places(_tournament: dict, _graph: networkx.Graph):
    source = [x for x in _graph.nodes() if _graph.out_degree(x) > 0 and _graph.in_degree(x) == 0][
        0]  # only one source, first place
    targets = [x for x in _graph.nodes() if _graph.out_degree(x) == 0 and _graph.in_degree(x) > 0]



    # 1. set places
    _tournament[source]["place"] = 1

    node, position = source, _tournament[source]["place"]
    print(node, 'place:\t', _tournament[node]["place"])
    while len(list(_graph.out_edges(node))) == 1:
        node = list(_graph.out_edges(node))[0][1]
        position += 1
        _tournament[node]["place"] = position
        print(node, 'place:\t', _tournament[node]["place"])

    count, max_count = 0, 10
    stop_condition = False
    max_place = len(_tournament)
    targets_iter = targets.copy()
    print("max_place", max_place)
    while not stop_condition:
        print("count:", count)
        print("targets", targets_iter)
        count += 1
        if count == max_count:
            break

        # calc metrics
        target_points = {}
        for target in targets_iter:
            target_winners = list(_graph.in_edges(target))
            winners_mean_level = sum([_tournament[winner[0]]["level"] for winner in target_winners]) / len(
                target_winners)
            winners_max_level = max([_tournament[winner[0]]["level"] for winner in target_winners])
            winners_min_level = min([_tournament[winner[0]]["level"] for winner in target_winners])
            winners_max_wins = max([_tournament[winner[0]]["wins"] for winner in target_winners])
            chain_up_length = len(max(nx.all_simple_paths(_graph, source, target), key=lambda x: len(x)))

            all_simple_paths = list(nx.all_simple_paths(_graph, target, targets[0])) if target not in targets else None
            print("all_simple_paths", all_simple_paths)
            chain_down_length = 0
            if all_simple_paths:
                chain_down_length = len(max(all_simple_paths, key=lambda x: len(x)))
            target_points[target] = {"winners_mean_level": winners_mean_level,
                                     "winners_max_wins": winners_max_wins,
                                     "chain_up_length": chain_up_length,
                                     "chain_down_length": chain_down_length,
                                     "winners_max_level": winners_max_level,
                                     "winners_min_level": winners_min_level}

        print()
        # sort by first important value
        sorted_targets = get_target_points_sorted(target_points,
                                                  ["chain_up_length", "winners_min_level", "winners_mean_level",
                                                   "winners_max_wins"],
                                                  [False, True, True, True])

        for e in sorted_targets:
            print(e)
        print()

        # set places
        for target in sorted_targets:
            name = target[0]
            _tournament[name]["place"] = max_place
            max_place -= 1
            print("Name %s set place %d" % (name, _tournament[name]["place"]))
            if max_place <= 3:
                stop_condition = True
                break

        print("max_place", max_place)
        _graph.remove_nodes_from(targets_iter)
        targets_iter = [x for x in _graph.nodes() if _graph.out_degree(x) == 0 and _graph.in_degree(x) > 0]

        if len(targets_iter) == 0:
            stop_condition = True

    return _tournament.copy()


tournament = get_places(tour, graph)

#for k, v in sorted(tournament.items(), key=lambda x: x[1]['place']):
for k, v in tournament.items():
    print("PLACE:", v["place"], "\t", k, "\tLEVEL:", v["level"], "\tW/L:", v["wins"], v["losses"])
