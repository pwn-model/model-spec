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

Beetles are represented individually only where relevant for nematode dispersal:
- [TODO] Eggs, larvae and pupae in nematode-infested trees
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

### Initialization

Each coarse grid cell is forested with probability `cell_probability`.
In forested cells, each fine cell holds a tree with probability `tree_probability`.
A tree is initially damaged with probability `damage_prevalence` (`Damaged` tag),
and a damaged tree is additionally colonized with probability `beetle_prevalence` (`Colonized` tag).
Each tree is linked to its containing coarse cell.

### Time

Time advances in weekly ticks, with `ticks_per_year` ticks per year.
Most submodels act once per year, at a fixed tick of the year (`tick_of_year`).

### Disease course

Infected trees become damaged (`Damaged` tag) `ticks_to_damage` ticks after infection.

### Nematode release

At tick `tick_of_infection`, `num_trees` randomly selected healthy, uninfected trees
in the coarse cell (`cell_x`, `cell_y`) are infected with nematodes (`Infected` tag, with the time of infection).

### Background tree removal

Trees with the `Damaged` tag are removed from the simulation with a fixed annual probability `removal_probability`.
Removal takes place in the same tick as background damage, right before it.

### Background tree damage

Healthy trees are damaged with a fixed annual probability `damage_probability`.
When damaged, the tree gets a `Damaged` tag.

### Beetle emergence

Once per year, `beetles_per_tree` individual beetles emerge from each tree that is both damaged and infected.
Each beetle starts at its source tree, and gets an exponentially distributed life span with mean `life_expectancy` ticks.

### Tree attraction

Once per year, two attraction fields on the fine grid are calculated, which guide beetle movement:
one for healthy trees (maturation feeding) and one for damaged trees (egg laying).

Each tree cell $s$ of the respective type is seeded with its local occupancy $o_s \in (0, 1]$,
i.e. the fraction of cells within `density_radius` that contain a tree of the same type.
The attraction of cell $x$ is the maximum over all sources, decaying with (chamfer) distance $d$
and half-distance $h$ = `half_distance`:

$$A(x) = \max_s \; o_s^{k} \cdot 2^{-d(x,s)/h}$$

with $k$ = `density_weight`. Thus, denser tree clusters attract beetles from farther away.

### Beetle movement

Beetles move on the fine grid, making `steps_per_tick` steps per tick.
For the first `duration_feeding` ticks after emergence, beetles are feeding and target healthy trees.
For the following `duration_egg_laying` ticks, they are egg laying and target damaged trees [not yet implemented, see [Background beetle colonization](#background-beetle-colonization) for now].
Afterwards, they are inactive.

In each step, a beetle on a target tree stays there with probability 1 - `leave_tree_probability`.
Otherwise, it moves to a neighboring cell (Moore neighborhood):
with probability `random_walk_probability` to a random one,
otherwise to the one with the highest attraction (see [Tree attraction](#tree-attraction)).

For each step that a beetle ends on a target tree, a feeding event is counted for that tree's cell.

### Beetle mortality

Beetles are removed when they reach the end of their life span.

### Background beetle colonization

Beetle dispersal operates on a separate dispersal grid with cell size `cell_size`
(a multiple of the fine grid's cell size).

For each cell, the number of trees colonized by beetles is counted.
Multiplied with the fixed `beetles_per_tree` factor, this gives the available emerging beetles.
These are distributed to the source cell as well as the surrounding cells using an exponential,
mass-preserving (i.e., normalized) kernel, giving the arriving beetles per cell.

$$w(d) = e^{-d/l} = 2^{-d/h}$$

with half-distance $h$ = `kernel_half_distance` (i.e. $l = h / \ln 2$).
The kernel is truncated at distance `kernel_radius`, rounded up to full cells.

Multiplied with the fixed `trees_per_beetle`,
this gives the number of colonization attempts $n$ per cell.
Together with the number of susceptible (i.e., damaged) trees $m$,
the colonization probability per susceptible tree is

$$p = 1 - \left(1 - \frac{1}{m}\right)^n$$

or, equivalently but numerically more stable:

$$p = 1 - \exp\left(n \cdot \ln\left(1 - \frac{1}{m}\right)\right)$$

After the `Colonized` flag is removed from all source trees (as beetles fly out),
this probability is applied in an independent Bernoulli trial
to each individual susceptible (damaged) tree,
adding the `Colonized` tag on success.

> Note: `beetles_per_tree` * `trees_per_beetle` = $R_0$ of the system.

> Note: With $\sigma = 1-\text{removal-probability}$ (from tree removal)
> and $p$ being the target beetle prevalence (in damaged trees), theoretically:  
> $$R_0 = \dfrac{1}{\sigma(1-\sigma p)}$$

### Nematode infection

Each tick, healthy, uninfected trees become infected based on the $f$ feeding events on their cell in the current tick.
With the per-event `infection_probability` $p_i$, the infection probability of a tree is

$$p = 1 - (1 - p_i)^f$$
