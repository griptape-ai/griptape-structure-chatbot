import json
import os
import requests
from clients.griptape_api_client import GriptapeApiClient

griptape_api_key_secret_name = os.environ.get("GRIPTAPE_API_KEY_SECRET_NAME")
griptape_aws_user_secret_name = os.environ.get("GRIPTAPE_AWS_USER_SECRET_NAME")
openai_api_key_secret_name = os.environ.get("OPENAI_API_KEY_SECRET_NAME")
secrets_extension_port = os.environ["SECRETS_EXTENSION_HTTP_PORT"]

github_repo_owner = os.getenv("GITHUB_REPO_OWNER", "griptape-ai")
github_repo_name = os.getenv("GITHUB_REPO_NAME", "griptape-structure-chatbot")
github_structure_branch = os.getenv("GITHUB_REPO_BRANCH", "main")


def get_griptape_api_key() -> str:
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_port}/secretsmanager/get?secretId={griptape_api_key_secret_name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    r = requests.get(secrets_extension_endpoint, headers=headers)
    return json.loads(r.text)["SecretString"]


def get_openai_api_key() -> str:
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_port}/secretsmanager/get?secretId={openai_api_key_secret_name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    r = requests.get(secrets_extension_endpoint, headers=headers)
    return json.loads(r.text)["SecretString"]


def get_griptape_aws_user_secret() -> tuple:
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_port}/secretsmanager/get?secretId={griptape_aws_user_secret_name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    r = requests.get(secrets_extension_endpoint, headers=headers)
    secret = json.loads(r.text)["SecretString"]
    return secret["accessKeyId"], secret["secretAccessKey"]


griptape_api_key = get_griptape_api_key()
griptape_api_client = GriptapeApiClient(api_key=griptape_api_key)


def on_event(event, context):
    print(event)
    request_type = event["RequestType"]
    if request_type == "Create":
        return on_create(event)
    if request_type == "Update":
        return on_update(event)
    if request_type == "Delete":
        return on_delete(event)
    raise Exception("Invalid request type: %s" % request_type)


def on_create(event):
    props = event["ResourceProperties"]
    print("create new resource with props %s" % props)

    aws_access_key_id, aws_secret_access_key = get_griptape_aws_user_secret()

    create_structure_params = {
        "name": "Griptape Structure Chatbot",
        "description": "Griptape Structure Chatbot",
        "code": {
            "github": {
                "owner": github_repo_owner,
                "name": github_repo_name,
                "push": {"branch": github_structure_branch},
            }
        },
        "env": {
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_DEFAULT_REGION": os.environ["AWS_REGION"],
        },
        "env_secret": {
            "OPENAI_API_KEY": get_openai_api_key(),
            "GT_CLOUD_API_KEY": griptape_api_key,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
        },
        "main_file": "structure/app.py",
        "requirements_file": "structure/requirements.txt",
    }

    structure_response = griptape_api_client.create_structure(
        params=create_structure_params
    )
    # add your create code here...
    physical_id = structure_response["structure_id"]

    return {"PhysicalResourceId": physical_id}


def on_update(event):
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]
    print("update resource %s with props %s" % (physical_id, props))

    structure_response = griptape_api_client.update_structure(physical_id, props)


def on_delete(event):
    physical_id = event["PhysicalResourceId"]
    print("delete resource %s" % physical_id)

    structure_response = griptape_api_client.delete_structure(physical_id)
