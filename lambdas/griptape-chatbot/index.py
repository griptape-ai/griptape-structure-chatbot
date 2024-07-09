import json
import os
import requests
from clients.griptape_api_client import GriptapeApiClient

griptape_api_key_secret_name = os.environ.get("GRIPTAPE_API_KEY_SECRET_NAME")
secrets_extension_port = os.environ["SECRETS_EXTENSION_HTTP_PORT"]
structure_id = os.environ["GT_CLOUD_STRUCTURE_ID"]


def get_griptape_api_key() -> str:
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_port}/secretsmanager/get?secretId={griptape_api_key_secret_name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    r = requests.get(secrets_extension_endpoint, headers=headers)
    return json.loads(r.text)["SecretString"]


griptape_api_client = GriptapeApiClient(api_key=get_griptape_api_key())


def handler(event, context):
    output = griptape_api_client.run(structure_id, ["hello there"])
    return {"output": output}
