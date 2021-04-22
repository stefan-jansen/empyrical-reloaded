.. _api-reference:

API
===

The empyrical API is organized into various modules:

* Performance & Risk Metrics: :mod:`empyrical.stats`
* Performance Attribution: :mod:`empyrical.perf_attrib`
* Utilities: :mod:`empyrical.utils`

Performance & Risk Metrics
--------------------------

The module :mod:`empyrical.stats` includes various return and risk metrics, such as the
computation of returns and volatility, alpha and beta, Value at Risk, and Shorpe or Sortino ratios.

.. automodule:: empyrical.stats
    :members:
    :undoc-members:
    :show-inheritance:

Performance Attribution
-----------------------

The module :mod:`empyrical.perf_attrib` facilitates the attribution of performance to various risk factors.

.. automodule:: empyrical.perf_attrib
    :members:
    :undoc-members:
    :show-inheritance:

Utilities
---------

The module :mod:`empyrical.utils` contains various helper functions, e.g. to source risk factor and
return data using `pandas-datareader and `yfinance`.

.. automodule:: empyrical.utils
    :members:
    :undoc-members:
    :show-inheritance:
