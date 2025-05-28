from dataclasses import dataclass

from models import Base


@dataclass
class Artist(Base):
    external_urls: dict
    href: str
    id: str
    name: str
    type: str
    uri: str
