"""
There is Grinev tournament algorithm (GrinTour algorithm), principles

    1. Пронумеровываем спортсменов после жеребьёвки (порядок в первом туре).
    2. Представляем турнир (сетку) как набор пар (n[i],n[j]), где n[j] победил n[i].
    3. Берем того, кто не победил ни разу (n[k]). Записываем в первой строке вспомогательного массива (n[k1],n[l1]),
    а во вторую строку (n[k1],n[l2]), где n[l1] и n[l2] - те, кто победил n[k1].
    4. Аналогично записываем в 3-ю и 4-ю строки пары с победителями второго спортсмена без побед.
    И т.д. - проходимся по всем без побед (начала цепочек будут именно с них).
    5. На второй итерации ищем (удлиняем ранее полученные цепочки) тех, кто победил победителя того, кто был без побед.
    Пример: (n[k1],n[l1],n[m1]), (n[k1],n[l1],n[m2]), (n[k1],n[l2],n[v2]) и (n[k1],n[l2],n[v2]). Таким образом увеличиваем цепочки.
    Повторяющиеся цепочки выбрасываем. Также можно выбрасывать короткие цепочки, которые имеют на конце победителя категории.
    Тут важно не выкинуть нужные цепочки, которые образутся в конце этого процесса.
    6. Продолжая этот процесс до конца, получим небольшой набор цепочек от тех, кто не выиграл ни одного поединка до того,
    кто занял первое место.
    7. Берем самые длинные цепочки с началом в не победивших ни разу и концом в победителе категории.
    Если цепочки равной максимальной длины, то берем обе.
    8. Ищем пересечения этих цепочек и строим итоговый граф (данный пункт не до конца формализован).
    тут есть ошибки, но для понимания принципа пойдет]

    input: networkx graph
    output: list of participants distributed by places

"""
import logging
from collections import Counter

import networkx
import networkx as nx

from utils import append2lists, drop_duplicates, get_max_chains

logger = logging.getLogger("algorithm")
logging.basicConfig()
logger.setLevel(logging.INFO)


class TournamentGraphConstructor:
    """Implementation of GrinTour algorithm"""

    def __init__(self, names: dict, pairs: list):
        self.names = names
        self.pairs = pairs

    def find_winner(self, sportsman: str) -> list:
        """Поиск спортсменов выигравших sportsman"""
        winners = []
        for pair in self.pairs:
            is_winner_condition = sportsman == pair[0] and pair[0] != "" \
                                  and pair[1] not in winners
            if is_winner_condition:
                winners.append(pair[1])
        return winners

    def find_total_losers(self) -> list:
        """Поиск ни разу не выигравших спортсменов"""
        total_losers = []
        for name in self.names.values():
            is_total_loser = True
            for pair in self.pairs:
                if name in pair[1]:
                    is_total_loser = False
            if is_total_loser:
                total_losers.append(name)
        logger.debug("total losers list %s", total_losers)
        return total_losers

    def make_chains(self, first_sportsman: str) -> list:
        """Нахождение всех цепочек от first_sportsman"""
        chain = [[first_sportsman]]
        sportsmen = [first_sportsman]
        stop_condition = True
        while stop_condition:
            for sportsman in sportsmen:
                winners = self.find_winner(sportsman)
                if len(winners) == 1:
                    chain = append2lists(chain, sportsman, winners[0])
                    sportsmen = winners
                    logger.debug("There is only one winner of %s, %s", sportsman, winners)
                elif len(winners) > 1:
                    chain_upd = []
                    logger.debug("There are more than one winner of %s, %s", sportsman, winners)
                    for winner in winners:
                        chain_winner = append2lists(chain, sportsman, winner)
                        chain_upd.extend(chain_winner)
                    chain = chain_upd
                    logger.debug("Updated chain %s", chain_upd)
                    sportsmen = winners
                elif not winners:
                    stop_condition = False
                    logger.debug("There are not winner of %s, chain ended", sportsman)
        return chain

    def make_all_chains(self) -> dict:
        """Нахождение всех цепочек от всех ни разу не выигравших спортсменов"""
        total_losers = self.find_total_losers()
        all_chains = {}
        for loser in total_losers:
            logger.info("Start chain construction for %s", loser)
            chain = drop_duplicates(self.make_chains(first_sportsman=loser))
            logger.info("Result chains for %s is %s", loser, chain)
            all_chains[loser] = chain
        return all_chains

    def make_graph(self) -> networkx.Graph:
        """Построение графа NX"""
        chains = self.make_all_chains()
        longest_chains = []
        for start_pos, chain in chains.items():
            max_chains = get_max_chains(chain)
            longest_chains.extend(max_chains)

        all_edges = []
        for chain in longest_chains:
            edges = [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]
            all_edges.extend(edges)
        edge_counter = Counter(all_edges)
        weighted_edges = []
        for edge, count in edge_counter.items():
            weighted_edges.append((edge[1], edge[0], count))
        graph = nx.DiGraph()
        graph.add_weighted_edges_from(weighted_edges)

        return graph

    def save_edgelist(self):
        """Сохранение графа в файл edgelist.txt"""
        chains = self.make_all_chains()
        longest_chains = []
        for start_pos, chain in chains.items():
            max_chains = get_max_chains(chain)
            longest_chains.extend(max_chains)

        all_edges = []
        for chain in longest_chains:
            edges = [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]
            all_edges.extend(edges)
        edge_counter = dict(Counter(all_edges))

        with open("edgelist.txt", "w", encoding="utf-8") as file:
            edges_number = len(edge_counter.values())
            file.write(f"{edges_number}\n")
            for edge, count in edge_counter.items():
                file.write(f"{edge[1]} {edge[0]} {count}\n")

        logger.info("File edgelist.txt saved")