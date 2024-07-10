# Griptape Structure Chatbot

This project deploys a Griptape Structure and AWS Infrastructure as an endpoint to invoke the Structure for use as a chatbot.

## Prerequisites

### AWS

You need:

1. An AWS Account
1. The [aws-cli installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
1. AWS credentials or aws sso configured

### AWS CDK

You need:

1. The [aws-cdk](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) installed

### Docker

You need:

1. [Docker](https://docs.docker.com/engine/install/) installed

### Griptape Cloud

You need:

1. A [Griptape Cloud account](https://cloud.griptape.ai)
1. A Griptape Cloud API Key

### Open AI

You need:

1. An [Open AI account](https://openai.com/)
1. An Open AI [API Key](https://platform.openai.com/docs/api-reference/api-keys)

## Deploy

1.  Follow the Token provider configuration documentation for [AWS IAM Identity Center](https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html)
1.  Export SSO credentials:

    ```
    eval $(aws configure export-credentials --profile <profile> --format env)
    ```

1.  `npm run bootstrap`
1.  `npm run deploy`

## Invoke

Invoke the endpoint as follows:

1. Retrieve a session_id

```
curl --json '{"operation": "create_session"}' https://<YOUR_LAMBDA_URL_ID>.lambda-url.<REGION>.on.aws/
```

1. Send a message

```
curl --json '{"operation": "message", "session_id": "<RETRIEVED_SESSION_ID>", "input": "<YOUR_CHAT_INPUT>"}' https://<YOUR_LAMBDA_URL_ID>.lambda-url.<REGION>.on.aws/
```

## Useful commands

- `npm run build` compile typescript to js
- `npm run watch` watch for changes and compile
- `npm run test` perform the jest unit tests
- `npx cdk deploy` deploy this stack to your default AWS account/region
- `npx cdk diff` compare deployed stack with current state
- `npx cdk synth` emits the synthesized CloudFormation template
