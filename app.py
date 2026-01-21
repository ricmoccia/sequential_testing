# app.py
import io
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

from io_json import load_problem_from_json_bytes
from heuristics import greedy_solution, simulated_annealing
from exact import exact_optimum
from graph_viz import show_dag


def format_order_inline(order) -> str:
    """Converte un ordine in una stringa compatta: A → B → C."""
    return " \u2192 ".join(str(x) for x in order)


st.title("Sequential Testing Problem — Demo")

st.write("""
Carica un file JSON con:
- **nodes**: lista di `{id, p, cost}`
- **edges**: lista di coppie `[u, v]`
""")

uploaded = st.file_uploader("Carica file JSON", type=["json"])

# -----------------------------
# Sidebar: parametri SA
# -----------------------------
st.sidebar.header("Simulated Annealing")
T_start = st.sidebar.slider("T_start", 0.1, 5.0, 1.0)
T_end = st.sidebar.slider("T_end", 1e-4, 0.1, 0.001)
alpha = st.sidebar.slider("alpha", 0.90, 0.999, 0.98)
iters_per_T = st.sidebar.slider("iters_per_T", 50, 500, 200)
max_steps = st.sidebar.slider("max_steps", 500, 50000, 15000)

# Ottimo esatto
st.sidebar.header("Ottimo esatto")
do_exact = st.sidebar.checkbox("Calcola ottimo (solo grafi piccoli)", value=True)
exact_limit = st.sidebar.slider("Limite nodi per ottimo", 5, 15, 12)

run = st.button("▶ Esegui")

# -----------------------------
# MAIN
# -----------------------------
if run:
    if uploaded is None:
        st.error("Carica prima un file JSON.")
        st.stop()

    # 1) Carica problema
    try:
        problem = load_problem_from_json_bytes(uploaded.read())
    except Exception as e:
        st.error(f"Errore nel caricamento JSON: {e}")
        st.stop()

    st.write(
        f"**Nodi:** {len(problem.nodes)} | "
        f"**Archi:** {problem.G.number_of_edges()}"
    )

    # 2) DAG
    st.subheader("DAG")
    show_dag(problem)

    # 3) Greedy
    st.subheader("Greedy")
    greedy_order, greedy_cost = greedy_solution(problem)
    st.write("**Ordine Greedy:**", format_order_inline(greedy_order))
    st.write(f"**Costo Greedy:** {greedy_cost:.4f}")

    # 4) SA
    st.subheader("Simulated Annealing")
    sa_order, sa_cost, history = simulated_annealing(
        problem,
        T_start=T_start,
        T_end=T_end,
        alpha=alpha,
        iters_per_T=iters_per_T,
        max_steps=max_steps,
        seed=42
    )
    st.write("**Ordine SA:**", format_order_inline(sa_order))
    st.write(f"**Costo SA:** {sa_cost:.4f}")

    # 5) Ottimo esatto (opzionale)
    opt_order, opt_cost = None, None
    if do_exact and len(problem.nodes) <= exact_limit:
        st.subheader("Ottimo esatto")
        opt_order, opt_cost = exact_optimum(problem)
        st.write("**Ordine ottimo:**", format_order_inline(opt_order))
        st.write(f"**Costo ottimo:** {opt_cost:.4f}")
    elif do_exact:
        st.info(f"Ottimo saltato: troppi nodi (>{exact_limit}).")

    # 6) Plot convergenza SA
    st.subheader("Convergenza SA")

    steps = [h["step"] for h in history]
    curr = [h["current_cost"] for h in history]
    best = [h["best_cost"] for h in history]

    fig, ax = plt.subplots()
    ax.plot(steps, curr, label="current")
    ax.plot(steps, best, label="best", linestyle="--")
    ax.axhline(greedy_cost, linestyle="-.", label="greedy")

    if opt_cost is not None:
        ax.axhline(opt_cost, linestyle=":", label="opt")

    ax.set_xlabel("step")
    ax.set_ylabel("expected cost")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # 7) Export Excel
    st.subheader("Export Excel")

    rows = [
        {"Algoritmo": "Greedy", "Costo": greedy_cost, "Ordine": format_order_inline(greedy_order)},
        {"Algoritmo": "Simulated Annealing", "Costo": sa_cost, "Ordine": format_order_inline(sa_order)},
    ]
    if opt_cost is not None:
        rows.append({"Algoritmo": "Ottimo", "Costo": opt_cost, "Ordine": format_order_inline(opt_order)})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="results")
    buffer.seek(0)

    st.download_button(
        "💾 Scarica risultati.xlsx",
        data=buffer,
        file_name="risultati.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
