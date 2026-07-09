from deepgram import AsyncDeepgramClient
from deepgram.agent.v1.types import AgentV1Settings, AgentV1SettingsAgent, AgentV1FunctionCallRequest, AgentV1SendFunctionCallResponse

from agent.general.config import SETTINGS as GENERAL_SETTINGS
from agent.general.functions import FUNCTIONS as GENERAL_FUNCTIONS, FUNCTIONS_MAP as GENERAL_FUNCTIONS_MAP
from agent.weeb.config import SETTINGS as WEEB_SETTINGS
from agent.weeb.functions import FUNCTIONS as WEEB_FUNCTIONS, FUNCTIONS_MAP as WEEB_FUNCTIONS_MAP
from agent.support.config import SETTINGS as SUPPORT_SETTINGS
from agent.support.functions import FUNCTIONS as SUPPORT_FUNCTIONS, FUNCTIONS_MAP as SUPPORT_FUNCTIONS_MAP
from agent.config import AUDIO_SETTINGS

import asyncio
import json
import asyncio
import traceback
import datetime
from fastapi import WebSocket, WebSocketDisconnect

from typing import Literal, Any

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')
import os

class Agent:

    def __init__(self, websocket: WebSocket):
        
        self.ws = websocket

        self.audio_queue = asyncio.Queue()

        self.loop = None

        self.deepgram_client = None
        self.agent_context = None
        self.agent_conn = None
        self.listen_task = None

        self.functions = None
        self.funcitons_map = None
        self.prompt = None

        self.is_running = False

        self.settings = None
        
    def set_loop(self, loop):
        self.loop = loop

    async def connect(self, mode, language):
        if not self.is_running:

            match mode:
                case 'general':
                    self.functions = GENERAL_FUNCTIONS
                    self.functions_map = GENERAL_FUNCTIONS_MAP
                    self.settings = AgentV1Settings(
                        audio=GENERAL_SETTINGS[language].get('audio') or AUDIO_SETTINGS, 
                        agent=AgentV1SettingsAgent(
                            language=language,
                            listen=GENERAL_SETTINGS[language]['listen'],
                            think=GENERAL_SETTINGS[language]['think'],
                            speak=GENERAL_SETTINGS[language]['speak'],
                            greeting=GENERAL_SETTINGS[language]['greeting']
                        ),
                    )

                case 'weeb':
                    self.functions = WEEB_FUNCTIONS
                    self.functions_map = WEEB_FUNCTIONS_MAP
                    self.settings = AgentV1Settings(
                        audio=WEEB_SETTINGS[language].get('audio') or AUDIO_SETTINGS,
                        agent=AgentV1SettingsAgent(
                            language=language,
                            listen=WEEB_SETTINGS[language]['listen'],
                            think=WEEB_SETTINGS[language]['think'],
                            speak=WEEB_SETTINGS[language]['speak'],
                            greeting=WEEB_SETTINGS[language]['greeting']
                        )
                    )

                case 'support':
                    self.functions = SUPPORT_FUNCTIONS
                    self.functions_map = SUPPORT_FUNCTIONS_MAP
                    self.settings = AgentV1Settings(
                        audio=SUPPORT_SETTINGS[language].get('audio') or AUDIO_SETTINGS,
                        agent=AgentV1SettingsAgent(
                            language=language,
                            listen=SUPPORT_SETTINGS[language]['listen'],
                            think=SUPPORT_SETTINGS[language]['think'],
                            speak=SUPPORT_SETTINGS[language]['speak'],
                            greeting=SUPPORT_SETTINGS[language]['greeting']
                        )
                    )

                case _:
                    self.funcitons = GENERAL_FUNCTIONS
                    self.funcitons_map = GENERAL_FUNCTIONS_MAP
                    self.settings = AgentV1Settings(
                        audio=GENERAL_SETTINGS[language].get('audio', False) or AUDIO_SETTINGS, 
                        agent=AgentV1SettingsAgent(
                            language=language,
                            listen=GENERAL_SETTINGS[language]['listen'],
                            think=GENERAL_SETTINGS[language]['think'],
                            speak=GENERAL_SETTINGS[language]['speak'],
                            greeting=GENERAL_SETTINGS[language]['greeting']

                        )
                    )

            self.deepgram_client = AsyncDeepgramClient(api_key=os.getenv('DEEPGRAM_API_KEY'))

            self.agent_context = self.deepgram_client.agent.v1.connect()
            self.agent_conn = await self.agent_context.__aenter__()


            def on_message(message):
                asyncio.create_task(self.handle_agent_message(message))

            self.agent_conn.on('message', on_message)
            self.agent_conn.on('error', lambda err: print(err))
            self.listen_task = asyncio.create_task(self.agent_conn.start_listening())

            await self.agent_conn.send_settings(self.settings)

            return True
        
        return False

    async def run(self, mode:Literal['general', 'weeb', 'support']='general', language:Literal['en', 'ja', 'ar']='en'):
        try:
            result = await self.connect(mode, language)
            if result:
                self.is_running = True

                await asyncio.gather(
                    self.handle_send_audio(),
                    self.handle_receive_audio()
                )
        except Exception as exc:
            traceback.print_exc()

        finally:
            await self.close()
    
    async def handle_receive_audio(self):
        try:
            while self.is_running:
                data = await self.ws.receive()
                
                if "bytes" in data:
                    await self.audio_queue.put(data['bytes'])

        except (WebSocketDisconnect, RuntimeError):
            await self.close()
        
        except Exception as exc:
            traceback.print_exc()
            await self.close()

    async def handle_send_audio(self):
        try:
            while self.is_running:
                data = await self.audio_queue.get()
                if self.ws and data:
                    await self.agent_conn.send_media(data)

        except Exception as exc:
            traceback.print_exc()

    async def handle_agent_message(self, message):
        
        try:
            
            if isinstance(message, bytes):
                await self.ws.send_bytes(message)
                return
            
            message_type = message.type
            print(message_type)
            if message_type == 'UserStartedSpeaking':
                print('User started Speaking...')


            elif message_type == 'AgentAudioDone':
                await self.ws.send_json({
                    'status': message_type
                })

            elif message_type == 'ConversationText':
                print(f'')

            elif message_type == 'FunctionCallRequest':
                await self.handle_function_call(message)

            elif message_type == 'Welcome':
                print('Welcome...')
            elif message_type == 'Error':
                print(message)
            elif message_type == 'CloseConnection':
                await self.close()


        except Exception as exc:
            print('EXCEPTION')
            traceback.print_exc()

    async def handle_function_call(self, ev: AgentV1FunctionCallRequest):
        
        functions = ev.functions
        if len(functions) > 1:
            raise NotImplementedError('Multiple functions not supported')
        
        function_name = functions[0].name
        function_call_id = functions[0].id
        parameters = json.loads(functions[0].arguments)

        try:
            if function_name == 'end_call':

                await self.end_conversation(parameters.get('farewell', 'Take care.'))
                return
            
            function = self.funcitons_map.get(function_name)
            if not function:
                raise ValueError(f'Function does not exist: {function_name}')
            
            result = await function(parameters)

            response = AgentV1SendFunctionCallResponse(
                id=function_call_id,
                name=function_name,
                content=json.dumps(result)
            )

            await self.agent_conn.send_function_call_response(response)

        except Exception as exc:
            print('EXCEPTION')
            traceback.print_exc()

    async def end_conversation(self, farewell: str):
        pass

    async def cleanup(self):
        if self.listen_task and not self.listen_task.done():
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                print('cancelled')
            self.listen_task = None
        
        self.agent_context = None
        self.agent_conn = None
        self.deepgram_client = None

    async def close(self):
        import websockets
        
        try:
            if self.agent_context:
                await self.agent_context.__aexit__(None, None, None)

        except (websockets.exceptions.ConnectionClosed, websockets.exceptions.ConnectionClosedError):
            print('closed')
        except Exception as exc:
            print('CLOSE EXCEPTION')
            traceback.print_exc()

        await self.cleanup()

        self.is_running = False