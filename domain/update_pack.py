from dataclasses import dataclass
from domain.asset import Asset


@dataclass
class UpdatePack:
    link: str
    backup_link: str
    assets: list[Asset]
    full_unit: str

    def __repr__(self):
        return self.full_unit
