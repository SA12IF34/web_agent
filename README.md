<h1 align='center'>Web Based Voice Agent</h1>

## Description
Voice agent that speaks Arabic, English and Japanese and has three modes: 
- General: Casual/daily conversation
- Weeb: Loves anime and manga, likes talking about them, has tools to lookup and discuss anime and manga
- Customer Support: CS representative for technology hardware retail store

## Technical Details
### Agent Infrastructure

Used Deepgram API's to connect TTS, STT, and OpenAI models:

**Arabic**:

TTS: Deepgram Nova 3

Thinker model: OpenAI GPT-4o-mini

STT: OpenAI gpt-4o-mini-tts Fable (Cedar for customer support)

**English**: 

TTS: Deepgram Nova 3

Thinker model: OpenAI GPT-4o-mini

STT: Deepgram Aura

**Japanese**:

TTS: Deepgram Nova 3

Thinker model: OpenAI GPT-4o-mini

STT: Deepgram Fujin

### Interface
Exposed an API with FastAPI to connet to the agent via websockets from a simple frontend page

## Run Locally
### Installation
Install required dependencies (Using virtual env is recommended):
```
pip install -r requirements.txt
```
### Run The application
Simply run it with `python main.py`

***Important***<br>
You can find a function in support agent `logic.py` that runs on running the server to generate data for the agent, make sure to comment it after running the server for the first time 

