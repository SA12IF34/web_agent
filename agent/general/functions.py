from deepgram.types import ThinkSettingsV1FunctionsItem
from typing import Any
from .logic import handle_search

async def search(params: dict[str, Any]):
    """Search the world wide web"""
    query = params.get('query')

    if query is None:
        return "Please specify search query."
    
    result = await handle_search(query)

    return result


FUNCTIONS = [
    ThinkSettingsV1FunctionsItem(
        name='search',
        description="""A function used to search for things on the Web.
        Use this function when:
        - The user asks you to search for something
        - You don't no the answer for the user request or question
        - You need up-to-date information
        
        How to use this function:
        - Determine your query to use for the search
        - The, call the function with the determined query""",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """query to be used in the search process (e.g "What is the whether now", "Letest released games")"""
                }
            },
            "required": ["query"]
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
    "search": search
}