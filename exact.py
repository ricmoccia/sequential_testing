# exact.py
import networkx as nx


def all_topological_sorts(G: nx.DiGraph):
    """
    Generatore: enumera tutti gli ordinamenti topologici (backtracking).
    Attenzione: può esplodere -> usarlo solo per pochi nodi.
    """
    indeg = {u: G.in_degree(u) for u in G.nodes()}
    used = set()
    order = []

    def backtrack():
        candidates = [u for u in G.nodes() if indeg[u] == 0 and u not in used]
        if not candidates:
            if len(order) == len(G.nodes()):
                yield list(order)
            return

        for u in candidates:
            used.add(u)
            order.append(u)

            changed = []
            for v in G.successors(u):
                indeg[v] -= 1
                changed.append(v)

            yield from backtrack()

            for v in changed:
                indeg[v] += 1
            order.pop()
            used.remove(u)

    yield from backtrack()


def exact_optimum(problem):
    """Trova ordine ottimo enumerando tutti i topological sorts."""
    best_order = None
    best_cost = float("inf")

    for order in all_topological_sorts(problem.G):
        c = problem.expected_cost(order)
        if c < best_cost:
            best_cost = c
            best_order = order

    return best_order, best_cost
