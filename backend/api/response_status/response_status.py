from enum import Enum


class ResponseCode(Enum):
    SUCCESS = ("success", 200)
    CREATED = ("created", 201)
    ACCEPTED = ("accepted", 202)

    VALIDATION_ERROR = ("validation_error", 400)
    UNAUTHORIZED = ("unauthorized", 401)
    FORBIDDEN = ("forbidden", 403)
    NOT_FOUND = ("not_found", 404)
    METHOD_NOT_ALLOWED = ("method_not_allowed", 405)

    INTERNAL_ERROR = ("internal_error", 500)
    NOT_IMPLEMENTED = ("not_implemented", 501)
    SERVICE_UNAVAILABLE = ("service_unavailable", 503)

    @property
    def text(self) -> str:
        return self.value[0]

    @property
    def http_code(self) -> int:
        return self.value[1]

    def to_dict(self) -> dict:
        return {
            "code": self.text,
            "http_status": self.http_code
        }


class ProcessingStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    PROCESSING = "processing"
