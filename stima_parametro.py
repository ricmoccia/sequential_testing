import os
import math
import csv
import argparse
import random
from statistics import median

from load_graph import load_graph_from_json
"""
python stima_parametro.py --folder testN10 --out stima_N10.xlsx
python stima_parametro.py --folder testN15 --out stima_N15.xlsx
python stima_parametro.py --folder testN20 --out stima_N20.xlsx
"""


def quantile(sorted_vals, q):
    """q in [0,1]. sorted_vals must be sorted."""
    if not sorted_vals:
        return None
    if q <= 0:
        return sorted_vals[0]
    if q >= 1:
        return sorted_vals[-1]
    pos = q * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_vals[lo]
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def estimate_T_start(problem, samples=1000, p0=0.8, repeats=3, seed=42):
    """
    Stima T_start dal grafo.
    - samples: tentativi swap per ogni repeat
    - repeats: quante soluzioni iniziali random (migliora robustezza)
    - p0: prob. target di accettare un peggioramento "tipico" all'inizio (0.7-0.9)
    """
    rng = random.Random(seed)
    n = len(problem.nodes)

    deltas_pos = []

    for r in range(repeats):
        # ordine topologico casuale
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
        return None, None  # non stimabile (troppi swap invalidi o delta mai > 0)

    deltas_pos.sort()
    d_typ = quantile(deltas_pos, 0.50)  # mediana dei delta positivi

    # T_start = - d / ln(p0)
    T_start = - d_typ / math.log(p0)
    return float(T_start), float(d_typ)


def list_json_files(folder):
    files = []
    for name in os.listdir(folder):
        if name.lower().endswith(".json"):
            files.append(os.path.join(folder, name))
    files.sort()
    return files


def write_xlsx(out_xlsx, rows):
    # minimale: una sola sheet con header
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "stima_T"

    header = list(rows[0].keys()) if rows else []
    ws.append(header)
    for r in rows:
        ws.append([r.get(k) for k in header])

    wb.save(out_xlsx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", help="Path di un singolo grafo JSON")
    ap.add_argument("--folder", help="Cartella con grafi JSON (batch)")

    ap.add_argument("--samples", type=int, default=1000)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--p0", type=float, default=0.8)
    ap.add_argument("--seed", type=int, default=42)

    ap.add_argument("--T_end_frac", type=float, default=0.01, help="T_end = T_start * frac (default 0.01)")
    ap.add_argument("--out", default="stima_T.csv", help="Output .csv o .xlsx")

    args = ap.parse_args()

    if (args.graph is None) == (args.folder is None):
        raise SystemExit("Usa ESATTAMENTE uno tra --graph oppure --folder")

    paths = [args.graph] if args.graph else list_json_files(args.folder)
    if not paths:
        raise SystemExit("Nessun file .json trovato.")

    rows = []
    T_starts = []

    for path in paths:
        problem = load_graph_from_json(path)

        T_start, d_typ = estimate_T_start(
            problem,
            samples=args.samples,
            p0=args.p0,
            repeats=args.repeats,
            seed=args.seed
        )

        n = len(problem.nodes)
        m = problem.G.number_of_edges()

        if T_start is None:
            # fallback sensato (se non stimabile)
            T_start = 300.0
            d_typ = None

        T_end = T_start * args.T_end_frac

        # suggerimenti "tipici" per gli altri parametri (puoi cambiarli)
        iters_per_T = 50 * n
        max_steps = 5000 * n

        rows.append({
            "file": os.path.basename(path),
            "path": path,
            "n": n,
            "m": m,
            "p0": args.p0,
            "samples": args.samples,
            "repeats": args.repeats,
            "d_typ": d_typ,
            "T_start": T_start,
            "T_end": T_end,
            "alpha_suggested": 0.99,
            "iters_per_T_suggested": iters_per_T,
            "max_steps_suggested": max_steps,
        })

        T_starts.append(T_start)

    # summary globale (utile per scegliere un T_start unico per tutti)
    T_starts_sorted = sorted(T_starts)
    summary = {
        "count": len(T_starts_sorted),
        "T_start_median": quantile(T_starts_sorted, 0.50),
        "T_start_p25": quantile(T_starts_sorted, 0.25),
        "T_start_p75": quantile(T_starts_sorted, 0.75),
    }

    print("\n=== SUMMARY ===")
    for k, v in summary.items():
        print(k, "=", v)

    # scrittura output
    out = args.out
    if out.lower().endswith(".xlsx"):
        write_xlsx(out, rows)
    else:
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    print("\nScritto:", out)


if __name__ == "__main__":
    main()
