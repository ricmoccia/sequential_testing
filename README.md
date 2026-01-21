# sequential_testing

Progetto in Python dedicato a esperimenti e strumenti per **sequential testing** (test statistici/sequenziali) e relative utilità di esecuzione/visualizzazione.

> Repo ancora in evoluzione: alcune sezioni (dipendenze, esempi di input/output) sono pensate per essere completate man mano.

---

## Contenuti del repository

Struttura principale (file/cartelle principali):
- `app.py` — entrypoint dell’app (es. demo/interfaccia o orchestrazione principale)
- `batch_run.py` — esecuzioni batch / esperimenti ripetuti
- `exact.py` — metodi “exact” (soluzione/valutazione esatta)
- `heuristics.py` — metodi euristici
- `problem.py` — definizione del problema/istanza
- `load_graph.py` — loader di istanze (grafi/dati)
- `graph_viz.py` — funzioni di visualizzazione
- `io_json.py` — I/O su JSON (configurazioni e/o risultati)
- `lib/` — libreria di supporto
- `test/` — test
- `sequential_testing_presentation.pptx` — slide/presentazione del progetto

---

## Requisiti

- Python 3.10+ (consigliato)

Consiglio: usa un virtual environment.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
python -m pip install --upgrade pip
