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
        'greeting': 'مرحبًا! يسعدني التحدث معك عن الأنمي والمانغا. ما الأعمال التي تشاهدها أو تقرأها هذه الفترة؟'
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
        'greeting': 'Hey! Nice to meet you. I love talking about anime and manga. What are you watching or reading lately?'
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
        'greeting': 'こんにちは！アニメやマンガの話が大好きです。最近はどんな作品を見たり読んだりしていますか？'
    }
}