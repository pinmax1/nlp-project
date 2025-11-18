from typing import Dict, List, Optional
import requests
from api.kernel import Server
def example_tool(
    string_param: str,
    number_param: float,
    integer_param: Optional[int] = None,
    boolean_param: Optional[bool] = None,
    simple_array: Optional[List[str]] = None,
    object_array: Optional[List[Dict]] = None,
    nested_object: Optional[Dict] = None,
    mixed_array: Optional[List] = None,
    optional_param: str = "default_value",
) -> str:
    result = f"""
Параметры функции:
- string_param: {string_param}
- number_param: {number_param}
- integer_param: {integer_param}
- boolean_param: {boolean_param}
- simple_array: {simple_array}
- object_array: {object_array}
- nested_object: {nested_object}
- mixed_array: {mixed_array}
- optional_param: {optional_param}
"""
    return result.strip()

def steam_search_tool(game_name):
    url = "https://store.steampowered.com/api/storesearch/"
    params = {
        "term": game_name,
        "l": "english",
        "cc": "US"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return [game['name'] for game in data['items'][:5]]

def steam_search_by_desc_tool(desc):
    return Server.steamdb_manager.find_similar_games(desc, k=50)
