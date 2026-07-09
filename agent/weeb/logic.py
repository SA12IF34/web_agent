import requests
from tavily import TavilyClient
from typing import Literal
import os

async def handle_get_entry_details(entry_type: Literal['anime', 'manga'], entry_id: str):
    try:
        response = requests.get(f"https://api.jikan.moe/v4/{entry_type}/{entry_id}")

        status = response.status_code
        if status == 200:
            data = response.json()['data']

            return {
                'mal_id': data.get('mal_id'),
                "titles": data.get('titles'),
                'score': data.get('score'),
                'status': data.get('status'),
                'synopsis': data.get('synopsis')
            }

    except Exception as exc:
        print("Errort at handle_get_entry_details ", str(exc))

        return "Could not retrieve anime details"
    

async def handle_get_anime_episode_details(anime_name: str, episode_number: int):
    try:
        client = TavilyClient(os.getenv('TAVILY_API_KEY'))
        response = client.search(
            query=f"What happend in the anime {anime_name} episode {episode_number}?",
            include_answer="advanced",
            search_depth="advanced"
        )

        answer = response.get('answer')

        return answer if answer else response.get('results')[0]

    except Exception as exc:
        print('Error at handle_get_anime_episode_details ', str(exc))

        return 'Could not retrieve episode details'
    

async def handle_search_entry(entry_type: Literal['anime', 'manga'], entry_name: str):
    try:
        response = requests.get(f'https:api.jikan.moe/v4/{entry_type}?q={entry_name}')

        if response.status_code == 200:
            data = response.json()

            if data.get('data') and len(data['data']) > 0:
                entry = data['data'][0]

                return {
                    "mal_id": entry.get('mal_id'),
                    "titles": entry.get('titles'),
                    "type":entry.get('type'),
                    "status": entry.get('status'),
                    "score": entry.get('score'),
                    "synopsis": entry.get('synopsis')
                }
            
        return 'Could not retrieve details about the entry ' + entry_name

    except Exception  as exc:
        print('Error at handle_search_entry ', str(exc))

        return 'Could not retrieve details about the entry ' + entry_name
    