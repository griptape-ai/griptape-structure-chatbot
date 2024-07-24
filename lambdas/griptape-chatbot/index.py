import boto3
import json
import os
import urllib3
from uuid import uuid4 as uuid

griptape_api_key_secret_name = os.environ.get("GRIPTAPE_API_KEY_SECRET_NAME")
secrets_extension_port = os.environ["SECRETS_EXTENSION_HTTP_PORT"]
structure_id = os.environ["GT_CLOUD_STRUCTURE_ID"]
table_name = os.environ["DYNAMODB_TABLE_NAME"]

http = urllib3.PoolManager()


def get_griptape_api_key() -> str:
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_port}/secretsmanager/get?secretId={griptape_api_key_secret_name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    r = http.request("GET", secrets_extension_endpoint, headers=headers)  # type: ignore
    return json.loads(r.data)["SecretString"]


def handler(event, context):

    event_body = json.loads(event["body"])
    operation = event_body["operation"] if "operation" in event_body else None

    match operation:
        case "create_session":
            return handle_create_session()
        case _:
            return {"message": "Operation not supported"}


def handle_create_session() -> dict:
    session_id = _get_unique_session_id()
    return {"session_id": session_id}


def _get_unique_session_id() -> str:
    session = boto3.Session()
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)  # type: ignore
    session_id = ""
    response = {"Item": None}
    while "Item" in response:
        session_id = str(uuid())
        response = table.get_item(Key={"id": session_id})

    return session_id
