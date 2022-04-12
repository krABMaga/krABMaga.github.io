+++
title = "Model Exploration"
insert_anchor_links = "right"
+++

---

ABMs are too heterogeneous to be managed and explored in a traditional way, because each model has its agents, its ecosystem and variadic number of parameters. You need to write code able to generate code: *metaprogramming*, and in Rust is possible using macros.

[Rust language](https://www.rust-lang.org/) has a powerful macro system, based on two categories: declarative and procedural. Procedural macros need to be written in a specific library, and cannot be directly included in [Rust-AB](https://github.com/rust-ab/rust-ab), so we chose declarative ones, which are also the most used.

Our framework provides several algorithms to explore parameter space:
- [Parameter Sweeping](#parameter-sweeping);
- [Genetic Algorithms](#genetic-algorithms);
- [Bayesian Optimization](#bayesian-optimization);
- [Random Search](#random-search);


Because the number of simulations to run  can easily explode based on the parameters, the amount of values generated, the algorithm and its settings, we provide parallel, distributed (using MPI) and "on Cloud" (using AWS API) explorations to run multiple simulations simultaneously. At the moment, they are available for [Parameter Sweeping](#parameter-sweeping) and [Genetic Algorithms](#genetic-algorithms).



---
# Parameter Sweeping
 Runs a model many times, varying the model’s settings based on a discrete range of values and recording the results. 

For each parameter, the user has to call a macro to generate the set of values to test on different simulation configurations: with macro, user can pass types as a parameter, so the same code can be adapted for any parameter type.

Generated parameters, the user can call the macro that provides the exploration: the macro creates an ad hoc dataframe to store all configurations and output of each run, define all configurations (all possible combinations) and finally run the simulation, thanks to another macro able to schedule steps of simulations.

The only restriction is defining input and output parameters inside your *State*, and  inout parameter names need to match with generated ones. For example, if you have and input parameter called **X** of type **u32** inside *State*, you have to generate a subset of **u32** values  and store in a Vec called **X**   


```rs
let result = explore_sequential!(
  STEP, REPS, State,  // Simulation Step, Repetitions for each configuration, name of your State struct
  input{
    par1: u32   // Parameters generated
    par2: f64  
  },
  output [ output: f64], 
  ExploreMode::Matched,
);
```

There are two *Explore Mode* options:
- *Exaustive*, the standard mode;
- *Matched*, if you have to test only specific combinations;

---
# Genetic Algorithm
A genetic algorithm is a search heuristic that is inspired by Charles Darwin’s theory of natural evolution. Starting from an initial population, at each generation this algorithm selects the fittest individuals to create offspring of next generation. An individual is a string called **chromosome** that, in this case, represents a combination of parameters. A single parameter is called **gene**.

To use this algorithm we need to define 5 functions: 
- Init population;
- Fitness function to evaluate an individual, so that you can compare if one is better than one other;
- Selection to select which part of population can survive and/or can be used to create the offspring;
- Crossover to combine genes of a couple of individuals;
- Mutation to apply some little changes to offspring genes with a low random probability;


```rs
let result = explore_ga_sequential!(
    init_population,
    fitness,
    selection,   //with macro u can pass function you define
    mutation,
    crossover,
    cmp,  // function to compare two fitness
    State,
    DESIRED_FITNESS,
    MAX_GENERATION,
    STEP,
    REPETITIONS,
);
```
To use model exploration using Genetic Algorithms you have to pass several functions to Rust-AB macro.
In this way modelist can use specific functions based on his model or needs.

