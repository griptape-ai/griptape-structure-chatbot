from __future__ import annotations
import time
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
    poll_attempts: int = field(default=120, kw_only=True)
    poll_interval: int = field(default=0.5, kw_only=True)

    def run(self, structure_id: str, args: list) -> str:
        run = self.create_run(structure_id, args)
        run_id = run["structure_run_id"]

        poll_attempts = 0
        while (
            run["status"] in ["QUEUED", "RUNNING"]
            and poll_attempts <= self.poll_attempts
        ):
            try:
                run = self.poll_for_run_status(run_id)
                if not run["status"] in ["QUEUED", "RUNNING"]:
                    break
            except Exception as e:
                print(f"Failed to poll for run status: {e}")
            poll_attempts += 1
            time.sleep(self.poll_interval)

        if run["status"] == "SUCCEEDED":
            return run["output"]
        else:
            raise Exception(f"Run failed!")

    def create_run(self, structure_id: str, args: list) -> dict:
        url = urljoin(self.base_url, f"/api/structures/{structure_id}/runs/")
        response = requests.post(url, headers=self.headers, json={"args": args})

        response.raise_for_status()

        return response.json()

    def poll_for_run_status(self, run_id: str) -> dict:
        url = urljoin(self.base_url, f"/api/structure-runs/{run_id}/")
        response = requests.get(url, headers=self.headers)

        response.raise_for_status()

        return response.json()
