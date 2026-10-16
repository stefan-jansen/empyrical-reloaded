import numpy as np
import pandas as pd
import pytest

import empyrical


@pytest.mark.parametrize("multi_index", [False, True])
def test_alpha_aligned_preserves_dataframe_column_labels(multi_index):
    columns = pd.Index(["strategy-a", "strategy-b"], name="strategy")
    if multi_index:
        columns = pd.MultiIndex.from_tuples(
            [("long", "a"), ("short", "b")], names=["side", "strategy"]
        )
    returns = pd.DataFrame(
        [[0.01, -0.01], [-0.02, 0.02], [0.03, -0.01], [0.01, 0.02]],
        columns=columns,
    )
    factors = pd.DataFrame(
        [[0.02, 0.02], [-0.01, -0.01], [0.01, 0.01], [0.03, 0.03]],
        columns=columns,
    )
    result = empyrical.alpha_aligned(returns, factors)
    pd.testing.assert_index_equal(result.index, columns)
    for column in columns:
        np.testing.assert_allclose(
            result[column], empyrical.alpha_aligned(returns[column], factors[column])
        )
    buffer = np.empty(2)
    buffered = empyrical.alpha_aligned(returns, factors, out=buffer)
    assert buffered is buffer
    np.testing.assert_allclose(buffered, result.to_numpy())
