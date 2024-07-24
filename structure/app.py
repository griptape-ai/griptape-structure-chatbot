import json
import boto3
import os
import sys
from uuid import uuid4 as uuid
from griptape.config import OpenAiStructureConfig
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent, Structure
from griptape.drivers import (
    AmazonDynamoDbConversationMemoryDriver,
    GriptapeCloudEventListenerDriver,
)
from griptape.events import EventListener
from griptape.memory.structure import ConversationMemory


base_url = os.environ["GT_CLOUD_BASE_URL"]
api_key = os.environ["GT_CLOUD_API_KEY"]
conversation_memory_table_name = os.environ.get("CONVERSATION_MEMORY_TABLE_NAME", "ConversationMemoryTable")
#conversation_memory_table_name = os.environ["TABLE_NAME"]
table_name = os.environ.get("DYNAMODB_TABLE_NAME", "ConversationMemoryTable")
griptape_api_key_secret_name = os.environ.get("GRIPTAPE_API_KEY_SECRET_NAME")


# Create a session to interact with DynamoDB. Simple and no changes needed. 
def handle_create_session() -> dict:
    session_id = _get_unique_session_id()
    return {"session_id": session_id}

# Create a unique sesssion ID 
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

#Publish events to the griptape cloud- Doesn't necessarily need to run locally? / no Structure_RUn_Id when running locally
event_driver = GriptapeCloudEventListenerDriver(base_url=base_url, api_key=api_key)


#Changed this to Structure instead of agent - Is that ok? TODO: Check this 
def init_structure() -> Structure:

    session_id = handle_create_session()["session_id"] 

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
            rulesets=rulesets,
            event_listeners=[EventListener(driver=event_driver)], 
        )
    except:
        #ERROR HANDLING!!! 
        print(f"Failed to initialize structure")
    
    return agent

# Makes sure that structure is initialized!!
#agent = init_structure()
#input = sys.argv[1]
#agent.run(input)

#This is the part that is causing the error: specifically json.loads
if __name__ == "__main__":
    agent = init_structure()
    input_arg = sys.argv[1]
    print(input_arg)
    #input_arg_dict = json.loads(input_arg)
    #agent = init_structure(input_arg_dict["session_id"])
    agent.run(input_arg)