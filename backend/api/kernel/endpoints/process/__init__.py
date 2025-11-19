from flask import Blueprint
from api.config import ServerConfig
from .handler import process
from tools.tool_dispatcher import ToolsDispatcher
from model.model_requester import ModelRequester

__all__ = [
    'process_bp',
    'register_process_handler'
]


process_bp: Blueprint = Blueprint('process', __name__)


def register_process_handler(config: ServerConfig, tools_dispatcher: ToolsDispatcher):
    def process_with_config():
        return process(config, tools_dispatcher)

    process_bp.route('/process', methods=['POST'])(process_with_config)
