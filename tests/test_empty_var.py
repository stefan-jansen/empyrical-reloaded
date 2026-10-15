import numpy as np
import pandas as pd

import empyrical


def test_value_at_risk_empty_input_is_nan():
    assert np.isnan(empyrical.value_at_risk(np.array([])))
    assert np.isnan(empyrical.value_at_risk(pd.Series([], dtype=float)))
