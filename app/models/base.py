class Base:
    def to_json(self) -> dict:
        return {
            k: v
            for k, v in self.__dict__.items()
            if not callable(v) and not k.startswith("__")
        }

    @staticmethod
    def from_json(json_data: dict) -> "Base":
        raise NotImplementedError
