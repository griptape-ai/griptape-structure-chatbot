import json
import os
import urllib3
from dotenv import load_dotenv
from clients.griptape_api_client import GriptapeApiClient

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), ".env")

# Load the .env file
load_dotenv(env_path)

griptape_api_key_secret_name = os.environ.get("GRIPTAPE_API_KEY_SECRET_NAME")
secrets_extension_port = os.environ["SECRETS_EXTENSION_HTTP_PORT"]


http = urllib3.PoolManager()


def get_griptape_api_key() -> str:
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_port}/secretsmanager/get?secretId={griptape_api_key_secret_name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    r = http.request("GET", secrets_extension_endpoint, headers=headers)  # type: ignore
    return json.loads(r.data)["SecretString"]


# Determine how the function behaves on different events
def on_event(event, context):
    print(event)
    request_type = event["RequestType"]
    griptape_api_key = get_griptape_api_key()
    griptape_api_client = GriptapeApiClient(api_key=griptape_api_key)
    if request_type == "Create":
        return on_create(event, griptape_api_client)
    if request_type == "Update":
        return on_update(event, griptape_api_client)
    if request_type == "Delete":
        return on_delete(event, griptape_api_client)
    raise Exception("Invalid request type: %s" % request_type)


# Create a new secret
def on_create(event, griptape_api_client):
    props = event["ResourceProperties"]
    print("create new resource with props %s" % props["secret_name"])
    secret_response = griptape_api_client.create_secret(
        params={"name": props["secret_name"], "value": props["secret_value"]}
    )
    physical_id = secret_response["secret_id"]
    return {"PhysicalResourceId": physical_id}


# Update an existing secret
def on_update(event, griptape_api_client):
    props = event["ResourceProperties"]
    print("Update resource with props %s" % props["secret_name"])
    physical_id = event["PhysicalResourceId"]
    secret_response = griptape_api_client.update_secret(
        physical_id,
        params={"name": props["secret_name"], "value": props["secret_value"]},
    )
    physical_id = secret_response["secret_id"]
    return {"PhysicalResourceId": physical_id}


# Delete a secret
def on_delete(event, griptape_api_client):
    physical_id = event["PhysicalResourceId"]
    print("delete resource %s" % physical_id)
    secret_response = griptape_api_client.delete_secret(physical_id)
