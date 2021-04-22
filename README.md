[![PyPI Wheels](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/build_wheels.yml/badge.svg)](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/build_wheels.yml)
[![CI Tests](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/unit_tests.yml)

# empyrical

Common financial risk metrics in Python.

## Installation

empyrical requires Python 3.7+. You can install it using `pip`:

```bash
pip install empyrical-reloaded
```

or `conda`:
```bash
conda install -c ml4t empyrical-reloaded
```

empyrical requires and installs the following packages while executing the above commands:

- numpy>=1.9.2
- pandas>=1.0.0
- scipy>=0.15.1
- pandas-datareader>=0.4
- yfinance>=0.1.55

## Usage

Simple Statistics
```python
import numpy as np
from empyrical import max_drawdown, alpha_beta

returns = np.array([.01, .02, .03, -.4, -.06, -.02])
benchmark_returns = np.array([.02, .02, .03, -.35, -.05, -.01])

# calculate the max drawdown
max_drawdown(returns)

# calculate alpha and beta
alpha, beta = alpha_beta(returns, benchmark_returns)

```

Rolling Measures
```python
import numpy as np
from empyrical import roll_max_drawdown

returns = np.array([.01, .02, .03, -.4, -.06, -.02])

# calculate the rolling max drawdown
roll_max_drawdown(returns, window=3)

```

Pandas Support
```python
import pandas as pd
from empyrical import roll_up_capture, capture

returns = pd.Series([.01, .02, .03, -.4, -.06, -.02])

# calculate a capture ratio
capture(returns)

# calculate capture for up markets on a rolling 60 day basis
roll_up_capture(returns, window=60)
```

## Support

Please [open an issue](https://github.com/stefan-jansen/empyrical-reloaded/issues/new) for support.

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/stefan-jansen/empyrical-reloaded/compare/).

## Testing
- install requirements
  - "nose>=1.3.7",
  - "parameterized>=0.6.1"

```bash
nosetests empyrical.tests
```
