#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { GriptapeStructureChatbotStack } from "../lib/griptape-structure-chatbot-stack";

const app = new cdk.App();
new GriptapeStructureChatbotStack(app, "GriptapeStructureChatbotStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  stackName: "GriptapeStructureChatbotStack",
});
