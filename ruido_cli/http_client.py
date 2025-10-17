import os
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv


class HttpClient:
    def __init__(self, base_url: str, timeout_seconds: int, token_env: Optional[str], auth_scheme: str = "x-token", header_name: str = "x-token"):
        load_dotenv()
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.token_env = token_env
        self.auth_scheme = auth_scheme
        self.header_name = header_name
        self.session = requests.Session()
        retry = Retry(total=5, backoff_factor=0.6, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        token = os.getenv(self.token_env or "", "").strip()
        if token:
            if self.auth_scheme.lower() == "x-token":
                headers[self.header_name or "x-token"] = token
            elif self.auth_scheme.lower() == "bearer":
                headers["Authorization"] = f"Bearer {token}"
        return headers

    def request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.base_url}{path}"
        response = self.session.request(method=method.upper(), url=url, headers=self._headers(), params=params, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response


