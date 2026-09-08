# PWN model specs

Specification and documentation of the PWN model.

## Model entities

### Trees

Trees are represented individually with state variables representing health state and nematode infestation.

### Vectors

Vectors are represented explicitly only where relevant for nematode dispersal:
- Eggs and larvae in nematode-infested trees
- Adults with nematodes during maturation and ovipositioning

Vectors are represented as cohorts instead of individuals where possible

## Scales

### Time

The model has a weekly time step.

### Spatial structure

Trees are positioned on a grid with either one large tree or multiple small trees per cell. Cell size is in the order of magnitude of 10m.

Another spatial grid structure of approx. 500m grid cells is used for vector dispersal and search flights. This results in 2500 trees per grid cell.

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
