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

    @staticmethod
    def from_json(json_data: dict) -> "Track":
        album = Album.from_json(json_data["album"])
        artists = [Artist.from_json(artist) for artist in json_data["artists"]]
        available_markets = json_data["available_markets"]
        disc_number = json_data["disc_number"]
        duration_ms = json_data["duration_ms"]
        episode = json_data["episode"]
        explicit = json_data["explicit"]
        external_ids = json_data["external_ids"]
        external_urls = json_data["external_urls"]
        href = json_data["href"]
        id = json_data["id"]
        is_local = json_data["is_local"]
        name = json_data["name"]
        popularity = json_data["popularity"]
        preview_url = json_data["preview_url"]
        track = json_data["track"]
        track_number = json_data["track_number"]
        type = json_data["type"]
        uri = json_data["uri"]

        return Track(
            album=album,
            artists=artists,
            available_markets=available_markets,
            disc_number=disc_number,
            duration_ms=duration_ms,
            episode=episode,
            explicit=explicit,
            external_ids=external_ids,
            external_urls=external_urls,
            href=href,
            id=id,
            is_local=is_local,
            name=name,
            popularity=popularity,
            preview_url=preview_url,
            track=track,
            track_number=track_number,
            type=type,
            uri=uri,
        )
