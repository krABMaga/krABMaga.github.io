+++
title = "Schelling"
[extra]
last_updated = "2022-07-12"
sim_name = "schelling"
+++

# Schelling

---

This simulation is based on the Schelling's segregation model. The agents can belong to one of the
two existing different groups, represented by differently colored hearts (blue or red).
- If an agent has enough neighbours of the same group near himself, then he's happy and he will stay in his current location.
- Otherwise, the agent will move randomly in the next step.

Each agent has an id `u32` and a `Status` that represent its group.
```rs
#[derive(Copy, Clone, PartialEq, Eq, Hash)]
pub enum Status {
    Red,
    Blue,
}
```
