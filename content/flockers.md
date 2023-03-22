+++
title = "Flockers"
[extra]
last_updated = "2023-03-22"
sim_name = "flockers"
+++

# Boids

---

The Boids model was the first simulation to be implemented with the use of the krABMaga framework. It is a steering behaviour
agent-based model for autonomous agents simulating the flocking behaviour of birds. The agent behaviour is derived by a linear
combination of three independent rules:
- Avoidance
- Consistency
- Cohesion

There are currently two versions:

- The simulation without the visualization framework. Outputs the time elapsed for given a number of steps and number of
  agents (currently hardcoded), along with the step for seconds.
- The simulation with the visualization framework enabled (either natively or compiled to WebAssembly). It shows a
  graphical interface describing the flockers moving in the environment, casually grouping together and avoiding other
  flockers. The simulation never stops.
  
---

# Implementation

The structure of the main agent of this simulation, the `Bird`, is very simple:
```rs
#[derive(Clone, Copy)]
pub struct Bird {
    pub id: u32,
    pub pos: Real2D,
    pub last_d: Real2D,
}
```

Birds simply have a current and a previous location field, along with an ID to differentiate them.

The definition of the state is just as simple:
```rs
pub struct Flocker {
    pub step: u64,
    pub field1: Field2D<Bird>,
    pub initial_flockers: u32,
    pub dim: (f32, f32),
}

impl Flocker {
    pub fn new(dim: (f32, f32), initial_flockers: u32) -> Self {
        Flocker {
            step: 0,
            field1: Field2D::new(dim.0, dim.1, DISCRETIZATION, TOROIDAL),
            initial_flockers,
            dim,
        }
    }
}
```
