from deepgram.agent.v1.types import (
    AgentV1SettingsAgentListen,
    AgentV1SettingsAgentListenProvider_V1,
    AgentV1SettingsAudio,
    AgentV1SettingsAudioInput,
    AgentV1SettingsAudioOutput
)
from deepgram.types import (
    ThinkSettingsV1,
    ThinkSettingsV1Provider_OpenAi,
    SpeakSettingsV1,
    SpeakSettingsV1Provider_OpenAi,
    SpeakSettingsV1Endpoint,
    SpeakSettingsV1Provider_Deepgram
)

from .prompt import SYSTEM_PROMPT_AR, SYSTEM_PROMPT, SYSTEM_PROMPT_JA
from .functions import FUNCTIONS

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent.parent / '.env')

import os

SETTINGS = {
    'ar': {
        'audio': AgentV1SettingsAudio(
            input=AgentV1SettingsAudioInput(
                encoding="linear16",
                sample_rate=24000
            ),
            output=AgentV1SettingsAudioOutput(
                encoding="linear16",
                sample_rate=24000
            )
        ),
        'listen': AgentV1SettingsAgentListen(
            provider=AgentV1SettingsAgentListenProvider_V1(
                language='ar',
                type="deepgram",
                model="nova-3",
                keyterms=["hello", "goodbye", "bye"]
            )
        ),
        'think': ThinkSettingsV1(
            provider=ThinkSettingsV1Provider_OpenAi(
                model="gpt-4o-mini",
                temperature=0.2,
            ),
            prompt=SYSTEM_PROMPT_AR,
            functions=FUNCTIONS
        ),
        'speak': SpeakSettingsV1(
            provider=SpeakSettingsV1Provider_OpenAi(
                model='tts-1',
                voice='fable',
            ),
            endpoint=SpeakSettingsV1Endpoint(
                url="https://api.openai.com/v1/audio/speech",
                headers= {
                    "authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
                }
            )
        ),
        'greeting': 'مرحبًا، أنا خالد من فريق دعم Tech. كيف يمكنني مساعدتك اليوم؟'
    },
    'en': {
        'listen': AgentV1SettingsAgentListen(
            provider=AgentV1SettingsAgentListenProvider_V1(
                language='en',
                type="deepgram",
                model="nova-3",
            )
        ),
        'think': ThinkSettingsV1(
            provider=ThinkSettingsV1Provider_OpenAi(
                model="gpt-4o-mini",
                temperature=0.2,
            ),
            prompt=SYSTEM_PROMPT,
            functions=FUNCTIONS
        ),
        'speak': SpeakSettingsV1(
            provider=SpeakSettingsV1Provider_Deepgram(
                model="aura-2-thalia-en"
            )
        ),
        'greeting': 'Hello, I’m Scarlett from Tech support. How can I assist you today?'
    },
    'ja': {
        'listen': AgentV1SettingsAgentListen(
            provider=AgentV1SettingsAgentListenProvider_V1(
                language='ja',
                type="deepgram",
                model="nova-3",
            )
        ),
        'think': ThinkSettingsV1(
            provider=ThinkSettingsV1Provider_OpenAi(
                model="gpt-4o-mini",
                temperature=0.2,
            ),
            prompt=SYSTEM_PROMPT_JA,
            functions=FUNCTIONS
        ),
        'speak': SpeakSettingsV1(
            provider=SpeakSettingsV1Provider_Deepgram(
                model="aura-2-fujin-ja"
            )
        ),
        'greeting': 'こんにちは、Techサポート担当の直樹です。本日はどのようなご用件でしょうか？'
    }
}