from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["lap_number", "time_s", "distance_m", "speed_kmh"]
FLOAT_COLUMNS = ["time_s", "distance_m", "speed_kmh"]

class InvalidLapDataError(ValueError):
    """Données de tours invalides ou inexploitables."""

def load_laps(path: str | Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise InvalidLapDataError("Le fichier CSV est vide.") from exc
    if df.empty:
        raise InvalidLapDataError("Le fichier CSV est vide.")
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise InvalidLapDataError(
            f"Colonnes manquantes dans le fichier CSV : {', '.join(missing_columns)}"
        )
    return _validate_numeric(df)

def _file_lines(mask: pd.Series) -> str:
    return ", ".join(str(i + 2) for i in mask[mask].index)

def _validate_numeric(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in REQUIRED_COLUMNS:
        empty = df[col].isna()
        if empty.any():
            raise InvalidLapDataError(
                f"Valeur manquante dans '{col}', ligne(s) {_file_lines(empty)}."
            )
        converted = pd.to_numeric(df[col], errors="coerce")
        not_numeric = converted.isna() & ~empty
        if not_numeric.any():
            raise InvalidLapDataError(
                f"Valeur non numérique dans '{col}', ligne(s) {_file_lines(not_numeric)}."
            )
        df[col] = converted
    df[FLOAT_COLUMNS] = df[FLOAT_COLUMNS].astype(float)
    return df