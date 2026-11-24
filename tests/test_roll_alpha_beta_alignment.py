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


@pytest.mark.parametrize("metric", ["alpha", "beta"])
def test_roll_alpha_beta_preserve_documented_lhs_rhs_keywords(metric):
    method = getattr(empyrical, "roll_" + metric)
    result = method(
        lhs=np.array([0.02, -0.04, 0.06]),
        rhs=np.array([0.01, -0.02, 0.03]),
        window=2,
    )
    np.testing.assert_allclose(result, 0.0 if metric == "alpha" else 2.0, atol=1e-12)


@pytest.mark.parametrize("metric", ["alpha", "beta"])
@pytest.mark.parametrize(
    "left_index,left_values,right_index,right_values,expected_index,valid",
    [
        (
            [0, 1, 2, 3],
            [0.123, 0.021, -0.039, 0.061],
            [1, 2, 3, 4],
            [0.01, -0.02, 0.03, 0.11],
            [1, 2, 3, 4],
            [False, True, True, False],
        ),
        (
            [3, 1, 2],
            [0.061, 0.021, -0.039],
            [0, 1, 2, 3, 4],
            [0.2, 0.01, -0.02, 0.03, 0.11],
            [1, 2, 0, 4],
            [True, True, False, False],
        ),
        ([0, 1], [0.021, -0.039], [3, 4], [0.03, 0.11], [1, 3, 4], [False] * 3),
        (
            [0, 0, 1, 2],
            [0.021, -0.039, 0.061, 0.081],
            [0, 0, 1, 2],
            [0.01, -0.02, 0.03, 0.04],
            [0, 1, 2],
            [True] * 3,
        ),
    ],
    ids=[
        "shifted-labels",
        "unequal-reordered-labels",
        "disjoint-labels",
        "identical-duplicates",
    ],
)
def test_rolling_pairs_labels_before_windows_not_positions(
    metric, left_index, left_values, right_index, right_values, expected_index, valid
):
    returns = pd.Series(left_values, index=left_index, name="strategy")
    benchmark = pd.Series(right_values, index=right_index, name="benchmark")
    result = getattr(empyrical, "roll_" + metric)(
        returns,
        benchmark,
        window=2,
        **({"annualization": 12} if metric == "alpha" else {}),
    )
    expected_value = (1.001**12) - 1 if metric == "alpha" else 2.0
    expected = pd.Series(
        [expected_value if item else np.nan for item in valid], index=expected_index
    )
    pd.testing.assert_series_equal(result, expected, atol=1e-12, rtol=1e-10)


@pytest.mark.parametrize(
    "api", ["roll_alpha", "roll_beta", "roll_alpha_beta", "alpha", "beta", "alpha_beta"]
)
def test_ambiguous_duplicate_labels_rejected_instead_of_silent_pairing(api):
    a = pd.Series([0.02, -0.04, 0.06], index=[1, 1, 2])
    b = pd.Series([0.01, 0.03, -0.02], index=[1, 2, 2])
    with pytest.raises(ValueError, match="duplicate"):
        getattr(empyrical, api)(
            a, b, **({"window": 2} if api.startswith("roll") else {})
        )


@pytest.mark.parametrize("window", [1, 2, 3, 9])
@pytest.mark.parametrize("metric", ["alpha", "beta"])
def test_windows_count_missing_rows_but_regression_needs_two_valid_pairs(
    window, metric
):
    dates = pd.date_range("2024-01-01", periods=4, tz="UTC")
    benchmark = pd.Series([0.01, -0.02, 0.03, 0.04], index=dates)
    returns = (2 * benchmark + 0.001).drop(dates[1])
    result = getattr(empyrical, "roll_" + metric)(
        returns,
        benchmark,
        window=window,
        **({"annualization": 12} if metric == "alpha" else {}),
    )
    effective = min(4, window)
    valid_pairs = [True, False, True, True]
    valid = [
        sum(valid_pairs[i - effective + 1 : i + 1]) >= 2
        for i in range(effective - 1, 4)
    ]
    expected_value = 1.001**12 - 1 if metric == "alpha" else 2.0
    expected = pd.Series(
        [expected_value if item else np.nan for item in valid],
        index=dates[effective - 1 :],
    )
    pd.testing.assert_series_equal(
        result, expected, check_freq=False, atol=1e-12, rtol=1e-10
    )


@pytest.mark.parametrize("metric", ["alpha", "beta"])
def test_actual_pct_change_missing_returns_keep_window_positions(metric):
    dates = pd.date_range("2024-02-01", periods=7)
    prices = pd.Series([100, 102, np.nan, 107, 104, 110, 115], index=dates)
    factor = prices.pct_change(fill_method=None)
    strategy = 2 * factor + 0.001
    result = getattr(empyrical, "roll_" + metric)(
        strategy,
        factor,
        window=3,
        **({"annualization": 12} if metric == "alpha" else {}),
    )
    expected_value = 1.001**12 - 1 if metric == "alpha" else 2.0
    expected = pd.Series(
        [np.nan, np.nan, np.nan, expected_value, expected_value], index=dates[2:]
    )
    pd.testing.assert_series_equal(result, expected, atol=1e-12, rtol=1e-10)
    scalar = getattr(empyrical, metric)(
        strategy, factor, **({"annualization": 12} if metric == "alpha" else {})
    )
    assert scalar == pytest.approx(expected_value, abs=1e-12)


@pytest.mark.parametrize("metric", ["alpha", "beta"])
@pytest.mark.parametrize("missing", [True, False])
def test_all_missing_and_constant_factor_have_no_identifiable_slope(metric, missing):
    factor = pd.Series([np.nan] * 4 if missing else [0.01] * 4)
    result = getattr(empyrical, "roll_" + metric)(
        pd.Series([0.01, 0.02, 0.03, 0.04]), factor, window=3
    )
    assert len(result) == 2
    assert result.isna().all()


@pytest.mark.parametrize("metric", ["alpha", "beta"])
def test_empty_inputs_return_empty_series_and_no_min_periods_option(metric):
    method = getattr(empyrical, "roll_" + metric)
    result = method(pd.Series([], dtype=float), pd.Series([], dtype=float), window=3)
    assert isinstance(result, pd.Series) and result.empty
    with pytest.raises(TypeError, match="min_periods"):
        method(
            pd.Series([0.02, -0.04]), pd.Series([0.01, -0.02]), window=2, min_periods=2
        )


@pytest.mark.parametrize("metric", ["alpha", "beta"])
def test_ndarray_and_series_buffers_match_independent_regression(metric):
    x = np.array([0.01, -0.02, 0.03, -0.01, 0.02])
    y = np.array([0.02, -0.05, 0.01, 0.03, 0.06])
    risk_free = 0.001
    expected = []
    for start in range(3):
        design = np.column_stack((np.ones(3), x[start : start + 3] - risk_free))
        intercept, slope = np.linalg.lstsq(
            design, y[start : start + 3] - risk_free, rcond=None
        )[0]
        expected.append((1 + intercept) ** 12 - 1 if metric == "alpha" else slope)
    kwargs = {"risk_free": risk_free}
    if metric == "alpha":
        kwargs.update(period=empyrical.DAILY, annualization=12)
    for as_series in (False, True):
        a = pd.Series(y) if as_series else y
        b = pd.Series(x) if as_series else x
        buf = np.zeros(3)
        got = getattr(empyrical, "roll_" + metric)(a, b, 3, buf, **kwargs)
        assert got is buf
        np.testing.assert_allclose(got, expected, atol=1e-12)
        np.testing.assert_array_equal(np.asarray(a), y)
        np.testing.assert_array_equal(np.asarray(b), x)
    for column, scalar_api in enumerate(("alpha", "beta")):
        actual = getattr(empyrical, scalar_api)(
            pd.Series(y),
            pd.Series(x),
            **(
                {"risk_free": risk_free, "annualization": 12}
                if column == 0
                else {"risk_free": risk_free}
            ),
        )
        intercept, slope = np.linalg.lstsq(
            np.column_stack((np.ones(5), x - risk_free)), y - risk_free, rcond=None
        )[0]
        assert actual == pytest.approx(
            (1 + intercept) ** 12 - 1 if column == 0 else slope
        )


@pytest.mark.parametrize("metric", ["alpha", "beta"])
def test_datetime_alignment_returns_union_window_end_labels(metric):
    dates = pd.date_range("2024-01-01", periods=5)
    factor = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02], index=dates)
    strategy = (2 * factor + 0.001).iloc[[2, 0, 4, 1, 3]]
    result = getattr(empyrical, "roll_" + metric)(
        strategy,
        factor,
        window=3,
        **({"annualization": 12} if metric == "alpha" else {}),
    )
    pd.testing.assert_index_equal(result.index, dates[2:])
    expected = 1.001**12 - 1 if metric == "alpha" else 2.0
    np.testing.assert_allclose(result, expected, rtol=1e-10, atol=1e-12)


@pytest.mark.parametrize("metric", ["alpha", "beta"])
def test_unique_to_duplicate_alignment_preserves_supported_pandas_behavior(metric):
    returns = pd.Series([0.021, 0.021, 0.061], index=[1, 1, 2])
    factor = pd.Series([0.01, 0.03], index=[1, 2])
    kwargs = {"annualization": 12} if metric == "alpha" else {}
    scalar = getattr(empyrical, metric)
    rolling = getattr(empyrical, "roll_" + metric)
    try:
        total = scalar(returns, factor, **kwargs)
    except ValueError:
        with pytest.raises(ValueError, match="duplicate"):
            rolling(returns, factor, window=2, **kwargs)
    else:
        expected = 1.001**12 - 1 if metric == "alpha" else 2.0
        assert total == pytest.approx(expected, abs=1e-12)
        result = rolling(returns, factor, window=2, **kwargs)
        pd.testing.assert_series_equal(
            result,
            pd.Series([np.nan, expected], index=[1, 2]),
            atol=1e-12,
            rtol=1e-10,
        )
