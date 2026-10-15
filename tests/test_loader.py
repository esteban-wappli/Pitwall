from pathlib import Path

import pytest

from pitwall.ingestion.loader import InvalidLapDataError, load_laps

SAMPLE = Path(__file__).parent.parent / "data" / "samples" / "tiny.csv"


def test_load_tiny_sample():
    df = load_laps(SAMPLE)

    assert len(df) == 10
    assert df.groupby("lap_number")["time_s"].max().to_dict() == {1: 40, 2: 38}


def test_zero_byte_file_raises(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")

    with pytest.raises(InvalidLapDataError) as excinfo:
        load_laps(path)
    assert excinfo.value.__cause__ is not None


def test_header_only_file_raises(tmp_path):
    path = tmp_path / "header.csv"
    path.write_text("lap_number,time_s,distance_m,speed_kmh\n")

    with pytest.raises(InvalidLapDataError):
        load_laps(path)


def test_missing_column_raises(tmp_path):
    path = tmp_path / "missing.csv"
    path.write_text("lap_number,time_s,distance_m\n1,0,0\n")

    with pytest.raises(InvalidLapDataError, match="speed_kmh"):
        load_laps(path)
