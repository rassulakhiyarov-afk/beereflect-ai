# BeeReflect AI

BeeReflect AI turns ambient wearable voice notes into a supportive stress check-in and a prioritized, editable task list. It is a hackathon prototype for the Bee Wearable AI Track, AWS Builder Mini-Challenge, and Open Source Mini Challenge.

## Architecture

**Streamlit UI / Bee Voice Input -> Amazon Nova 2 Sonic Transcription -> Amazon Nova 2 Lite Analysis -> Pydantic Validation -> Dashboard Output**

- **Audio transcription:** Amazon Nova 2 Sonic (`us.amazon.nova-2-sonic-v1:0`) transcribes browser voice recordings through AWS Bedrock Runtime's Converse API.
- **Stress analysis and task extraction:** Amazon Nova 2 Lite (`us.amazon.nova-2-lite-v1:0`) analyzes the transcript for stress reflections and practical follow-up tasks.
- **Quota/regional fallback:** Amazon Nova Lite (`us.amazon.nova-lite-v1:0`) is used as the analysis fallback. When daily quota throttling prevents inference, the app can return a structured sample payload so the dashboard remains usable.
- **Validation and output:** Pydantic validates the analysis response before the Streamlit dashboard displays the stress summary, recommendation, and task list.

You can provide audio through Bee voice input/browser recording, choose a sample transcript, or enter text directly. Audio and transcripts are processed using the configured AWS Bedrock models. The stress reflection is supportive and is not a medical assessment.

## Setup & Reproducible Testing Instructions

Use Python 3.11 or newer. Live inference requires AWS credentials with access to the Bedrock models and inference profiles listed above.

1. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

2. Activate it:

   ```powershell
   .\.venv\Scripts\activate
   ```

   On macOS or Linux, use `source .venv/bin/activate`.

3. Install the project dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create a local `.env` file in the project root and configure AWS credentials:

   ```dotenv
   AWS_ACCESS_KEY_ID=your-access-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-access-key
   AWS_DEFAULT_REGION=us-east-1
   ```

   Keep `.env` local; it is excluded from Git. You can also configure credentials through the standard AWS credential provider chain.

5. Start the application:

   ```powershell
   streamlit run main.py
   ```

In the dashboard, record or select a voice log and process it with Bedrock. Without live Bedrock access, sample transcript selection is available, but AWS credentials and model access are required for live analysis. A Bedrock quota throttle uses the app's structured sample analysis payload.

## License

BeeReflect AI is distributed under the [MIT License](./LICENSE).
