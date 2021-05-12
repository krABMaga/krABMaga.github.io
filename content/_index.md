+++
title = "Introduction"
insert_anchor_links = "right"
+++

---

[Rust-AB](https://github.com/rust-ab/rust-ab) is a discrete events simulation engine for developing ABM simulation
written in the [Rust language](https://www.rust-lang.org/).

[Rust-AB](https://github.com/rust-ab/rust-ab) is designed to be a ready-to-use tool for the ABM community and for this
reason the architectural concepts of the well-adopted [MASON library](https://cs.gmu.edu/~eclab/projects/mason/) were
re-engineered to exploit the Rust peculiarities and programming model, in particular by keeping the visualization and the
simulation subsystems fully separated.

⚡ The actual community effort on [Rust-AB](https://github.com/rust-ab/rust-ab) is mainly devoted to supporting parallel
execution and model visualization using the [Bevy game engine](https://bevyengine.org/).

---

# Architecture

#### Agents

The Rust-AB framework defines a trait `Agent` that can be implemented on a struct to define `Agent` specific functionalities,
mainly the `step` method which specifies how the agent behaves for each simulation step, and the `SimState` associated type,
to link the agent to the state it refers to. As for now, the Rust-AB framework doesn't allow clean multi-agent implementations yet,
even though such a limitation can be easily circumvented by declaring a single agent type which encapsulates the various agent types
of the model in analysis.

#### Simulation state

The simulation state can be considered as the single source of truth of the simulation, where data resides and is updated.
Like `Agent`, Rust-AB exposes a `State` trait to let the user mark a particular structure as a simulation state, along with
exposing an `update` method to define logic to execute once for each simulation step. The simulation state is the perfect
structure to put field definitions on (such as 2D continuous fields, grids and so on). An important effect of the state being
the single source of truth forces agents to update (and most importantly read) their own location by interacting with the
state, even though they can store their own location locally in the agent structure too. Although, to be sure one is interacting
with the latest computed data, it is considered a good practice to update both an agent own location field and its copy on the
state structure.

#### Schedule

The simulation timeline is controlled by a Schedule structure that takes care of notifying all the scheduled agents, and the
simulation state that a step has been taken. For this reason, agents should be scheduled so that they can be notified when
a step has been taken.
The scheduler works as a priority queue, where the agents are sorted according to their scheduled time
and a priority value - an integer. The simulation time - a real value - starts from the scheduling time of the first agent.

The schedule structure exposed by the Rust-AB framework provides two methods to do so:

- `schedule_once` to insert an agent in the schedule for a specific simulation step. The scheduling time and the
  priority are given as parameters. The priority is used to sort all agents within the same simulation time.
  
- `schedule_repeating` which acts like schedule once, with the difference that the agent will be scheduled for all
  subsequent simulation steps.

The schedule provides the `step` method which allows executing one simulation step. In this way, the programmer can
easily design his/her simulation by looping for a certain number of step or for a given amount of CPU time.

#### Data structures

The Rust-AB framework exposes a few data structures based on the `DBDashMap`, a customized version of the 
[Rust HashMap](https://doc.rust-lang.org/std/collections/struct.HashMap.html) that implements a double
buffering technique to avoid indeterminism caused by the lack of knowledge of the agents' step execution order within a step.
The `DBDashMap` implements the interior mutability pattern, which allows the user to safely write in it without having an actual
mutable reference to the structure, because the reads are done on a different memory block than the writes. Only the `update`
method actually requires a mutable reference, to swap the read and the write buffers and commit the changes.

The currently implemented structures are:

- `Field2D`, a sparse matrix structure modelling agent interactions on a
  2D real space with coordinates represented by 2D f64 tuples (`Real2D`).
  
- `Grid2D`, a discrete field representing agents locations as 2D i64 tuples (`Int2D`). This structure keeps two copies of a DBDashMap in sync,
  one the inverse of the other, to allow constant time access both by key (agent) and by value (position).
  
- `NumberGrid2D`, a simpler version of the `Grid2D` to use with simpler values. This is useful to represent simulation spaces
  covered by a simple entity that can be represented with a non-agent structure. This data structure can be used with any
  structure that can be cloned, most notably simple primitive values such as f64s.
  


