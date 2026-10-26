Capability reference
====================

This is a historical, source-pinned assessment. Its classifications predate
later successor implementations. Use Diagnostic's maintained
`Empyrical migration guide <https://github.com/ml4t/diagnostic/blob/main/docs/user-guide/empyrical-migration.md>`_
for current routes and release requirements; the counts below do not establish
current coverage or a complete-replacement recommendation.

This reference covers 82 capabilities. Thirty-nine have partial destination
coverage and 43 have no verified equivalent. Aliases and small public helpers
are included; the counts do not measure the proportion of a user's analytical
workload. No capability is marked complete without its relevant API, numerical
and workflow contracts being qualified.

Source and test links are pinned. Test links identify navigation targets; they
do not assert that every linked test was executed in this assessment. The
recorded numerical comparison contains 169 shared-input cases, of which 143
match values and shapes within rtol=1e-10 and atol=1e-12, including equal NaNs.
An equal case does not establish complete contract coverage.

Use :doc:`migration` for the runnable columnwise recipe. This page is a lookup
reference, not a replacement implementation. The
:download:`machine-readable coverage <_static/empyrical-successor-coverage.json>`
retains the same classification and precise source/test links.
The :download:`shared-input numerical evidence <_static/empyrical-numerical-evidence.json>`
records inputs, package versions, pinned source fingerprints and every result.

.. list-table::
   :header-rows: 1
   :widths: 16 23 9 52

   * - Empyrical capability
     - Existing destination
     - Coverage
     - Migration requirement
   * - `annualization_factor <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L50>`_
     - None verified
     - missing
     - Documented period constants and explicit scale can be passed as periods_per_year/annualization_factor. No verified public resolver preserves Empyrical's period validation and explicit-override precedence.
   * - `simple_returns <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L88>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L50>`_)
     - `returns <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/src/ml4t/engineer/features/utils/arithmetic.py#L12>`_ (`test <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/tests/test_api_bar_grid.py#L66>`_)
     - partial
     - Polars expression accepts a column name and retains a leading null; Empyrical accepts array/Series/DataFrame and drops the first row. Float-price probe matches after trimming. Integer precision needs PR88's exact-difference contract.
   * - `cum_returns <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L117>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L107>`_)
     - None verified
     - missing
     - No standalone equivalent verified. Preserve starting_value=0 (fractional gain) versus nonzero wealth base, neutral treatment of NaN, per-column labels, empty inputs and out identity. NumPy recipes are possible adapters, not existing successor implementations.
   * - `cum_returns_final <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L180>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L137>`_)
     - None verified
     - missing
     - No standalone equivalent verified. Preserve starting_value=0 (fractional gain) versus nonzero wealth base, neutral treatment of NaN, per-column labels, empty inputs and out identity. NumPy recipes are possible adapters, not existing successor implementations.
   * - `aggregate_returns <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L216>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_iso_week.py#L23>`_)
     - `PortfolioAnalysis.compute_monthly_returns <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/analysis.py#L762>`_; `PortfolioAnalysis.compute_annual_returns <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/analysis.py#L793>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_input_contract.py#L22>`_)
     - partial
     - Month/year reporting exists; generic weekly ISO-year, monthly, quarterly and yearly compounding with Empyrical labels has not been numerically qualified. Preserve sparse dates/timezones and distinguish civil grouping from exchange sessions.
   * - `drawdown_series <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L257>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_drawdown_shape.py#L9>`_)
     - `PortfolioAnalysis.compute_drawdown_analysis <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/analysis.py#L579>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L781>`_)
     - partial
     - Extract underwater_curve. Finite/initial-loss probes match. Constructor rejects NaN and duplicate dates; preserve labels, out identity, empty and total-loss behavior in a compatibility wrapper.
   * - `max_drawdown <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L320>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L204>`_)
     - `max_drawdown <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L144>`_; `maximum_drawdown <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/metrics/risk_adjusted.py#L213>`_; `maximum_drawdown <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/src/ml4t/engineer/features/risk.py#L225>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L163>`_)
     - partial
     - Diagnostic scalar kernel matches tested finite, missing and degenerate one-dimensional cases. Risk-adjusted API returns a dict, Engineer takes prices and returns expressions; DataFrame flattening, labels and out require adapters.
   * - `roll_max_drawdown <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L362>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1198>`_)
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `annual_return <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L365>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L243>`_)
     - `annual_return <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L162>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L194>`_)
     - partial
     - annualization -> periods_per_year; cagr is a legacy alias. Tested one-dimensional scalar cases match, including NaN length convention. High-level constructor rejects NaN. Columnwise DataFrame and empty/type/default contracts remain adapter requirements.
   * - `cagr <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L407>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1105>`_)
     - `annual_return <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L162>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L194>`_)
     - partial
     - annualization -> periods_per_year; cagr is a legacy alias. Tested one-dimensional scalar cases match, including NaN length convention. High-level constructor rejects NaN. Columnwise DataFrame and empty/type/default contracts remain adapter requirements.
   * - `roll_cagr <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L441>`_
     - `PortfolioAnalysis.compute_rolling_metrics <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/analysis.py#L388>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L712>`_)
     - partial
     - Related returns output exists with n-row padded warmup; Empyrical usually trims warmup. Sharpe/volatility window1/3/n/>n probes record actual results; returns is compounded window return, not automatically annualized CAGR. Beta alignment/missingness and output labels require qualification. Preserve explicit observation counts and annualization.
   * - `annual_volatility <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L444>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L260>`_)
     - `annual_volatility <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L191>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L220>`_)
     - partial
     - Sample standard deviation and ordinary scale match tested one-dimensional cases. Levy alpha parameter is absent; unannualized result times factor\*\*(1/alpha) was verified for alpha=1.5. Preserve axis, output buffer and fractional scale.
   * - `roll_annual_volatility <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L496>`_
     - `PortfolioAnalysis.compute_rolling_metrics <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/analysis.py#L388>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L712>`_)
     - partial
     - Related volatility output exists with n-row padded warmup; Empyrical usually trims warmup. Sharpe/volatility window1/3/n/>n probes record actual results; returns is compounded window return, not automatically annualized CAGR. Beta alignment/missingness and output labels require qualification. Preserve explicit observation counts and annualization.
   * - `calmar_ratio <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L501>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L278>`_)
     - `calmar_ratio <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L68>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L324>`_)
     - partial
     - Tested scalar cases and explicit scales match. DataFrame, empty, invalid returns and annualization type contracts require compatibility qualification.
   * - `omega_ratio <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L550>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L301>`_)
     - `omega_ratio <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L92>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L89>`_)
     - partial
     - No-loss denominator differs: Empyrical NaN versus Diagnostic +Inf. Preserve periodic risk_free subtraction and geometric conversion of annual required_return using annualization; do not silently convert both as annual rates.
   * - `sharpe_ratio <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L606>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L340>`_)
     - `periodic_sharpe_ratio <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/metrics/risk_adjusted.py#L99>`_; `sharpe_ratio <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/metrics/risk_adjusted.py#L36>`_; `risk_adjusted_returns <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/src/ml4t/engineer/features/risk.py#L539>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_metrics.py#L181>`_)
     - partial
     - Use Diagnostic periodic API for Empyrical's per-observation risk_free; ordinary Diagnostic API takes annual rf. Periodic adapters match 1/12/52/252/365 scales in executed probes. Preserve sample ddof=1, columnwise outputs and out. Engineer epsilon and annual-rf convention differ.
   * - `roll_sharpe_ratio <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L677>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1221>`_)
     - `PortfolioAnalysis.compute_rolling_metrics <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/analysis.py#L388>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L712>`_)
     - partial
     - Related sharpe output exists with n-row padded warmup; Empyrical usually trims warmup. Sharpe/volatility window1/3/n/>n probes record actual results; returns is compounded window return, not automatically annualized CAGR. Beta alignment/missingness and output labels require qualification. Preserve explicit observation counts and annualization.
   * - `sortino_ratio <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L680>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_sortino_labels.py#L7>`_)
     - `periodic_sortino_ratio <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/metrics/risk_adjusted.py#L326>`_; `sortino_ratio <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/metrics/risk_adjusted.py#L284>`_; `risk_adjusted_returns <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/src/ml4t/engineer/features/risk.py#L539>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_metrics.py#L359>`_)
     - partial
     - Use periodic API for per-observation required_return/MAR. Tested periodic cases/scales match; preserve all-observation downside denominator, optional precomputed _downside_risk, axis/out and nonfinite behavior.
   * - `roll_sortino_ratio <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L767>`_
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `downside_risk <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L770>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_downside_alignment.py#L7>`_)
     - `downside_deviation <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/src/ml4t/engineer/features/risk.py#L359>`_ (`test <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/tests/features/test_low_coverage_boost.py#L769>`_)
     - partial
     - Engineer full-window result matches Empyrical annualization=1 in one probe. Add explicit factor\*\*0.5, per-observation MAR, vector/column and out adapter; rolling expression minimum window and warmup differ.
   * - `roll_downside_risk <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L854>`_
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `roll_downsize_risk <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L858>`_
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `excess_sharpe <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L867>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_excess_sharpe.py#L7>`_)
     - `information_ratio <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L315>`_; `information_ratio <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/src/ml4t/engineer/features/risk.py#L711>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/validation/test_pyfolio_comparison.py#L404>`_)
     - partial
     - Diagnostic periods_per_year=1 matches tested finite active returns. Empyrical is unannualized; preserve dated outer alignment, paired NaNs, ddof, zero tracking error, labels/out. Engineer returns a rolling expression.
   * - `roll_excess_sharpe <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L920>`_
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `alpha_beta <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L923>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L780>`_)
     - `alpha_beta <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L271>`_; `signal.compute_factor_alpha_beta <https://github.com/ml4t/diagnostic/blob/94345f90b7b92ecc300541184a1bc23fb560f55a/src/ml4t/diagnostic/signal/factor_regression.py#L222>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/validation/test_pyfolio_comparison.py#L378>`_)
     - partial
     - Diagnostic uses arithmetic annual alpha; Empyrical compounds periodic intercept geometrically. Verified adapter requests periods_per_year=1 then compounds (1+a)\*\*factor-1. Extract alpha/beta as needed. Implement dated alignment separately from aligned row API, pairwise missingness, constant benchmark, risk_free and axis/out. Existing factor-panel regression compounds alpha but fixes its benchmark to the same asset universe; reuse its method without claiming arbitrary-benchmark compatibility.
   * - `roll_alpha_beta <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L979>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1300>`_)
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `alpha_beta_aligned <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1002>`_
     - `alpha_beta <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L271>`_; `signal.compute_factor_alpha_beta <https://github.com/ml4t/diagnostic/blob/94345f90b7b92ecc300541184a1bc23fb560f55a/src/ml4t/diagnostic/signal/factor_regression.py#L222>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/validation/test_pyfolio_comparison.py#L378>`_)
     - partial
     - Diagnostic uses arithmetic annual alpha; Empyrical compounds periodic intercept geometrically. Verified adapter requests periods_per_year=1 then compounds (1+a)\*\*factor-1. Extract alpha/beta as needed. Implement dated alignment separately from aligned row API, pairwise missingness, constant benchmark, risk_free and axis/out. Existing factor-panel regression compounds alpha but fixes its benchmark to the same asset universe; reuse its method without claiming arbitrary-benchmark compatibility.
   * - `roll_alpha_beta_aligned <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1067>`_
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `alpha <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1072>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L798>`_)
     - `alpha_beta <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L271>`_; `signal.compute_factor_alpha_beta <https://github.com/ml4t/diagnostic/blob/94345f90b7b92ecc300541184a1bc23fb560f55a/src/ml4t/diagnostic/signal/factor_regression.py#L222>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/validation/test_pyfolio_comparison.py#L378>`_)
     - partial
     - Diagnostic uses arithmetic annual alpha; Empyrical compounds periodic intercept geometrically. Verified adapter requests periods_per_year=1 then compounds (1+a)\*\*factor-1. Extract alpha/beta as needed. Implement dated alignment separately from aligned row API, pairwise missingness, constant benchmark, risk_free and axis/out. Existing factor-panel regression compounds alpha but fixes its benchmark to the same asset universe; reuse its method without claiming arbitrary-benchmark compatibility.
   * - `roll_alpha <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1135>`_
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `alpha_aligned <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1138>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_alpha_labels.py#L9>`_)
     - `alpha_beta <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L271>`_; `signal.compute_factor_alpha_beta <https://github.com/ml4t/diagnostic/blob/94345f90b7b92ecc300541184a1bc23fb560f55a/src/ml4t/diagnostic/signal/factor_regression.py#L222>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/validation/test_pyfolio_comparison.py#L378>`_)
     - partial
     - Diagnostic uses arithmetic annual alpha; Empyrical compounds periodic intercept geometrically. Verified adapter requests periods_per_year=1 then compounds (1+a)\*\*factor-1. Extract alpha/beta as needed. Implement dated alignment separately from aligned row API, pairwise missingness, constant benchmark, risk_free and axis/out. Existing factor-panel regression compounds alpha but fixes its benchmark to the same asset universe; reuse its method without claiming arbitrary-benchmark compatibility.
   * - `roll_alpha_aligned <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1228>`_
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `beta <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1231>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L961>`_)
     - `alpha_beta <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L271>`_; `signal.compute_factor_alpha_beta <https://github.com/ml4t/diagnostic/blob/94345f90b7b92ecc300541184a1bc23fb560f55a/src/ml4t/diagnostic/signal/factor_regression.py#L222>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/validation/test_pyfolio_comparison.py#L378>`_)
     - partial
     - Diagnostic uses arithmetic annual alpha; Empyrical compounds periodic intercept geometrically. Verified adapter requests periods_per_year=1 then compounds (1+a)\*\*factor-1. Extract alpha/beta as needed. Implement dated alignment separately from aligned row API, pairwise missingness, constant benchmark, risk_free and axis/out. Existing factor-panel regression compounds alpha but fixes its benchmark to the same asset universe; reuse its method without claiming arbitrary-benchmark compatibility.
   * - `roll_beta <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1265>`_
     - `PortfolioAnalysis.compute_rolling_metrics <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/analysis.py#L388>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L712>`_)
     - partial
     - Related beta output exists with n-row padded warmup; Empyrical usually trims warmup. Sharpe/volatility window1/3/n/>n probes record actual results; returns is compounded window return, not automatically annualized CAGR. Beta alignment/missingness and output labels require qualification. Preserve explicit observation counts and annualization.
   * - `beta_aligned <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1268>`_
     - `alpha_beta <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L271>`_; `signal.compute_factor_alpha_beta <https://github.com/ml4t/diagnostic/blob/94345f90b7b92ecc300541184a1bc23fb560f55a/src/ml4t/diagnostic/signal/factor_regression.py#L222>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/validation/test_pyfolio_comparison.py#L378>`_)
     - partial
     - Diagnostic uses arithmetic annual alpha; Empyrical compounds periodic intercept geometrically. Verified adapter requests periods_per_year=1 then compounds (1+a)\*\*factor-1. Extract alpha/beta as needed. Implement dated alignment separately from aligned row API, pairwise missingness, constant benchmark, risk_free and axis/out. Existing factor-panel regression compounds alpha but fixes its benchmark to the same asset universe; reuse its method without claiming arbitrary-benchmark compatibility.
   * - `roll_beta_aligned <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1384>`_
     - `PortfolioAnalysis.compute_rolling_metrics <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/analysis.py#L388>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L712>`_)
     - partial
     - Related beta output exists with n-row padded warmup; Empyrical usually trims warmup. Sharpe/volatility window1/3/n/>n probes record actual results; returns is compounded window return, not automatically annualized CAGR. Beta alignment/missingness and output labels require qualification. Preserve explicit observation counts and annualization.
   * - `stability_of_timeseries <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1387>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1073>`_)
     - `stability_of_timeseries <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L243>`_
     - partial
     - Empyrical regresses cumulative log returns; Diagnostic regresses wealth. Finite and constant-positive probes differ. Provide explicit legacy logarithmic definition rather than relabel wealth R-squared.
   * - `tail_ratio <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1416>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1090>`_)
     - `tail_ratio <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L121>`_; `tail_ratio <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/src/ml4t/engineer/features/risk.py#L409>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L138>`_)
     - partial
     - Empyrical abs(p95)/abs(p5); Diagnostic p95/abs(p5) changes sign for entirely negative returns. Zero denominator gives Inf versus NaN. Engineer rolling expression uses epsilon. Preserve quantile interpolation, NaN omission and undefined outcomes.
   * - `capture <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1445>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1239>`_)
     - `up_down_capture <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L351>`_
     - partial
     - Diagnostic returns up/down components based on cumulative wealth ratios; Empyrical ratios annualized geometric returns on selected benchmark signs and up_down_capture divides those components. Finite probe differs by more than tolerance. No equivalent behavior can be claimed from the shared name.
   * - `beta_fragility_heuristic <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1480>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_fragility_pairs.py#L26>`_)
     - None verified
     - missing
     - No verified implementation in either successor. Preserve minimum three usable pairs, corrected order-statistic interpolation, middle weights and NaN output. Equal-factor ordering remains an explicit unresolved definition decision; do not encode PR57 wholesale.
   * - `beta_fragility_heuristic_aligned <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1516>`_
     - None verified
     - missing
     - No verified implementation in either successor. Preserve minimum three usable pairs, corrected order-statistic interpolation, middle weights and NaN output. Equal-factor ordering remains an explicit unresolved definition decision; do not encode PR57 wholesale.
   * - `gpd_risk_estimates <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1594>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_gpd_probability.py#L9>`_)
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_risk_estimates_aligned <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1635>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1185>`_)
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_es_calculator <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1723>`_
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_var_calculator <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1733>`_
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_loglikelihood_minimizer_aligned <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1745>`_
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_loglikelihood_factory <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1764>`_
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_loglikelihood <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1768>`_
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_loglikelihood_scale_and_shape_factory <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1775>`_
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_loglikelihood_scale_and_shape <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1785>`_
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_loglikelihood_scale_only_factory <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1797>`_
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `gpd_loglikelihood_scale_only <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1802>`_
     - None verified
     - missing
     - No verified generalized-Pareto tail estimator/helpers in successors. Preserve five returned estimates (threshold, scale, shape, VaR, ES), loss sign, optimizer failures, small samples, nonpositive scale, shape-zero limit and parameter validity. Low-level public-module helpers also require replacement or documented retention.
   * - `up_capture <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1811>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1498>`_)
     - `up_down_capture <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L351>`_
     - partial
     - Diagnostic returns up/down components based on cumulative wealth ratios; Empyrical ratios annualized geometric returns on selected benchmark signs and up_down_capture divides those components. Finite probe differs by more than tolerance. No equivalent behavior can be claimed from the shared name.
   * - `down_capture <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1845>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1257>`_)
     - `up_down_capture <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L351>`_
     - partial
     - Diagnostic returns up/down components based on cumulative wealth ratios; Empyrical ratios annualized geometric returns on selected benchmark signs and up_down_capture divides those components. Finite probe differs by more than tolerance. No equivalent behavior can be claimed from the shared name.
   * - `up_down_capture <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1879>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1480>`_)
     - `up_down_capture <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L351>`_
     - partial
     - Diagnostic returns up/down components based on cumulative wealth ratios; Empyrical ratios annualized geometric returns on selected benchmark signs and up_down_capture divides those components. Finite probe differs by more than tolerance. No equivalent behavior can be claimed from the shared name.
   * - `batting_average <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1911>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1815>`_)
     - None verified
     - missing
     - Directional prediction hit_rate is not benchmark-relative batting average. Required tuple covers overall/up/down outperformance with paired missingness and dated alignment; use PR92 regression cases.
   * - `up_alpha_beta <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1956>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1463>`_)
     - `alpha_beta <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L271>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/validation/test_pyfolio_comparison.py#L378>`_)
     - partial
     - No direct conditional API verified; select benchmark >0 or <0 using paired aligned observations, then use corrected geometric-alpha adapter. Preserve empty sign subsets and row-versus-date alignment.
   * - `down_alpha_beta <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1974>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1442>`_)
     - `alpha_beta <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L271>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/validation/test_pyfolio_comparison.py#L378>`_)
     - partial
     - No direct conditional API verified; select benchmark >0 or <0 using paired aligned observations, then use corrected geometric-alpha adapter. Preserve empty sign subsets and row-versus-date alignment.
   * - `roll_up_capture <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L1990>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1419>`_)
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `roll_down_capture <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L2014>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1385>`_)
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `roll_up_down_capture <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L2038>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1356>`_)
     - None verified
     - missing
     - No matching rolling family verified. Compose only after scalar definition and alignment are fixed; preserve output shape/labels, duplicate dates, out identity and NaNs. Historical misspelling roll_downsize_risk is a deprecated alias. Overlong-window behavior remains a separate explicit contract question.
   * - `value_at_risk <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L2068>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_empty_var.py#L8>`_)
     - `value_at_risk <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L208>`_; `value_at_risk <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/src/ml4t/engineer/features/risk.py#L51>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L242>`_)
     - partial
     - cutoff -> 1-confidence. Diagnostic omits NaN while legacy VaR currently propagates it; Engineer historical quantile defaults nearest, versus Empyrical linear (verified -.18 versus -.181). Preserve signed return quantile, cutoff bounds, axis and degeneracy.
   * - `conditional_value_at_risk <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/stats.py#L2090>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1526>`_)
     - `conditional_var <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L225>`_; `conditional_value_at_risk <https://github.com/ml4t/engineer/blob/83b7d0d4e0e79bc36bb5044c7ac9aa63ca0e69b3/src/ml4t/engineer/features/risk.py#L136>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_portfolio_analysis.py#L263>`_)
     - partial
     - cutoff -> 1-confidence. Legacy tail uses floor((n-1)\*cutoff)+1 order statistics; Diagnostic percentile-threshold selection includes all cutoff ties (verified -.15 versus -.133333). PR56 independently repairs NaN/empty handling, not tie definition. Freeze the intended release contract before adapter acceptance.
   * - `roll <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L73>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_rolling_window_offset.py#L7>`_)
     - None verified
     - missing
     - No generic public callable rolling/sign-filter/strided-window utility verified. Need explicit positive windows, row pairing, labels, duplicate timestamps, mutability and overlong-window contract. Reuse verified duplicate-index fixes; do not infer schedule semantics.
   * - `up <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L116>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1662>`_)
     - None verified
     - missing
     - No generic public callable rolling/sign-filter/strided-window utility verified. Need explicit positive windows, row pairing, labels, duplicate timestamps, mutability and overlong-window contract. Reuse verified duplicate-index fixes; do not infer schedule semantics.
   * - `down <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L142>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_stats.py#L1649>`_)
     - None verified
     - missing
     - No generic public callable rolling/sign-filter/strided-window utility verified. Need explicit positive windows, row pairing, labels, duplicate timestamps, mutability and overlong-window contract. Reuse verified duplicate-index fixes; do not infer schedule semantics.
   * - `cache_dir <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L185>`_
     - None verified
     - missing
     - Compatibility utility rather than analytical metric. Standard-library/pandas replacement or small documented wrapper is sufficient after verifying environment override, path/error behavior, timezone conversion and warning stacklevel. No existing successor drop-in verified.
   * - `data_path <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L198>`_
     - None verified
     - missing
     - Compatibility utility rather than analytical metric. Standard-library/pandas replacement or small documented wrapper is sufficient after verifying environment override, path/error behavior, timezone conversion and warning stacklevel. No existing successor drop-in verified.
   * - `ensure_directory <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L202>`_
     - None verified
     - missing
     - Compatibility utility rather than analytical metric. Standard-library/pandas replacement or small documented wrapper is sufficient after verifying environment override, path/error behavior, timezone conversion and warning stacklevel. No existing successor drop-in verified.
   * - `get_utc_timestamp <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L214>`_
     - None verified
     - missing
     - Compatibility utility rather than analytical metric. Standard-library/pandas replacement or small documented wrapper is sufficient after verifying environment override, path/error behavior, timezone conversion and warning stacklevel. No existing successor drop-in verified.
   * - `get_fama_french <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L245>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_fama_french.py#L12>`_)
     - `FactorData.from_fama_french <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/factor/data.py#L131>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_factor_data.py#L201>`_)
     - partial
     - Related provider workflow exists but schema/units are unqualified: FactorData keeps RF separately and Polars timestamps; Empyrical uses UTC pandas frames and Mkt-RF/SMB/HML/RF plus momentum columns (four risk factors and RF), despite stale five-factor wording in its docstring. Verify actual provider values, RF percent conversion, bounds and cache behavior before recommending adapter.
   * - `get_returns_cached <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L288>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_return_cache.py#L12>`_)
     - None verified
     - missing
     - No equivalent destination-owned public provider/cache workflow verified. Retain Empyrical, or qualify ML4T-Data integration separately with exact Yahoo adjustment, FRED units, optional dependency, default-end and UTC-cache behavior. PR110 fixes the reproduced pandas3 self-cache failure.
   * - `load_portfolio_risk_factors <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L361>`_
     - `FactorData.from_fama_french <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/factor/data.py#L131>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_factor_data.py#L201>`_)
     - partial
     - Related provider workflow exists but schema/units are unqualified: FactorData keeps RF separately and Polars timestamps; Empyrical uses UTC pandas frames and Mkt-RF/SMB/HML/RF plus momentum columns (four risk factors and RF), despite stale five-factor wording in its docstring. Verify actual provider values, RF percent conversion, bounds and cache behavior before recommending adapter.
   * - `get_treasury_yield <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L391>`_
     - None verified
     - missing
     - No equivalent destination-owned public provider/cache workflow verified. Retain Empyrical, or qualify ML4T-Data integration separately with exact Yahoo adjustment, FRED units, optional dependency, default-end and UTC-cache behavior. PR110 fixes the reproduced pandas3 self-cache failure.
   * - `get_symbol_returns_from_yahoo <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L420>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_yahoo_errors.py#L8>`_)
     - None verified
     - missing
     - No equivalent destination-owned public provider/cache workflow verified. Retain Empyrical, or qualify ML4T-Data integration separately with exact Yahoo adjustment, FRED units, optional dependency, default-end and UTC-cache behavior. PR110 fixes the reproduced pandas3 self-cache failure.
   * - `default_returns_func <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L462>`_
     - None verified
     - missing
     - No equivalent destination-owned public provider/cache workflow verified. Retain Empyrical, or qualify ML4T-Data integration separately with exact Yahoo adjustment, FRED units, optional dependency, default-end and UTC-cache behavior. PR110 fixes the reproduced pandas3 self-cache failure.
   * - `rolling_window <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L510>`_
     - None verified
     - missing
     - No generic public callable rolling/sign-filter/strided-window utility verified. Need explicit positive windows, row pairing, labels, duplicate timestamps, mutability and overlong-window contract. Reuse verified duplicate-index fixes; do not infer schedule semantics.
   * - `perf_attrib <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/perf_attrib.py#L5>`_ (`test <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/tests/test_perf_attrib.py#L13>`_)
     - `compute_return_attribution <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/factor/attribution.py#L25>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_factor_attribution.py#L30>`_)
     - partial
     - Empyrical multiplies supplied holdings by supplied asset-factor loadings and decomposes factor/common/specific/tilt/timing returns. Diagnostic estimates lagged rolling betas from portfolio returns and FactorData, with warmup. This is a related workflow, not coverage of supplied holdings/exposures. Preserve date/ticker alignment, cash, factor units and common+specific=total.
   * - `compute_exposures <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/perf_attrib.py#L139>`_
     - `compute_return_attribution <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/factor/attribution.py#L25>`_ (`test <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/tests/test_evaluation/test_factor_attribution.py#L30>`_)
     - partial
     - Empyrical multiplies supplied holdings by supplied asset-factor loadings and decomposes factor/common/specific/tilt/timing returns. Diagnostic estimates lagged rolling betas from portfolio returns and FactorData, with warmup. This is a related workflow, not coverage of supplied holdings/exposures. Preserve date/ticker alignment, cash, factor units and common+specific=total.
   * - `deprecated <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/deprecate.py#L21>`_
     - None verified
     - missing
     - Compatibility utility rather than analytical metric. Standard-library/pandas replacement or small documented wrapper is sufficient after verifying environment override, path/error behavior, timezone conversion and warning stacklevel. No existing successor drop-in verified.
   * - `period constants and metric registries <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/periods.py#L1>`_
     - `annual_return <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L162>`_; `annual_volatility <https://github.com/ml4t/diagnostic/blob/8faa03f5d8b72d44391451074da4c3f906f9d57b/src/ml4t/diagnostic/evaluation/portfolio_analysis/metrics.py#L191>`_
     - partial
     - Retain DAILY/WEEKLY/MONTHLY/QUARTERLY/YEARLY, 252/52/12/4/1 scales and SIMPLE_STAT_FUNCS/FACTOR_STAT_FUNCS iteration order where used. Successors accept explicit numeric scales, not these registries. A 252 convention alone is not a defect.
   * - `provider default end-date boundary (_1_bday_ago) <https://github.com/stefan-jansen/empyrical-reloaded/blob/4ee3e80c6dacaf38b572e0e0e9f7c349713906c1/src/empyrical/utils.py#L241>`_
     - None verified
     - missing
     - Legacy pandas BDay counts weekdays, not NYSE holidays. Do not describe it as exchange-session-aware. Destination time-aware wrappers must preserve explicit calendar > declared metadata > NYSE; explicit None is row mode, not a 24/7 schedule. Session labels, timestamp instants, DST and annualization overrides require separate acceptance tests; no calendar implementation change is authorized by this assessment.
