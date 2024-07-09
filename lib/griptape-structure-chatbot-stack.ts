import { Stack, StackProps, Tags } from "aws-cdk-lib";
import { Construct } from "constructs";
import { GriptapeStructureChatbot } from "./constructs/griptape-structure-chatbot";

export class GriptapeStructureChatbotStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const griptapeStructureChatbot = new GriptapeStructureChatbot(
      this,
      "GriptapeStructureChatbot"
    );
    Tags.of(griptapeStructureChatbot).add(
      "created-by",
      "griptape-structure-chatbot"
    );
  }
}
