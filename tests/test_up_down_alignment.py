import numpy as np
import pandas as pd
import pytest

import empyrical


def test_up_and_down_capture_ignore_dropped_na_differences():
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    factor = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02, 0.04], index=idx)
    returns_with_nan = pd.Series([np.nan, 0.04, -0.02, 0.06, np.nan, 0.08], index=idx)
    returns_dropped = returns_with_nan.dropna()

    assert empyrical.up_capture(
        returns_dropped, factor, period=empyrical.YEARLY
    ) == pytest.approx(
        empyrical.up_capture(returns_with_nan, factor, period=empyrical.YEARLY)
    )
    assert empyrical.down_capture(
        returns_dropped, factor, period=empyrical.YEARLY
    ) == pytest.approx(
        empyrical.down_capture(returns_with_nan, factor, period=empyrical.YEARLY)
    )
    assert empyrical.up_down_capture(
        returns_dropped, factor, period=empyrical.YEARLY
    ) == pytest.approx(
        empyrical.up_down_capture(returns_with_nan, factor, period=empyrical.YEARLY)
    )


def test_up_and_down_alpha_beta_align_series():
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    factor = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02, 0.04], index=idx)
    returns_with_nan = pd.Series([np.nan, 0.04, -0.02, 0.06, -0.04, 0.08], index=idx)
    returns_dropped = returns_with_nan.dropna()

    np.testing.assert_allclose(
        empyrical.up_alpha_beta(returns_dropped, factor),
        empyrical.up_alpha_beta(returns_with_nan, factor),
    )

    reordered_factor = factor.iloc[[2, 0, 5, 1, 4, 3]]
    np.testing.assert_allclose(
        empyrical.up_alpha_beta(returns_with_nan, reordered_factor),
        empyrical.up_alpha_beta(returns_with_nan, factor),
    )
    np.testing.assert_allclose(
        empyrical.down_alpha_beta(returns_with_nan, reordered_factor),
        empyrical.down_alpha_beta(returns_with_nan, factor),
    )


def test_up_and_down_capture_align_dataframe_returns():
    idx1 = pd.date_range("2024-01-01", periods=5, freq="D")
    idx2 = pd.date_range("2024-01-02", periods=5, freq="D")
    factor = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02], index=idx2)
    returns = pd.DataFrame(
        {
            "a": [0.99, 0.02, -0.04, 0.06, -0.02],
            "b": [0.99, 0.01, -0.02, 0.03, -0.01],
        },
        index=idx1,
    )
    aligned_returns = returns.reindex(factor.index)
    pd.testing.assert_series_equal(
        empyrical.up_capture(returns, factor),
        empyrical.up_capture(aligned_returns, factor),
    )
    pd.testing.assert_series_equal(
        empyrical.down_capture(returns, factor),
        empyrical.down_capture(aligned_returns, factor),
    )
    pd.testing.assert_series_equal(
        empyrical.up_down_capture(returns, factor),
        empyrical.up_down_capture(aligned_returns, factor),
    )


def test_up_and_down_capture_preserve_duplicate_timestamps():
    dup_idx = pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02"])
    returns = pd.Series([0.02, 0.04, -0.02], index=dup_idx)
    factor = pd.Series([0.01, 0.02, -0.01], index=dup_idx)

    assert empyrical.up_capture(
        returns, factor, period=empyrical.YEARLY
    ) == pytest.approx(
        empyrical.up_capture(
            returns.to_numpy(), factor.to_numpy(), period=empyrical.YEARLY
        )
    )
    assert empyrical.down_capture(
        returns, factor, period=empyrical.YEARLY
    ) == pytest.approx(
        empyrical.down_capture(
            returns.to_numpy(), factor.to_numpy(), period=empyrical.YEARLY
        )
    )


def test_roll_capture_aligns_series():
    idx1 = pd.date_range("2024-01-01", periods=5, freq="D")
    idx2 = pd.date_range("2024-01-02", periods=5, freq="D")
    shared = pd.Series([0.01, -0.02, 0.03, -0.01], index=idx2[:4])
    factor = pd.concat([shared, pd.Series([0.02], index=idx2[4:])])
    returns = pd.concat([pd.Series([-0.5], index=idx1[:1]), 2.0 * shared])

    aligned_returns, aligned_factor = empyrical.utils._aligned_series(returns, factor)
    pd.testing.assert_series_equal(
        empyrical.roll_up_capture(returns, factor, window=3),
        empyrical.roll_up_capture(aligned_returns, aligned_factor, window=3),
    )
    pd.testing.assert_series_equal(
        empyrical.roll_down_capture(returns, factor, window=3),
        empyrical.roll_down_capture(aligned_returns, aligned_factor, window=3),
    )
    pd.testing.assert_series_equal(
        empyrical.roll_up_down_capture(returns, factor, window=3),
        empyrical.roll_up_down_capture(aligned_returns, aligned_factor, window=3),
    )


@pytest.mark.parametrize("direction", [empyrical.utils.up, empyrical.utils.down])
@pytest.mark.parametrize("option", ["predicate", "kwargs"])
def test_up_down_callbacks_receive_keywords_without_internal_helper_collisions(
    direction, option
):
    returns = np.array([0.02, -0.02])
    factor = np.array([0.01, -0.01])

    def callback(selected_returns, selected_factor, **options):
        return selected_returns, selected_factor, options

    actual_returns, actual_factor, options = direction(
        returns, factor, function=callback, **{option: "callback-option"}
    )
    selected = 0 if direction is empyrical.utils.up else 1
    np.testing.assert_array_equal(actual_returns, returns[[selected]])
    np.testing.assert_array_equal(actual_factor, factor[[selected]])
    assert options == {option: "callback-option"}
