# Griptape Structure Chatbot

## Description 
This project creates an AWS CDK and deploys it with a Griptape Structure to invoke the Structure for use as a chatbot with the Gradio Interface in the Griptape Cloud. 
Deploying the CDK creates both a DynamoDB table with AWS and creates a Griptape Structure in the Griptape Cloud. 
Once deployed, the user can call the Griptape Structure with the Griptape Cloud to invoke their structure. 

## Prerequisites

### AWS

You need:

1. An AWS Account
1. The [aws-cli installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
```shell
    Add commands to configure it 
```

1. AWS credentials or aws sso configured
To configure aws sso: 
```shell
    aws configure sso
```
```
    SSO session name (Recommended): my-sso
    SSO start URL [None]: <YourStartURL>
    SSO region [None]: <YourRegion>
    SSO registration scopes [None]: sso:account:access
```
```shell
    aws s3 ls --profile <YourProfileName>
```

### AWS CDK

You need:

1. Node.js installed
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
1. A [Griptape Cloud API Key](https://cloud.griptape.ai/account/api-keys)

### Open AI

You need:

1. An [Open AI account](https://openai.com/)
1. An Open AI [API Key](https://platform.openai.com/docs/api-reference/api-keys)

## Griptape Chat 
To run the structure with Gradio, you need to clone and configure the Griptape Chat repository. 
1. Follow the instructions on the [README](https://github.com/griptape-ai/griptape-chat)

## Environment Setup

### If you plan on modifying the structure
1. Create your own Repository on Github
1. Copy the code into your repository 
1. Set the .env variables 
```shell
GITHUB_REPO_OWNER=<your-owner>
GITHUB_REPO_NAME=<your-repo-name>
GITHUB_REPO_BRANCH=<your-branch>
```
### If you do not plan on modifying the structure
1. Clone the Repository
```shell
    git clone git!@github.com:griptape-ai/griptape-structure-chatbot.git
```
Install dependencies
```shell
    npm install
```
Create a .env file, and populate it accordingly to .env.example file. 

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
Prerequisites: 
1. Go to IAM Dashboard 
1. Under Access Management - Go to Users
1. Go to griptape-chatbot-user (Should exist if CDK has been deployed) 
1. Create Access Key and save the values in the .env: 
```shell
    AWS_ACCESS_KEY_ID=<YourAccessKey>
    AWS_SECRET_ACCESS_KEY=<YourAccessKey>
```
1. Additional environment variables needed: 
```shell
    GT_CLOUD_BASE_URL=http://127.0.0.1:5000
```
*http://127.0.0.1:5000 is the default for Skatepark, but you can configure this when running gt skatepark start*

## Run 
1. Start in Skatepark: 
``` shell
    gt skatepark start
```
1. Navigate to the directory of your structure: 
``` shell
    gt skatepark register --main-file <StructureFilename>
```
1. Put your Structure ID in your [Griptape Chat](https://github.com/griptape-ai/griptape-chat) .env 

If you change any environment variables 
``` shell
    gt skatepark build
```
## Run Structure in GriptapeCloud with Griptape Chat
After you deploy the structure
1. Get the Structure ID from the Griptape Structure Chatbot: https://cloud.griptape.ai/structures
1. Put the Structure ID in your .env in [Griptape Chat](https://github.com/griptape-ai/griptape-chat)
```shell
GT_STRUCTURE_ID=<your-structure-id>
```
1. Run Griptape Chat
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
