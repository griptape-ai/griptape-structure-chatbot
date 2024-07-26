import json
import boto3
import os
import sys
from dotenv import load_dotenv
from griptape.config import OpenAiStructureConfig
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent, Structure
from griptape.drivers import (
    AmazonDynamoDbConversationMemoryDriver,
    GriptapeCloudEventListenerDriver,
)
from griptape.events import EventListener
from griptape.memory.structure import ConversationMemory

# TODO: Replace the agent in this file with your own agent. 

# Used only in local development
load_dotenv()

# Get environment variables 
base_url = os.environ["GT_CLOUD_BASE_URL"]
# If no API key is provided, will default to an empty string since it isn't necessary for local development.
api_key = os.environ.get("GT_CLOUD_API_KEY", "")

# If running in the cloud, will load these variables from the cloud environment. Otherwise will default to "ConversationMemoryTable". 
conversation_memory_table_name = os.environ.get("CONVERSATION_MEMORY_TABLE_NAME", "ConversationMemoryTable")
table_name = os.environ.get("DYNAMODB_TABLE_NAME", "ConversationMemoryTable")

#Create an event listener for the GriptapeCloudStructure
event_driver = GriptapeCloudEventListenerDriver(base_url=base_url, api_key=api_key)

# If using your own agent, replace the logic with your own agent initialization logic with the conversation memory configuration.
def init_structure(session_id: str) -> Structure:

    # TODO: Define your own rulesets and tools here. 
    # Example Ruleset 
    rulesets = [
        Ruleset(
            name="Agent",
            rules=[
                Rule(
                    "You are an intelligent agent tasked with answering user questions."
                ),
            ],
        ),
    ]

    try:
        agent = Agent(
            config=OpenAiStructureConfig(),
            # TODO: If configuring with your own agent, copy and use this conversation memory configuration. 
            # COPY
            conversation_memory=ConversationMemory(
                driver=AmazonDynamoDbConversationMemoryDriver(
                    session=boto3.Session(
                        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                    ),
                    table_name=conversation_memory_table_name,
                    partition_key="id",
                    partition_key_value=session_id, 
                    value_attribute_key="value",
                )
            ),
            # END COPY
            rulesets=rulesets,
            event_listeners=[EventListener(driver=event_driver)], 
        )
        return agent
    except Exception as e:
        print(f'Failed to initialize structure. {e}')
        raise e
    

# When the structure is running, the Gradio interface will pass both the input and session_id as a dict to the structure. 
# TODO: Keep this logic for running your own structure
if __name__ == "__main__":
    input_arg = sys.argv[1]
    input_arg_dict = json.loads(input_arg)
    agent = init_structure(input_arg_dict["session_id"]) # Initialize the structure with the session_id for Cloud based Conversation Memory. 
    agent.run(input_arg_dict["input"])