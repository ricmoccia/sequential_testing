# io_json.py
import json
import networkx as nx
from problem import SequentialTestingProblem, TestData


def load_problem_from_json_bytes(json_bytes: bytes) -> SequentialTestingProblem:
    """
    Carica un problema da bytes JSON (utile per Streamlit upload).
    Nessuna validazione avanzata: se il JSON è malformato Python lancerà errore.
    """
    data = json.loads(json_bytes.decode("utf-8"))

    G = nx.DiGraph()
    test_data = {}

    # nodi
    for n in data["nodes"]:
        node_id = n["id"]
        p = float(n["p"])
        c = float(n["cost"])
        G.add_node(node_id)
        test_data[node_id] = TestData(p_success=p, cost=c)

    # archi
    for u, v in data["edges"]:
        G.add_edge(u, v)

    # qui facciamo solo un controllo “soft”
    # (se non è DAG, i metodi non hanno senso)
    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("Il grafo caricato NON è un DAG (contiene cicli).")

    return SequentialTestingProblem(G, test_data)
