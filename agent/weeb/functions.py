from deepgram.types import ThinkSettingsV1FunctionsItem
from .logic import handle_get_entry_details, handle_get_anime_episode_details, handle_search_entry


async def get_entry_details(params):
    """Get anime or manga details"""

    entry_type = params.get('entry_type', None)
    entry_id = params.get('entry_id', None)

    if not entry_type or not entry_id:
        return "You must specify the entry type and id"
    
    result = await handle_get_entry_details(entry_type, entry_id)

    return result

async def get_anime_episode_details(params):
    "Get details of what happend in a specific anime episode"

    anime_name = params.get('anime_name')
    episode_number = params.get('episode_number')

    if not anime_name or not episode_number:
        return "You must provide both the anime name and episode number"
    
    result = await handle_get_anime_episode_details(anime_name, episode_number)

    return result

async def search_entry(params):
    "Search for specific anime or manga entry by name"

    entry_type = params.get('entry_type')
    entry_name = params.get('entry_name')

    if not entry_type or not entry_name:
        return 'You must provide both entry type and name'
    
    result = await handle_search_entry(entry_type, entry_name)

    return result


FUNCTIONS = [
    ThinkSettingsV1FunctionsItem(
        name="get_entry_details",
        description="""Get anime or manga details by using he MyAnimeList id of the entry.
        Use this function when:
        - You want to get more details of certain entry and you know the MAL id of that entry, otherwise use search_entry function instead
        
        How to use this function:
        - You call the function with the entry type as "manga" or "anime" and the entry MAL id as "<entry id>" specified.
        
        You must call this function scilently, you must not tell the user that you will get the entry details.
        NEVER EVER MAKE UP THE MAL ID, if you don't know it, then use the search_entry function.""",
        parameters={
            "type": "object",
            "properties": {
                "entry_type": {
                    "type": "string",
                    "description": "The entry type represented as anime or manga",
                    "enum": ['anime', 'manga']
                },
                "entry_id": {
                    "type": "string",
                    "description": """The MyAnimeList id of the entry represented as digit string (e.g. "1657"), DO NOT MAKE UP THE MAL ID OF THE ENTRY"""
                }
            },
            "required": ["entry_type", "entry_id"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="get_anime_episode_details",
        description="""Get anime episode details by provide the anime title and episode number.
        When to call this function:
        - When the user starts talking about certain episode of some anime, so you can engage in the discussion give the user a good experience
        - When you need to know more details about specific anime or anime episode
        
        How to use this function:
        - You specify the anime title (including the season or part if there are more than one) and episode number (as integer string e.g. "3")
        - When you call this function with the specified parameters, You will get a details description of what happened in that episode.
        
        You must call this function scilently, the user must not know that you are calling this function.
        You must make sure that this information you get is as you already know it.""",
        parameters={
            "type": "object",
            "properties": {
                "anime_name": {
                    "type": "string",
                    "description": """The title of the anime including the specific season or part (e.g. "Attack on Titan Season 4")"""
                },
                "episode_number": {
                    "type": "string",
                    "description": """A digit representing the episode number (e.g. "2")"""
                }
            },
            "required": ["anime_name", "episode_number"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="search_entry",
        description="""Search for the anime or manga details by providing it's title and type ("anime" or "manga").
        When to call this function:
        - When you need to know the details of specific anime or manga but you don't know the MAL id
        - The user asks you about some anime or manga or wants to know more about it

        How to use this function:
        - You call this function and provide the entry type and name (entry title)
        - When you call this function and receive the result, you can engage with the use in the discussion or tell them about the entry

        You must call this function scilently, the user must not know that you are calling this function.
        """,
        parameters= {
            "type": "object",
            "properties": {
                "entry_type": {
                    "type": "string",
                    "description": """The entry type represented as anime or manga""",
                    "enum": ['anime', 'manga']
                },
                "entry_name": {
                    "type": "string",
                    "description": "The entry title either in English or Romaji."
                }
            },
            "required": ["entry_type", "entry_name"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name='end_call',
        description="""End current conversation gracefully and in friendly way.
        When to call this function:
        - The user expressed they want to end (e.g. "Thank you for today", "This was fun", "I have to go", "bye")
        
        How to use this function:
        - When you decide to end the conversation, specify the farewell phrase and call this function with it
        - The farewell phrase will be sent to the user and the conversation will end gracefully
        
        You must call this function when you end the conversation, do not farewell the user, but call this function instead.""",
        parameters={
            "type": "object",
            "properties": {
                "farewell": {
                    "type": "string",
                    "description": """The farewell phrase to be used before ending the call. must be simple and straightforward."""
                }
            },
            "required": ["farewell"]
        }
    )
]

FUNCTIONS_MAP = {
    'get_entry_details': get_entry_details,
    'get_anime_episode_details': get_anime_episode_details,
    'search_entry': search_entry
}