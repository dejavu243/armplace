import logging

import matplotlib.pyplot as plt
import networkx as nx

from data.left_hand_75kg.left_hand_75kg import names, pairs
from grinev_algorithm import TournamentGraphConstructor

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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_alg()
