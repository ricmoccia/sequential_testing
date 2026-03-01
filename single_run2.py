import argparse
import time
import matplotlib.pyplot as plt
# esegui su tutte euristiche: python single_run2.py testN10/grafo_01.json --algo greedy_cp greedy_cfail sa
# per plot: python single_run2.py testN10/grafo_01.json --algo sa --plot_sa
# per salvare plot: python single_run.py testN10/grafo_01.json --algo sa --save_sa sa_plot.png  

from io_json import load_problem_from_json_bytes
from heuristics import greedy_solution, simulated_annealing


def load_problem(path):
    with open(path, "rb") as f:
        return load_problem_from_json_bytes(f.read())


def plot_sa_history(history, save=None):
    steps = [h["step"] for h in history]
    current = [h["current_cost"] for h in history]
    best = [h["best_cost"] for h in history]

    plt.figure()
    plt.plot(steps, current, label="current")
    plt.plot(steps, best, label="best")
    plt.xlabel("step")
    plt.ylabel("expected cost")
    plt.title("Simulated Annealing")
    plt.legend()

    if save:
        plt.savefig(save, dpi=200, bbox_inches="tight")
        print("Plot salvato in:", save)
    else:
        plt.show()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("graph", help="Path del grafo JSON (es. testN10/g1.json)")

    # quali algoritmi eseguire
    p.add_argument(
        "--algo",
        nargs="+",
        default=["greedy_cp", "greedy_cfail", "sa"],
        choices=["greedy_cp", "greedy_cfail", "sa"],
        help="Algoritmi da eseguire (default: greedy_cp sa)"
    )

    # SA params
    p.add_argument("--T_start", type=float, default=50.0)
    p.add_argument("--T_end", type=float, default=1.0)
    p.add_argument("--alpha", type=float, default=0.99)
    p.add_argument("--iters_per_T", type=int, default=500)
    p.add_argument("--max_steps", type=int, default=50000)
    p.add_argument("--seed", type=int, default=42)

    # plot SA (opzionale)
    p.add_argument("--plot_sa", action="store_true", help="Mostra il plot dell'andamento SA")
    p.add_argument("--save_sa", default=None, help="Salva plot SA (es. sa.png)")

    args = p.parse_args()

    problem = load_problem(args.graph)

    print("File:", args.graph)
    print("Nodes:", len(problem.nodes), "Edges:", problem.G.number_of_edges())

    # ------------------------------------------------------------------
    # Plot grafo (PER ORA COMMENTATO)
    # ------------------------------------------------------------------
    # import networkx as nx
    # pos = nx.spring_layout(problem.G, seed=1)
    # nx.draw(problem.G, pos, with_labels=True, node_size=600)
    # plt.show()

    # ------------------------------------------------------------------
    # GREEDY c/p
    # ------------------------------------------------------------------
    if "greedy_cp" in args.algo:
        t0 = time.perf_counter()
        order, cost = greedy_solution(problem, mode="c_over_p")
        dt = time.perf_counter() - t0
        print("\n[Greedy c/p]")
        print("cost =", cost, "| time =", f"{dt:.4f}s")
        print("order =", " -> ".join(map(str, order)))

    # ------------------------------------------------------------------
    # GREEDY c/(1-p)
    # ------------------------------------------------------------------
    if "greedy_cfail" in args.algo:
        t0 = time.perf_counter()
        order, cost = greedy_solution(problem, mode="c_over_fail")
        dt = time.perf_counter() - t0
        print("\n[Greedy c/(1-p)]")
        print("cost =", cost, "| time =", f"{dt:.4f}s")
        print("order =", " -> ".join(map(str, order)))

    # ------------------------------------------------------------------
    # SIMULATED ANNEALING
    # ------------------------------------------------------------------
    if "sa" in args.algo:
        t0 = time.perf_counter()
        sa_order, sa_cost, history = simulated_annealing(
            problem,
            T_start=args.T_start,
            T_end=args.T_end,
            alpha=args.alpha,
            iters_per_T=args.iters_per_T,
            max_steps=args.max_steps,
            seed=args.seed,
            record_every_step=True,   # per plot (se vuoi history compatta metti False)
        )
        dt = time.perf_counter() - t0

        print("\n[Simulated Annealing]")
        print("params: ",
              f"T_start={args.T_start}, T_end={args.T_end}, alpha={args.alpha}, "
              f"iters_per_T={args.iters_per_T}, max_steps={args.max_steps}, seed={args.seed}")
        print("cost =", sa_cost, "| time =", f"{dt:.4f}s")
        print("order =", " -> ".join(map(str, sa_order)))

        if args.plot_sa or args.save_sa:
            plot_sa_history(history, save=args.save_sa)


if __name__ == "__main__":
    main()