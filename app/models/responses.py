from models import Base


class StandardResponse:
    def __init__(self, message: str = "Success", status: int = 200) -> None:
        self.message = message
        self.status = status
        self.response_body = {"message": message}

    def build(self) -> tuple[dict, int]:
        return (self.response_body, self.status)


class ErrorResponse(StandardResponse):
    def __init__(self, error: str, message: str = "Failure", status: int = 400):
        super().__init__(message=message, status=status)
        self.error = error

    def build(self) -> tuple[dict, int]:
        self.response_body["error"] = self.error
        return super().build()


class AuthUrlResponse(StandardResponse):
    def __init__(self, message: str, status: int, auth_url: str) -> None:
        super().__init__(message=message, status=status)
        self.auth_url = auth_url

    def build(self) -> tuple[dict, int]:
        self.response_body["auth_url"] = self.auth_url
        return super().build()


class TokenInfoResponse(StandardResponse):
    def __init__(self, message: str, status: int, token_info: str) -> None:
        super().__init__(message=message, status=status)
        self.token_info = token_info

    def build(self) -> tuple[dict, int]:
        self.response_body["token_info"] = self.token_info
        return super().build()


class DataResponse(StandardResponse):
    def __init__(self, message: str, status: int, data: Base) -> None:
        super().__init__(message=message, status=status)
        self.data = data

    def build(self) -> tuple[dict, int]:
        self.response_body["data"] = self.data
        return super().build()
