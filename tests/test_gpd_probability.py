import numpy as np
import pandas as pd

import empyrical


def test_gpd_risk_estimates_accepts_scalar_tail_probability():
    """The public wrapper must forward var_p, not try to align it as a series."""
    returns = pd.Series(
        [0.01, -0.02, 0.03, -0.04, 0.02, -0.01, -0.03, 0.015, 0.005, -0.025]
    )
    result = empyrical.gpd_risk_estimates(returns, var_p=0.01)
    expected = empyrical.gpd_risk_estimates_aligned(returns, var_p=0.01)
    np.testing.assert_almost_equal(np.asarray(result), np.asarray(expected))
    assert len(result) == 5
