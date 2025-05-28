from dataclasses import dataclass
from tkinter import Image

from models import Base, SpotifyUser, Tracks


@dataclass
class Playlist(Base):
    collaborative: bool
    description: str
    followers: dict
    href: str
    id: str
    images: list[Image]
    name: str
    owner: SpotifyUser
    primary_color: str | None
    public: bool
    snapshot_id: str
    tracks: Tracks
    type: str
    uri: str
