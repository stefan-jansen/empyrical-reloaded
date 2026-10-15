import numpy as np
import pandas as pd
import pytest

import empyrical


@pytest.mark.parametrize("labelled", [False, True])
def test_gpd_risk_estimates_forwards_nondefault_scalar_tail_probability(labelled):
    returns = np.array(
        [0.01, -0.02, 0.03, -0.04, 0.02, -0.01, -0.03, 0.015, 0.005, -0.025]
    )
    if labelled:
        returns = pd.Series(returns)
    rare_tail = np.asarray(empyrical.gpd_risk_estimates(returns, var_p=0.01))
    common_tail = np.asarray(empyrical.gpd_risk_estimates(returns, var_p=0.05))
    assert rare_tail.shape == common_tail.shape == (5,)
    assert np.isfinite(rare_tail).all() and np.isfinite(common_tail).all()
    assert rare_tail[3] > common_tail[3]
    assert rare_tail[4] > common_tail[4]
