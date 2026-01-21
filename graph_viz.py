# graph_viz.py
import os
import tempfile
import streamlit as st
from pyvis.network import Network

def show_dag(problem):
    G = problem.G
    net = Network(height="650px", width="100%", directed=True)

    net.set_options("""
    {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "UD",
          "sortMethod": "directed",
          "levelSeparation": 110,
          "nodeSpacing": 160
        }
      },
      "physics": { "enabled": false }
    }
    """)

    for node in G.nodes():
        p = problem.test_data[node].p_success
        c = problem.test_data[node].cost

        # label nodo
        label = f"{node}  p={p:.2f}  c={c:.1f}"
        net.add_node(node, label=label, shape="box", margin=10)

    for u, v in G.edges():
        net.add_edge(u, v, arrows="to")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        html_path = tmp.name

    net.write_html(html_path, notebook=False)

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=650, scrolling=True)

    try:
        os.remove(html_path)
    except:
        pass
