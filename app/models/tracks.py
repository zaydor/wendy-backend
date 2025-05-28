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
