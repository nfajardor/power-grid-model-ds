<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

[![](https://github.com/PowerGridModel/.github/blob/main/artwork/svg/color.svg)](#)

# Power Grid Model Data Science (DS)

The Power Grid Model DS project extends the capabilities of the `power-grid-model` calculation core with a modelling and simulation interface. This is aimed at building data science software applications related to or using the power-grid-model project. It defines a `Grid` dataclass which manages the consistency of the complete network.

Some highlighted features:

- Using a model definition that corresponds to the power-grid-model, through
  which it is easy to do efficient grid calculations.
- The extended numpy model provides features which make development more
  pleasant and easy.
- Using the graph representation of the network, graph algorithms in rustworkx
  can be used to analyze the network.
- An interface to model network mutations which is useful in
  simulation use-cases.

## Installation

### Pip

```
pip install power-grid-model-ds
```

## Contributing

Please read [CODE_OF_CONDUCT](https://github.com/PowerGridModel/.github/blob/main/CODE_OF_CONDUCT.md) and [CONTRIBUTING](https://github.com/PowerGridModel/.github/blob/main/CONTRIBUTING.md) for details on the process 
for submitting pull requests to us.