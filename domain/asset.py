from domain.survey import Survey
from domain.common import shorten_text_repr
from loguru import logger


class Asset:
    def __init__(self, raw_asset: list[str | bool | None], survey: Survey):
        self.name: str = raw_asset[0].strip()
        self.type: str = raw_asset[1]
        self.is_in_pci_dss_scope: bool = True if raw_asset[2].lower() == "true" else False
        self.has_iid: bool = True if raw_asset[3].lower() == "true" else False
        self.sensitive_data_description: list[str] | str = list()
        self.business_owner: list[str] | str = list()
        self.purpose: list[str] | str = list()
        self.access_owner: list[str] | str = list()
        self.comments: list[str] | str = list()

        try:
            if raw_asset[4]: self.sensitive_data_description.append(raw_asset[4])
        except IndexError:
            ""
        try:
            if raw_asset[5]: self.business_owner.append(raw_asset[5])
        except IndexError:
            ""
        try:
            if raw_asset[6]: self.purpose.append(raw_asset[6])
        except IndexError:
            ""
        try:
            if raw_asset[7]: self.access_owner.append(raw_asset[7])
        except IndexError:
            ""
        try:
            if raw_asset[8]: self.comments.append(raw_asset[8])
        except IndexError:
            ""

        self.department: str = survey.department
        self.unit: str = survey.unit
        self.department_and_unit = f"{survey.department} {survey.unit}"

    def collapse(self):
        self.sensitive_data_description = Asset._collapse_entity(self.sensitive_data_description)
        self.business_owner = Asset._collapse_entity(self.business_owner)
        self.purpose = Asset._collapse_entity(self.purpose)
        self.access_owner = Asset._collapse_entity(self.access_owner)
        self.comments = Asset._collapse_entity(self.comments)

    @staticmethod
    def _collapse_entity(entity: list[str]) -> str:
        if not entity:
            return ""
        unique_set = set(entity)
        string = ", ".join(list(unique_set))
        return string

    def __repr__(self):
        message = (f"| {shorten_text_repr(self.name, 25)} | "
                   f"{self.type.ljust(11)} | "
                   f"{str(self.is_in_pci_dss_scope).ljust(5)} | "
                   f"{str(self.has_iid).ljust(5)} | "
                   f"{shorten_text_repr(self.sensitive_data_description, 25)} | "
                   f"{shorten_text_repr(self.business_owner, 25)} | "
                   f"{shorten_text_repr(self.purpose, 25)} | "
                   f"{shorten_text_repr(self.access_owner, 25)} | "
                   f"{shorten_text_repr(self.department, 25)} | "
                   f"{shorten_text_repr(self.unit, 25)} | "
                   f"{shorten_text_repr(self.department_and_unit, 30)} | "
                   f"{shorten_text_repr(self.comments, 25)} | ")
        return message
