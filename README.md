# sequential_testing

Implementazione (Python) di algoritmi **euristici** e **esatti** per un problema di *Sequential Testing* su **grafi diretti aciclici (DAG)**.

---

## Il problema: Sequential Testing su DAG

Consideriamo un **DAG** \(G=(V,E)\). Ogni nodo i rappresenta un **attività/test** che deve essere eseguito.

A ogni nodo sono associati:
- un **costo** \(c(i) > 0\) (tempo, denaro, risorse) sostenuto quando si esegue il test;
- una **probabilità di successo** \(p(i) in (0,1)\) (tipicamente indipendente tra nodi; il test restituisce esito binario successo/fallimento).

Vincolo di precedenza (DAG):
- un nodo è **eseguibile** solo quando sono soddisfatte le sue dipendenze (i predecessori nel DAG secondo la tua modellazione; spesso: “tutti i predecessori devono aver avuto successo”, ma la logica esatta dipende dall’istanza).

Obiettivo (idea generale):
-trovare un sequenziamento dei nodi che minimizzi il costo atteso e rispetti le precedenze.
---

## Cosa c’è nel repository

File principali:
- `problem.py` — definizione dell’istanza/problema (DAG, costi, probabilità, vincoli, goal)
- `load_graph.py` — caricamento di istanze (grafi) da file
- `exact.py` — algoritmo esatto (recursive backtracking)
- `heuristics.py` — euristiche  (simulated annealing, greedy)
- `batch_run.py` — esecuzioni ripetute e raccolta risultati (benchmark)
- `graph_viz.py` — visualizzazione del DAG (layered)
- `io_json.py` — import/export di istanze e risultati in JSON
- `lib/` — moduli di supporto
- `test/` — grafi di test
- `sequential_testing_presentation.pptx` — presentazione del progetto

---
