<p align="center">
<a href="https://empyrical.ml4trading.io">
<img src="https://i.imgur.com/PbZNeud.png" width="35%">
</a>
</p>

![PyPI](https://img.shields.io/pypi/v/empyrical-reloaded)
![PyPI - Downloads](https://img.shields.io/pypi/dm/empyrical-reloaded)

[![Conda Version](https://img.shields.io/conda/vn/conda-forge/empyrical-reloaded.svg)](https://anaconda.org/conda-forge/empyrical-reloaded)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/empyrical-reloaded.svg)](https://anaconda.org/conda-forge/empyrical-reloaded)

[![PyPI Wheels](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/build_wheels.yml/badge.svg)](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/build_wheels.yml)
[![Conda packages](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/conda_package.yml/badge.svg)](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/conda_package.yml)
[![CI Tests](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/stefan-jansen/empyrical-reloaded/actions/workflows/unit_tests.yml)

Common financial return and risk metrics in Python.

## Installation

empyrical requires Python 3.9+. You can install it using `pip`:

```bash
pip install empyrical-reloaded
```

or `conda` from the `conda-forge` channel

```bash
conda install empyrical-reloaded -c conda-forge
```

empyrical requires and installs the following packages while executing the above commands:

- numpy>=1.9.2
- pandas>=1.0.0
- scipy>=0.15.1
- pandas-datareader>=0.4

Optional dependencies include [yfinance](https://github.com/ranaroussi/yfinance) to download price data from [Yahoo! Finance](https://finance.yahoo.com/) and [pandas-datareader](https://pandas-datareader.readthedocs.io/en/latest/) to access [Fama-French](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) risk factors.
- yfinance>=0.1.59

To install the optional dependencies, use:

```bash
pip install empyrical-reloaded[yfinance]
```

## Usage

### Simple Statistics

Empyrical computes basic metrics from returns and volatility to alpha and beta, Value at Risk, and Shorpe or Sortino ratios.

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

### Rolling Measures

Empyrical also aggregates return and risk metrics for rolling windows:

```python
import numpy as np
from empyrical import roll_max_drawdown

returns = np.array([.01, .02, .03, -.4, -.06, -.02])

# calculate the rolling max drawdown
roll_max_drawdown(returns, window=3)
```

### Pandas Support

Empyrical also works with both [NumPy](https://numpy.org/) arrays and [Pandas](https://pandas.pydata.org/) data structures:

```python
import pandas as pd
from empyrical import roll_up_capture, capture

returns = pd.Series([.01, .02, .03, -.4, -.06, -.02])
factor_returns = pd.Series([.02, .01, .03, -.01, -.02, .02])

# calculate a capture ratio
capture(returns, factor_returns)
-0.147387712263491

```

### Fama-French Risk Factors

Empyrical downloads Fama-French risk factors from 1970 onward:

>> Note: requires optional dependency `yfinance` - see installation instructions above.gst

```python
import empyrical as emp

risk_factors = emp.utils.get_fama_french()

risk_factors.head().append(risk_factors.tail())

                           Mkt-RF     SMB     HML       RF     Mom
Date
1970-01-02 00:00:00+00:00  0.0118  0.0131  0.0100  0.00029 -0.0341
1970-01-05 00:00:00+00:00  0.0059  0.0066  0.0072  0.00029 -0.0152
1970-01-06 00:00:00+00:00 -0.0074  0.0010  0.0020  0.00029  0.0040
1970-01-07 00:00:00+00:00 -0.0015  0.0039 -0.0032  0.00029  0.0011
1970-01-08 00:00:00+00:00  0.0004  0.0018 -0.0015  0.00029  0.0033
2021-02-22 00:00:00+00:00 -0.0112 -0.0009  0.0314  0.00000 -0.0325
2021-02-23 00:00:00+00:00 -0.0015 -0.0128  0.0090  0.00000 -0.0185
2021-02-24 00:00:00+00:00  0.0115  0.0120  0.0134  0.00000 -0.0007
2021-02-25 00:00:00+00:00 -0.0273 -0.0112  0.0087  0.00000 -0.0195
2021-02-26 00:00:00+00:00 -0.0028  0.0072 -0.0156  0.00000  0.0195
```

### Asset Prices and Benchmark Returns

Empyrical [yfinance](https://github.com/ranaroussi/yfinance) to download price data from [Yahoo! Finance](https://finance.yahoo.com/). To obtain the S&P returns since 1950, use:

>> Note: requires optional dependency `yfinance` - see installation instructions above.

```python
import empyrical as emp

symbol = '^GSPC'
returns = emp.utils.get_symbol_returns_from_yahoo(symbol,
                                                  start='1950-01-01')

import seaborn as sns  # requires separate installation
import matplotlib.pyplot as plt  # requires separate installation

fig, axes = plt.subplots(ncols=2, figsize=(14, 5))

with sns.axes_style('whitegrid'):
    returns.plot(ax=axes[0], rot=0, title='Time Series', legend=False)
    sns.histplot(returns, ax=axes[1], legend=False)
axes[1].set_title('Histogram')
sns.despine()
plt.tight_layout()
plt.suptitle('Daily S&P 500 Returns')
```

<a href="https://empyrical.ml4trading.io">
<img src="https://i.imgur.com/0PSxfSI.png" width="100%">
</a>

### Documentation

See the [documentation](https://empyrical.ml4trading.io) for details on the API.

## Support

Please [open an issue](https://github.com/stefan-jansen/empyrical-reloaded/issues/new) for support.

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/stefan-jansen/empyrical-reloaded/compare/).

## Testing

- install requirements
    - "pytest>=6.2.0",

```bash
pytest tests
```
