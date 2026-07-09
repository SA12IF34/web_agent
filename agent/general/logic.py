from tavily import TavilyClient
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent.parent / '.env')

import os
import json

async def handle_search(query: str):
    
    client = TavilyClient(os.getenv('TAVILY_API_KEY'))
    response = client.search(query, search_depth='advanced', include_answer='advanced')
    answer = response.get('answer', response['results'])

    return answer