from domain.survey import Survey
from domain.common import shorten_text_repr


class Asset:
    def __init__(self, raw_asset: list[str | bool| None], survey: Survey):
        self.name: str = raw_asset[0].strip()
        self.type: str = raw_asset[1]
        self.is_in_pci_dss_scope: bool = True if raw_asset[2] == "TRUE" else False
        self.has_iid: bool = True if raw_asset[3] == "TRUE" else False
        try:
            self.sensitive_data_description: str = raw_asset[4]
            self.business_owner: str = raw_asset[5].strip()
            self.purpose: str = raw_asset[6]
            self.access_owner: str = raw_asset[7]
        except IndexError:
            self.sensitive_data_description: str = ""
            self.business_owner: str = ""
            self.purpose: str = ""
            self.access_owner: str = ""

        try:
            self.comments: str = raw_asset[8]
        except IndexError:
            self.comments: str = ""

        self.department: str = survey.department
        self.unit: str = survey.unit
        self.department_and_unit = f"{survey.department} {survey.unit}"

    def __repr__(self):
        return (f"| {shorten_text_repr(self.name, 25)} | "
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
