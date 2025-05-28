from models import Playlist, User


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


class UserResponse(StandardResponse):
    def __init__(self, message: str, status: int, user: User) -> None:
        super().__init__(message=message, status=status)
        self.user = user

    def build(self) -> tuple[dict, int]:
        self.response_body["user"] = self.user.to_json()
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


class PlaylistResponse(StandardResponse):
    def __init__(self, message: str, status: int, playlist: Playlist) -> None:
        super().__init__(message=message, status=status)
        self.playlist = playlist

    def build(self) -> tuple[dict, int]:
        self.response_body["playlist"] = self.playlist.to_json()
        return super().build()
