import numpy as np
import pandas as pd
import pytest

import empyrical


@pytest.mark.parametrize("as_array", [False, True], ids=["dataframe", "ndarray"])
@pytest.mark.parametrize(
    "function",
    [empyrical.up_capture, empyrical.down_capture, empyrical.up_down_capture],
    ids=["up", "down", "up_down"],
)
def test_capture_preserves_identical_multiple_strategy_columns(function, as_array):
    prices = pd.DataFrame(
        {
            "first": [100.0, 110.0, 100.0, 120.0, 105.0],
            "second": [100.0, 110.0, 100.0, 120.0, 105.0],
        },
        index=pd.date_range("2024-01-02", periods=5, freq="B"),
    )
    returns = empyrical.simple_returns(prices)
    benchmark = empyrical.simple_returns(prices["first"])
    if as_array:
        result = function(returns.to_numpy(), benchmark.to_numpy())
        assert isinstance(result, np.ndarray)
        np.testing.assert_allclose(result, np.ones(2))
    else:
        result = function(returns, benchmark)
        assert isinstance(result, pd.Series)
        pd.testing.assert_index_equal(result.index, returns.columns)
        np.testing.assert_allclose(result.to_numpy(), np.ones(2))
