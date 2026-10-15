import numpy as np
import pandas as pd

import empyrical


def test_aggregate_returns_weekly_keeps_iso_week_across_new_year():
    # 2019-12-30 is a Monday. That ISO week is 2020-W01 and includes 2 Jan.
    index = pd.to_datetime(["2019-12-30", "2019-12-31", "2020-01-02", "2020-01-03"])
    returns = pd.Series([0.01, 0.01, 0.01, 0.01], index=index)
    aggregated = empyrical.aggregate_returns(returns, empyrical.WEEKLY)
    assert len(aggregated) == 1
    np.testing.assert_almost_equal(aggregated.iloc[0], (1.01**4) - 1, 8)
