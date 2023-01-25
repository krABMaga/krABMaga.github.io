+++
title = "Forest fire"
[extra]
last_updated = "2023-01-25"
sim_name = "forestfire"
+++

# Forest fire

---

The forest fire model is defined as a cellular automaton, where each cell can represent a tree (or it can be empty).
The trees have three states:
- 🌲 alive, which is represented visually with a tree emoji;
- 🔥 burning, which is represented visually with a fire emoji;
- 💀 dead, which is represented visually with a dust emoji;

The simulation relies on two parameters, the space dimension and the density.
The latter, in particular, is used to choose the number of trees to randomly generate at the start of the simulation.
In the initial configuration, all the leftmost trees of the model are forced on the "burning" status.
The alive trees near a burning trees will catch fire on the next step.

