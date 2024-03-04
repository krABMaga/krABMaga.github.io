+++
title = "Virus on a Network"
[extra]
last_updated = "2024-03-04"
sim_name = "virusnetwork"
+++

# Virus on a Network

---
In the academic literature such a model is sometimes referred to as an **SIR model for epidemics**.

With this model we want to simulate how a virus (or a warm) can be spread through a network. It's an abstraction of several dynamics:
- Network is based on a graph, where:
  - `nodes` represent computers (or any other device);
  - `edges` represent communication link into the network (edges are undirected);
- A node can be in 1 of 3 possible states:
  - `Susceptible`: a standard node and a potential victim;
  - `Infected`: an infected node. This kind of nodes can be unaware of the infection;
  - `Resistant`: after virus detection, this node became resistent to this kind of infection (this state simulates an antivirus update);
- At each step, communication between all nodes is performed, and infected nodes spread virus to their neighbours (for examples, as attachment of an email);
- Periodically nodes start a scan with their antivirus to detect virus; if they detect something, a recovery will be done. If the recovery is performed, there is a possibility for that node to became `Resistant`;

The network is created using `preferential attachment` algorithm; it's provided by a krABMaga macro: given a list of nodes, it adds nodes one by one, and it creates ages based on node degree.
```rs
preferential_attachment_BA!(nodes_set, state.network, NetNode, String, INIT_EDGE);
```


`Node` struct is simple: an id to identify nodes into the network, its status and if some problem is detected.
`Real2D` parameter is necessary for visualization

```rs
#[derive(Clone, Copy, Debug)]
pub enum NodeStatus {
    Susceptible,
    Infected,
    Resistent,
}

#[derive(Clone, Copy)]
pub struct NetNode {
    pub id: u32,
    pub pos: Real2D,
    pub status: NodeStatus,
    pub virus_detected: bool,
}
```

`EpidemicNetworkState` has two main fields:
- `Field2D` for visualization;
- `Network<NetNode, String>` to manage nodes connection and comunication;
