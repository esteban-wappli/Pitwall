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


HEADER = "lap_number,time_s,distance_m,speed_kmh\n"


def test_integer_columns_become_float(tmp_path):
    path = tmp_path / "ints.csv"
    path.write_text(HEADER + "1,0,0,100\n1,10,500,200\n")

    df = load_laps(path)

    for col in ["time_s", "distance_m", "speed_kmh"]:
        assert df[col].dtype == float


def test_empty_cell_raises_with_line(tmp_path):
    path = tmp_path / "empty_cell.csv"
    path.write_text(HEADER + "1,0,0,100\n1,10,500,\n")

    with pytest.raises(InvalidLapDataError, match=r"manquante.*speed_kmh.*ligne\(s\) 3\b"):
        load_laps(path)


def test_text_value_raises_with_line(tmp_path):
    path = tmp_path / "text.csv"
    path.write_text(HEADER + "1,0,0,100\n1,10,500,200\n1,20,900,rapide\n")

    with pytest.raises(InvalidLapDataError, match=r"non numérique.*speed_kmh.*ligne\(s\) 4\b"):
        load_laps(path)
