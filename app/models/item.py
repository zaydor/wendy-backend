from dataclasses import dataclass

from .base import Base
from .track import Track
from .user import SpotifyUser


@dataclass
class Item(Base):
    added_at: str
    added_by: SpotifyUser
    is_local: bool
    primary_color: str | None
    track: Track
    video_thumbnail: dict

    @staticmethod
    def from_json(json_data: dict) -> "Item":
        added_at = json_data["added_at"]
        added_by = SpotifyUser.from_json(json_data["added_by"])
        is_local = json_data["is_local"]
        primary_color = json_data["primary_color"]
        track = Track.from_json(json_data["track"])
        video_thumbnail = json_data["video_thumbnail"]

        return Item(
            added_at=added_at,
            added_by=added_by,
            is_local=is_local,
            primary_color=primary_color,
            track=track,
            video_thumbnail=video_thumbnail,
        )
