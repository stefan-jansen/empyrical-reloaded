import numpy as np
import pandas as pd
import pytest

import empyrical


def test_roll_alpha_and_roll_beta_align_shifted_series():
    benchmark_dates = pd.date_range("2024-01-02", periods=4, freq="D")
    strategy_dates = pd.date_range("2024-01-01", periods=4, freq="D")
    shared_benchmark = pd.Series([0.01, -0.02, 0.03], index=benchmark_dates[:3])
    benchmark = pd.concat(
        [shared_benchmark, pd.Series([0.04], index=benchmark_dates[3:])]
    )
    strategy = pd.concat(
        [pd.Series([-0.05], index=strategy_dates[:1]), 2.0 * shared_benchmark]
    )

    expected = empyrical.roll_alpha_beta(strategy, benchmark, window=2)
    got_alpha = empyrical.roll_alpha(strategy, benchmark, window=2)
    got_beta = empyrical.roll_beta(strategy, benchmark, window=2)

    pd.testing.assert_series_equal(got_alpha, expected[0], check_names=False)
    pd.testing.assert_series_equal(got_beta, expected[1], check_names=False)
    np.testing.assert_allclose(got_alpha.iloc[1:3], [0.0, 0.0], atol=1e-12)
    np.testing.assert_allclose(got_beta.iloc[1:3], [2.0, 2.0], atol=1e-12)


def test_roll_alpha_and_roll_beta_align_reordered_series():
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    benchmark = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02], index=dates)
    strategy = (2.0 * benchmark + 0.001).iloc[[2, 0, 4, 1, 3]]

    expected = empyrical.roll_alpha_beta(strategy, benchmark, window=3)
    got_alpha = empyrical.roll_alpha(strategy, benchmark, window=3)
    got_beta = empyrical.roll_beta(strategy, benchmark, window=3)

    pd.testing.assert_series_equal(got_alpha, expected[0], check_names=False)
    pd.testing.assert_series_equal(got_beta, expected[1], check_names=False)
    np.testing.assert_allclose(got_beta.to_numpy(), np.full(3, 2.0), rtol=1e-12)


def test_roll_alpha_and_roll_beta_handle_unequal_length_series():
    dates_short = pd.date_range("2024-01-02", periods=3, freq="D")
    dates_long = pd.date_range("2024-01-01", periods=5, freq="D")
    benchmark = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02], index=dates_long)
    strategy = pd.Series([0.02, -0.01, 0.03], index=dates_short)

    expected = empyrical.roll_alpha_beta(strategy, benchmark, window=2)
    got_alpha = empyrical.roll_alpha(strategy, benchmark, window=2)
    got_beta = empyrical.roll_beta(strategy, benchmark, window=2)

    pd.testing.assert_series_equal(got_alpha, expected[0], check_names=False)
    pd.testing.assert_series_equal(got_beta, expected[1], check_names=False)


@pytest.mark.parametrize("positional_out", [False, True])
def test_roll_alpha_and_roll_beta_preserve_ndarray_and_output_buffer(positional_out):
    returns = np.array([0.01, 0.03, -0.02, 0.04, 0.01])
    benchmark = np.array([0.005, 0.015, -0.01, 0.02, 0.01])
    expected = empyrical.roll_alpha_beta(
        returns, benchmark, window=3, risk_free=0.001, period=empyrical.MONTHLY
    )

    alpha_buf = np.empty(3)
    beta_buf = np.empty(3)
    if positional_out:
        got_alpha = empyrical.roll_alpha(
            returns, benchmark, 3, alpha_buf, risk_free=0.001, period=empyrical.MONTHLY
        )
        got_beta = empyrical.roll_beta(returns, benchmark, 3, beta_buf, risk_free=0.001)
    else:
        got_alpha = empyrical.roll_alpha(
            returns,
            benchmark,
            window=3,
            out=alpha_buf,
            risk_free=0.001,
            period=empyrical.MONTHLY,
        )
        got_beta = empyrical.roll_beta(
            returns, benchmark, window=3, out=beta_buf, risk_free=0.001
        )

    assert got_alpha is alpha_buf
    assert got_beta is beta_buf
    np.testing.assert_allclose(got_alpha, expected[:, 0])
    np.testing.assert_allclose(got_beta, expected[:, 1])


def test_roll_alpha_and_roll_beta_default_window_matches_roll_alpha_beta():
    dates = pd.date_range("2024-01-01", periods=12, freq="D")
    benchmark = pd.Series(
        [0.01, -0.02, 0.015, 0.005, -0.01, 0.02, -0.005, 0.01, 0.02, -0.015, 0.01, 0.0],
        index=dates,
    )
    strategy = 1.5 * benchmark + 0.0005

    expected = empyrical.roll_alpha_beta(strategy, benchmark)
    pd.testing.assert_series_equal(
        empyrical.roll_alpha(strategy, benchmark), expected[0], check_names=False
    )
    pd.testing.assert_series_equal(
        empyrical.roll_beta(strategy, benchmark), expected[1], check_names=False
    )
