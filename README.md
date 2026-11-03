# PWN model specs

Specification and documentation of the PWN model.

Results of model experiments can be found under https://pwn-model.github.io/PWNModel.jl

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

## Submodels

### Initialization

The world is divided into blocks of 1×1 km (rounded to whole tree cells; blocks at the
upper world edges may be smaller), and each block is forested with probability `km2_probability`.
In forested blocks, each tree cell holds a tree with probability `tree_probability`.
A tree is initially damaged with probability `damage_prevalence` (`Damaged` tag),
and a damaged tree is additionally colonized with probability `beetle_prevalence` (`Colonized` tag).

### Time

Time advances in weekly ticks, with `ticks_per_year` ticks per year.
Most submodels act once per year, at a fixed tick of the year (`tick_of_year`).

### Disease course

Infected trees become damaged (`Damaged` tag) `ticks_to_damage` ticks after infection.

### Nematode release

At tick `tick_of_infection`, `num_trees` damaged, uninfected trees, randomly selected
from the entire world, are infected with nematodes (`Infected` tag, with the time of infection).

### Background tree removal

Trees with the `Damaged` tag are removed from the simulation with a fixed annual probability `removal_probability`.
Removal takes place in the same tick as background damage, right before it.

### Background tree damage

Healthy trees are damaged with a fixed annual probability `damage_probability`.
When damaged, the tree gets a `Damaged` tag.

### Beetle emergence

Once per year, `beetles_per_tree` individual beetles emerge from each tree that is both colonized and infected.
Each beetle starts at its source tree, and gets an exponentially distributed life span with mean `life_expectancy` ticks,
capped at `max_age` ticks.

### Tree attraction

Once per year, two attraction fields on the fine grid are calculated, which guide beetle movement:
one for healthy trees (maturation feeding) and one for damaged trees (egg laying).

Each tree cell $s$ of the respective type is seeded with its local occupancy $o_s \in (0, 1]$,
i.e. the fraction of cells within `density_radius` that contain a tree of the same type.
The attraction of cell $x$ is the maximum over all sources, decaying with (chamfer) distance $d$
and half-distance $h$ = `half_distance`:

$$A(x) = \max_s \; o_s^{k} \cdot 2^{-d(x,s)/h}$$

with $k$ = `density_weight`. Thus, denser tree clusters attract beetles from farther away.

Along with the field, each cell records its *source*: the tree cell $s$ that attains the maximum.
Beetles fly towards the source of the cell they are in (see [Beetle movement](#beetle-movement)).
The source is not necessarily the nearest tree: a cell can be won by a farther, denser cluster.

*Rationale:* An earlier movement variant (`BeetleMovementByField`) moved beetles to the neighboring cell with the highest attraction.
Taking the maximum (rather than summing kernels over sources) keeps the field bounded,
without a hard radius limit, and cheap to compute (two in-place sweeps).
Further, every local maximum is a tree, so beetles cannot get trapped between trees.
Summing variants were tried, but suffered from a background level dominated by distant trees,
instability, or hard cut-offs.
With deterministic neighbor choice, any monotone transformation of the final field
(e.g. raising a summed field to a power) leaves all movement decisions unchanged.
Density must therefore enter through the seeds, before aggregation.
With $k = 0$, beetles simply head for the nearest tree.
A source with $r$ times the occupancy of another wins up to $h \cdot k \cdot \log_2 r$ farther away.
$k$ is a phenomenological parameter.

### Beetle movement

Beetles move on the fine grid, making `steps_per_tick` steps (days) per tick.
In each step, a beetle either feeds and targets healthy trees, or lays eggs and targets damaged trees.
For the first `duration_feeding` ticks after emergence, beetles always feed.
Afterwards, they feed with probability `feeding_probability` per step, and lay eggs otherwise.

In each step, a beetle can fly up to `distance_per_step`:

1. In its first step after emergence, a beetle makes an undirected flight away from the tree it emerged from,
   over a distance drawn uniformly between 0 and `emergence_flight_distance` (but at most `distance_per_step`),
   in a uniformly random direction.
   This spreads out the beetles emerging from the same tree, which would otherwise all target the same first tree.
   Otherwise, a beetle on a target tree leaves it with probability `leave_tree_probability`.
   It then flies straight in a uniformly random direction, checking its cell after each fine cell size of distance,
   until it reaches a cell whose attraction source (see [Tree attraction](#tree-attraction)) is another tree,
   or the step's distance is used up.
   In both cases, a beetle that leaves the world dies.
2. A beetle that is (still) on a target tree stays there.
3. Otherwise, it flies straight towards the attraction source of its cell, with the remaining distance.
   If the source is within reach, it lands there.

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

### Nematode infection

Each tick, healthy, uninfected trees become infected based on the $f$ feeding events on their cell in the current tick.
With the per-event `infection_probability` $p_i$, the infection probability of a tree is

$$p = 1 - (1 - p_i)^f$$
