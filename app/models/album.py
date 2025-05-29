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

    @staticmethod
    def from_json(json_data: dict) -> "Album":
        album_type = json_data["album_type"]
        artists = [Artist.from_json(artist) for artist in json_data["artists"]]
        available_markets = json_data["available_markets"]
        external_urls = json_data["external_urls"]
        href = json_data["href"]
        id = json_data["id"]
        images = [Image.from_json(image) for image in json_data["images"]]
        name = json_data["name"]
        release_date = json_data["release_date"]
        release_date_precision = json_data["release_date_precision"]
        total_tracks = json_data["total_tracks"]
        type = json_data["type"]
        uri = json_data["uri"]

        return Album(
            album_type=album_type,
            artists=artists,
            available_markets=available_markets,
            external_urls=external_urls,
            href=href,
            id=id,
            images=images,
            name=name,
            release_date=release_date,
            release_date_precision=release_date_precision,
            total_tracks=total_tracks,
            type=type,
            uri=uri,
        )
