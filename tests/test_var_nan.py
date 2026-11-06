import numpy as np
import pandas as pd
import pytest

import empyrical

RETURNS = np.random.default_rng(5).normal(0.0004, 0.011, 1512)
PADDED = np.insert(
    RETURNS, np.random.default_rng(5).integers(0, RETURNS.size, 40), np.nan
)


@pytest.mark.parametrize("cutoff", [0.0, 0.01, 0.05, 0.2, 1.0])
def test_value_at_risk_ignores_nan(cutoff):
    expected = empyrical.value_at_risk(RETURNS, cutoff)
    assert empyrical.value_at_risk(PADDED, cutoff) == expected
    assert empyrical.value_at_risk(pd.Series(PADDED), cutoff) == expected


def test_value_at_risk_leading_nan_from_pct_change():
    prices = pd.Series(100 * np.cumprod(1 + RETURNS[:250]))
    returns = prices.pct_change()
    assert np.isnan(returns.iloc[0])
    expected = empyrical.value_at_risk(returns.iloc[1:])
    assert empyrical.value_at_risk(returns) == expected


@pytest.mark.parametrize("cutoff", [0.0, 0.05, 0.2, 1.0])
def test_value_at_risk_and_cvar_agree_on_nan(cutoff):
    # CVaR is the mean of the returns at or below VaR, with or without NaNs
    var = empyrical.value_at_risk(PADDED, cutoff)
    observed = PADDED[~np.isnan(PADDED)]
    np.testing.assert_almost_equal(
        empyrical.conditional_value_at_risk(PADDED, cutoff),
        observed[observed <= var].mean(),
    )


@pytest.mark.parametrize(
    "returns", [np.array([np.nan]), np.array([np.nan, np.nan]), pd.Series([np.nan])]
)
def test_value_at_risk_all_nan_is_nan(returns):
    assert np.isnan(empyrical.value_at_risk(returns))
