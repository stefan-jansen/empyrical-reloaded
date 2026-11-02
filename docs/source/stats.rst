.. _stats:

Performance & Risk Metrics
--------------------------

The module :mod:`empyrical.stats` includes various return and risk metrics, such as the
computation of returns and volatility, alpha and beta, Value at Risk, and Sharpe or Sortino ratios.

Omega zero-downside results in 0.7.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``omega_ratio`` now returns positive infinity when its adjusted returns have
positive upside and zero downside, provided the nonmissing adjusted returns are
finite. For example, returns ``[0.01, 0.02, 0.03]`` at the default threshold produce
``inf`` instead of the ``nan`` returned by 0.7.1 and earlier. This intentionally
changes the historical, explicitly tested convention to represent an unbounded
gain-to-shortfall ratio. Code that used ``isnan`` to identify no-loss samples
should distinguish ``isposinf`` from undefined results.

When every adjusted return equals the threshold, or every observation is missing,
both sums are zero and the result remains ``nan``. Loss-only samples still return
zero. The risk-free rate remains periodic; only ``required_return`` is converted
geometrically using ``annualization``, unless ``annualization=1``. Missing adjusted
returns are omitted and the existing minimum of two input rows is unchanged.
Inputs with infinite adjusted returns retain their previous behavior; this change
does not introduce general input validation or change Calmar's no-drawdown result.

.. automodule:: empyrical.stats
    :members:
    :undoc-members:
    :show-inheritance:
