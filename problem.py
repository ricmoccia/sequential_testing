# problem.py
import random
import networkx as nx
from dataclasses import dataclass


@dataclass
class TestData:
    """Dati associati a ogni test/nodo."""
    p_success: float  # Probabilità di successo
    cost: float       # Costo del test


class SequentialTestingProblem:
    """
    Incapsula:
    - DAG (precedenze)
    - p_i e c_i su ogni nodo
    - funzione costo atteso di un ordine
    - mosse che rispettano il DAG
    """
    def __init__(self, G: nx.DiGraph, test_data: dict):
        self.G = G
        self.test_data = test_data
        self.nodes = list(G.nodes())

    def is_topological_order(self, order):
        """Controlla se 'order' rispetta tutte le precedenze (archi u->v)."""
        pos = {v: i for i, v in enumerate(order)}
        for u, v in self.G.edges():
            if pos[u] >= pos[v]:
                return False
        return True

    def random_topological_order(self):
        """Genera un ordinamento topologico casuale (valido)."""
        # networkx genera un topological order; poi facciamo qualche swap valido
        order = list(nx.topological_sort(self.G))
        for _ in range(2 * len(order)):
            i, j = random.sample(range(len(order)), 2)
            new_order = self.try_swap(order, i, j)
            if new_order is not None:
                order = new_order
        return order

    def expected_cost(self, order):
        """
        Costo atteso assumendo:
        - esegui i test in sequenza
        - ti fermi al primo fallimento

        E[C] = sum_k c_k * prod_{j<k} p_j
        """
        exp_cost = 0.0
        prob_reach = 1.0
        for v in order:
            exp_cost += self.test_data[v].cost * prob_reach
            prob_reach *= self.test_data[v].p_success
        return exp_cost

    def try_swap(self, order, i, j):
        """
        Swap di due posizioni i,j.
        Se l'ordine rimane topologico -> restituisce il nuovo ordine,
        altrimenti -> None.
        """
        if i == j:
            return list(order)

        new_order = list(order)
        new_order[i], new_order[j] = new_order[j], new_order[i]

        if self.is_topological_order(new_order):
            return new_order
        return None
