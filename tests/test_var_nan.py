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
    # These returns are distinct, so the VaR threshold selects the CVaR tail.
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


@pytest.mark.parametrize("as_series", [False, True], ids=["array", "series"])
def test_value_at_risk_preserves_clean_float32_percentile(as_series):
    values = np.array([-0.3, 0.1, 0.2], dtype=np.float32)
    returns = pd.Series(values) if as_series else values
    expected = np.percentile(values, 5)

    actual = empyrical.value_at_risk(returns)

    assert actual.dtype == expected.dtype
    assert actual == expected


def test_value_at_risk_preserves_extended_precision_at_cutoff_one():
    upper = np.nextafter(np.longdouble(1), np.longdouble(2))
    returns = np.array([1, upper], dtype=np.longdouble)

    assert empyrical.value_at_risk(returns, cutoff=1) == upper


@pytest.mark.parametrize("cutoff", [-0.01, 1.01])
def test_value_at_risk_validates_cutoff_for_nonempty_all_nan_sample(cutoff):
    with pytest.raises(ValueError, match="Percentiles must be in the range"):
        empyrical.value_at_risk(np.array([np.nan]), cutoff)


def test_value_at_risk_omits_nullable_pct_change_missing_value():
    returns = pd.Series([128, 112, 140], dtype="Float64").pct_change()

    assert pd.isna(returns.iloc[0])
    assert empyrical.value_at_risk(returns, cutoff=0.25) == -0.03125


def test_value_at_risk_preserves_nullable_float32_pct_change_precision():
    returns = pd.Series([100, 70, 77, 92], dtype="Float32").pct_change()
    assert pd.isna(returns.iloc[0])
    expected = np.percentile(np.asarray(returns.iloc[1:]), 5)

    actual = empyrical.value_at_risk(returns)

    assert actual.dtype == expected.dtype
    assert actual == expected


def test_value_at_risk_omits_nan_from_numeric_object_storage():
    returns = np.array([-0.25, np.nan, 0.25], dtype=object)

    assert empyrical.value_at_risk(returns, cutoff=0.25) == -0.125


def test_value_at_risk_does_not_treat_infinity_as_missing():
    returns = np.array([-0.125, np.nan, np.inf])

    assert np.isposinf(empyrical.value_at_risk(returns, cutoff=0.25))


def test_cvar_keeps_rank_based_tail_when_var_cutoff_ties():
    returns = np.array([-0.3, -0.2, np.nan, -0.2, 0.1])

    assert empyrical.value_at_risk(returns, cutoff=0.5) == -0.2
    assert empyrical.conditional_value_at_risk(returns, cutoff=0.5) == -0.25
