import numpy as np
import pytest

from empyrical import gpd_risk_estimates
from empyrical.stats import gpd_es_calculator


@pytest.mark.parametrize("shape", [1.0, 1.5])
def test_gpd_expected_shortfall_cannot_be_zero_or_negative_for_infinite_mean(shape):
    # The positive GPD survival integral diverges for shape >= 1.
    assert np.isposinf(gpd_es_calculator(0.2, 0.1, 0.02, shape))


@pytest.mark.parametrize("shape, expected", [(0.0, 0.22), (0.5, 0.34)])
def test_gpd_expected_shortfall_retains_finite_conditional_tail_means(shape, expected):
    assert gpd_es_calculator(0.2, 0.1, 0.02, shape) == pytest.approx(expected)


def test_gpd_estimator_does_not_report_negative_expected_loss_for_heavy_tail():
    returns = -0.1 * np.random.default_rng(2026).pareto(0.5, 2048)
    threshold, scale, shape, value_at_risk, expected_shortfall = gpd_risk_estimates(
        returns
    )

    assert threshold > 0
    assert scale > 0
    assert shape > 1
    assert value_at_risk > 0
    assert np.isposinf(expected_shortfall)
