from dataclasses import dataclass

from models import Base


@dataclass
class User(Base):
    name: str
    email: str
    uid: str


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
