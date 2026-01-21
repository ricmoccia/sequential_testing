# batch_run.py
import os
import glob
import time
import pandas as pd

from io_json import load_problem_from_json_bytes
from heuristics import greedy_solution, simulated_annealing
from exact import exact_optimum


def load_problem_from_json_file(path):
    """Carica un problema da file JSON (senza validazione avanzata)."""
    with open(path, "rb") as f:
        content = f.read()
    return load_problem_from_json_bytes(content)


def run_batch(
    folder="test",
    out_excel="batch_results.xlsx",
    do_exact=True,
    exact_limit=12,
    # parametri SA
    T_start=1.0,
    T_end=1e-3,
    alpha=0.98,
    iters_per_T=200,
    max_steps=15000,
    seed=42,
):
    """
    Esegue Greedy + SA (e opzionalmente Exact) su tutti i JSON in folder,
    e salva i risultati in un file Excel.
    """
    pattern = os.path.join(folder, "*.json")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"[Batch] Nessun file .json trovato in: {folder}")
        return

    results = []

    print(f"[Batch] Trovati {len(files)} file JSON in '{folder}'")

    for path in files:
        fname = os.path.basename(path)
        print(f"\n=== {fname} ===")

        # -------------------------
        # 1) Caricamento
        # -------------------------
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

        # -------------------------
        # 2) Greedy
        # -------------------------
        t0 = time.perf_counter()
        greedy_order, greedy_cost = greedy_solution(problem)
        greedy_time = time.perf_counter() - t0
        print(f"  Greedy cost={greedy_cost:.4f}  time={greedy_time:.3f}s")

        # -------------------------
        # 3) Simulated Annealing
        # -------------------------
        t0 = time.perf_counter()
        sa_order, sa_cost, history = simulated_annealing(
            problem,
            T_start=T_start,
            T_end=T_end,
            alpha=alpha,
            iters_per_T=iters_per_T,
            max_steps=max_steps,
            seed=seed
        )
        sa_time = time.perf_counter() - t0
        print(f"  SA     cost={sa_cost:.4f}  time={sa_time:.3f}s")

        # Gap rispetto a Greedy (utile anche quando non fai exact)
        gap_sa_vs_greedy = None
        if greedy_cost > 0:
            gap_sa_vs_greedy = (sa_cost - greedy_cost) / greedy_cost

        # -------------------------
        # 4) Exact (opzionale)
        # -------------------------
        opt_order, opt_cost, opt_time = None, None, None
        gap_greedy_vs_opt = None
        gap_sa_vs_opt = None

        if do_exact and n_nodes <= exact_limit:
            t0 = time.perf_counter()
            opt_order, opt_cost = exact_optimum(problem)
            opt_time = time.perf_counter() - t0
            print(f"  OPT    cost={opt_cost:.4f}  time={opt_time:.3f}s")

            # gap relativi vs optimum
            if opt_cost > 0:
                gap_greedy_vs_opt = (greedy_cost - opt_cost) / opt_cost
                gap_sa_vs_opt = (sa_cost - opt_cost) / opt_cost
        else:
            if do_exact:
                print(f"  OPT saltato (n_nodes={n_nodes} > {exact_limit})")

        # -------------------------
        # 5) Salvataggio riga risultati
        # -------------------------
        results.append({
            "file": fname,
            "status": "ok",
            "error": "",
            "n_nodes": n_nodes,
            "n_edges": n_edges,

            "greedy_cost": greedy_cost,
            "sa_cost": sa_cost,
            "opt_cost": opt_cost,

            "gap_sa_vs_greedy": gap_sa_vs_greedy,
            "gap_greedy_vs_opt": gap_greedy_vs_opt,
            "gap_sa_vs_opt": gap_sa_vs_opt,

            "greedy_time_s": greedy_time,
            "sa_time_s": sa_time,
            "opt_time_s": opt_time,

            # ordini (stringhe, comode in Excel)
            "greedy_order": " -> ".join(map(str, greedy_order)),
            "sa_order": " -> ".join(map(str, sa_order)),
            "opt_order": (" -> ".join(map(str, opt_order)) if opt_order else None),
        })

    df = pd.DataFrame(results)
    df.to_excel(out_excel, index=False)
    print(f"\n[Batch] Risultati salvati in: {out_excel}")


if __name__ == "__main__":
    run_batch(
        folder="test",
        out_excel="batch_results.xlsx",
        do_exact=True,
        exact_limit=12,
        T_start=1.0,
        T_end=1e-3,
        alpha=0.98,
        iters_per_T=200,
        max_steps=15000,
        seed=42,
    )
