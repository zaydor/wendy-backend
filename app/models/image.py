from dataclasses import dataclass

from models import Base


@dataclass
class Image(Base):
    height: int
    width: int
    url: str

    @staticmethod
    def from_json(json_data: dict) -> "Image":
        height = json_data["height"]
        width = json_data["width"]
        url = json_data["url"]

        return Image(height=height, width=width, url=url)
