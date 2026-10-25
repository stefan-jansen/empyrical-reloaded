import numpy as np
import pandas as pd
import pytest

import empyrical


@pytest.mark.parametrize("n", [3, 21, 252])
@pytest.mark.parametrize("active", [0.001, -0.0001, 0.0003])
def test_constant_active_return_has_infinite_excess_sharpe(n, active):
    # A nonzero constant active return has zero tracking error at any length.
    returns = pd.Series([active] * n)
    benchmark = pd.Series([0.0] * n)
    result = empyrical.excess_sharpe(returns, benchmark)
    assert np.isinf(result) and np.sign(result) == np.sign(active)


@pytest.mark.parametrize("n", [3, 21, 252])
def test_constant_return_sharpe_is_infinite_for_any_length(n):
    assert np.isposinf(empyrical.sharpe_ratio(pd.Series([0.001] * n)))


def test_constant_columns_do_not_affect_varying_columns():
    returns = pd.DataFrame(
        {"flat": [0.001] * 252, "noisy": np.linspace(-0.01, 0.012, 252)}
    )
    result = empyrical.sharpe_ratio(returns)
    assert np.isposinf(result[0])
    assert result[1] == pytest.approx(empyrical.sharpe_ratio(returns["noisy"]))
