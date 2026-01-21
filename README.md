# sequential_testing

Implementazione (Python) di algoritmi **exact** e **euristici** per un problema di *Sequential Testing* su **grafi diretti aciclici (DAG)**, con utilità di esecuzione batch e visualizzazione.

---

## Il problema: Sequential Testing su DAG

Consideriamo un **DAG** \(G=(V,E)\). Ogni nodo \(v \in V\) rappresenta un **test/azione** che può essere eseguita per ottenere informazione sul sistema (o per “sbloccare” nodi successivi).

A ogni nodo sono associati:
- un **costo** \(c(v) > 0\) (tempo, denaro, risorse) sostenuto quando si esegue il test;
- una **probabilità di successo** \(p(v) \in (0,1)\) (tipicamente indipendente tra nodi; il test restituisce esito binario successo/fallimento).

Vincolo di precedenza (DAG):
- un nodo è **eseguibile** solo quando sono soddisfatte le sue dipendenze (i predecessori nel DAG secondo la tua modellazione; spesso: “tutti i predecessori devono aver avuto successo”, ma la logica esatta dipende dall’istanza).

Obiettivo (idea generale):
- progettare una **policy adattiva** (strategia sequenziale) che, osservando gli esiti dei test già eseguiti, scelga quale test eseguire dopo, con l’obiettivo di **minimizzare il costo atteso totale** fino a quando si determina lo stato di interesse (es. raggiungere/validare un nodo goal, o decidere se il goal è raggiungibile, ecc.).

Questo si inserisce nella famiglia classica dei **sequential testing problems**: si hanno componenti stocastiche con costi di osservazione e si vuole determinare lo “stato del sistema” (una funzione degli esiti dei componenti) minimizzando il costo atteso. :contentReference[oaicite:1]{index=1}

---

## Cosa c’è nel repository

File principali:
- `problem.py` — definizione dell’istanza/problema (DAG, costi, probabilità, vincoli, goal)
- `load_graph.py` — caricamento di istanze (grafi) da file
- `exact.py` — algoritmi esatti (es. DP/ricorsione/branching) per policy ottima su istanze piccole/medie
- `heuristics.py` — euristiche per istanze più grandi (strategie greedy / score / rollout / ecc.)
- `batch_run.py` — esecuzioni ripetute e raccolta risultati (benchmark)
- `graph_viz.py` — visualizzazione del DAG e/o della policy/ordine di test
- `io_json.py` — import/export di istanze e risultati in JSON
- `lib/` — moduli di supporto
- `test/` — test
- `sequential_testing_presentation.pptx` — presentazione del progetto

---

## Installazione

Consigliato Python 3.10+ e un virtual environment:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
python -m pip install --upgrade pip
