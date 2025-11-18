from flask import jsonify, Response
from api.config import ServerConfig
from api.response_status import ResponseCode


def ping(config: ServerConfig) -> Response:
    config.logger_config.get_logger("/ping").debug("Get request")

    return jsonify(
        {"status": ResponseCode.SUCCESS.text}
    ), ResponseCode.SUCCESS.http_code
