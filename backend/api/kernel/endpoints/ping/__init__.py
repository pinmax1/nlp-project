from flask import Blueprint
from api.config import ServerConfig
from .handler import ping

__all__ = [
    'ping_bp',
    'register_ping_handler'
]


ping_bp: Blueprint = Blueprint('ping', __name__)


def register_ping_handler(config: ServerConfig):
    def ping_with_config():
        return ping(config)

    ping_bp.route('/ping')(ping_with_config)
