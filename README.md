# PWN model specs

Specification and documentation of the PWN model.

## Model entities

### Trees

Trees are represented individually with state variables representing health state,
beetle colonization and nematode infestation.

### Vectors

Beetles are represented in an abstract way when no nematode is involved.
There is a beetle presence flag for trees, and a simple annual dispersal process
based on a mass-conserving kernel.

[TODO] Beetles are represented individually only where relevant for nematode dispersal:
- Eggs, larvae and pupae in nematode-infested trees
- Adults with nematodes during maturation and ovipositioning

## Scales

### Time

The model has a weekly time step.

### Spatial structure

Trees are positioned on a grid with either one large tree or multiple small trees per cell.
Cell size is in the order of magnitude of 10m.

Another spatial grid structure of approx. 500m grid cells is used for vector dispersal and search flights.
This results in 2500 trees per grid cell.

```
        ______________  _
       /_/_/_/_/_/_/_/---\--- 10x10m cell for trees
      /_/_/_/_/_/_/_/    |
     /_/_/_/_/_/_/_/     |
    /_/_/_/_/_/_/_/       > 500x500m cell for vector dispersal
   /_/_/_/_/_/_/_/       |
  /_/_/_/_/_/_/_/        |
 /_/_/_/_/_/_/_/        _/
```

## Submodels

### Background tree damage

Healthy trees are damaged with a fixed annual probability `damage_probability`.
When damaged, the tree gets a `Damaged` tag.

### Background tree removal

Trees with the `Damaged` tag are removed from the simulation with a fixed annual probability `removal_probability`.

### Background beetle colonization

Beetle dispersal operates on the coarse 500m grid.

For each cell, the number of trees colonized by beetles is counted.
Multiplied with the fixed `beetles_per_tree` factor, this gives the available emerging beetles.
These are distributed to the source cell as well as the surrounding cells using an exponential,
mass-preserving (i.e., normalized) kernel with scale $l$, giving the arriving beetles per cell.

$$w(d) = e^{-d/l}$$

Multiplied with the fixed `trees_per_beetles`,
this gives the number of colonization attempts $n$ per cell.
Together with the number of susceptible (i.e., damaged) trees $m$,
the colonization probability per susceptible tree is

$$p = 1 - \left(1 - \frac{1}{m}\right)^n$$

or, equivalently but numerically more stable:

$$p = 1 - \exp\left(n \cdot \ln\left(1 - \frac{1}{m}\right)\right)$$

After the `Damaged` flag is removed from all trees (as beetles fly out),
this probability is applied in an independent Bernoulli trial
to each individual susceptible (damaged) tree,
adding the `Colonized` tag on success.

> Note: `beetles_per_tree` * `trees_per_beetles` = $R_0$ of the system.

> Note: With $\sigma = 1-\text{removal-probability}$ (from tree removal)
> and $p$ being the target beetle prevalence (in damaged trees), theoretically:  
> $$R_0 = \dfrac{1}{\sigma(1-\sigma p)}$$
