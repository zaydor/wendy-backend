from dataclasses import dataclass

from .base import Base
from .image import Image
from .tracks import Tracks
from .user import SpotifyUser


@dataclass
class Playlist(Base):
    collaborative: bool
    description: str
    external_urls: dict
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

    @staticmethod
    def from_json(json_data: dict) -> "Playlist":
        collaborative = json_data["collaborative"]
        description = json_data["description"]
        external_urls = json_data["external_urls"]
        followers = json_data["followers"]
        href = json_data["href"]
        id = json_data["id"]
        images = [Image.from_json(img) for img in json_data["images"]]
        name = json_data["name"]
        owner = SpotifyUser.from_json(json_data["owner"])
        primary_color = json_data["primary_color"]
        public = json_data["public"]
        snapshot_id = json_data["snapshot_id"]
        tracks = Tracks.from_json(json_data["tracks"])
        type = json_data["type"]
        uri = json_data["uri"]

        return Playlist(
            collaborative=collaborative,
            description=description,
            external_urls=external_urls,
            followers=followers,
            href=href,
            id=id,
            images=images,
            name=name,
            owner=owner,
            primary_color=primary_color,
            public=public,
            snapshot_id=snapshot_id,
            tracks=tracks,
            type=type,
            uri=uri,
        )
