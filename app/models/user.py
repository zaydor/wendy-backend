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
