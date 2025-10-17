from typing import Any, Dict, List, Optional

import yaml

from http_client import HttpClient
from utils import normalize_to_rows, to_csv, validate_date_range, split_date_range, flatten_noise_payload


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class Endpoint:
    def __init__(self, spec: Dict[str, Any]):
        self.name: str = spec.get("name")
        self.path: str = spec.get("path")
        self.method: str = spec.get("method", "GET")
        self.requires_params: bool = bool(spec.get("requires_params", False))
        self.params_spec: List[Dict[str, Any]] = spec.get("params", []) or []
        self.csv_spec: Dict[str, Any] = spec.get("csv", {}) or {}


class App:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        api_cfg = self.config.get("api", {})
        auth_cfg = self.config.get("auth", {})
        self.client = HttpClient(
            base_url=api_cfg.get("base_url", ""),
            timeout_seconds=int(api_cfg.get("timeout_seconds", 30)),
            token_env=auth_cfg.get("token_env"),
            auth_scheme=str(auth_cfg.get("scheme", "x-token")),
            header_name=str(auth_cfg.get("header_name", "x-token")),
        )
        self.endpoints: List[Endpoint] = [Endpoint(e) for e in self.config.get("endpoints", [])]

    def list_endpoints(self) -> List[Endpoint]:
        return self.endpoints

    def get_endpoint(self, name: str) -> Optional[Endpoint]:
        for e in self.endpoints:
            if e.name == name:
                return e
        return None

    def _format_path(self, ep: Endpoint, params: Optional[Dict[str, Any]]) -> str:
        path = ep.path
        if params:
            for key, value in list(params.items()):
                placeholder = "{" + key + "}"
                if placeholder in path:
                    path = path.replace(placeholder, str(value))
                    params.pop(key, None)
        return path

    def call_endpoint(self, name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ep = self.get_endpoint(name)
        if not ep:
            raise ValueError(f"Endpoint not found: {name}")
        params = dict(params or {})
        path = self._format_path(ep, params)
        response = self.client.request(ep.method, path, params=params or None)
        return response.json()

    def call_and_maybe_export(self, name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = dict(params or {})
        ep = self.get_endpoint(name)
        if ep and ep.requires_params:
            keys = {p.get("name"): p for p in ep.params_spec}
            if "start_date" in keys and "end_date" in keys and "start_date" in params and "end_date" in params:
                validate_date_range(params["start_date"], params["end_date"])
            if "station" in keys and "station" in params:
                raw_station = str(params["station"]).strip()
                if "|" in raw_station:
                    raw_station = raw_station.split("|")[-1].strip()
                params["station"] = raw_station
                stations_data = self.call_endpoint("stations")
                rows = normalize_to_rows(stations_data)
                known_ids = set()
                for r in rows:
                    for key in ("id", "station", "code", "name"):
                        if key in r:
                            known_ids.add(str(r[key]).strip().lower())
                candidate = raw_station.strip().lower()
                # Si no se encuentra, continuamos igualmente y dejamos que el API responda
                if not known_ids or candidate in known_ids:
                    pass
        # Para endpoints con fechas, dividir en chunks para minimizar timeouts
        if ep and ep.requires_params and {"start_date", "end_date"}.issubset(set(params.keys())):
            merged_rows: List[Dict[str, Any]] = []
            for s, e in split_date_range(params["start_date"], params["end_date"]):
                part_params = dict(params)
                part_params["start_date"] = s
                part_params["end_date"] = e
                part_data = self.call_endpoint(name, params=part_params)
                merged_rows.extend(normalize_to_rows(part_data))
            data = merged_rows
        else:
            data = self.call_endpoint(name, params=params)
        if ep and ep.csv_spec and ep.csv_spec.get("enabled"):
            rows = normalize_to_rows(data)
            csv_path = ep.csv_spec.get("file", f"data/{name}.csv")
            to_csv(rows, csv_path)
            flat_rows = flatten_noise_payload(data)
            if flat_rows:
                flat_path = csv_path.replace(".csv", "_flat.csv")
                to_csv(flat_rows, flat_path)
        return data


