import {
  CfnOutput,
  CustomResource,
  Duration,
  RemovalPolicy,
  SecretValue,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { AttributeType, Billing, TableV2 } from "aws-cdk-lib/aws-dynamodb";
import {
  FunctionUrlAuthType,
  ParamsAndSecretsLogLevel,
  ParamsAndSecretsLayerVersion,
  ParamsAndSecretsVersions,
  Runtime,
} from "aws-cdk-lib/aws-lambda";
import { PythonFunction } from "@aws-cdk/aws-lambda-python-alpha";
import { Secret } from "aws-cdk-lib/aws-secretsmanager";
import { Provider } from "aws-cdk-lib/custom-resources";
import { LogGroup, RetentionDays } from "aws-cdk-lib/aws-logs";
import { AccessKey, AnyPrincipal, User } from "aws-cdk-lib/aws-iam";

export interface GriptapeStructureChatbotProps {}

export class GriptapeStructureChatbot extends Construct {
  constructor(
    scope: Construct,
    id: string,
    props?: GriptapeStructureChatbotProps
  ) {
    super(scope, id);

    const conversationMemoryTable = new TableV2(
      this,
      "ConversationMemoryTable",
      {
        billing: Billing.onDemand(),
        partitionKey: { name: "id", type: AttributeType.STRING },
        tableName: process.env.TABLE_NAME || "ConversationMemoryTable",
        removalPolicy: RemovalPolicy.DESTROY,
      }
    );

    const awsUser = new User(this, "GriptapeChatbotUser", {
      userName: "griptape-chatbot-user",
    });

    conversationMemoryTable.grantReadWriteData(awsUser);

    const accessKey = new AccessKey(this, "GriptapeChatbotAccessKey", {
      user: awsUser,
    });

    const griptapeUserSecret = new Secret(
      this,
      "GriptapeChatbotAWSUserSecret",
      {
        secretName: "griptape-chatbot-aws-user",
        secretObjectValue: {
          accessKeyId: SecretValue.unsafePlainText(accessKey.accessKeyId),
          secretAccessKey: accessKey.secretAccessKey,
        },
      }
    );

    const griptapeApiKeySecret = Secret.fromSecretNameV2(
      this,
      "GriptapeApiKeySecret",
      "griptape-api-key"
    );

    const openaiApiKeySecret = Secret.fromSecretNameV2(
      this,
      "OpenAIApiKeySecret",
      "openai-api-key"
    );

    const secretsHttpPort = 2773;
    const paramsAndSecrets = ParamsAndSecretsLayerVersion.fromVersion(
      ParamsAndSecretsVersions.V1_0_103,
      {
        cacheSize: 500,
        httpPort: secretsHttpPort,
        logLevel: ParamsAndSecretsLogLevel.WARN,
      }
    );

    const griptapeSecretProviderLambda = new PythonFunction(
      this,
      "GriptapeSecretProviderLambda",
      {
        entry: "lambdas/griptape-secret-provider",
        runtime: Runtime.PYTHON_3_12,
        index: "index.py",
        handler: "on_event",
        environment:{
          SECRETS_EXTENSION_HTTP_PORT: `${secretsHttpPort}`,
          GRIPTAPE_API_KEY_SECRET_NAME: griptapeApiKeySecret.secretName,
          GRIPTAPE_AWS_USER_SECRET_NAME: griptapeUserSecret.secretName,
        },
        paramsAndSecrets,
        memorySize: 1024,
      }
    );

    griptapeApiKeySecret.grantRead(griptapeSecretProviderLambda);
    griptapeUserSecret.grantRead(griptapeSecretProviderLambda);

    const griptapeSecretProvider = new Provider(
      this,
      "GriptapeSecretProvider",
      {
        onEventHandler: griptapeSecretProviderLambda,
        logGroup: new LogGroup(this, "GriptapeSecretProviderLogs", {
          retention: RetentionDays.ONE_WEEK,
        }),
      }
    );

    const griptapeSecretProviderResourceGT = new CustomResource(
      this,
      "GriptapeSecretProviderResourceGT",
      {
        serviceToken: griptapeSecretProvider.serviceToken,
        properties:{
          secret_name: "GT Cloud API Key",
          secret_value: process.env.GT_CLOUD_API_KEY,
        }
      }
    );

    const griptapeSecretProviderResourceOpenAI = new CustomResource(
      this,
      "GriptapeSecretProviderResourceOpenAI",
      {
        serviceToken: griptapeSecretProvider.serviceToken,
        properties:{
          secret_name: "OpenAI API Key",
          secret_value: process.env.OPENAI_API_KEY,
        }
      }
    );

    const griptapeSecretProviderResourceAWSSecret = new CustomResource(
      this,
      "GriptapeSecretProviderResourceAWSSecret",
      {
        serviceToken: griptapeSecretProvider.serviceToken,
        properties:{
          secret_name: "AWS Secret Access Key",
          secret_value: process.env.AWS_SECRET_ACCESS_KEY,
        }
      }
    );

    const griptapeStructureProviderLambda = new PythonFunction(
      this,
      "GriptapeStructureProviderLambda",
      {
        entry: "lambdas/griptape-structure-provider",
        runtime: Runtime.PYTHON_3_12,
        index: "index.py",
        handler: "on_event",
        environment: {
          SECRETS_EXTENSION_HTTP_PORT: `${secretsHttpPort}`,
          GRIPTAPE_API_KEY_SECRET_NAME: griptapeApiKeySecret.secretName,
          GRIPTAPE_AWS_USER_SECRET_NAME: griptapeUserSecret.secretName,
          OPENAI_API_KEY_SECRET_NAME: openaiApiKeySecret.secretName,
          CONVERSATION_MEMORY_TABLE_NAME: conversationMemoryTable.tableName,
          GT_API_KEY_SECRET_ID : griptapeSecretProviderResourceGT.ref,
          OPENAI_API_KEY_SECRET_ID : griptapeSecretProviderResourceOpenAI.ref,
          AWS_SECRET_ACCESS_KEY_SECRET_ID : griptapeSecretProviderResourceAWSSecret.ref,
        },
        paramsAndSecrets,
        memorySize: 1024,
      }
    );
    griptapeUserSecret.grantRead(griptapeStructureProviderLambda);
    griptapeApiKeySecret.grantRead(griptapeStructureProviderLambda);
    openaiApiKeySecret.grantRead(griptapeStructureProviderLambda);

    const griptapeStructureProvider = new Provider(
      this,
      "GriptapeStructureProvider",
      {
        onEventHandler: griptapeStructureProviderLambda,
        logGroup: new LogGroup(this, "GriptapeStructureProviderLogs", {
          retention: RetentionDays.ONE_WEEK,
        }),
      }
    );

    const griptapeStructureProviderResource = new CustomResource(
      this,
      "GriptapeStructureProviderResource",
      {
        serviceToken: griptapeStructureProvider.serviceToken,
        properties: {
          github_repo_branch: process.env.GITHUB_REPO_BRANCH,
          github_repo_owner: process.env.GITHUB_REPO_OWNER,
          github_repo_name: process.env.GITHUB_REPO_NAME,
        }
      }
    );

    const griptapeChatbotSessionManagerLambda = new PythonFunction(
      this,
      "GriptapeChatbotSessionManagerLambda",
      {
        description:
          "Griptape Chatbot Lambda Session Manager function to manage sessions for Griptape Structure Chats ",
        entry: "lambdas/griptape-chatbot",
        runtime: Runtime.PYTHON_3_12,
        index: "index.py",
        handler: "handler",
        environment: {
          SECRETS_EXTENSION_HTTP_PORT: `${secretsHttpPort}`,
          DYNAMODB_TABLE_NAME: conversationMemoryTable.tableName,
          GRIPTAPE_API_KEY_SECRET_NAME: griptapeApiKeySecret.secretName,
          GT_CLOUD_STRUCTURE_ID: griptapeStructureProviderResource.ref,
        },
        paramsAndSecrets,
        memorySize: 1024,
        timeout: Duration.minutes(5),
      }
    );
    griptapeChatbotSessionManagerLambda.addPermission("Invoke", {
      principal: new AnyPrincipal(),
    });

    const fnUrl = griptapeChatbotSessionManagerLambda.addFunctionUrl({
      authType: FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
      },
    });

    conversationMemoryTable.grantReadWriteData(griptapeChatbotSessionManagerLambda);
    griptapeApiKeySecret.grantRead(griptapeChatbotSessionManagerLambda);

    new CfnOutput(this, "GriptapeChatbotLambdaEndpoint", {
      value: fnUrl.url,
      exportName: "GriptapeChatbotLambdaEndpoint",
      description: "The endpoint of the Griptape Chatbot Lambda function",
    });
  }
}
