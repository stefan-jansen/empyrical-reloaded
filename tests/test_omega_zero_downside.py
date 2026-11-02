"""Preserve Omega's threshold contract while representing an unbounded ratio."""

import numpy as np
import pandas as pd
import pytest

import empyrical


@pytest.mark.parametrize("as_series", [False, True], ids=["array", "series"])
@pytest.mark.parametrize(
    "values, kwargs",
    [
        pytest.param([0.01, 0.02, 0.03], {}, id="reported-gains"),
        pytest.param([0.0, 0.01], {}, id="threshold-tie-and-gain"),
        pytest.param([np.nan, 0.01, 0.02], {}, id="missing-and-gains"),
        pytest.param([np.nan, 0.01], {}, id="one-present-observation"),
        pytest.param([0.01, 0.02, 0.03], {"risk_free": 0.01}, id="periodic-risk-free"),
        pytest.param(
            [0.125, 0.25],
            {"required_return": 0.125, "annualization": 1},
            id="periodic-required-return",
        ),
        pytest.param(
            [0.125, 0.25],
            {"required_return": 0.601806640625, "annualization": 4},
            id="geometric-annual-required-return",
        ),
        pytest.param(
            [0.375, 0.5],
            {"risk_free": 0.125, "required_return": 0.125, "annualization": 1},
            id="both-threshold-components",
        ),
        pytest.param(
            [0.0, 0.0],
            {"required_return": -1.0, "annualization": 1},
            id="periodic-threshold-does-not-use-annual-domain-guard",
        ),
        pytest.param([0.0, np.nextafter(0.0, 1.0)], {}, id="no-epsilon-cutoff"),
    ],
)
def test_omega_reports_unbounded_finite_upside_without_downside(
    values, kwargs, as_series
):
    returns = pd.Series(values) if as_series else np.array(values)

    assert np.isposinf(empyrical.omega_ratio(returns, **kwargs))


@pytest.mark.parametrize("as_series", [False, True], ids=["array", "series"])
@pytest.mark.parametrize(
    "values, kwargs, expected",
    [
        pytest.param([], {}, np.nan, id="empty"),
        pytest.param([0.01], {}, np.nan, id="single-return"),
        pytest.param([np.nan, np.nan], {}, np.nan, id="all-missing"),
        pytest.param([0.0, 0.0], {}, np.nan, id="zero-upside-zero-downside"),
        pytest.param(
            [0.125, 0.125],
            {"required_return": 0.601806640625, "annualization": 4},
            np.nan,
            id="annual-threshold-ties",
        ),
        pytest.param(
            [0.01, 0.01], {"risk_free": 0.01}, np.nan, id="risk-free-threshold-ties"
        ),
        pytest.param(
            [0.01, 0.02], {"required_return": -1.0}, np.nan, id="invalid-annual-rate"
        ),
        pytest.param([-0.01, -0.02], {}, 0.0, id="losses-only"),
        pytest.param([-0.01, 0.02], {}, 2.0, id="finite-mixed-ratio"),
        pytest.param([np.nan, -0.02, 0.01], {}, 0.5, id="missing-and-mixed"),
        pytest.param(
            [0.0, 0.25],
            {"required_return": 0.601806640625, "annualization": 4},
            1.0,
            id="annual-threshold-mixed-ratio",
        ),
        pytest.param(
            [np.inf, 0.01], {}, np.nan, id="infinite-input-is-not-finite-upside"
        ),
        pytest.param([-np.inf, 0.01], {}, 0.0, id="infinite-downside-unchanged"),
    ],
)
def test_omega_retains_other_threshold_and_missingness_results(
    values, kwargs, expected, as_series
):
    returns = (
        pd.Series(values, dtype=float) if as_series else np.array(values, dtype=float)
    )

    np.testing.assert_allclose(empyrical.omega_ratio(returns, **kwargs), expected)
