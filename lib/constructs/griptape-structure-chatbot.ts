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
      }
    );

    const griptapeChatbotLambda = new PythonFunction(
      this,
      "GriptapeChatbotLambda",
      {
        description:
          "Griptape Chatbot Lambda function to invoke a Griptape Structure",
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
    griptapeChatbotLambda.addPermission("Invoke", {
      principal: new AnyPrincipal(),
    });

    const fnUrl = griptapeChatbotLambda.addFunctionUrl({
      authType: FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
      },
    });

    conversationMemoryTable.grantReadWriteData(griptapeChatbotLambda);
    griptapeApiKeySecret.grantRead(griptapeChatbotLambda);

    new CfnOutput(this, "GriptapeChatbotLambdaEndpoint", {
      value: fnUrl.url,
      exportName: "GriptapeChatbotLambdaEndpoint",
      description: "The endpoint of the Griptape Chatbot Lambda function",
    });
  }
}
