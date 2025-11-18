import requests
import json
from tools import ToolsDispatcher
from api.config import ServerConfig
class ModelRequester:
    def __init__(self, tools_dispatcher : ToolsDispatcher, server_config : ServerConfig):
        self.API_TOKEN = server_config.API_TOKEN
        self.URL = server_config.URL
        self.MODEL = server_config.MODEL
        self.logger = server_config.logger_config.get_logger("ModelRequester")
        self.tools_dispatcher = tools_dispatcher
        self.memory = []
        self.tools_limit = 10
        self.model_prompt = (
            "You are an intelligent reasoning agent which must solve the following task with strict discipline.\n\n"
            "You have access to a set of tools (functions).\n"
            "Each tool is described in JSON format below:\n"
            f"{self.tools_dispatcher.tools_config}\n\n"
            "GENERAL OUTPUT RULES:\n"
            "- You must ALWAYS respond with EXACTLY ONE valid JSON object.\n"
            "- The JSON must be returned as a plain text string.\n"
            "- You must NEVER output anything outside the JSON object.\n"
            "- NEVER output markup, commentary, or framework tokens such as:\n"
            "  <|start|>, <|assistant|>, <|system|>, <|channel|>, <|call|>, <|message|>,\n"
            "  'to=tool_name', or any similar routing indicators.\n"
            "- NEVER include fields like 'role', 'metadata', or anything not defined in allowed formats.\n"
            "- NEVER copy or reuse the example model outputs. They are examples ONLY.\n\n"
            "ALLOWED OUTPUT FORMATS:\n"
            "1) When calling a tool:\n"
            "{\"function\": \"function_name\", \"arguments\": { ... }}\n\n"
            "2) When returning the final user-facing answer:\n"
            "{\"text\": \"your final answer to the user\"}\n\n"
            "TASK ALGORITHM:\n"
            "1. You will receive a user query containing a game description or a name of a game.\n"
            "2. Extract and generate a detailed description of the game and tag list relevant to user query.\n"
            "   - Tags must be directly relevant to the user’s query.\n"
            "   - DO NOT copy tags from examples.\n"
            "3. If you are not SURE that you can answer query, then call the tool 'steam_search_by_desc_tool' using ONLY this format:\n"
            "   {\"function\": \"steam_search_by_desc_tool\", \"arguments\": {\"desc\": \"tag1, tag2, ...\"}}\n"
            "4. You will then receive the full chat history and the tool response.\n"
            "   The tool response is a list of dictionaries:\n"
            "     {\"name\": \"game_name\", \"description\": \"game_description\"}\n"
            "5. Select EXACTLY 5 games:\n"
            "   - You can either choose it from the list from tools or find it by yourself. If you think that the list from tool answer is irrelevant you MUST generate games by yourself. Remember, that the final answer MUST be relevant to user query\n."
            "6. Return the final result using ONLY this format:\n"
            "   {\"text\": \"game1, game2, game3, game4, game5\"}\n\n"
            "HARD RESTRICTIONS TO PREVENT INVALID OUTPUT:\n"
            "- CALL the tool ONLY if you are not sure, because i have LIMITED api requests"
            "- NEVER reuse example results.\n"
            "- REMEMBER THAT TOOLS OUTPUT IS JUST ADDITIONAL INFO AND YOU MUST DECIDE EITHER USE IT OR NOT"
            "- NEVER hallucinate tool results.\n"
            "- NEVER output placeholder names like 'game_added_by_you'.\n"
            "- ONLY output real game names relevant to the query, that you either GENERATE by yourself or found in the tool results.\n"
            "- FINAL OUTPUT MUST ONLY contain the 5 selected game names separated by commas.\n"
            "- ALL INFORMATION THAT GOES TO TOOLS MUST BE IN ENGLISH"
            "- ALL GAMES IN THE FINAL ANSWER MUST BE POPULAR"
        )
        self.add_to_memory("system", self.model_prompt)

    def parse_tools_from_response(self, response):
        try:
            self.logger.info(f"Start parsing {response}")
            if not isinstance(response, dict):
                self.logger.error("Error response is not dict")
                return {}

            if "choices" in response:
                content = response["choices"][0]["message"]["content"]
                try:
                    parsed = content
                    if isinstance(parsed, str):
                        parsed = json.loads(content)
                    return parsed
                except json.JSONDecodeError as e:
                    self.logger.error(f"Exception {e} while parsing response")
                    return {}

            if "function" in response:
                return response

            return {}
        except Exception as e:
            self.logger.error(f"Exception {e} while parsing response")
            return {}
    
    def get_model_answer(self):
        try:
            response = requests.post(
                url=self.URL,
                headers={
                    "Authorization": f"Bearer {self.API_TOKEN}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": self.MODEL,
                    "messages": self.memory
                })
            )

            if response.status_code != 200:
                self.logger.error(f"Error API: {response.status_code} {response.text}")
                return {}
            self.memory.append(response.json()["choices"][0]["message"])
            self.logger.info(f'Got final answer{response.json()["choices"][0]["message"]["content"]}')
            return response.json()
        except Exception as e:
            self.logger.error(f"Error in get_model_answer: {e}")
            return {}

    def add_to_memory(self, role, text):
        self.memory.append({"role": role, "content": text})
        self.logger.info("Added to memory " + text)

    def model(self, text : str):
        self.add_to_memory("user", text)
        for _ in range(self.tools_limit):
            response = self.get_model_answer()
            self.add_to_memory("assistant", response["choices"][0]["message"]["content"])
            parsed = self.parse_tools_from_response(response)
            if "text" in parsed:
                break
            tool_answer = self.tools_dispatcher.parse_and_call(parsed)
            self.add_to_memory("system", self.model_prompt)
            if len(str(tool_answer)) != 0 and tool_answer:
                self.add_to_memory("user", str(tool_answer))
            else:
                self.add_to_memory("user", "Error: mistake in tool description or tool not found")
        return parsed["text"]
