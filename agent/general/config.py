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
                temperature=0.7,
            ),
            prompt=SYSTEM_PROMPT_AR,
            functions=FUNCTIONS
        ),
        'speak': SpeakSettingsV1(
            provider=SpeakSettingsV1Provider_OpenAi(
                model='gpt-4o-mini-tts',
                voice='fable',
            ),
            endpoint=SpeakSettingsV1Endpoint(
                url="https://api.openai.com/v1/audio/speech",
                headers= {
                    "authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
                }
            )
        ),
        'greeting': 'أهلًا بك، يسعدني التحدث معك. ما الذي ترغب في الحديث عنه اليوم؟'
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
                temperature=0.7,
            ),
            prompt=SYSTEM_PROMPT,
            functions=FUNCTIONS
        ),
        'speak': SpeakSettingsV1(
            provider=SpeakSettingsV1Provider_Deepgram(
                model="aura-2-thalia-en"
            )
        ),
        'greeting': 'Hey, nice to talk with you. What would you like to chat about?'
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
                temperature=0.7,
            ),
            prompt=SYSTEM_PROMPT_JA,
            functions=FUNCTIONS
        ),
        'speak': SpeakSettingsV1(
            provider=SpeakSettingsV1Provider_Deepgram(
                model="aura-2-fujin-ja"
            )
        ),
        'greeting': 'こんにちは、お話できてうれしいです。今日はどんなことについて話しましょうか？'
    }
}