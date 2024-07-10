import json
import boto3
import os
import sys

from griptape.config import OpenAiStructureConfig
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent
from griptape.drivers import (
    AmazonDynamoDbConversationMemoryDriver,
    GriptapeCloudEventListenerDriver,
)
from griptape.events import EventListener
from griptape.memory.structure import ConversationMemory

base_url = os.environ["GT_CLOUD_BASE_URL"]
api_key = os.environ["GT_CLOUD_API_KEY"]
conversation_memory_table_name = os.environ["CONVERSATION_MEMORY_TABLE_NAME"]

event_driver = GriptapeCloudEventListenerDriver(base_url=base_url, api_key=api_key)


def init_structure(session_id: str) -> Agent:

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
                partition_key_value=session_id,  # The value of the partition key
                value_attribute_key="value",
            )
        ),
        rulesets=rulesets,
        event_listeners=[EventListener(driver=event_driver)],
    )
    return agent


if __name__ == "__main__":
    input_arg = sys.argv[1]
    input_arg_dict = json.loads(input_arg)
    agent = init_structure(input_arg_dict["session_id"])
    agent.run(input_arg_dict["input"])
