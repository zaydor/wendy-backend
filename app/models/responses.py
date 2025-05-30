class StandardResponse:
    def __init__(self, message: str = "Success", status: int = 200) -> None:
        self.message = message
        self.status = status
        self.response_body = {
            "status": self.status,
            "message": message,
            "Access-Control-Allow-Credentials": "true",
        }

    def build(self) -> tuple[dict, int]:
        return (self.response_body, self.status)


class ErrorResponse(StandardResponse):
    def __init__(self, error: str, message: str = "Failure", status: int = 400) -> None:
        super().__init__(message=message, status=status)
        self.error = error

    def build(self) -> tuple[dict, int]:
        self.response_body["error"] = self.error
        return super().build()


class AuthUrlResponse(StandardResponse):
    def __init__(
        self, auth_url: str, message: str = "Success", status: int = 200
    ) -> None:
        super().__init__(message=message, status=status)
        self.auth_url = auth_url

    def build(self) -> tuple[dict, int]:
        self.response_body["auth_url"] = self.auth_url
        return super().build()


class TokenInfoResponse(StandardResponse):
    def __init__(
        self, token_info: dict, message: str = "Success", status: int = 200
    ) -> None:
        super().__init__(message=message, status=status)
        self.token_info = token_info

    def build(self) -> tuple[dict, int]:
        self.response_body["token_info"] = self.token_info
        return super().build()


class DataResponse(StandardResponse):
    def __init__(self, data: dict, message: str = "Success", status: int = 200) -> None:
        super().__init__(message=message, status=status)
        self.data = data if data is not None else {}

    def build(self) -> tuple[dict, int]:
        self.response_body["data"] = self.data
        return super().build()
