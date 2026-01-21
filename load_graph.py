# load_graph.py
import json
import networkx as nx
from problem import SequentialTestingProblem, TestData


class GraphValidationError(Exception):
    """Errore specifico di validazione del grafo."""
    pass


def validate_graph_data(raw: dict):
    """
    Valida la struttura del file JSON e restituisce (G, test_data).
    Lancia GraphValidationError con messaggio chiaro in caso di problemi.
    """
    if not isinstance(raw, dict):
        raise GraphValidationError("Il file JSON deve contenere un oggetto ({}).")

    if "nodes" not in raw or "edges" not in raw:
        raise GraphValidationError("Il JSON deve contenere i campi 'nodes' e 'edges'.")

    nodes_raw = raw["nodes"]
    edges_raw = raw["edges"]

    if not isinstance(nodes_raw, list):
        raise GraphValidationError("'nodes' deve essere una lista.")
    if not isinstance(edges_raw, list):
        raise GraphValidationError("'edges' deve essere una lista di coppie [u, v].")

    G = nx.DiGraph()
    test_data = {}
    node_ids = set()

    # --- Valida nodi ---
    for i, node in enumerate(nodes_raw):
        if not isinstance(node, dict):
            raise GraphValidationError(f"Nodo in posizione {i} non è un oggetto JSON.")

        for key in ("id", "p", "cost"):
            if key not in node:
                raise GraphValidationError(f"Nodo {i}: manca il campo '{key}'.")

        node_id = node["id"]
        if node_id in node_ids:
            raise GraphValidationError(f"ID nodo duplicato: {node_id}")
        node_ids.add(node_id)

        try:
            p = float(node["p"])
            c = float(node["cost"])
        except ValueError:
            raise GraphValidationError(f"Nodo {node_id}: 'p' e 'cost' devono essere numeri.")

        if not (0.0 <= p <= 1.0):
            raise GraphValidationError(f"Nodo {node_id}: probabilità p={p} fuori da [0,1].")
        if c <= 0:
            raise GraphValidationError(f"Nodo {node_id}: costo={c} deve essere > 0.")

        G.add_node(node_id)
        test_data[node_id] = TestData(p_success=p, cost=c)

    if not node_ids:
        raise GraphValidationError("Il grafo non contiene nodi.")

    # --- Valida archi ---
    for k, edge in enumerate(edges_raw):
        if (not isinstance(edge, list) and not isinstance(edge, tuple)) or len(edge) != 2:
            raise GraphValidationError(f"Arco in posizione {k} non è una coppia [u, v].")

        u, v = edge
        if u not in node_ids:
            raise GraphValidationError(f"Arco {k}: nodo sorgente '{u}' non esiste.")
        if v not in node_ids:
            raise GraphValidationError(f"Arco {k}: nodo destinazione '{v}' non esiste.")
        if u == v:
            raise GraphValidationError(f"Arco {k}: self-loop ({u} -> {v}) non ammesso.")

        G.add_edge(u, v)

    # --- Deve essere un DAG ---
    if not nx.is_directed_acyclic_graph(G):
        raise GraphValidationError("Il grafo contiene cicli: non è un DAG.")

    return G, test_data


def load_graph_from_json(path: str) -> SequentialTestingProblem:
    """
    Carica un grafo da file JSON, lo valida e restituisce un SequentialTestingProblem.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    G, test_data = validate_graph_data(raw)
    return SequentialTestingProblem(G, test_data)
