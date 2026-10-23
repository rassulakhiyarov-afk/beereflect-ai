# BeeReflect AI — AWS & Bee CLI Integration Friction Log

> **Developer Feedback for Amazon & Devpost Judges**
> This log documents real technical friction, service quota bottlenecks, and API schema edge cases encountered while building BeeReflect AI on AWS Bedrock and Bee CLI during the hackathon window.

---

## 1. AWS Bedrock Onboarding & Quotas

### Entry 1.1: Promotional Credits vs. Default Service Quotas (TPD/TPM)
* **Task Attempted:** Executing real-time inference via Bedrock `converse()` using a granted $250 promotional credit balance.
* **Steps Taken:** Activated promo credits in AWS Billing, submitted Anthropic Use Case details, and sent text prompts via `boto3`.
* **Expected Result:** Immediate API execution funded by the active credit grant.
* **Actual Result:** `ThrottlingException: Too many tokens per day, please wait before trying again`. New accounts default to 0 Tokens Per Day (TPD) for third-party models despite active credits.
* **Severity Rating:** **CRITICAL** (Completely blocks live demonstration under tight hackathon deadlines).
* **Workaround Used:** Implemented an explicit fallback handler in `main.py` catching `botocore.exceptions.ClientError`. Upon encountering `ThrottlingException`, the application gracefully catches the error and serves a structured sample JSON matching Bedrock's exact schema to ensure uninterrupted UI demonstration for judges.
* **Actionable Suggestion:** Automatically elevate default TPD/TPM Service Quotas for developer accounts whenever an official AWS hackathon credit code is redeemed.

---

### Entry 1.2: Model Version Deprecation & Inference Profile Naming
* **Task Attempted:** Invoking standard Claude model IDs listed in legacy tutorials and documentation.
* **Steps Taken:** Passed `modelId="anthropic.claude-3-haiku-20240307-v1:0"` directly to `boto3`.
* **Expected Result:** Model invocation or automatic routing to the latest active patch version.
* **Actual Result:** `botocore.errorfactory.ResourceNotFoundException: This model version has reached the end of its life`.
* **Severity Rating:** **HIGH**
* **Workaround Used:** Updated model constants in `main.py` to active US Cross-Region Inference Profiles (`us.anthropic.claude-3-5-haiku-20241022-v1:0`, `us.amazon.nova-2-lite-v1:0`).
* **Actionable Suggestion:** Add auto-redirection in `boto3` for deprecated model IDs to active Cross-Region Inference Profiles with a clear SDK deprecation warning rather than dropping the request.

---

### Entry 1.3: Multi-modal ContentBlock Validation in Converse API
* **Task Attempted:** Sending audio bytes directly alongside text prompts in a unified Converse API payload.
* **Steps Taken:** Appended an `audio` block to `messages[0].content` when triggering Claude analysis.
* **Expected Result:** Multi-modal models accept or gracefully ignore non-supported content blocks.
* **Actual Result:** `ValidationException: ContentBlock object at messages.0.content.1 must set one of the following keys: text, image...`.
* **Severity Rating:** **HIGH**
* **Workaround Used:** Architected a strict two-stage pipeline: audio recordings go exclusively to `us.amazon.nova-2-lite-v1:0` for transcription. The output text string is cleaned before being sent to Claude in a single-element text-only block.
* **Actionable Suggestion:** Improve Converse API error messages to explicitly name which models support `audio` blocks, or allow automatic backend stripping/routing of unsupported block types.

---

### Entry 1.4: AWS Marketplace & Bedrock UI Onboarding Ambiguity
* **Task Attempted:** Enabling Bedrock models via AWS Console.
* **Steps Taken:** Navigated through Bedrock Model Catalog and AWS Marketplace Subscriptions.
* **Expected Result:** A single toggle button to activate model access.
* **Actual Result:** Marketplace UI shows misleading "Set up product" buttons for active serverless subscriptions, while the mandatory "Submit Use Case Details" modal is hidden inside the Playground interface.
* **Severity Rating:** **MODERATE**
* **Workaround Used:** Manually opened Playground for Claude 3.5 Haiku to force the Use Case modal to appear and submit project details.
* **Actionable Suggestion:** Unify Marketplace subscription status, Use Case submission, and Service Quota verification into a single guided Onboarding Wizard inside Amazon Bedrock.

---

## 2. Bee CLI & Wearable Integration Seams

### Entry 2.1: Transcript Ingestion & Export Contracts
* **Task Attempted:** Interfacing dashboard UI directly with ambient audio streams.
* **Steps Taken:** Simulated continuous voice note streams from Bee CLI.
* **Expected Result:** A standardized JSON stdout contract for exported transcripts with precise timestamps.
* **Actual Result:** Ambient streams produce fragmented, partial text notes requiring custom text sanitization.
* **Severity Rating:** **MODERATE**
* **Workaround Used:** Built a flexible text/preset input layer in Streamlit that accepts raw text streams while preserving the original transcript for user verification before extraction.
* **Actionable Suggestion:** Provide an official Bee CLI adapter package that exposes a standardized `transcript_stream` interface with built-in time-zone and capture-timestamp metadata.