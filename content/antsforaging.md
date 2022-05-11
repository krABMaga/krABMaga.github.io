+++
title = "Ants Foraging"
[extra]
last_updated = "2022-05-11"
sim_name = "antsforaging"
+++

# Ants Foraging

---

The ants foraging simulation is based on a model which represents the behaviour of a colony of ants looking for
food around their nest through the use of pheromones to find the shortest path connecting the nest and the food source.
The ants represent the agents of this simulation, with the logic implemented on them consisting in two actions:

- Look around the nest in the simulation space for food sources, either randomly or by using the information left by
other ants in the form of pheromones, represented by simple f64 values.
- Once the food source is found, return to the nest by using the previously left pheromones to find the shortest path, while
also leaving a different type of pheromone to mark the presence of a food source.
  
When a site is reached, the ants will leave the strongest pheromone possible and weaker amounts will be left in
the neighbour cells. While moving, if no pheromone is found, a random step is taken. If a pheromone of the matching type
is found, based on whether the ant is looking for the food source or for the nest, a step is taken towards the cell with
the strongest pheromone.

The space consists of a discrete grid where agents and static objects live in. There are three types of entities:
- Ants, representing the agents of this simulation.
- Obstacles, representing dense objects occupying a cell, preventing ants from stepping on such cells.
- Sites, representing points of interest, that is the food source and the nest.

The major result of the simulation that can be seen is the creation of a short path, in terms of steps taken by the ants to
reach each site, which is improved over time as the simulation steps forward. It isn't uncommon seeing an initial, non-optimal path
created by the ants due to the presence of obstacles, which is then later improved as the ants try out different directions,
causing stronger pheromones to be left and inducing the other ants to prioritize the new path.

As time goes on, pheromones evaporate with a constant ratio. This is especially important due to the most active paths
remaining traveled by ants due to them constantly leaving pheromones, whereas inactive paths disappear over time.
  
---

# Implementation

The structure of the main agent of this simulation, the `Ant`, is shown below:
```rs
/// A struct representing an ant, with an id, a position, whether it's holding food or not and the
/// current reward, used to increase the pheromone on the location of the ant if a site is reached.
#[derive(Copy, Clone)]
pub struct Ant {
    /// An unique id.
    pub id: u128,
    /// The position of the agent.
    pub loc: Int2D,
    /// Last position of the agent, starts as None
    pub last: Option<Int2D>,
    /// False means the agent will try to find food by following food pheromones if possible, or by
    /// flooding the grid until it is found. True means the agent will try to return home by using the
    /// previously deposited pheromones.
    pub has_food: bool,
    /// Value used to increase the pheromones in the nest and in the food source.
    /// This will let the agents spread pheromones in the surrounding areas from point of interests
    /// so that other agents will know which path to take to do their job.
    pub reward: f64,
}
```

The simulation state is definitely more complex than simpler models such as Boids, as shown below:
```rs
/// The global simulation state. This holds the various grids used for movement, exposing setter methods
/// so that the state itself will worry about ownership rules by mutating its own fields.
pub struct State {
    pub ants_grid: AntsGrid,
    pub obstacles_grid: ObstaclesGrid,
    pub sites_grid: SitesGrid,
    pub to_food_grid: ToFoodGrid,
    pub to_home_grid: ToHomeGrid,
    pub food_source_found: RwLock<bool>,
    pub food_returned_home: RwLock<bool>,
    pub step: u128,
}
```

This increase in complexity is caused by different requirements to represent the location of each entity. For example,
ants require the use of a sparse grid, since most of the time more than half of the grid's cells do not have an ant in them.
Pheromones, on the other part, can be represented by a simple primitive value, a `f64`, and a dense grid is better to represent them,
especially considering the initial phase when the ants flood the grid and leave traces of pheromones everywhere.
There is also another reason regarding the use of a different type of grid for pheromones: visualization performance. Instead of
representing pheromones as single entities, thus causing an enormous amount of entities existing at all times at runtime, a different
approach was taken. The whole grid is represented with a single entity by transforming it into a texture, with each cell being a
pixel with a constant color and varying alpha, the latter being a quantized pheromone value, to simplify the visualization of pheromones.
This decreases the communication step between the CPU and the GPU, by batching the required renderer calls from `w * h`
(with `w` being the grid's width and `h` being the grid's height) to a single one. This allows for an enormous improvement and the
possibility of updating the pheromones' visualization each frame, instead of once every 200 frames as it was done in a previous release.
