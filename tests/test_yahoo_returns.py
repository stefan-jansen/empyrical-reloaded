import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from empyrical import utils


def test_yahoo_returns_request_adjusted_close_from_current_provider(monkeypatch):
    record = json.loads(
        (Path(__file__).parent / "test_data/yahoo-adjustment-provider.json").read_text()
    )

    def download(symbol, start, end, **kwargs):
        assert {"symbol": symbol, "start": start, "end": end} == record["request"]
        response = record["records"][
            "explicit" if kwargs.get("auto_adjust") is False else "default"
        ]
        return pd.DataFrame(
            response["data"],
            columns=pd.MultiIndex.from_tuples(
                [tuple(column) for column in response["columns"]],
                names=["Price", "Ticker"],
            ),
            index=pd.DatetimeIndex(response["index"], name="Date"),
        )

    monkeypatch.setattr(utils, "yf", SimpleNamespace(download=download))
    result = utils.get_symbol_returns_from_yahoo(
        "SPY", start="2024-01-02", end="2024-01-06"
    )
    assert result.columns.tolist() == ["SPY"]
    pd.testing.assert_index_equal(
        result.index,
        pd.date_range("2024-01-03", periods=3, tz="UTC", name="Date"),
        check_names=True,
    )
    np.testing.assert_allclose(
        result["SPY"].to_numpy(),
        [-0.008166490164911507, -0.0032212077747587145, 0.0013696300933097464],
        rtol=1e-12,
        atol=1e-15,
    )
