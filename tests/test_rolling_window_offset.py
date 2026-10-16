import numpy as np
import pandas as pd

from empyrical import utils


def test_roll_keeps_multi_observation_windows_with_duplicate_dates():
    dates = pd.DatetimeIndex(
        ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"], name="date"
    )
    returns = pd.Series([0.1, 0.2, 0.3, 0.4], index=dates)
    result = utils.roll(returns, function=np.sum, window=2)
    np.testing.assert_allclose(result.to_numpy(), [0.3, 0.5, 0.7])
    pd.testing.assert_index_equal(result.index, dates[1:])
