import numpy as np
import pandas as pd
import pytest

import empyrical


@pytest.mark.parametrize(
    "function",
    [empyrical.beta_fragility_heuristic, empyrical.beta_fragility_heuristic_aligned],
)
@pytest.mark.parametrize("as_series", [False, True])
@pytest.mark.parametrize("valid_count", [0, 1, 2])
def test_fragility_requires_three_nonmissing_pairs(function, as_series, valid_count):
    strategy = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    benchmark = np.array([-0.02, -0.01, 0.0, 0.01, 0.02])
    strategy[valid_count:] = np.nan
    if as_series:
        dates = pd.date_range("2024-01-02", periods=5)
        strategy = pd.Series(strategy, index=dates)
        benchmark = pd.Series(benchmark, index=dates)
    assert np.isnan(function(strategy, benchmark))
    assert np.isnan(function(strategy[:valid_count], benchmark[:valid_count]))


def test_fragility_disjoint_dates_have_no_paired_observations():
    strategy = pd.Series(
        [0.01, 0.02, 0.03], index=pd.date_range("2024-01-02", periods=3)
    )
    benchmark = pd.Series(
        [0.02, 0.03, 0.04], index=pd.date_range("2024-01-05", periods=3)
    )
    assert np.isnan(empyrical.beta_fragility_heuristic(strategy, benchmark))


@pytest.mark.parametrize(
    "function",
    [empyrical.beta_fragility_heuristic, empyrical.beta_fragility_heuristic_aligned],
)
@pytest.mark.parametrize("as_series", [False, True])
def test_fragility_retains_eligible_affine_sample_with_missing_data(
    function, as_series
):
    strategy = np.array([-0.03, -0.01, 0.01, 0.03, 0.05, np.nan])
    benchmark = np.array([-0.02, -0.01, 0.0, 0.01, 0.02, 0.03])
    if as_series:
        strategy = pd.Series(strategy)
        benchmark = pd.Series(benchmark)
    np.testing.assert_allclose(function(strategy, benchmark), 0.0, atol=1e-15)
