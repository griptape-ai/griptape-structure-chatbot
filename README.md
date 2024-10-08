# Griptape Structure Chatbot

## Description 
This project runs a script that generates resources through an AWS CDK and deploys it with a Griptape Structure to invoke the Structure for use as a chatbot with the Gradio Interface in the Griptape Cloud. 
Deploying the resources creates both a DynamoDB table with AWS and creates a Griptape Structure in the Griptape Cloud. 
Once deployed, the user can call the Griptape Structure with the Griptape Cloud to invoke their structure. 

## Prerequisites

### AWS

You need:

1. An AWS Account
1. The [aws-cli installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
Follow the instructions for your OS. 

1. AWS credentials or aws sso configured
2. To configure aws sso: 
```shell
    aws configure sso
```

Values for the SSO: 

    `SSO session name (Recommended): my-sso`

    `SSO start URL [None]: <YourStartURL>`

    `SSO region [None]: <YourRegion>`

    `SSO registration scopes [None]: sso:account:access`

```shell
    aws s3 ls --profile <YourProfileName>
```

### AWS CDK

You need:

1. Node.js installed

This is necessary in order to install aws-cdk. 

```shell
    https://nodejs.org/en/download/package-manager
```

1. The [aws-cdk](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) installed
```shell
    npm install -g aws-cdk
```
To verify installation: 
```shell
    cdk --version
```

### Docker

You need:

1. [Docker](https://docs.docker.com/engine/install/) installed

### Griptape Cloud

You need:

1. A [Griptape Cloud account](https://cloud.griptape.ai)
1. A [Griptape Cloud API Key](https://cloud.griptape.ai/configuration/api-keys)

### Open AI

You need:

1. An [Open AI account](https://openai.com/)
1. An Open AI [API Key](https://platform.openai.com/docs/api-reference/api-keys)

## Griptape Chat 
To run the structure with Gradio, you need to clone and configure the Griptape Chat repository. 
1. Follow the instructions on the [README](https://github.com/griptape-ai/griptape-chat)

## Environment Setup

### If you plan on modifying the structure to be deployed to the cloud:  
1. Set the .env variables based on the repository of your structure.
```shell
        GITHUB_REPO_OWNER=<your-owner>
        GITHUB_REPO_NAME=<your-repo-name>
        GITHUB_REPO_BRANCH=<your-branch>
        STRUCTURE_FILE_PATH=<your-path-from-repo>
        REQUIREMENTS_FILE_PATH=<your-path-from-repo>
```
1. In your repository, add this configuration to your agent and pass a session_id when creating your agent.

```python
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
    )
```

1. Update your structure with the parsing information at the bottom of the app.py - this is necessary for the way that Gradio passes in the session_id and inputs. Replace ```init_structure``` with your own agent creation method. 

```python
    # TODO: Keep this logic for running your own structure
    if __name__ == "__main__":
        input_arg = sys.argv[1]
        input_arg_dict = json.loads(input_arg)
        agent = init_structure(input_arg_dict["session_id"])
        agent.run(input_arg_dict["input"])
```

### If you do not plan on modifying the structure: 
1. Clone the Repository
```shell
    git clone git!@github.com:griptape-ai/griptape-structure-chatbot.git
```
### Install dependencies
```shell
    npm install
```
Create a .env file, and populate it accordingly to .env.example file.
Do not forget to add your Griptape Cloud API Key. 
```shell
    GRIPTAPE_API_KEY=<YOUR_GRIPTAPE_CLOUD_API_KEY>
 ```

## Deploy

1.  Follow the Token provider configuration documentation for [AWS IAM Identity Center](https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html)
1. Configure Token provider
```shell
    aws configure sso-session 
```

If necessary to sign into an IAM Identity Center session: 

```shell
    aws sso login --profile <your-profile-name>
```
1.  Export SSO credentials:

```shell
    eval $(aws configure export-credentials --profile <profile> --format env)
```
1.  `npm run bootstrap`
1.  `npm run deploy`

## Run Structure in Skatepark
*This can only be accomplished after deploying the CDK*
Prerequisites: 
1. Go to IAM Dashboard 
1. Under Access Management go to Users
1. Go to griptape-chatbot-user (Should exist if CDK has been deployed) 
1. Create an access key and save the values in the .env: 
```shell
    AWS_ACCESS_KEY_ID=<YourAccessKey>
    AWS_SECRET_ACCESS_KEY=<YourSecretAccessKey>
```
Additional environment variables needed: 
```shell
    GT_CLOUD_BASE_URL=http://127.0.0.1:5000
```
*http://127.0.0.1:5000 is the default for Skatepark, but you can change this when running gt skatepark start*

## Run Structure in Skatepark with Griptape Chat 
Start in Skatepark: 
``` shell
    gt skatepark start
```
Navigate to the directory of your structure: 
``` shell
    gt skatepark register --main-file <StructureFilename>
```
Put your Structure ID in your [Griptape Chat](https://github.com/griptape-ai/griptape-chat) .env 
```shell
GT_STRUCTURE_ID=<your-structure-id>
```
If you change any environment variables 
``` shell
    gt skatepark build
```
## Run Structure in GriptapeCloud with Griptape Chat
After you deploy the structure
1. Get the Structure ID from the Griptape Structure Chatbot: https://cloud.griptape.ai/structures
1. Add additional environment variables in the Griptape Cloud 
    1. [Create any additional](https://cloud.griptape.ai/configuration/secrets) secrets necessary and add them to your structure in the [Griptape Cloud](https://cloud.griptape.ai/structures). 
        1. ex: Adding a Zenrows API Key 
            1. Click `Create Secret`
                1. Name: `Zenrows API Key`
                1. Value: `<your-Zenrows-API-key-value>`
            1. Go to your structure and click `Add Variable`.
                1. Name: `ZENROWS_API_KEY`
                1. Source: `Secret`
                1. Value: select `Zenrows API Key` from the dropdown menu.
    1. Add any environment variables that your structure requires that haven't already been set by clicking `Add Variable` and setting the source to `Manual`. 
        1. ex: Adding a Knowledge Base
            1. Click `Add Variable`
                1. Name: `KNOWLEDGE_BASE_ID`
                1. Source: `Manual`
                1. Value: `<your-kb-id>`
1. Put the Structure ID in your .env in [Griptape Chat](https://github.com/griptape-ai/griptape-chat)
```shell
    GT_STRUCTURE_ID=<your-structure-id>
```
## Run Griptape Chat
In your CLI in the Griptape Chat folder
```shell 
    poetry run python app.py 
```
## Invoke the Lambda Function

Invoke the endpoint as follows:

1. Retrieve a session_id

```
curl --json '{"operation": "create_session"}' https://<YOUR_LAMBDA_URL_ID>.lambda-url.<REGION>.on.aws/
```

## Useful commands

- `npm run build` compile typescript to js
- `npm run watch` watch for changes and compile
- `npm run test` perform the jest unit tests
- `npx cdk deploy` deploy this stack to your default AWS account/region
- `npx cdk diff` compare deployed stack with current state
- `npx cdk synth` emits the synthesized CloudFormation template
