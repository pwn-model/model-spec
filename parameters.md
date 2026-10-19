> [!WARNING]
> This file is auto-generated from `parameters.yaml`. Do not edit it by hand!
> Instead, edit `parameters.yaml` and regenerate this file with:
>
> ```
> python scripts/parameters_table.py -o parameters.md
> ```

## WorldSize

Spatial extent of the world and resolution of the tree grid

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `width` | World size in east-west direction. Must be a multiple of cell_size *(technical)* | 4000 m | 1000 – 100000 m | None, technical parameter |
| `height` | World size in north-south direction. Must be a multiple of cell_size *(technical)* | 3000 m | 1000 – 100000 m | None, technical parameter |
| `cell_size` | Cell size of the fine tree grid, holding at most one tree per cell *(technical)* | 10 m | 5 – 20 m | TODO |

## InitTrees

Initializes trees and their damage and beetle colonization state

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `km2_probability` | Probability that a 1x1 km block is forested *(scenario)* | 0.6 | 0 – 1 | None, preliminary to generate heterogeneous landscapes |
| `tree_probability` | Probability that a fine grid cell within a forested block holds a tree *(ecological)* | 0.9 | 0 – 1 | TODO |
| `damage_prevalence` | Initial proportion of damaged trees *(ecological)* | 0.03 | 0 – 1 | TODO |
| `beetle_prevalence` | Initial proportion of damaged trees that are colonized by beetles *(ecological)* | 0.2 | 0 – 1 | TODO |

## UpdateTime

Updates model time

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `ticks_per_year` | Number of model ticks per year *(technical)* | 52 ticks / year | – | None, technical parameter |

## DiseaseCourse

Progression of nematode-infected trees to damaged state

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `ticks_to_damage` | Time from nematode infection of a tree until it becomes damaged *(ecological)* | 8 weeks | TODO | TODO |

## RandomRelease

Initial introduction of the nematode by infecting randomly selected trees anywhere in the world

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `tick_of_infection` | Model tick at which the trees are infected *(scenario)* | 0 weeks | – | None, scenario parameter |
| `num_trees` | Number of trees to infect. Capped at the number of undamaged, uninfected trees *(scenario)* | 10 trees | – | None, scenario parameter |

## DamageTrees

Annual background damage of trees (by causes other than the nematode) and removal of damaged trees

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `tick_of_year` | Week of the year when trees are damaged and removed *(ecological)* | 35 week | 0 – 51 week | TODO |
| `damage_probability` | Annual probability of an undamaged tree to become damaged *(ecological)* | 0.01 1 / year | 0 – 1 1 / year | TODO |
| `removal_probability` | Annual probability of a damaged tree to be removed *(management)* | 0.333 1 / year | 0 – 1 1 / year | TODO |

## BeetleEmergence

Annual emergence of nematode-carrying beetles from damaged, infected trees

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `tick_of_year` | Week of the year when beetles emerge *(ecological)* | 19 week | 0 – 51 week | TODO |
| `beetles_per_tree` | Number of beetles emerging from each damaged, infected tree *(ecological)* | 5 beetles / tree | TODO | TODO |
| `life_expectancy` | Mean adult beetle life span (exponentially distributed) *(ecological)* | 5 weeks | TODO | TODO |

## TreeAttraction (damaged)

Attraction field of damaged trees, guiding beetles during egg laying

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `tick_of_year` | Week of the year when the attraction field is calculated *(technical)* | 18 week | 0 – 51 week | None, technical parameter |
| `damaged_trees` | Whether this instance computes the attraction of damaged (true) or healthy (false) trees *(technical)* | true | – | None, technical parameter |
| `half_distance` | Distance at which a tree's attraction has decayed to half its value at the tree *(ecological)* | 50 m | TODO | TODO |
| `density_radius` | Radius within which neighboring damaged trees count towards a tree's local density. Must be a multiple of the fine cell size *(ecological)* | 20 m | TODO | TODO |
| `density_weight` | Exponent applied to a tree's local density to scale its attraction. 0 disables the density effect *(ecological)* | 1.0 | TODO | TODO |

## TreeAttraction (healthy)

Attraction field of healthy trees, guiding beetles during maturation feeding

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `tick_of_year` | Week of the year when the attraction field is calculated *(technical)* | 18 week | 0 – 51 week | None, technical parameter |
| `damaged_trees` | Whether this instance computes the attraction of damaged (true) or healthy (false) trees *(technical)* | false | – | None, technical parameter |
| `half_distance` | Distance at which a tree's attraction has decayed to half its value at the tree *(ecological)* | 50 m | TODO | TODO |
| `density_radius` | Radius within which neighboring healthy trees count towards a tree's local density. Must be a multiple of the fine cell size *(ecological)* | 20 m | TODO | TODO |
| `density_weight` | Exponent applied to a tree's local density to scale its attraction. 0 disables the density effect *(ecological)* | 1.0 | TODO | TODO |

## BeetleMovement

Movement of nematode-carrying beetles during maturation feeding and egg laying

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `steps_per_tick` | Number of movement steps (to a neighboring fine grid cell) per week *(ecological)* | 7 steps / week | TODO | TODO |
| `duration_feeding` | Duration of the maturation feeding phase after emergence *(ecological)* | 6 weeks | TODO | TODO |
| `duration_egg_laying` | Duration of the egg laying phase after maturation feeding *(ecological)* | 6 weeks | TODO | TODO |
| `leave_tree_probability` | Per-step probability of a beetle to leave a suitable tree *(ecological)* | 0.25 1 / step | 0 – 1 1 / step | TODO |
| `random_walk_probability` | Per-step probability of a moving beetle to move to a random neighbor cell rather than the most attractive one *(ecological)* | 0.6 1 / step | 0 – 1 1 / step | TODO |

## Colonization

Annual background spread of beetles (without nematodes) to damaged trees, via a dispersal kernel

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `tick_of_year` | Week of the year when colonization takes place *(ecological)* | 20 week | 0 – 51 week | TODO |
| `cell_size` | Cell size of the dispersal grid *(technical)* | 100 m | TODO | None, technical parameter |
| `kernel_half_distance` | Distance at which the dispersal kernel's weight has decayed to half its value at the source cell *(ecological)* | 50 m | TODO | TODO |
| `kernel_radius` | Cutoff radius of the dispersal kernel. Rounded up to full cells *(ecological)* | 300 m | TODO | TODO |
| `beetles_per_tree` | Number of beetles emerging from each colonized tree per year *(ecological)* | 2.0 beetles / tree / year | TODO | TODO |
| `trees_per_beetle` | Mean number of damaged trees within a cell that an arriving beetle attempts to colonize *(ecological)* | 1.0 trees / beetle | TODO | TODO |

## NematodeInfection

Infection of healthy trees by feeding, nematode-carrying beetles

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `infection_probability` | Probability of a tree to become infected per feeding step of a beetle on it *(ecological)* | 0.01 1 / step | 0 – 1 1 / step | TODO |

## FixedTermination

Stops the simulation after a fixed number of ticks

| Parameter | Description | Value | Range | Source |
|---|---|---|---|---|
| `steps` | Number of simulation ticks to run *(technical)* | 5200 weeks | – | None, technical parameter |
