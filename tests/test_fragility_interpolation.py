import numpy as np
import pandas as pd
import pytest

import empyrical


@pytest.mark.parametrize(
    "function",
    [empyrical.beta_fragility_heuristic, empyrical.beta_fragility_heuristic_aligned],
)
@pytest.mark.parametrize("as_series", [False, True])
@pytest.mark.parametrize(
    "factors,quadratic_gap",
    [
        ([-0.02, 0.0, 0.03], -0.0006),
        ([-0.02, -0.01, 0.01, 0.03], -0.0006),
        ([-0.04, -0.02, 0.0, 0.01, 0.03], -0.0012),
        ([-0.05, -0.03, -0.02, 0.0, 0.01, 0.02, 0.04], -0.002),
    ],
)
@pytest.mark.parametrize("exposure", ["affine", "concave"])
def test_fragility_matches_convex_gap_for_unique_factors(
    function, as_series, factors, quadratic_gap, exposure
):
    benchmark = np.array(factors)
    if exposure == "affine":
        strategy = 0.01 + 2 * benchmark
        expected = 0.0
    else:
        strategy = -(benchmark**2)
        expected = quadratic_gap
    if as_series:
        dates = pd.date_range("2024-01-02", periods=len(benchmark))
        strategy = pd.Series(strategy, index=dates)
        benchmark = pd.Series(benchmark, index=dates)
    np.testing.assert_allclose(
        function(strategy, benchmark), expected, rtol=1e-12, atol=1e-15
    )
