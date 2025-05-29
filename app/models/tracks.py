from dataclasses import dataclass

from models import Base, Item


@dataclass
class Tracks(Base):
    href: str
    items: list[Item]
    limit: int
    next: str | None
    offset: int
    previous: str | None
    total: int

    @staticmethod
    def from_json(json_data: dict) -> "Tracks":
        href = json_data["href"]
        items = [Item.from_json(item) for item in json_data["items"]]
        limit = json_data["limit"]
        next = json_data["next"]
        offset = json_data["offset"]
        previous = json_data["previous"]
        total = json_data["total"]

        return Tracks(
            href=href,
            items=items,
            limit=limit,
            next=next,
            offset=offset,
            previous=previous,
            total=total,
        )
