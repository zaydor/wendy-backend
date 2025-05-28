from dataclasses import dataclass

from models import Artist, Base, Image


@dataclass
class Album(Base):
    album_type: str
    artists: list[Artist]
    available_markets: list[str]
    external_urls: dict
    href: str
    id: str
    images: list[Image]
    name: str
    release_date: str
    release_date_precision: str
    total_tracks: int
    type: str
    uri: str
