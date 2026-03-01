# batch_run.py
# Script per eseguire un batch di test su tutti i file JSON in una cartella.
#es run: >python batch_run.py --folder testN10 --out risultati_N10.xlsx
import os
import glob
import time
import math
import argparse
import pandas as pd

from io_json import load_problem_from_json_bytes
from heuristics import greedy_solution, simulated_annealing
from exact import exact_optimum


def load_problem_from_json_file(path):
    with open(path, "rb") as f:
        content = f.read()
    return load_problem_from_json_bytes(content)


def estimate_T_start(problem, samples=1000, repeats=3, p0=0.8, seed=42):
    """
    Stima T_start dal grafo usando la mediana dei delta peggiorativi (delta>0)
    e formula T_start = -d / ln(p0).
    Ritorna (T_start, d_typ) oppure (None, None) se non stimabile.
    """
    import random
    rng = random.Random(seed)

    order = problem.random_topological_order()
    base_cost = problem.expected_cost(order)
    n = len(order)

    deltas_pos = []

    for _ in range(repeats):
        order = problem.random_topological_order()
        base_cost = problem.expected_cost(order)

        for _ in range(samples):
            i, j = rng.sample(range(n), 2)
            neigh = problem.try_swap(order, i, j)
            if neigh is None:
                continue
            d = problem.expected_cost(neigh) - base_cost
            if d > 0:
                deltas_pos.append(d)

    if not deltas_pos:
        return None, None

    deltas_pos.sort()
    d_typ = deltas_pos[len(deltas_pos) // 2]  # mediana
    T_start = -d_typ / math.log(p0)
    return float(T_start), float(d_typ)


def run_batch(
    folder="test",
    out_excel="batch_results.xlsx",
    out_csv=None,
    do_exact=True,
    exact_limit=12,
    # SA params (usati se non auto_T)
    T_start=50.0,
    T_end=1.0,
    alpha=0.99,
    iters_per_T=200,
    max_steps=15000,
    seed=42,
    # auto T_start
    auto_T=False,
    auto_samples=1000,
    auto_repeats=3,
    auto_p0=0.8,
):
    pattern = os.path.join(folder, "*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"[Batch] Nessun file .json trovato in: {folder}")
        return

    # crea directory output se serve
    out_dir = os.path.dirname(out_excel)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    if out_csv:
        out_dir2 = os.path.dirname(out_csv)
        if out_dir2:
            os.makedirs(out_dir2, exist_ok=True)

    results = []
    print(f"[Batch] Trovati {len(files)} file JSON in '{folder}'")

    for path in files:
        fname = os.path.basename(path)
        print(f"\n=== {fname} ===")

        # 1) load
        try:
            problem = load_problem_from_json_file(path)
        except Exception as e:
            print(f"  ERRORE caricamento: {e}")
            results.append({
                "file": fname,
                "status": "error",
                "error": str(e),
            })
            continue

        n_nodes = len(problem.nodes)
        n_edges = problem.G.number_of_edges()
        density = None
        if n_nodes > 1:
            density = n_edges / (n_nodes * (n_nodes - 1) / 2)

        # stats cost/p
        costs = [problem.test_data[u].cost for u in problem.G.nodes()]
        ps = [problem.test_data[u].p_success for u in problem.G.nodes()]
        avg_cost = sum(costs) / len(costs) if costs else None
        avg_p = sum(ps) / len(ps) if ps else None
        min_p = min(ps) if ps else None
        max_p = max(ps) if ps else None

        # 2) Greedy c/p
        t0 = time.perf_counter()
        g1_order, g1_cost = greedy_solution(problem, mode="c_over_p")
        g1_time = time.perf_counter() - t0
        print(f"  Greedy c/p      cost={g1_cost:.4f}  time={g1_time:.3f}s")

        # 3) Greedy c/(1-p)
        t0 = time.perf_counter()
        g2_order, g2_cost = greedy_solution(problem, mode="c_over_fail")
        g2_time = time.perf_counter() - t0
        print(f"  Greedy c/(1-p)  cost={g2_cost:.4f}  time={g2_time:.3f}s")

        # 4) SA params (T_start per-grafo se auto_T)
        T_start_used = T_start
        d_typ = None
        if auto_T:
            T_est, d_est = estimate_T_start(
                problem,
                samples=auto_samples,
                repeats=auto_repeats,
                p0=auto_p0,
                seed=seed
            )
            if T_est is not None:
                T_start_used = T_est
                d_typ = d_est

        # 5) Simulated Annealing
        t0 = time.perf_counter()
        sa_order, sa_cost, history = simulated_annealing(
            problem,
            T_start=T_start_used,
            T_end=T_end,
            alpha=alpha,
            iters_per_T=iters_per_T,
            max_steps=max_steps,
            seed=seed,
            record_every_step=False,  # history compatta: iniziale + miglioramenti best
        )
        sa_time = time.perf_counter() - t0
        print(f"  SA              cost={sa_cost:.4f}  time={sa_time:.3f}s")

        # tempo in cui trovi il best finale (se heuristics.py è aggiornato con t_s)
        sa_step_to_final_best = None
        sa_time_to_final_best_s = None
        sa_time_to_final_best_frac = None
        sa_best_updates = None

        if history and isinstance(history[-1], dict):
            sa_best_updates = len(history) - 1
            sa_step_to_final_best = history[-1].get("step")
            sa_time_to_final_best_s = history[-1].get("t_s")
            if sa_time_to_final_best_s is not None and sa_time > 0:
                sa_time_to_final_best_frac = sa_time_to_final_best_s / sa_time

        # gap vs greedy
        gap_sa_vs_g1 = (sa_cost - g1_cost) / g1_cost if g1_cost and g1_cost > 0 else None
        gap_sa_vs_g2 = (sa_cost - g2_cost) / g2_cost if g2_cost and g2_cost > 0 else None

        # 6) Exact (opzionale)
        opt_cost, opt_time = None, None
        gap_g1_vs_opt, gap_g2_vs_opt, gap_sa_vs_opt = None, None, None

        if do_exact and n_nodes <= exact_limit:
            t0 = time.perf_counter()
            opt_order, opt_cost = exact_optimum(problem)
            opt_time = time.perf_counter() - t0
            print(f"  OPT             cost={opt_cost:.4f}  time={opt_time:.3f}s")

            if opt_cost and opt_cost > 0:
                gap_g1_vs_opt = (g1_cost - opt_cost) / opt_cost
                gap_g2_vs_opt = (g2_cost - opt_cost) / opt_cost
                gap_sa_vs_opt = (sa_cost - opt_cost) / opt_cost
        else:
            if do_exact:
                print(f"  OPT saltato (n_nodes={n_nodes} > {exact_limit})")
            opt_order = None

        # 7) salva riga
        results.append({
            "file": fname,
            "status": "ok",
            "error": "",

            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "density_undirected_like": density,
            "avg_cost": avg_cost,
            "avg_p": avg_p,
            "min_p": min_p,
            "max_p": max_p,

            # greedy
            "g1_mode": "c_over_p",
            "g1_cost": g1_cost,
            "g1_time_s": g1_time,
            "g1_order": " -> ".join(map(str, g1_order)),

            "g2_mode": "c_over_fail",
            "g2_cost": g2_cost,
            "g2_time_s": g2_time,
            "g2_order": " -> ".join(map(str, g2_order)),

            # SA params used
            "sa_T_start_used": T_start_used,
            "sa_T_end": T_end,
            "sa_alpha": alpha,
            "sa_iters_per_T": iters_per_T,
            "sa_max_steps": max_steps,
            "sa_seed": seed,
            "sa_auto_T": auto_T,
            "sa_auto_p0": auto_p0,
            "sa_auto_samples": auto_samples if auto_T else None,
            "sa_auto_repeats": auto_repeats if auto_T else None,
            "sa_d_typ": d_typ,

            # SA results
            "sa_cost": sa_cost,
            "sa_time_s": sa_time,
            "sa_order": " -> ".join(map(str, sa_order)),

            "sa_best_updates": sa_best_updates,
            "sa_step_to_final_best": sa_step_to_final_best,
            "sa_time_to_final_best_s": sa_time_to_final_best_s,
            "sa_time_to_final_best_frac": sa_time_to_final_best_frac,

            "gap_sa_vs_g1": gap_sa_vs_g1,
            "gap_sa_vs_g2": gap_sa_vs_g2,

            # exact
            "opt_cost": opt_cost,
            "opt_time_s": opt_time,
            "opt_order": (" -> ".join(map(str, opt_order)) if opt_order else None),

            "gap_g1_vs_opt": gap_g1_vs_opt,
            "gap_g2_vs_opt": gap_g2_vs_opt,
            "gap_sa_vs_opt": gap_sa_vs_opt,
        })

    df = pd.DataFrame(results)
    df.to_excel(out_excel, index=False)
    print(f"\n[Batch] Excel salvato in: {out_excel}")

    if out_csv:
        df.to_csv(out_csv, index=False)
        print(f"[Batch] CSV salvato in: {out_csv}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", default="test", help="Cartella con i .json (es: testN10)")
    ap.add_argument("--out", default="batch_results.xlsx", help="Output Excel (.xlsx)")
    ap.add_argument("--out_csv", default=None, help="Output CSV (opzionale)")

    ap.add_argument("--no_exact", action="store_true", help="Disabilita exact")
    ap.add_argument("--exact_limit", type=int, default=12)

    # SA base
    ap.add_argument("--T_start", type=float, default=50.0)
    ap.add_argument("--T_end", type=float, default=1.0)
    ap.add_argument("--alpha", type=float, default=0.99)
    ap.add_argument("--iters_per_T", type=int, default=200)
    ap.add_argument("--max_steps", type=int, default=15000)
    ap.add_argument("--seed", type=int, default=42)

    # auto T
    ap.add_argument("--auto_T", action="store_true", help="Stima T_start per-grafo")
    ap.add_argument("--auto_samples", type=int, default=1000)
    ap.add_argument("--auto_repeats", type=int, default=3)
    ap.add_argument("--auto_p0", type=float, default=0.8)

    args = ap.parse_args()

    run_batch(
        folder=args.folder,
        out_excel=args.out,
        out_csv=args.out_csv,
        do_exact=(not args.no_exact),
        exact_limit=args.exact_limit,
        T_start=args.T_start,
        T_end=args.T_end,
        alpha=args.alpha,
        iters_per_T=args.iters_per_T,
        max_steps=args.max_steps,
        seed=args.seed,
        auto_T=args.auto_T,
        auto_samples=args.auto_samples,
        auto_repeats=args.auto_repeats,
        auto_p0=args.auto_p0,
    )


if __name__ == "__main__":
    main()
