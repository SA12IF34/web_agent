from deepgram.agent.v1.types import (
    AgentV1SettingsAgent,
    AgentV1SettingsAudio,
    AgentV1SettingsAudioInput,
    AgentV1SettingsAudioOutput,
    AgentV1SettingsAgentListen,
    AgentV1SettingsAgentListenProvider_V1,
    AgentV1FunctionCallRequest,
    AgentV1SendFunctionCallResponse,
    AgentV1InjectAgentMessage,
    AgentV1Settings
)

from deepgram.types import (
    ThinkSettingsV1,
    ThinkSettingsV1Provider_OpenAi,
    SpeakSettingsV1,
    SpeakSettingsV1Provider_Deepgram
)

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / '.env')


AUDIO_SETTINGS = AgentV1SettingsAudio(
    input=AgentV1SettingsAudioInput(
        encoding="linear16",
        sample_rate=16000
    ),
    output=AgentV1SettingsAudioOutput(
        encoding="linear16",
        sample_rate=16000
    )
)


SETTINGS = AgentV1Settings(
    audio=AgentV1SettingsAudio(
        input=AgentV1SettingsAudioInput(
            encoding="linear16",
            sample_rate=24000
        ),
        output=AgentV1SettingsAudioOutput(
            encoding="linear16",
            sample_rate=24000,
            container=None
        )
    ),
    agent=AgentV1SettingsAgent(
        language="en",
        listen=AgentV1SettingsAgentListen(
            provider=AgentV1SettingsAgentListenProvider_V1(
                type="deepgram",
                model="nova-3",
                keyterms=["hello", "goodbye", "bye"]
            )
        ),
        think=ThinkSettingsV1(
            provider=ThinkSettingsV1Provider_OpenAi(
                model="gpt-4o-mini",
                temperature=0.7
            ),
        ),
        speak=SpeakSettingsV1(
            provider=SpeakSettingsV1Provider_Deepgram(
                model="aura-2-thalia-en"
            )
        ),
        greeting="Hello"
    ),
)