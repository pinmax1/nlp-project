from typing import NoReturn
from flask import Flask, Response, jsonify
from api.config import ServerConfig
from tools import ToolsDispatcher
from model.model_requester import ModelRequester
from api.steamdb_manager import SteamDBManager

from waitress import serve


class Server:
    def __init__(self, server_config: ServerConfig):
        self.config = server_config
        self.logger = server_config.logger_config.get_logger("server")
        self.tools_dispatcher = ToolsDispatcher(server_config)
        Server.steamdb_manager = SteamDBManager(server_config)
        self.app = self._create_app()

    def _create_app(self) -> Flask:
        app = Flask(__name__)
        app.config.update(
            SECRET_KEY=self.config.SECRET_KEY,
            DEBUG=self.config.DEBUG
        )

        self._register_blueprints(app)
        self._register_error_handlers(app)
        app.config['JSON_AS_ASCII'] = False

        return app

    def _register_error_handlers(self, app: Flask) -> None:
        from werkzeug.exceptions import HTTPException

        @app.errorhandler(404)
        def not_found(error: HTTPException) -> tuple[Response, int]:
            self.logger.warning(f"404 error: {error}")
            return jsonify({"error": "Not found"}), 404

        @app.errorhandler(500)
        def internal_error(error: HTTPException) -> tuple[Response, int]:
            self.logger.error(f"500 error: {error}")
            return jsonify({"error": "Internal server error"}), 500

    def run(self) -> NoReturn:
        try:
            self.logger.info(f"Starting Waitress server on {self.config.HOST}:{self.config.PORT}")
            self.logger.info(f"Threads number: {self.config.THREADS}, Connection limit: {self.config.CONNECTION_LIMIT}")

            serve(
                self.app,
                host=self.config.HOST,
                port=self.config.PORT,
                threads=self.config.THREADS,
                connection_limit=self.config.CONNECTION_LIMIT,
                channel_timeout=self.config.REQUEST_TIMEOUT,
            )

        except ImportError:
            self.logger.warning("Waitress is not available, falling back to Flask server")

            self.app.run(
                host=self.config.HOST,
                port=self.config.PORT,
                debug=self.config.DEBUG,
                threaded=True
            )

    def get_app(self) -> Flask:
        return self.app

    def _register_blueprints(self, app: Flask) -> None:
        from api.kernel.endpoints.ping import ping_bp, register_ping_handler
        register_ping_handler(self.config)
        app.register_blueprint(ping_bp)
        self.logger.info("Ping handler has been registered")

        from api.kernel.endpoints.process import process_bp, register_process_handler
        register_process_handler(self.config, self.tools_dispatcher)
        app.register_blueprint(process_bp)
        self.logger.info("Process handler has been registered")
