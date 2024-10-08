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
griptape_aws_user_secret_name = os.environ.get("GRIPTAPE_AWS_USER_SECRET_NAME")
openai_api_key_secret_name = os.environ.get("OPENAI_API_KEY_SECRET_NAME")
secrets_extension_port = os.environ["SECRETS_EXTENSION_HTTP_PORT"]

github_repo_owner = os.getenv("GITHUB_REPO_OWNER", "griptape-ai")
github_repo_name = os.getenv("GITHUB_REPO_NAME", "griptape-structure-chatbot")
github_structure_branch = os.getenv("GITHUB_REPO_BRANCH", "main")
structure_config_file_path = os.getenv(
    "STRUCTURE_CONFIG_FILE_PATH", "/structure/structure_config.yaml"
)


http = urllib3.PoolManager()


def get_griptape_api_key() -> str:
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_port}/secretsmanager/get?secretId={griptape_api_key_secret_name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    r = http.request("GET", secrets_extension_endpoint, headers=headers)  # type: ignore
    return json.loads(r.data)["SecretString"]


def get_openai_api_key() -> str:
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_port}/secretsmanager/get?secretId={openai_api_key_secret_name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    r = http.request("GET", secrets_extension_endpoint, headers=headers)  # type: ignore
    return json.loads(r.data)["SecretString"]


def get_griptape_aws_user_secret() -> tuple:
    secrets_extension_endpoint = f"http://localhost:{secrets_extension_port}/secretsmanager/get?secretId={griptape_aws_user_secret_name}"
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    r = http.request("GET", secrets_extension_endpoint, headers=headers)  # type: ignore
    secret_string = json.loads(r.data)["SecretString"]
    secret_json = json.loads(secret_string)
    return secret_json["accessKeyId"], secret_json["secretAccessKey"]


def on_event(event, context):
    print(event)
    request_type = event["RequestType"]

    griptape_api_key = get_griptape_api_key()
    griptape_api_client = GriptapeApiClient(api_key=griptape_api_key)

    if request_type == "Create":
        return on_create(event, griptape_api_client, griptape_api_key)
    if request_type == "Update":
        return on_update(event, griptape_api_client, griptape_api_key)
    if request_type == "Delete":
        return on_delete(event, griptape_api_client)
    raise Exception("Invalid request type: %s" % request_type)


def on_create(event, griptape_api_client, griptape_api_key):
    props = event["ResourceProperties"]
    print("create new resource with props %s" % props)

    aws_access_key_id, aws_secret_access_key = get_griptape_aws_user_secret()

    gt_cloud_api_key_id = os.environ.get("GT_API_KEY_SECRET_ID")
    openai_api_key_id = os.environ.get("OPENAI_API_KEY_SECRET_ID")
    aws_secret_access_key_id = os.environ.get("AWS_SECRET_ACCESS_KEY_SECRET_ID")

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
        "env_vars": [
            {
                "name": "AWS_SECRET_ACCESS_KEY",
                "source": "secret_ref",
                "value": aws_secret_access_key_id,
            },
            {
                "name": "GT_CLOUD_API_KEY",
                "source": "secret_ref",
                "value": gt_cloud_api_key_id,
            },
            {
                "name": "OPENAI_API_KEY",
                "source": "secret_ref",
                "value": openai_api_key_id,
            },
            {
                "name": "AWS_ACCESS_KEY_ID",
                "source": "manual",
                "value": aws_access_key_id,
            },
            {
                "name": "AWS_DEFAULT_REGION",
                "source": "manual",
                "value": os.environ["AWS_REGION"],
            },
            {
                "name": "CONVERSATION_MEMORY_TABLE_NAME",
                "source": "manual",
                "value": os.environ["CONVERSATION_MEMORY_TABLE_NAME"],
            },
        ],
        "structure_config_file": structure_config_file_path,
    }
    print(create_structure_params)

    structure_response = griptape_api_client.create_structure(
        params=create_structure_params
    )

    physical_id = structure_response["structure_id"]

    return {"PhysicalResourceId": physical_id}


def on_update(event, griptape_api_client, griptape_api_key):
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]
    props_past = event["OldResourceProperties"]
    print("update resource %s with props %s" % (physical_id, props))
    # If the branch has changed, the structure is re-created.
    if props != props_past:
        # Creates a new structure
        aws_access_key_id, aws_secret_access_key = get_griptape_aws_user_secret()
        gt_cloud_api_key_id = os.environ.get("GT_API_KEY_SECRET_ID")
        openai_api_key_id = os.environ.get("OPENAI_API_KEY_SECRET_ID")
        aws_secret_access_key_id = os.environ.get("AWS_SECRET_ACCESS_KEY_SECRET_ID")
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
            "env_vars": [
                {
                    "name": "AWS_SECRET_ACCESS_KEY",
                    "source": "secret_ref",
                    "value": aws_secret_access_key_id,
                },
                {
                    "name": "GT_CLOUD_API_KEY",
                    "source": "secret_ref",
                    "value": gt_cloud_api_key_id,
                },
                {
                    "name": "OPENAI_API_KEY",
                    "source": "secret_ref",
                    "value": openai_api_key_id,
                },
                {
                    "name": "AWS_ACCESS_KEY_ID",
                    "source": "manual",
                    "value": aws_access_key_id,
                },
                {
                    "name": "AWS_DEFAULT_REGION",
                    "source": "manual",
                    "value": os.environ["AWS_REGION"],
                },
                {
                    "name": "CONVERSATION_MEMORY_TABLE_NAME",
                    "source": "manual",
                    "value": os.environ["CONVERSATION_MEMORY_TABLE_NAME"],
                },
            ],
            "structure_config_file": structure_config_file_path,
        }
        structure_response = griptape_api_client.create_structure(
            params=create_structure_params
        )
        physical_id = structure_response["structure_id"]
        # Returns a new PhysicalResourceId, which triggers the deletion of the old structure.
        return {"PhysicalResourceId": physical_id}

    structure_response = griptape_api_client.update_structure(physical_id, props)


def on_delete(event, griptape_api_client):
    physical_id = event["PhysicalResourceId"]
    print("delete resource %s" % physical_id)

    structure_response = griptape_api_client.delete_structure(physical_id)
