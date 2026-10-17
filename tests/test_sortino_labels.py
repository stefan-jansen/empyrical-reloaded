import numpy as np
import pandas as pd

import empyrical


def test_sortino_ratio_dataframe_keeps_column_names():
    returns = pd.DataFrame(
        {
            "a": [0.01, -0.02, 0.015, 0.01],
            "b": [-0.01, 0.02, -0.03, 0.005],
        }
    )
    result = empyrical.sortino_ratio(returns)
    pd.testing.assert_index_equal(result.index, returns.columns)
    np.testing.assert_almost_equal(
        result["a"], empyrical.sortino_ratio(returns["a"]), 8
    )
    np.testing.assert_almost_equal(
        result["b"], empyrical.sortino_ratio(returns["b"]), 8
    )
