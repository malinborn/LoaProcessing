from dataclasses import dataclass
from domain.asset import Asset
from domain.common import shorten_text_repr


@dataclass
class UpdatePack:
    sheet_id: str
    assets: list[Asset] | None
    full_unit: str

    def __repr__(self):
        return (f"{shorten_text_repr(self.full_unit, 50)} | "
                f"{shorten_text_repr(self.sheet_id, 50)} | "
                f"{shorten_text_repr(str(len(self.assets)), 10)}")

    def debug_repr(self):
        return {"sheet_id": self.sheet_id,
                "full_unit": self.full_unit}, self.assets
