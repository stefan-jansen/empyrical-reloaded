import numpy as np
import pandas as pd
import pytest

import empyrical


@pytest.mark.parametrize(
    "dates, expected_keys, expected_returns",
    [
        (
            ["2019-12-30", "2019-12-31", "2020-01-02", "2020-01-03"],
            [(2020, 1)],
            [(1.01**4) - 1],
        ),
        (
            ["2020-12-30", "2020-12-31", "2021-01-01", "2021-01-04"],
            [(2020, 53), (2021, 1)],
            [(1.01**3) - 1, 0.01],
        ),
    ],
)
def test_aggregate_returns_keeps_both_iso_year_boundaries(
    dates, expected_keys, expected_returns
):
    returns = pd.Series(0.01, index=pd.to_datetime(dates))
    aggregated = empyrical.aggregate_returns(returns, empyrical.WEEKLY)
    assert aggregated.index.tolist() == expected_keys
    np.testing.assert_allclose(aggregated.to_numpy(), expected_returns)
