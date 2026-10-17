import numpy as np
import pandas as pd
import pytest

import empyrical


def test_value_at_risk_empty_input_is_nan():
    assert np.isnan(empyrical.value_at_risk(np.array([])))
    assert np.isnan(empyrical.value_at_risk(pd.Series([], dtype=float)))


@pytest.mark.parametrize(
    "returns, expected",
    [(0.01, 0.01), (np.float64(0.01), 0.01), (np.array(0.01), 0.01), (np.int64(2), 2)],
)
def test_value_at_risk_empty_guard_preserves_scalar_percentiles(returns, expected):
    assert empyrical.value_at_risk(returns) == expected
