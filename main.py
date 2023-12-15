import logging

import matplotlib.pyplot as plt
import networkx as nx

import data.left_hand_80kg.left_hand_80kg as lh80
import data.left_hand_75kg.left_hand_75kg as lh75
import data.right_hand_70kg.right_hand_70kg as rh70
from grinev_algorithm import TournamentGraphConstructor
from topological_sort import calc_and_save_places

names, pairs = lh75.names, lh75.pairs
# names, pairs = rh70.names, rh70.pairs
# names, pairs = lh80.names, lh80.pairs

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

logger.info("names for tournament %s", names)
logger.info("pairs for tournament %s", pairs)

plt.rcParams["figure.figsize"] = (20, 10)


def run_alg():
    alg = TournamentGraphConstructor(names, pairs)
    graph = alg.make_graph()

    pos = nx.circular_layout(graph)
    nx.draw_networkx(graph, pos=pos, with_labels=True, node_size=5000)
    plt.show()


def save_graph():
    alg = TournamentGraphConstructor(names, pairs)
    alg.save_edgelist()
    calc_and_save_places(names, pairs)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    save_graph()
