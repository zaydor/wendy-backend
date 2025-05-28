from dataclasses import dataclass

from models import Base


@dataclass
class Image(Base):
    height: int
    url: str
    width: int
