from dataclasses import dataclass

from models import Album, Artist, Base


@dataclass
class Track(Base):
    album: Album
    artists: list[Artist]
    available_markets: list[str]
    disc_number: int
    duration_ms: int
    episode: bool
    explicit: bool
    external_ids: dict
    external_urls: dict
    href: str
    id: str
    is_local: bool
    name: str
    popularity: int
    preview_url: str | None
    track: bool
    track_number: int
    type: str
    uri: str
