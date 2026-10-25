import numpy as np
import pandas as pd
import pytest

import empyrical


def ratio(values, method, out=None):
    if method == "sharpe":
        return empyrical.sharpe_ratio(values, out=out)
    return empyrical.excess_sharpe(values, np.zeros_like(values), out=out)


@pytest.mark.parametrize("method", ["sharpe", "excess"])
@pytest.mark.parametrize("length", [10, 252, 1000])
@pytest.mark.parametrize("value", [0.001, -0.001])
def test_exact_repeated_returns_preserve_signed_infinity(method, length, value):
    assert ratio(np.full(length, value), method) == np.copysign(np.inf, value)


@pytest.mark.parametrize("method", ["sharpe", "excess"])
@pytest.mark.parametrize(
    "sample", [[], [0.001], [np.nan, 0.001], [np.nan] * 3, [0.0] * 252]
)
def test_undefined_samples_do_not_become_infinite(method, sample):
    assert np.isnan(ratio(np.asarray(sample), method))


@pytest.mark.parametrize("method", ["sharpe", "excess"])
@pytest.mark.parametrize("direction", [np.inf, -np.inf])
def test_one_ulp_real_variation_is_not_erased(method, direction):
    values = np.full(252, 0.001)
    values[-1] = np.nextafter(values[-1], direction)
    assert np.isfinite(ratio(values, method))


@pytest.mark.parametrize("method", ["sharpe", "excess"])
def test_missing_and_constant_columns_preserve_varying_column_and_output(method):
    values = np.column_stack(
        [np.full(252, 0.001), np.full(252, -0.001), np.tile([-0.01, 0.03], 126)]
    )
    values[0, :2] = np.nan
    frame = pd.DataFrame(values, columns=["gain", "loss", "varying"])
    before = frame.copy(deep=True)
    out = np.empty(3)
    result = ratio(frame, method, out=out)
    assert result is out
    assert np.isposinf(out[0])
    assert np.isneginf(out[1])
    # 126 symmetric pairs around .01 have sum of squared deviations252*.02**2.
    expected = 0.01 / np.sqrt(252 * 0.02**2 / 251)
    if method == "sharpe":
        expected *= np.sqrt(252)
    assert out[2] == pytest.approx(expected, rel=1e-12)
    pd.testing.assert_frame_equal(frame, before)


def test_periodic_risk_free_adjustment_retains_negative_constant_sign():
    values = pd.Series(np.full(252, 0.001), name="strategy")
    assert np.isneginf(empyrical.sharpe_ratio(values, risk_free=0.002))


@pytest.mark.parametrize("method", ["sharpe", "excess"])
def test_infinite_input_is_not_misclassified_as_finite_constant(method):
    assert np.isnan(ratio(np.array([np.inf, np.inf]), method))
