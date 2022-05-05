+++
title = "Wolf Sheep Grass (Predator Prey)"
[extra]
last_updated = "2022-05-04"
sim_name = "wolfsheepgrass"
+++


# Wolf Sheep Grass (Predator Prey)

---

Also known as Wolf Sheep predation, it is the simulation implemented to introduce "dynamic scheduling" feature into the krABMaga framework, because it was the first model with the concepts of "death" and "birth": there is an ecosystem that involves animals into their life-cycle.

The main objective is to understand and explore the stability of this ecosystem, trying to change life parameters (like `GAIN_ENEGRY`) or population size.

There are currently two versions of this model:
- The simulation without the visualization framework. Outputs are the interaction between 2 agents (wolf eats sheep) and animal death. At each output, its step number is associated;
- The simulation with the visualization framework enabled (either natively or compiled to WebAssembly). Allows the viewer to see wolves and sheeps moving around the map. Wolves try to follow sheeps. Grass growth is represented by different colors. Only when grass is dark green (full grown), it can be eaten by sheeps;

---

# Implementation

With this example we tested mulit-agent scheduling: wolves and sheeps are different entities with their methods implementation, but both are `Agent`.

`Wolf` and `Sheep` structs have same fields:
```rs
#[derive(Copy, Clone)]
pub struct Sheep/Wolf {
    pub id: u32,
    pub animal_state: LifeState,
    pub loc: Int2D,
    pub last: Option<Int2D>,
    pub energy: f64,
    pub gain_energy: f64,
    pub prob_reproduction: f64,
}
```
They "move" on different Grid, because each grid can contain a single type of entity. For the same reason, grass has its own grid.
To manage the process of birth and death, there are several elements into `State` struct:
- `next_id` to properly assign id to animals when reproduction happens;
- `new_sheeps` and `new_animals` are vectors to store agents created during this step. during `after_step` phase, `State` add these new elements to scheduler;
- `eaten_grass` and `killed_sheep` allow to remove correct elements at the end of current step and they are use to prevent two agents on a same "prey", because food can be eaten only by one agent.


Before grids and schedule update, Animals can check prey state through `LifeState` enum:
```rs
#[derive(Clone, Copy, Debug)]
pub enum LifeState {
    Alive,
    Dead,
}
```
