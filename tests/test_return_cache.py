import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from empyrical import utils


def test_yahoo_returns_cache_can_read_its_own_timezone_aware_csv(tmp_path, monkeypatch):
    record = json.loads(
        (Path(__file__).parent / "test_data/yahoo-adjustment-provider.json").read_text()
    )
    requests = []

    def download(symbol, start, end, **kwargs):
        assert {"symbol": symbol, "start": start, "end": end} == record["request"]
        assert kwargs["auto_adjust"] is False
        requests.append(symbol)
        response = record["records"]["explicit"]
        return pd.DataFrame(
            response["data"],
            columns=pd.MultiIndex.from_tuples(
                [tuple(column) for column in response["columns"]],
                names=["Price", "Ticker"],
            ),
            index=pd.DatetimeIndex(response["index"], name="Date"),
        )

    monkeypatch.setattr(utils, "yf", SimpleNamespace(download=download))
    monkeypatch.setenv("EMPYRICAL_CACHE_DIR", str(tmp_path))
    path = str(tmp_path / "spy.csv")
    latest = pd.Timestamp("2024-01-05", tz="UTC")

    fetched = utils.get_returns_cached(
        path, utils.get_symbol_returns_from_yahoo, latest, **record["request"]
    )
    restored = utils.get_returns_cached(
        path, utils.get_symbol_returns_from_yahoo, latest, **record["request"]
    )

    expected = pd.DataFrame(
        {
            "SPY": [
                -0.008166490164911507,
                -0.0032212077747587145,
                0.0013696300933097464,
            ]
        },
        index=pd.DatetimeIndex(
            ["2024-01-03", "2024-01-04", "2024-01-05"], tz="UTC", name="Date"
        ),
    )
    pd.testing.assert_frame_equal(fetched, expected)
    pd.testing.assert_frame_equal(restored, expected)
    assert requests == ["SPY"]


@pytest.mark.parametrize("timezone", [None, "UTC", "America/New_York"])
def test_returns_cache_normalizes_produced_timestamps_without_changing_instants(
    timezone, tmp_path, monkeypatch
):
    index = pd.date_range("2024-03-08", periods=5, tz=timezone, name="date")
    produced = pd.DataFrame({"returns": np.arange(5) * 0.01}, index=index)
    expected_index = (
        index.tz_localize("UTC") if timezone is None else index.tz_convert("UTC")
    )
    requests = []

    def update():
        requests.append(True)
        return produced

    monkeypatch.setenv("EMPYRICAL_CACHE_DIR", str(tmp_path))
    path = str(tmp_path / "returns.csv")
    latest = expected_index[-1]
    fetched = utils.get_returns_cached(path, update, latest)
    restored = utils.get_returns_cached(path, update, latest)

    pd.testing.assert_frame_equal(fetched, produced)
    expected = produced.copy()
    expected.index = expected_index
    pd.testing.assert_frame_equal(restored, expected, check_freq=False)
    assert requests == [True]
