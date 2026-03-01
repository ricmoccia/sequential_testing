testN15 — 40 graph instances (N=15 nodes, M=23 edges each)

Structure:
  - 10 distinct non-trivial DAG topologies (files start with 01_ ... 10_)
  - For each topology, 4 attribute intervals:
      I1: p in [0.95, 1.0], cost in [1, 100]
      I2: p in [0.70, 1.0], cost in [10, 1000]
      I3: p in [0.95, 1.0], cost in [10, 1000]
      I4: p in [0.70, 1.0], cost in [1, 100]

Notes:
  - Edges are directed and acyclic (always from earlier letter to later letter).
  - Node ids are A..O.
  - Topologies avoid trivial paths: layered / ladder / diamond cascade / augmented tree / degree-constrained random DAGs / multi-hub / interwoven chains.
  - Values are deterministic (seeded) so you can regenerate consistently.
