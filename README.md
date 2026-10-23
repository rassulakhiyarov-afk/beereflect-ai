# BeeReflect AI

**BeeReflect AI turns ambient wearable voice notes into a gentle stress
check-in and a prioritized, editable task list.** It is a hackathon prototype
for the Bee Wearable AI Track and AWS Builder Mini-Challenge, designed to make
everyday reflections easier to act on.

## Architecture

1. A voice log is recorded in the browser, selected from the samples, or
   entered as text in the Streamlit dashboard.
2. Browser recordings are transcribed by Amazon Nova 2 Lite through AWS
   Bedrock Runtime's `converse` API.
3. The resulting transcript is analyzed by Anthropic Claude Haiku 5.5 through
   Bedrock's `converse` API, with Claude Sonnet 5.5 as the fallback if the
   primary model returns a Bedrock client error.
4. Pydantic validates the returned emotional analysis and tasks before the
   dashboard renders a stress summary, recommendation, and checkable task
   table.

Audio recordings and transcripts are sent to the configured AWS Bedrock
models. The stress reflection is supportive and is not a medical assessment.

## Setup

Requires Python 3.11 or newer and AWS credentials authorized to invoke both
Bedrock models in your chosen region.

1. Create and activate a virtual environment.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a local `.env` file in the project directory:

   ```dotenv
   AWS_ACCESS_KEY_ID=your-access-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-access-key
   AWS_DEFAULT_REGION=us-east-1
   ```

   Do not commit `.env` or share its credentials. Alternatively, configure
   credentials through the standard AWS credential provider chain.

4. Start the dashboard:

   ```powershell
   streamlit run main.py
   ```

Record a voice log, choose one of the sample logs, or enter a transcript, then
select **Process Ambient Voice Log with AWS Bedrock**. A recording takes
precedence over text until it is cleared. In `us-east-1`, the app uses the
`us.amazon.nova-2-lite-v1:0` inference profile for transcription,
`us.anthropic.claude-haiku-5-5` for analysis, and
`us.anthropic.claude-sonnet-5-5` as fallback. Ensure these profiles are
available to your account.
