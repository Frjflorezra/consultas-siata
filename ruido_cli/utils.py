from typing import Any, Dict, List, Tuple

from datetime import datetime
import pandas as pd


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_DAYS_RANGE = 62
CHUNK_DAYS = 14


def normalize_to_rows(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [item if isinstance(item, dict) else {"value": item} for item in data]
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            return [item if isinstance(item, dict) else {"value": item} for item in data["data"]]
        return [data]
    return [{"value": data}]


def to_csv(rows: List[Dict[str, Any]], csv_path: str) -> Tuple[str, int]:
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    return csv_path, len(df)


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, DATE_FORMAT)


def validate_date_range(start_date: str, end_date: str) -> None:
    start = parse_date(start_date)
    end = parse_date(end_date)
    if start >= end:
        raise ValueError("start_date debe ser menor que end_date")
    delta_days = (end - start).days
    if delta_days > MAX_DAYS_RANGE:
        raise ValueError("El rango máximo de consulta es de 2 meses (<= 62 días)")


def split_date_range(start_date: str, end_date: str) -> list[tuple[str, str]]:
    start = parse_date(start_date)
    end = parse_date(end_date)
    chunks: list[tuple[str, str]] = []
    cursor = start
    while cursor < end:
        nxt = min(cursor + pd.Timedelta(days=CHUNK_DAYS), end)
        chunks.append((cursor.strftime(DATE_FORMAT), nxt.strftime(DATE_FORMAT)))
        cursor = nxt
    return chunks


def flatten_noise_payload(data: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    # Caso 1: una estación {codigo_serial, nombre_corto, datos:{ts:{...}}}
    if isinstance(data, dict) and "datos" in data:
        station_code = str(data.get("nombre_corto") or data.get("station") or data.get("code") or data.get("id") or "")
        codigo_serial = data.get("codigo_serial")
        datos = data.get("datos") or {}
        if isinstance(datos, dict):
            for ts, vals in datos.items():
                if isinstance(vals, dict):
                    rows.append({
                        "station": station_code,
                        "datetime": ts,
                        "LRAeqH": vals.get("LRAeqH"),
                        "LAeqH": vals.get("LAeqH"),
                        "calidad": vals.get("calidad"),
                        "codigo_serial": codigo_serial,
                    })
        return rows

    # Caso 2: todas estaciones: dict station_code -> {codigo_serial, nombre_corto, datos:{...}}
    if isinstance(data, dict):
        for station_code, item in data.items():
            if isinstance(item, dict):
                sub = flatten_noise_payload({**item, "nombre_corto": item.get("nombre_corto") or station_code})
                rows.extend(sub)
        return rows

    # Caso 3: lista de objetos por estación
    if isinstance(data, list):
        for item in data:
            sub = flatten_noise_payload(item)
            rows.extend(sub)
    return rows


