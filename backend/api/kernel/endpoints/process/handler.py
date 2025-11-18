from flask import jsonify, request, Response
from api.config import ServerConfig
from api.response_status import ResponseCode
from tools.tool_dispatcher import ToolsDispatcher
from model.model_requester import ModelRequester

import uuid


def process(config: ServerConfig, tools_dispatcher: ToolsDispatcher, model_requester: ModelRequester) -> Response:
    """
        Expected usage:
            curl http://<host_name>/process \
            -H "Content-Type: application/json" \
            -d '{"text": "user_text"}'
    """
    logger = config.logger_config.get_logger("/process")

    request_id = str(uuid.uuid4())
    logger.info(f"Get request {request_id}")

    data = request.get_json() or {}
    text = data.get('text')

    if text is None:
        logger.debug(f"Miss 'text' field for request {request_id}")

        return jsonify(
            {
                "status": ResponseCode.VALIDATION_ERROR.text,
                "message": "Field 'text' is required",
                "details": {"missing_field": "text"},
            }
        ), ResponseCode.VALIDATION_ERROR.http_code
    text = text.strip()

    if not text:
        logger.debug(f"Request {request_id} has empty text")

        return jsonify(
            {
                "status": ResponseCode.VALIDATION_ERROR.text,
                "message": "'text' field can not be empty",
                "details": {"field": "text"},
            }
        ), ResponseCode.VALIDATION_ERROR.http_code
    # result = model(text, tools_dispatcher) <- sending response to model
    # TODO: here expected to send request and get response from model and pass it to 'data' field

    logger.info(f'Send request to model with text {text}')
    result = model_requester.model(text=text)

    return jsonify(
        {
            "status": ResponseCode.SUCCESS.text,
            "message": "Text processed successfully",
            "data": result,
        }
    ), ResponseCode.SUCCESS.http_code
