# Fritzing Stripboard Generator

Generates Fritzing components matching your particular stripboard.

![](https://coddingtonbear-public.s3.us-west-2.amazonaws.com/github/fritzing-stripboard/practical.png)

Inspired by Robert P Heller's project having a similar aim: https://github.com/RobertPHeller/fritzing-Stripboards

## Installation

```
pip install fritzing-stripboard
```

You can also install the in-development version with:

```

pip install https://github.com/coddingtonbear/fritzing-stripboard/archive/master.zip

```

## Use

```
fritzing-stripboard /path/to/board.yaml /path/to/output/part.fzpz
```

## Defining Your Board

While digging through my project supplies, I happened across a
large collection of stripboards that look like this:

![](https://coddingtonbear-public.s3.us-west-2.amazonaws.com/github/fritzing-stripboard/amz_example.jpg)

Although there are stripboards available online for Fritzing,
none quite looked like this.  Luckily, though, generating a 
Fritzing part for this board can be done easily with just a little
bit of yaml:


```yaml
meta:
  title: 3-5-5-2 Board with Solid Bus
  label: 3-5-5-2
width: 50.5
height: 100.5
board:
  - grid:
      components:
        - shared_bus:
          - bus: A1:T1
          - bus: E1:E36
          - bus: Q1:Q36
        - shared_bus:
          - bus: A37:T37
          - bus: T2:T37
          - bus: A2:A37
          - bus: K2:K37
        - drilled_rows: B2:D36
        - drilled_rows: F2:J36
        - drilled_rows: L2:P36
        - drilled_rows: R2:S36

```

The above will generate a board that looks like:

![](https://coddingtonbear-public.s3.us-west-2.amazonaws.com/github/fritzing-stripboard/rendered.png)

### The Grid

Definitions for boards use excel-like grid square ranges for defining
where new bus (trace) or drilled hole elements should appear:

![](https://coddingtonbear-public.s3.us-west-2.amazonaws.com/github/fritzing-stripboard/grid.png)


### Components

#### `bus` or `drilled`

These create a line or a line of drilled holes.  For example,
`bus` is used for creating this:

![](https://coddingtonbear-public.s3.us-west-2.amazonaws.com/github/fritzing-stripboard/bus.png)

Each `bus` or `drilled` range will be assigned its own "bus"
(a.k.a. "net") unless wrapped by `shared_bus` as you've seen in the
example above.

####  `drilled_rows` or `drilled_columns`

These create an array of rows or columns.  For example, 
`drilled_rows` is used for creating this:

![](https://coddingtonbear-public.s3.us-west-2.amazonaws.com/github/fritzing-stripboard/drilled_bus_rows.png)

Each row or column of the range will be assigned its own "bus"
(a.k.a. "net") unless wrapped by `shared_bus`.

#### `shared_bus`

`bus` and `drilled` ranges by default each get their own bus.  If your
stripboard has a more complex layout (like in the example), you can
use this 'component' for causing all components below it to share
the same bus.

### Metadata

See [BoardMetadata](https://github.com/coddingtonbear/fritzing-stripboard/blob/main/src/fritzing_stripboard/types.py#L12) for a full list of properties.
