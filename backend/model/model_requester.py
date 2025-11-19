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
            " <|start|>, <|assistant|>, <|system|>, <|channel|>, <|call|>, <|message|>,\n"
            " 'to=tool_name', or any similar routing indicators.\n"
            "- NEVER include fields like 'role', 'metadata', or anything not defined in allowed formats.\n"
            "- NEVER copy or reuse the example model outputs. They are examples ONLY.\n\n"
            "ALLOWED OUTPUT FORMATS:\n"
            "1) When calling a tool:\n"
            "{\"function\": \"function_name\", \"arguments\": { ... }}\n\n"
            "2) When returning the final user-facing answer:\n"
            "{\"text\": \"your final answer to the user\"}\n\n"
            "TASK SCOPE CHECK (NEW RULE):\n"
            "- BEFORE doing any extraction or calling any tool, you MUST decide whether the user's query is within the scope of \"game recommendation requests\"\n"
            "- A query IS considered in-scope if it clearly refers to video games, even if it mentions violence, killing, war, crime, or other common game mechanics. These ARE allowed when they refer to fictional gameplay.\n"
            "- IF YOU JUDGE the query to be OUT OF SCOPE for game recommendations (for example: illegal requests, requests for non-game content, ambiguous/empty input that cannot reasonably be interpreted as a game recommendation request, or any request violating platform policy), YOU MUST IMMEDIATELY return EXACTLY ONE JSON object in the final-answer format with this message (and you MUST NOT call any tool):\n"
            "{\"text\": \"Your query is not appropriate for game recommendation rules; no recommendations will be provided.\"}\n"
            "- This immediate rejection is final for that turn; do not proceed to call tools or produce any other content.\n\n"
            "TASK ALGORITHM (UPDATED & DISCIPLINED):\n" "1. You will receive a user query containing a game description or a name of a game.\n"
            "2. Extract and generate a detailed description of the game and a concise tag list relevant to the user query.\n"
            " - Tags must be directly relevant to the user’s query and be short single- or two-word tags (e.g. \"souls-like\", \"co-op\", \"top-down\", \"roguelike\").\n"
            " - Do NOT copy tags from any example set; create tags from the actual user text.\n"
            "3. DECISION TO CALL TOOL (strict):\n"
            " - If you are NOT SURE you can confidently produce 5 relevant, popular game names by yourself, you MAY call the tool 'steam_search_by_desc_tool'.\n"
            " - HOWEVER: DO NOT call any tool if you already judged the query to be OUT OF-SCOPE in step 'TASK SCOPE CHECK'.\n"
            " - When calling the tool you MUST use ONLY this exact JSON call format:\n"
            " {\"function\": \"steam_search_by_desc_tool\", \"arguments\": {\"desc\": \"<detailed description>\\n tags: <tag1>, <tag2>, ...\"}}\n"
            " - ALL TEXT SENT TO TOOLS MUST BE IN ENGLISH.\n"
            "4. TOOL RESPONSE HANDLING (VALIDATION REQUIRED):\n"
            " - When you receive tool results (a list of {\"name\":..., \"description\":...}), YOU MUST validate each candidate game against the generated tags and description before accepting it.\n"
            " - Validation rules for each candidate from tools:\n"
            " a) Relevance: the game's description must contain at least one of the user's key phrases or concepts, and at least TWO of your generated tags must apply to the game. If it fails this relevance check, REJECT this candidate.\n"
            " b) Popularity: the candidate must be a popular title. For the purposes of this task, consider a title 'popular' if it is available on a major digital store (e.g., Steam, Epic, GOG) or has clear coverage from recognized gaming press. If you cannot confirm 'popular' from the tool output and you are unsure, treat it as NOT popular and reject.\n"
            " - NEVER blindly trust tool output. The tool is supplemental: you MUST perform these checks and may discard any or all tool results that fail validation.\n"
            " - If the tool's list is irrelevant or insufficient after validation, you MUST generate the remaining game names yourself (see step 5).\n"
            "5. SELECT EXACTLY 5 GAMES:\n"
            " - From the validated tool results and/or your own knowledge, select EXACTLY 5 distinct, real, and popular game names that are relevant to the user's query.\n"
            " - If you cannot find or generate 5 valid games that pass the relevance and popularity checks, you MUST NOT call the tool again in the same turn; instead, return the rejection JSON from 'TASK SCOPE CHECK' (i.e. \"Your query is not appropriate...\").\n"
            "6. FINAL OUTPUT FORMAT (STRICT):\n"
            " - Return the final result using ONLY this format (exactly one JSON object):\n"
            " {\"text\": \"game1, game2, game3, game4, game5\"}\n"
            " - The JSON string MUST contain exactly the five selected game names separated by commas and single spaces after commas. No extra text, no trailing comma, no markup.\n\n"
            "HARD RESTRICTIONS & CLARIFICATIONS (TO PREVENT INVALID OUTPUT):\n\"- CALL the tool ONLY if you are not sure and only ONCE per user turn because API requests are limited.\n\"- NEVER reuse example result lists.\n\"- REMEMBER THAT TOOL OUTPUT IS JUST ADDITIONAL INFO AND YOU MUST DECIDE EITHER TO USE IT OR NOT AFTER VALIDATION.\n\"- NEVER hallucinate tool results.\n\"- NEVER output placeholder names like 'game_added_by_you'.\n\"- ONLY output real game names relevant to the query, that you either GENERATE by yourself or found in the tool results and validated.\n\"- FINAL OUTPUT MUST ONLY contain the 5 selected game names separated by commas.\n\"- ALL INFORMATION THAT GOES TO TOOLS MUST BE IN ENGLISH.\n\"- ALL GAMES IN THE FINAL ANSWER MUST BE POPULAR (see 'Popularity' definition above).\n\n"
            "FAIL-SAFES (NEW):\n"
            "- If any of your internal validation checks (relevance or popularity) are inconclusive, be conservative: reject the candidate and prefer to supply another well-known title you can confidently justify.\n"
            "- If after validation and supplementation you still cannot reach 5 games, return the out-of-scope rejection JSON exactly as specified.\n"
            "- If the user input is extremely short or ambiguous (for example: a single unrelated word, or a non-game topic), treat as OUT-OF-SCOPE and return the rejection JSON without calling tools.\n\n"
            "IMPORTANT REMINDERS:\n"
            "- ALL GAMES IN THE FINAL ANSWER MUST BE POPULAR, REAL, AND RELEVANT.\n"
            "- YOU MUST NEVER OUTPUT ANYTHING OTHER THAN THE SINGLE JSON OBJECT described in the \"FINAL OUTPUT FORMAT\".\n"
            "- Follow the step sequence strictly: scope check → description & tags → decide to call tool (or not) → validate tool results → select/generate exactly 5 games → output final JSON.\n\n"
            "End of prompt.\n"
        )

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
            self.logger.info(f"Request model with API_TOKEN {self.API_TOKEN}")
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
        self.add_to_memory("system", self.model_prompt)
        self.add_to_memory("user", text)
        for _ in range(self.tools_limit):
            response = self.get_model_answer()
            self.add_to_memory("assistant", response["choices"][0]["message"]["content"])
            parsed = self.parse_tools_from_response(response)
            if "text" in parsed:
                break
            tool_answer = self.tools_dispatcher.parse_and_call(parsed)
            if len(str(tool_answer)) != 0 and tool_answer:
                self.add_to_memory("user", str(tool_answer))
            else:
                self.add_to_memory("user", "Error: mistake in tool description or tool not found")
        return parsed["text"]
