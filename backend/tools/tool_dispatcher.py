import json
import importlib
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from api.config import ServerConfig


class ToolsDispatcher:
    TOOLS_MODULE = "tools.tools"

    def __init__(self, server_config: ServerConfig, tools_config_path: Optional[str] = None):
        self.logger = server_config.logger_config.get_logger("ToolsDispatcher")

        if tools_config_path is None:
            tools_config_path = str(Path(__file__).parent / "tools.json")
        self.tools_config_path = tools_config_path

        if not Path(self.tools_config_path).is_file():
            self.logger.error(f"Tools config file not found: {self.tools_config_path}")
            raise FileNotFoundError(f"Tools config file not found: {self.tools_config_path}")

        self.tools_config = self._load_config()
        self.tools_map = self._load_functions()

    def _load_config(self) -> List[Dict]:
        try:
            with open(self.tools_config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                if not isinstance(cfg, list):
                    self.logger.error("Tools config is not a list")
                    raise ValueError("Tools config is not a list")
                return cfg
        except Exception as e:
            self.logger.error(f"Failed to load tools config: {e}")
            raise

    def _load_functions(self) -> Dict[str, Callable]:
        tools_map = {}

        try:
            module = importlib.import_module(self.TOOLS_MODULE)
        except ModuleNotFoundError as e:
            self.logger.error(f"Failed to import module {self.TOOLS_MODULE}: {e}")
            raise

        if not isinstance(self.tools_config, list):
            self.logger.error("tools_config is not a list")
            raise ValueError("tools_config is not a list")

        for item in self.tools_config:
            if not isinstance(item, dict) or "type" not in item or item["type"] != "function":
                self.logger.warning(f"Skipped wrong config item: {item}")
                continue

            func_def = item.get("function")
            if not isinstance(func_def, dict):
                self.logger.warning(f"Function definition missing in item: {item}")
                continue

            func_name = func_def.get("name")
            if not isinstance(func_name, str):
                self.logger.warning(f"Function name invalid: {func_name} in item {item}")
                continue

            if hasattr(module, func_name):
                tools_map[func_name] = getattr(module, func_name)
            else:
                self.logger.warning(f"Function {func_name} not found in module {self.TOOLS_MODULE}")

        if not tools_map:
            self.logger.warning("No functions successfully mapped from tools config")

        return tools_map

    def parse_and_call(self, llm_response: Dict) -> Dict[str, Any]:
        try:
            if not isinstance(llm_response, dict):
                self.logger.error("llm_response is not a dict")
                return {}

            function_name = llm_response.get("function")
            if not isinstance(function_name, str):
                self.logger.error("function_name is missing or not a string")
                return {}

            arguments = llm_response.get("arguments", {})
            if not isinstance(arguments, dict):
                self.logger.error("arguments is not a dict")
                return {}

            if function_name not in self.tools_map:
                self.logger.error(f"Function not registered: {function_name}")
                return {}
            self.logger.info(f"Called tool {function_name}")
            function = self.tools_map[function_name]
            try:
                result = function(**arguments)
            except TypeError as e:
                self.logger.error(f"TypeError while calling {function_name}: {e}")
                return {}
            except Exception as e:
                self.logger.error(f"Error while calling {function_name}: {e}")
                return {}
            self.logger.info(f"Get result {result} from tool {function_name}")
            return {"result": result}

        except Exception as top_e:
            self.logger.exception(f"Unhandled exception in parse_and_call: {top_e}")
            return {}
