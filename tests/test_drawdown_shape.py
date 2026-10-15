import numpy as np
import pandas as pd

import empyrical


def test_drawdown_series_ndarray_has_one_value_per_return():
    values = np.array([0.10, -0.20, 0.05])
    as_array = empyrical.stats.drawdown_series(values)
    as_series = empyrical.stats.drawdown_series(pd.Series(values))
    assert len(as_array) == len(values)
    np.testing.assert_almost_equal(as_array, as_series.to_numpy(), 8)
    np.testing.assert_almost_equal(
        empyrical.max_drawdown(values),
        empyrical.max_drawdown(pd.Series(values)),
        8,
    )
