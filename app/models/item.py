from dataclasses import dataclass

from models import Base, SpotifyUser, Track


@dataclass
class Item(Base):
    added_at: str
    added_by: SpotifyUser
    is_local: bool
    primary_color: str | None
    track: Track
    video_thumbnail: dict
