from dataclasses import dataclass

from .base import Base


@dataclass
class Artist(Base):
    external_urls: dict
    href: str
    id: str
    name: str
    type: str
    uri: str

    @staticmethod
    def from_json(json_data: dict) -> "Artist":
        external_urls = json_data["external_urls"]
        href = json_data["href"]
        id = json_data["id"]
        name = json_data["name"]
        type = json_data["type"]
        uri = json_data["uri"]

        return Artist(
            external_urls=external_urls, href=href, id=id, name=name, type=type, uri=uri
        )
