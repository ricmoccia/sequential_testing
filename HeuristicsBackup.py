# heuristics.py
import random
import math


def greedy_solution(problem):
    """
    Euristica greedy semplice:
    finché ci sono nodi disponibili (in-degree 0 tra i rimanenti),
    scegli quello con score minimo cost/p.

    Nota: possiamo sperimentare piu avanti con lo score usando es., cost*(1-p)/p
    """
    G = problem.G
    indeg = {u: G.in_degree(u) for u in G.nodes()}
    chosen = []
    used = set()

    available = [u for u in G.nodes() if indeg[u] == 0]

    while available:
        best = min(available, key=lambda u: problem.test_data[u].cost / problem.test_data[u].p_success)
        chosen.append(best)
        used.add(best)
        available.remove(best)

        for v in G.successors(best):
            indeg[v] -= 1
            if indeg[v] == 0 and v not in used:
                available.append(v)

    return chosen, problem.expected_cost(chosen)


def simulated_annealing(problem, T_start=1.0, T_end=1e-3, alpha=0.98,
                       iters_per_T=200, max_steps=15000, seed=42):
    """
    Simulated Annealing con mossa = swap.
    Restituisce: best_order, best_cost, history
    history è una lista di dict per fare plot:
      {step, T, current_cost, best_cost}
    """
    random.seed(seed)

    current = problem.random_topological_order()
    current_cost = problem.expected_cost(current)

    best = list(current)
    best_cost = current_cost

    history = [{"step": 0, "T": T_start, "current_cost": current_cost, "best_cost": best_cost}]

    T = T_start
    step = 0

    while T > T_end and step < max_steps:
        for _ in range(iters_per_T):
            step += 1

            i, j = random.sample(range(len(current)), 2)
            neighbor = problem.try_swap(current, i, j)
            if neighbor is None:
                continue

            neighbor_cost = problem.expected_cost(neighbor)
            delta = neighbor_cost - current_cost

            # regola SA: accetta se migliora, altrimenti con prob exp(-delta/T)
            accept = (delta < 0) or (random.random() < math.exp(-delta / T))

            if accept:
                current, current_cost = neighbor, neighbor_cost
                if current_cost < best_cost:
                    best, best_cost = list(current), current_cost

            history.append({
                "step": step,
                "T": T,
                "current_cost": current_cost,
                "best_cost": best_cost
            })

            if step >= max_steps:
                break

        T *= alpha

    return best, best_cost, history
