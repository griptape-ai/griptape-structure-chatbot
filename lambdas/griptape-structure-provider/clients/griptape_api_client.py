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

    def create_structure(self, params: dict) -> dict:
        url = urljoin(self.base_url, "/api/structures/")
        response = requests.post(url, headers=self.headers, json=params)

        response.raise_for_status()
        print(response)

        return response.json()

    def update_structure(self, structure_id: str, params: Optional[dict]) -> dict:
        url = urljoin(self.base_url, f"/api/structures/{structure_id}/")
        response = requests.post(url, headers=self.headers, json=params)
        
        response.raise_for_status()

        return response.json()

    def delete_structure(self, structure_id: str) -> dict:
        url = urljoin(self.base_url, f"/api/structures/{structure_id}/")
        response = requests.delete(url, headers=self.headers)

        response.raise_for_status()

        return response.json()
