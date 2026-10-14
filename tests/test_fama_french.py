import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from empyrical import utils


@pytest.mark.parametrize("period_index", [True, False])
def test_fama_french_daily_provider_dates_remain_utc(period_index, monkeypatch):
    record = json.loads(
        (
            Path(__file__).parent / "test_data/famafrench-provider-response.json"
        ).read_text()
    )

    def read_factors(dataset, data_source, start, end):
        assert data_source == "famafrench"
        assert str(start) == "2024-01-02"
        assert str(end) == "2024-01-05"
        frame = record["records"][dataset]
        index = pd.PeriodIndex(frame["index"], freq="D", name="Date")
        if not period_index:
            index = index.to_timestamp()
        return {0: pd.DataFrame(frame["data"], index=index, columns=frame["columns"])}

    monkeypatch.setattr(utils, "web", SimpleNamespace(DataReader=read_factors))
    result = utils.get_fama_french(start="2024-01-02", end="2024-01-05")
    expected = pd.DataFrame(
        [
            [-0.007, -0.0055, 0.0079, 0.0002, -0.0211],
            [-0.0101, -0.0194, -0.001, 0.0002, 0.0059],
            [-0.0033, 0.0021, 0.0009, 0.0002, -0.003],
            [0.0015, -0.0081, 0.0063, 0.0002, -0.0025],
        ],
        columns=["Mkt-RF", "SMB", "HML", "RF", "Mom"],
        index=pd.date_range("2024-01-02", periods=4, tz="UTC", name="Date"),
    )
    pd.testing.assert_frame_equal(result, expected)
