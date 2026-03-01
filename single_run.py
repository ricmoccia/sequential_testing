# single_run.py
import argparse
import matplotlib.pyplot as plt

from load_graph import load_graph_from_json
from heuristics import greedy_solution, simulated_annealing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", help="Path del grafo JSON (es. test/g1.json)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--save", default=None, help="Se vuoi salvare il plot (es. sa.png)")
    args = parser.parse_args()

    # carica grafo
    problem = load_graph_from_json(args.graph)

    print("File:", args.graph)
    print("Nodes:", len(problem.nodes), "Edges:", problem.G.number_of_edges())

    # greedy
    g_order, g_cost = greedy_solution(problem)
    print("\nGREEDY cost =", g_cost)
    print("GREEDY order =", " -> ".join(map(str, g_order)))

    # simulated annealing (parametri default già nel repo)
    sa_order, sa_cost, history = simulated_annealing(problem, seed=args.seed)
    print("\nSA cost =", sa_cost)
    print("SA order =", " -> ".join(map(str, sa_order)))

    # plot semplice andamento SA
    steps = [h["step"] for h in history]
    current = [h["current_cost"] for h in history]
    best = [h["best_cost"] for h in history]

    plt.plot(steps, current, label="current")
    plt.plot(steps, best, label="best")
    plt.xlabel("step")
    plt.ylabel("expected cost")
    plt.title("Simulated Annealing")
    plt.legend()

    if args.save:
        plt.savefig(args.save, dpi=200, bbox_inches="tight")
        print("\nPlot salvato in:", args.save)
    else:
        plt.show()


if __name__ == "__main__":
    main()
