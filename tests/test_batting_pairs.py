import numpy as np
import pandas as pd
import pytest
import empyrical


@pytest.mark.parametrize("kind", ["array", "series", "mixed"])
def test_all_missing_pairs_remain_undefined(kind):
    returns = np.array([np.nan, np.nan])
    factor = np.array([0.01, -0.01])
    if kind in ["series", "mixed"]:
        returns = pd.Series(returns)
    if kind == "series":
        factor = pd.Series(factor)
    assert np.isnan(empyrical.batting_average(returns, factor).to_numpy()).all()


def test_mixed_series_and_array_excludes_missing_pairs():
    result = empyrical.batting_average(
        pd.Series([0.02, np.nan, 0.01]), np.array([0.01, -0.02, -0.01])
    )
    np.testing.assert_equal(result.to_numpy(), [1.0, 1.0, 1.0])


def test_nonfinite_returns_from_price_pipeline_do_not_count_as_wins():
    returns = empyrical.simple_returns(np.array([1.0, 1.0, 0.0, 1.0, 1.0]))
    assert np.isinf(returns[2])
    result = empyrical.batting_average(returns, np.array([0.01, -1.0, 0.01, -0.01]))
    np.testing.assert_allclose(result.to_numpy(), [1.0 / 3.0, 0.0, 0.5])
