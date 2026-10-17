import numpy as np
import pandas as pd

import empyrical


def test_excess_sharpe_undefined_tracking_error_is_nan():
    # One finite active return is not enough for a sample standard deviation.
    returns = pd.Series([0.01, np.nan])
    factor_returns = pd.Series([0.0, np.nan])
    assert np.isnan(empyrical.excess_sharpe(returns, factor_returns))


def test_excess_sharpe_zero_tracking_error_with_nonzero_active_is_inf():
    returns = pd.Series([0.02, 0.02, 0.02])
    factor_returns = pd.Series([0.01, 0.01, 0.01])
    assert np.isinf(empyrical.excess_sharpe(returns, factor_returns))
