import numpy as np
import pandas as pd

import empyrical


def test_downside_risk_aligns_required_return_by_index():
    index = pd.to_datetime(["2020-01-02", "2020-01-01"])
    returns = pd.Series([0.05, -0.04], index=index)
    # Same dates as returns, stored in the opposite order, and not constant.
    required_return = pd.Series([0.01, 0.00], index=index[::-1])
    # 2020-01-01: -0.04 - 0.01 = -0.05; 2020-01-02: 0.05 - 0.00 = 0.05
    expected = np.sqrt(np.mean(np.square([-0.05, 0.0])))
    got = empyrical.downside_risk(
        returns, required_return=required_return, annualization=1
    )
    np.testing.assert_almost_equal(got, expected, 8)


def test_downside_risk_ndarray_accepts_series_thresholds():
    returns = np.array([[0.05, 0.01], [-0.04, -0.03]])
    thresholds = pd.Series([0.0, 0.02], index=["a", "b"])
    actual = empyrical.downside_risk(returns, thresholds, annualization=1)
    np.testing.assert_allclose(actual, [np.sqrt(0.0008), np.sqrt(0.0013)])


def test_downside_risk_omits_dates_without_a_required_return():
    dates = pd.date_range("2020-01-01", periods=3)
    returns = pd.Series([-0.03, 0.04, -0.02], index=dates)
    required_return = pd.Series([0.02, 0.04], index=dates[:2])
    result = empyrical.downside_risk(
        returns, required_return=required_return, annualization=1
    )
    np.testing.assert_allclose(result, np.sqrt(0.0025 / 2))
    control = empyrical.downside_risk(
        np.array([-0.03, 0.04, np.nan]),
        required_return=np.array([0.02, 0.04, np.nan]),
        annualization=1,
    )
    np.testing.assert_allclose(result, control)
