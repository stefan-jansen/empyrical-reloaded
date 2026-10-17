import numpy as np
import pytest

import empyrical


@pytest.mark.parametrize("two_dimensional", [False, True])
@pytest.mark.parametrize("provided_buffer", [False, True])
def test_drawdown_series_omits_anchor_with_ndarrays_and_output_buffers(
    two_dimensional, provided_buffer
):
    values = np.array([0.10, -0.20, 0.05])
    expected = np.array([0.0, -0.20, -0.16])
    if two_dimensional:
        values = np.column_stack([values, values * 0.5])
        expected = np.column_stack([expected, [0.0, -0.10, -0.0775]])
    buffer = np.empty((len(values) + 1,) + values.shape[1:])
    result = empyrical.stats.drawdown_series(
        values, out=buffer if provided_buffer else None
    )
    assert result.shape == values.shape
    np.testing.assert_allclose(result, expected, atol=1e-15)
    if provided_buffer:
        assert np.shares_memory(result, buffer)
        np.testing.assert_allclose(buffer[0], 0.0)
        np.testing.assert_allclose(buffer[1:], expected, atol=1e-15)
