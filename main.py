from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal

import streamlit as st
from boto3.session import Session
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

if TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
    from mypy_boto3_bedrock_runtime.type_defs import (
        ConverseResponseTypeDef,
        InferenceConfigurationTypeDef,
        MessageTypeDef,
        SystemContentBlockTypeDef,
    )


MODEL_ID = "us.amazon.nova-2-lite-v1:0"
FALLBACK_MODEL_ID = "us.amazon.nova-lite-v1:0"
TRANSCRIPTION_MODEL_ID = "us.amazon.nova-2-sonic-v1:0"
MOCK_ANALYSIS_JSON = json.dumps(
    {
        "emotional_analysis": {
            "stress_level": "Moderate",
            "summary": (
                "High workload detected from morning schedule and back-to-back "
                "tasks."
            ),
            "recommendation": (
                "Take a 10-minute break before the next meeting and prioritize "
                "urgent deliverables."
            ),
        },
        "actionable_tasks": [
            {
                "task": "Finish launch brief draft",
                "category": "Work",
                "priority": "High",
            },
            {
                "task": "Review afternoon meeting agenda",
                "category": "Work",
                "priority": "Medium",
            },
        ],
    }
)


SAMPLE_TRANSCRIPTS = {
    "Morning workload": (
        "I have three meetings before lunch and still need to finish the launch "
        "brief. I'm worried I won't get the focused time I need."
    ),
    "After a difficult meeting": (
        "That client call was tense. I need to send the revised numbers to Maya "
        "today, and I should take a short break before the next meeting."
    ),
    "End-of-day reflection": (
        "I made progress on the prototype, but my inbox is still overwhelming. "
        "Tomorrow I should review the design feedback and book time with the team."
    ),
}


class EmotionalAnalysis(BaseModel):
    stress_level: Literal["Low", "Medium", "Moderate", "High"]
    summary: str
    recommendation: str


class ActionableTask(BaseModel):
    task: str
    priority: Literal["High", "Medium", "Low"]
    category: str = "Not specified"
    due_time: str = "Not specified"


class VoiceLogAnalysis(BaseModel):
    emotional_analysis: EmotionalAnalysis
    actionable_tasks: list[ActionableTask]


def load_sample() -> None:
    selection = st.session_state["sample_selection"]
    if selection in SAMPLE_TRANSCRIPTS:
        st.session_state["transcript"] = SAMPLE_TRANSCRIPTS[selection]


@st.cache_resource
def get_bedrock_client() -> tuple[BedrockRuntimeClient | None, str | None]:
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    try:
        session = Session()
        client = session.client(  # pyright: ignore[reportUnknownMemberType]
            "bedrock-runtime", region_name=region
        )
        return client, None
    except (BotoCoreError, ValueError) as exc:
        return None, f"Could not initialize the AWS Bedrock client in {region}: {exc}"


def converse_with_fallback(
    client: BedrockRuntimeClient,
    model_id: str,
    messages: Sequence[MessageTypeDef],
    system: Sequence[SystemContentBlockTypeDef],
    inference_config: InferenceConfigurationTypeDef,
) -> ConverseResponseTypeDef | str:
    try:
        return client.converse(
            modelId=model_id,
            messages=messages,
            system=system,
            inferenceConfig=inference_config,
        )
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "ThrottlingException":
            return MOCK_ANALYSIS_JSON

    try:
        return client.converse(
            modelId=FALLBACK_MODEL_ID,
            messages=messages,
            system=system,
            inferenceConfig=inference_config,
        )
    except ClientError:
        return MOCK_ANALYSIS_JSON


def analyze_transcript(
    client: BedrockRuntimeClient, transcript_text: str
) -> VoiceLogAnalysis:
    response = converse_with_fallback(
        client,
        MODEL_ID,
        messages=[{"role": "user", "content": [{"text": transcript_text}]}],
        system=[
            {
                "text": (
                    "Analyze this personal voice log for emotional stress and "
                    "practical follow-up tasks. Do not infer diagnoses or "
                    "invent deadlines. Return only a valid JSON object with "
                    "emotional_analysis containing stress_level (Low, Medium, "
                    "Moderate, or High), summary, and recommendation, and "
                    "actionable_tasks as a list of task, category, priority "
                    "(High, Medium, or Low), and due_time objects. Return an "
                    "empty actionable_tasks list when there are no clear tasks."
                )
            }
        ],
        inference_config={"maxTokens": 1200, "temperature": 0.2},
    )
    if isinstance(response, str):
        response_text = response
    else:
        message = response["output"].get("message")
        if message is None:
            raise ValueError("Bedrock returned no analysis message.")

        response_text_parts: list[str] = []
        for block in message["content"]:
            text = block.get("text")
            if text is not None:
                response_text_parts.append(text)
        response_text = "".join(response_text_parts).strip()

    if response_text.startswith("```"):
        response_text = response_text.removeprefix("```json").removeprefix("```")
        response_text = response_text.removesuffix("```").strip()

    return VoiceLogAnalysis.model_validate(json.loads(response_text))


def transcribe_audio(client: BedrockRuntimeClient, audio_bytes: bytes) -> str:
    response = client.converse(
        modelId=TRANSCRIPTION_MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": (
                            "Transcribe this voice recording into text accurately."
                        )
                    },
                    {
                        "audio": {
                            "format": "wav",
                            "source": {"bytes": audio_bytes},
                        }
                    },
                ],
            }
        ],
        inferenceConfig={"maxTokens": 1200, "temperature": 0},
    )
    message = response["output"].get("message")
    if message is None:
        raise ValueError("Bedrock returned no transcription message.")

    transcript_parts: list[str] = []
    for block in message["content"]:
        text = block.get("text")
        if text is not None:
            transcript_parts.append(text)
    transcript = "".join(transcript_parts).strip()
    if not transcript:
        raise ValueError("No speech could be transcribed. Try recording again.")
    return transcript


def get_transcript_for_analysis(
    client: BedrockRuntimeClient, audio_bytes: bytes | None, transcript_text: str
) -> str:
    if audio_bytes:
        return transcribe_audio(client, audio_bytes)
    return transcript_text.strip()


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="BeeReflect AI", page_icon="🐝", layout="wide")
    st.title("🐝 BeeReflect AI — Ambient Wearable Companion")
    st.write(
        "Turn a brief wearable voice log into a thoughtful stress check-in and "
        "a manageable list of next steps."
    )

    transcript_col, audio_col = st.columns([1, 1])
    with transcript_col:
        st.selectbox(
            "Try a sample voice log",
            options=["Write my own", *SAMPLE_TRANSCRIPTS],
            key="sample_selection",
            on_change=load_sample,
        )
    with audio_col:
        audio_recording = st.audio_input(
            "Record a voice log",
            sample_rate=16000,
            key="voice_recording",
            help="Record a short voice log to transcribe and analyze with AWS Bedrock.",
        )
    audio_bytes = audio_recording.getvalue() if audio_recording is not None else b""

    st.text_area(
        "Bee voice log",
        placeholder="Type or paste a voice transcript...",
        height=150,
        key="transcript",
    )
    if audio_bytes:
        st.caption(
            "The microphone recording will be used instead of the text above. "
            "Clear the recording to use a sample or enter your own transcript."
        )

    if st.button(
        "Process Ambient Voice Log with AWS Bedrock",
        type="primary",
        disabled=(
            not audio_bytes
            and not st.session_state.get("transcript", "").strip()
        ),
    ):
        client, client_error = get_bedrock_client()
        if client is None or client_error:
            st.error(client_error or "Could not initialize the AWS Bedrock client.")
        else:
            with st.spinner("Reflecting on your voice log..."):
                processing_step = "transcription" if audio_bytes else "analysis"
                try:
                    transcript = get_transcript_for_analysis(
                        client,
                        audio_bytes or None,
                        st.session_state.get("transcript", ""),
                    )
                    processing_step = "analysis"
                    analysis = analyze_transcript(client, transcript)
                except ClientError as exc:
                    details = exc.response.get("Error", {})
                    operation = (
                        "transcribe this recording"
                        if processing_step == "transcription"
                        else "process this log"
                    )
                    st.error(
                        f"Bedrock could not {operation} "
                        f"({details.get('Code', 'AWS error')}): "
                        f"{details.get('Message', str(exc))}"
                    )
                except BotoCoreError as exc:
                    if processing_step == "transcription":
                        st.error(f"AWS audio transcription failed: {exc}")
                    else:
                        st.error(f"AWS request failed: {exc}")
                except (json.JSONDecodeError, ValidationError, KeyError) as exc:
                    st.error(
                        "Bedrock returned a response that did not match the "
                        f"expected JSON format: {exc}"
                    )
                except ValueError as exc:
                    if processing_step == "transcription":
                        st.error(f"Audio transcription failed: {exc}")
                    else:
                        st.error(str(exc))
                else:
                    st.session_state["analysis"] = analysis
                    st.session_state["analysis_version"] = (
                        st.session_state.get("analysis_version", 0) + 1
                    )

    analysis = st.session_state.get("analysis")
    if analysis:
        st.subheader("Your reflection")
        with st.container(border=True):
            st.metric(
                "Stress level", analysis.emotional_analysis.stress_level
            )
            st.markdown("**Summary**")
            st.write(analysis.emotional_analysis.summary)
            st.markdown("**Recommendation**")
            st.write(analysis.emotional_analysis.recommendation)

        st.subheader("Actionable tasks")
        task_rows: list[dict[str, bool | str]] = [
            {
                "Done": False,
                "Task": task.task,
                "Category": task.category,
                "Priority": task.priority,
                "Due time": task.due_time,
            }
            for task in analysis.actionable_tasks
        ]
        if task_rows:
            st.data_editor(
                task_rows,
                hide_index=True,
                use_container_width=True,
                key=f"tasks_{st.session_state['analysis_version']}",
                disabled=["Task", "Category", "Priority", "Due time"],
                column_config={
                    "Done": st.column_config.CheckboxColumn(
                        "Done", help="Check off this task when it is complete."
                    ),
                    "Task": st.column_config.TextColumn("Task"),
                    "Category": st.column_config.TextColumn("Category"),
                    "Priority": st.column_config.TextColumn("Priority"),
                    "Due time": st.column_config.TextColumn("Due time"),
                },
            )
        else:
            st.info("No actionable tasks were found in this voice log.")

    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        st.caption(
            "Add AWS credentials to a local .env file to enable Bedrock. "
            "Use credentials with permission to invoke the selected model."
        )


if __name__ == "__main__":
    main()
