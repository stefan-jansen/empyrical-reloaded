Migrating selected metrics
==========================

Start with Diagnostic's maintained
`Empyrical migration guide <https://github.com/ml4t/diagnostic/blob/main/docs/user-guide/empyrical-migration.md>`_
for current workflow and release requirements. This page preserves an earlier
source-pinned comparison; its destination gaps and environment requirements are
historical findings, not a current successor coverage assessment. Source-only
APIs are not necessarily available in the published package.

Move one calculation at a time and compare its input and output contracts.
Empyrical remains available for workflows without verified successor coverage.
ML4T Diagnostic is the actively developed successor for portfolio analysis;
ML4T Engineer provides feature expressions. Neither is an Empyrical drop-in API.

The historical :doc:`migration-reference` records every owned public function, generated
rolling wrapper, metric registry and observable provider-date boundary. Related
names count as partial coverage until their relevant contracts are qualified.
No complete-replacement recommendation follows from this guide.

For the published ten-metric baseline, use Diagnostic's
`Empyrical migration guide <https://github.com/ml4t/diagnostic/blob/942f367f2f6aff269804d2600ba34814c661bf61/docs/user-guide/empyrical-migration.md>`_.
That guide pins its packages and comparison script. Current source examples and
older installed packages must not be combined without qualification.

Run the columnwise comparison
-----------------------------

The example calls both libraries on the same two price-derived return streams,
then repeats with one missing strategy observation. It checks values, result
types and column labels for annual return, sample volatility, maximum drawdown,
Sharpe and Sortino. It also rejects an unadapted flattened DataFrame result.

Use Python 3.12 for this recipe. The pinned Diagnostic source declares
Python >=3.12,<3.15, while the forthcoming Empyrical release supports 3.11-3.15.
Users on 3.11 or 3.15 must retain Empyrical or separately qualify a supported
destination environment; the broader legacy support range is not inherited.

From a qualified Empyrical source checkout, run the source-pinned comparison:

.. code-block:: console

   uv run --no-project --python 3.12 --with . --with 'ml4t-diagnostic @ git+https://github.com/ml4t/diagnostic.git@8faa03f5d8b72d44391451074da4c3f906f9d57b' python examples/migrate_metrics.py

The JSON output names installed package versions and reports ten matching
examples. The installed-wheel demonstration uses Empyrical revision
``9ba9143109047932482457400d84064f9e777c13`` (development version
``0.5.11.dev125``), Diagnostic source revision
``8faa03f5d8b72d44391451074da4c3f906f9d57b`` (version ``0.1.9``),
NumPy 2.5.4, pandas 3.0.6 and Python 3.12.11. The package metadata version of
the pinned Diagnostic source does not imply that published Diagnostic 0.1.9
contains all these repairs. The development Empyrical version follows reachable
Git tags and is not a proposed release number.

.. literalinclude:: ../../examples/migrate_metrics.py
   :language: python

Keep the conventions explicit
-----------------------------

* Apply scalar destination kernels per column. Direct two-dimensional input can
  flatten independent strategies and return a scalar.
* Pass the observation scale explicitly. Daily 252, weekly 52 and monthly 12
  are conventions; they do not validate exchange sessions or fill missing bars.
* Empyrical Sharpe's risk-free rate and Sortino's required return are periodic
  rates. The example uses Diagnostic's periodic APIs for those arguments.
* Preserve the actual legacy return type. Volatility and Sharpe return ndarrays
  for these DataFrames; annual return, drawdown and Sortino preserve column
  labels in Series on the corrected source.
* Do not drop missing rows globally. Observation counts affect annual return,
  and paired metrics need a shared sample. High-level PortfolioAnalysis rejects
  some inputs accepted by these low-level scalar kernels.
* These adapters cover neither output buffers nor paired-date alignment,
  rolling windows, duplicate dates, every empty/degenerate case or provider
  workflows.

Retain workflows whose definitions differ
-----------------------------------------

The generic Diagnostic alpha API annualizes an arithmetic intercept; Empyrical
compounds it. Diagnostic's separate factor-panel regression already compounds
alpha, but uses the same supplied asset universe as its benchmark. It does not
accept an arbitrary external benchmark with Empyrical's complete contract.

Stability fits cumulative log returns in Empyrical and wealth in the compared
Diagnostic API. Capture uses annualized geometric returns in Empyrical and
wealth ratios in the compared destination API. Tail-ratio signs, VaR missingness,
CVaR cutoff ties and no-loss Omega results also differ. The reference identifies
the exact implementations and tests; these are not rounding discrepancies.

Keep Empyrical for unqualified GPD estimation, beta fragility, benchmark batting
average, complete rolling families, supplied-holdings attribution and provider
workflows. Retention avoids losing a calculation while an explicit successor
implementation is developed and tested. It does not satisfy the migration
readiness gate.

Calendar-aware destination workflows must separately preserve explicit calendar
selection, declared feed metadata and NYSE fallback, with explicit calendar=None
disabling calendars. Row-only calculation differs from a 24/7 schedule.
Empyrical's observation kernels and explicit annualization overrides remain
legitimate; its BDay provider helper counts weekdays rather than exchange
holidays.
