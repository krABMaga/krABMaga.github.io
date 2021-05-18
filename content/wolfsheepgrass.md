+++
title = "Wolf Sheep Grass (Predator Prey)"
[extra]
last_updated = "2021-05-15"
sim_name = "wolfsheepgrass"
+++


# Wolf Sheep Grass (Predator Prey)

---

Also known as Wolf Sheep predation, it is the simulation implemented to introduce "dynamic scheduling" feature into the Rust-AB framework, because it was the first model with the concepts of "death" and "birth": there is an ecosystem that involves animals into their life-cycle.

The main objective is to understand and explore the stability of this ecosystem, trying to change life parameters (like `GAIN_ENEGRY`) or population size.

There are currently two versions of this model:
- The simulation without the visualization framework. Outputs are the interaction between 2 agents (wolf eats sheep) and animal death. At each output, its step number is associated;
- The simulation with the visualization framework enabled (either natively or compiled to WebAssembly). Allows the viewer to see wolves and sheeps moving around the map. Wolves try to follow sheeps. Grass growth is represented by different colors. Only when grass is dark green, it can be eaten by sheeps;

---

# Implementation

There is a main structure that represents an `Animal`, our simulation agent:
```rs
#[derive(Copy, Clone)]
pub struct Animal {
    pub id: u128,
    pub species: AnimalSpecies,
    pub animal_state: LifeState,
    pub loc: Int2D,
    pub last: Option<Int2D>,
    pub energy: f64,
    pub gain_energy: f64,
    pub prob_reproduction: f64,
}
```

And a trait to define animal behavior:
```rs
pub trait AnimalActions {
    fn consume_energy(&mut self) -> LifeState;
    fn act(&mut self, state: &State);
    fn reproduce(&mut self, state: &State);
    fn eat(&mut self, state: &State);
    fn die(&mut self, state: &State);
}
```

Animal behavior depends on `AnimalSpecies` value of field `species`:
```rs
#[derive(Copy, Clone, Debug)]
pub enum AnimalSpecies {
    Wolf,
    Sheep,
}
```
Before grids and schedule update, Animals can check prey state through `LifeState` enum:
```rs
#[derive(Clone, Copy, Debug)]
pub enum LifeState {
    Alive,
    Dead,
}
```