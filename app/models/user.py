from dataclasses import dataclass

from .base import Base


@dataclass
class User(Base):
    name: str
    email: str
    uid: str

    @staticmethod
    def from_json(json_data: dict) -> "User":
        name = json_data["name"]
        email = json_data["email"]
        uid = json_data["uid"]

        return User(name=name, email=email, uid=uid)


@dataclass
class SpotifyUser(Base):
    external_uris: dict
    href: str
    id: str
    type: str
    uri: str

    @staticmethod
    def from_json(json_data: dict) -> "SpotifyUser":
        external_uris = json_data["external_uris"]
        href = json_data["href"]
        id = json_data["id"]
        type = json_data["type"]
        uri = json_data["uri"]

        return SpotifyUser(
            external_uris=external_uris, href=href, id=id, type=type, uri=uri
        )
