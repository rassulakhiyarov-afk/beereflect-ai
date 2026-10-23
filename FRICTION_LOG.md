# BeeReflect AI — AWS Bedrock & Bee CLI Friction Log

This log records onboarding and integration friction encountered while connecting Bee voice input to AWS Bedrock for the hackathon.

## AWS Bedrock

### 1. Promotional credits do not provide inference quota

- **Task Attempted:** Run live analysis with AWS Bedrock using an account with active promotional credits.
- **Steps Taken:** Applied promotional credits, configured AWS credentials, and invoked the analysis model through the Bedrock Converse API.
- **Expected vs. Actual Result:** Expected the credit balance to allow inference. Instead, new-account default service quotas can be 0 tokens per day (TPD) or tokens per minute (TPM), and requests return `ThrottlingException` even when credits are available.
- **Severity Rating:** Critical — blocks live inference and a live demonstration.
- **Workaround Used:** On a primary-model `ThrottlingException`, the app returns a structured sample analysis payload matching the exact analysis JSON schema expected from Bedrock and validated by Pydantic. This preserves dashboard continuity, but does not provide live model analysis.
- **Actionable Suggestion:** Surface quota availability and requestable TPD/TPM limits during Bedrock onboarding, and clearly distinguish promotional billing credits from inference capacity.

### 2. Legacy model IDs and cross-region inference profiles

- **Task Attempted:** Invoke model IDs copied from older tutorials and examples.
- **Steps Taken:** Tried model identifiers directly in Bedrock Converse requests while configuring the current model stack.
- **Expected vs. Actual Result:** Expected a legacy identifier to remain callable or route automatically to a supported version. Deprecated or unavailable model IDs instead fail; supported models may require a US Cross-Region Inference Profile ID in the request.
- **Severity Rating:** High — prevents model invocation until the identifier and access configuration are corrected.
- **Workaround Used:** Configure the active US inference profile IDs: Nova 2 Sonic (`us.amazon.nova-2-sonic-v1:0`) for audio transcription, Nova 2 Lite (`us.amazon.nova-2-lite-v1:0`) for analysis, and Nova Lite (`us.amazon.nova-lite-v1:0`) as the analysis fallback.
- **Actionable Suggestion:** Keep model deprecation notices, supported inference profile IDs, region requirements, and migration guidance together in the Bedrock model catalog and API errors.

### 3. Converse API multimodal `ContentBlock` validation

- **Task Attempted:** Send voice audio and analysis text through the Bedrock Converse API.
- **Steps Taken:** Integrated audio and text content blocks and tested requests against the transcription and analysis models.
- **Expected vs. Actual Result:** Expected content blocks to be interchangeable across models. The API validates each block against the model's supported modalities and returns a `ValidationException` when a request contains an unsupported or malformed block.
- **Severity Rating:** High — malformed or model-incompatible blocks prevent transcription or analysis.
- **Workaround Used:** Keep the stages and payloads model-specific: send supported text-plus-audio blocks to Nova 2 Sonic for transcription, then send the resulting transcript as a text block to Nova 2 Lite for analysis. Validate the returned analysis with Pydantic.
- **Actionable Suggestion:** Include model-specific supported `ContentBlock` types and representative valid payloads in the Converse API documentation and validation errors.

### 4. Marketplace and Bedrock UI onboarding

- **Task Attempted:** Enable Bedrock model access and submit required use-case information in the AWS Console.
- **Steps Taken:** Navigated the Bedrock model catalog, AWS Marketplace subscription views, and the model Playground.
- **Expected vs. Actual Result:** Expected subscription status and required access steps to be visible together. Marketplace product setup and subscription status did not clearly indicate whether all required Bedrock steps were complete; the use-case submission prompt was surfaced from the Playground.
- **Severity Rating:** Moderate — delays setup and makes it difficult to identify the missing onboarding step.
- **Workaround Used:** Opened the relevant model in Playground and followed the use-case submission prompt, then verified access by attempting a Bedrock request.
- **Actionable Suggestion:** Provide one onboarding checklist that shows Marketplace status, use-case submission, model access, region, and quota readiness.

## Bee CLI & Voice Ingestion

### 5. Fragmented ambient logs and timestamp resolution

- **Task Attempted:** Bring ambient voice logs captured through Bee CLI into the Streamlit dashboard for analysis.
- **Steps Taken:** Compared fragmented voice-log output and timestamps with the dashboard's transcript input and processing flow.
- **Expected vs. Actual Result:** Expected a single, ordered transcript with consistent capture timestamps. Ambient ingestion can instead produce partial or fragmented text, and timestamps may need resolution across fragments before the text is useful as one reflection.
- **Severity Rating:** Moderate — fragments can lose context or appear out of order, reducing the quality of analysis.
- **Workaround Used:** Use the dashboard's text/preset input with a manually reviewed, ordered transcript; retain or clarify timestamps in the text when they are relevant. The current dashboard does not automatically merge fragments or reconcile timestamps.
- **Actionable Suggestion:** Provide a Bee CLI transcript-stream contract with stable event IDs, fragment ordering, timezone-aware capture timestamps, and explicit finalization of a voice log.
