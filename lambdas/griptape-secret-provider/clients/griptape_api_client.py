from __future__ import annotations
from typing import Optional
import requests
from attrs import Factory, define, field
from urllib.parse import urljoin


@define
class GriptapeApiClient:
    base_url: str = field(default="https://cloud.griptape.ai", kw_only=True)
    api_key: str = field(kw_only=True)
    headers: dict = field(
        default=Factory(
            lambda self: {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            takes_self=True,
        ),
        kw_only=True,
    )

    # Create each necessary secret
    def create_secret(self, params: dict) -> dict:
        url = urljoin(self.base_url, "/api/secrets/")
        response = requests.post(url, headers=self.headers, json=params)
        response.raise_for_status()
        return response.json()

    # If secrets need to be updated
    def update_secret(self, secret_id: str, params: Optional[dict]) -> dict:
        url = urljoin(self.base_url, f"/api/secrets/{secret_id}/")
        response = requests.patch(url, headers=self.headers, json=params)
        response.raise_for_status()
        return response.json()

    # If secrets need to be deleted
    def delete_secret(self, secret_id: str) -> dict:
        url = urljoin(self.base_url, f"/api/secrets/{secret_id}/")
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # If secrets need to be retrieved
    def get_secret(self, secret_id: str) -> dict:
        url = urljoin(self.base_url, f"/api/secrets/{secret_id}/")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
