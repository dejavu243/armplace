"""Применение топологической сортировки для расстановки мест в турнире"""
import matplotlib.pyplot as plt
import networkx as nx

import data.left_hand_75kg.left_hand_75kg as lh75
import data.right_hand_70kg.right_hand_70kg as rh70
from grinev_algorithm import TournamentGraphConstructor

names, pairs = lh75.names, lh75.pairs
#names, pairs = rh70.names, rh70.pairs

plt.rcParams["figure.figsize"] = (20, 10)


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

for name in top_sort:
    for rank, name_dict in names.items():
        if name == name_dict:
            print(rank, "\t", name)