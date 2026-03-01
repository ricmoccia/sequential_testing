# heuristics.py
import random
import math
import time


def greedy_solution(problem, mode="c_over_p"):
    """
    Greedy su DAG: finché ci sono nodi disponibili (in-degree 0),
    scegli quello con score minimo.

    mode:
      - "c_over_p"    : cost / p_success  (la tua attuale baseline)
      - "c_over_fail" : cost / (1 - p_success)  (più coerente col costo atteso con stop)
    """
    G = problem.G
    indeg = {u: G.in_degree(u) for u in G.nodes()}
    chosen = []
    used = set()

    available = [u for u in G.nodes() if indeg[u] == 0]

    def score(u):
        c = problem.test_data[u].cost
        p = problem.test_data[u].p_success
        if mode == "c_over_p":
            return c / p
        elif mode == "c_over_fail":
            q = max(1e-12, 1.0 - p)
            return c / q
        else:
            raise ValueError("mode must be 'c_over_p' or 'c_over_fail'")

    while available:
        best = min(available, key=score)
        chosen.append(best)
        used.add(best)
        available.remove(best)

        for v in G.successors(best):
            indeg[v] -= 1
            if indeg[v] == 0 and v not in used:
                available.append(v)

    return chosen, problem.expected_cost(chosen)


def simulated_annealing(problem, T_start=1.0, T_end=1e-3, alpha=0.98,
                       iters_per_T=200, max_steps=15000, seed=42,
                       record_every_step=True):
    """
    Simulated Annealing con mossa = swap.
    Restituisce: best_order, best_cost, history

    Se record_every_step=True  -> history contiene un record per ogni step (più pesante).
    Se record_every_step=False -> history contiene SOLO l'iniziale + i miglioramenti del best
                                 (perfetto per batch + tempo del best finale).
    Ogni record include anche t_s = secondi trascorsi dall'inizio della SA.
    """
    random.seed(seed)
    t0 = time.perf_counter()

    current = problem.random_topological_order()
    current_cost = problem.expected_cost(current)

    best = list(current)
    best_cost = current_cost

    history = [{
        "step": 0,
        "T": T_start,
        "current_cost": current_cost,
        "best_cost": best_cost,
        "t_s": 0.0
    }]

    T = T_start
    step = 0

    while T > T_end and step < max_steps:
        for _ in range(iters_per_T):
            step += 1

            i, j = random.sample(range(len(current)), 2)
            neighbor = problem.try_swap(current, i, j)

            # swap invalido -> non cambia nulla
            if neighbor is None:
                if record_every_step:
                    history.append({
                        "step": step,
                        "T": T,
                        "current_cost": current_cost,
                        "best_cost": best_cost,
                        "t_s": time.perf_counter() - t0
                    })
                if step >= max_steps:
                    break
                continue

            neighbor_cost = problem.expected_cost(neighbor)
            delta = neighbor_cost - current_cost

            accept = (delta < 0) or (random.random() < math.exp(-delta / T))

            if accept:
                current, current_cost = neighbor, neighbor_cost

                # miglioramento best
                if current_cost < best_cost:
                    best, best_cost = list(current), current_cost
                    if not record_every_step:
                        history.append({
                            "step": step,
                            "T": T,
                            "current_cost": current_cost,
                            "best_cost": best_cost,
                            "t_s": time.perf_counter() - t0
                        })

            if record_every_step:
                history.append({
                    "step": step,
                    "T": T,
                    "current_cost": current_cost,
                    "best_cost": best_cost,
                    "t_s": time.perf_counter() - t0
                })

            if step >= max_steps:
                break

        T *= alpha

    return best, best_cost, history