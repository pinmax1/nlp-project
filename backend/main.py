import sys
import time
import argparse
from typing import NoReturn

from api.kernel.server import Server
from api.config import ServerConfig


def main() -> NoReturn:
    parser = argparse.ArgumentParser(description="Start server options")
    parser.add_argument(
        "--env-file",
        "-e",
        type=str,
        help="Path to .env server configuration file"
    )
    args = parser.parse_args()

    config: ServerConfig = ServerConfig(env_file=args.env_file) if args.env_file else ServerConfig()
    logger = config.logger_config.get_logger("main")

    RESTART_COUNTER = 0
    SECONDS_TO_RESTART = 2
    while True:
        try:
            logger.info(f"Initializing server (attempt {RESTART_COUNTER}) with {args.env_file or 'default'} environment")
            server: Server = Server(config)
            RESTART_COUNTER += 1
            server.run()

        except KeyboardInterrupt:
            logger.error("Server stopped by outer interruption")
            sys.exit(0)

        except Exception as error:
            logger.error(f"Server has been crashed: {error}")
            logger.info(f"Restarting server in {SECONDS_TO_RESTART} seconds")
            time.sleep(SECONDS_TO_RESTART)


if __name__ == "__main__":
    main()
