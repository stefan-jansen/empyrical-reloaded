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

empyrical requires Python 3.10+. You can install it using `pip`:

```bash
pip install empyrical-reloaded
```

or `conda` from the `conda-forge` channel

```bash
conda install empyrical-reloaded -c conda-forge
```

empyrical requires and installs the following packages while executing the above commands:

- numpy>=1.23.5
- pandas>=1.3.0
- scipy>=0.15.1

> Note that Numpy>=2.0 requires pandas>=2.2.2. If you are using an older version of pandas, you may need to upgrade
> accordingly, otherwise you may encounter compatibility issues.

Optional dependencies include [yfinance](https://github.com/ranaroussi/yfinance) to download price data
from [Yahoo! Finance](https://finance.yahoo.com/)
and [pandas-datareader](https://pandas-datareader.readthedocs.io/en/latest/) to
access [Fama-French](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) risk factors and FRED
treasury yields.

> Note that `pandas-datareader` is not compatible with Python>=3.12.

To install the optional dependencies, use:

```bash
pip install empyrical-reloaded[yfinance]
```

or

```bash
pip install empyrical-reloaded[datreader]
```

or

```bash
pip install empyrical-reloaded[yfinance,datreader]
```

## Usage

### Simple Statistics

Empyrical computes basic metrics from returns and volatility to alpha and beta, Value at Risk, and Shorpe or Sortino
ratios.

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

Empyrical also works with both [NumPy](https://numpy.org/) arrays and [Pandas](https://pandas.pydata.org/) data
structures:

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

> Note: requires optional dependency `pandas-datareader` - see installation instructions above.gst

```python
import pandas as pd
import empyrical as emp

risk_factors = emp.utils.get_fama_french()

pd.concat([risk_factors.head(), risk_factors.tail()])

Mkt - RF
SMB
HML
RF
Mom
Date
1970 - 01 - 02
00: 00:00 + 00: 00
0.0118
0.0129
0.0101
0.00029 - 0.0340
1970 - 01 - 05
00: 00:00 + 00: 00
0.0059
0.0067
0.0072
0.00029 - 0.0153
1970 - 01 - 06
00: 00:00 + 00: 00 - 0.0074
0.0010
0.0021
0.00029
0.0038
1970 - 01 - 07
00: 00:00 + 00: 00 - 0.0015
0.0040 - 0.0033
0.00029
0.0011
1970 - 01 - 0
8
00: 00:00 + 00: 00
0.0004
0.0018 - 0.0017
0.00029
0.0033
2024 - 03 - 22
00: 00:00 + 00: 00 - 0.0023 - 0.0087 - 0.0053
0.00021
0.0043
2024 - 03 - 25
00: 00:00 + 00: 00 - 0.0026 - 0.0024
0.0088
0.00021 - 0.0034
2024 - 03 - 26
00: 00:00 + 00: 00 - 0.0026
0.0009 - 0.0013
0.00021
0.0009
2024 - 03 - 27
00: 00:00 + 00: 00
0.0088
0.0104
0.0091
0.00021 - 0.0134
2024 - 03 - 28
00: 00:00 + 00: 00
0.0010
0.0029
0.0048
0.00021 - 0.0044
```

### Asset Prices and Benchmark Returns

Empyrical use [yfinance](https://github.com/ranaroussi/yfinance) to download price data
from [Yahoo! Finance](https://finance.yahoo.com/). To obtain the S&P returns since 1950, use:

> Note: requires optional dependency `yfinance` - see installation instructions above.

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

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits,
and [open a pull request](https://github.com/stefan-jansen/empyrical-reloaded/compare/).

## Testing

- install requirements
    - "pytest>=6.2.0",

```bash
pytest tests
```
