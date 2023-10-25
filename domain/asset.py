from domain.survey import Survey
from domain.common import shorten_text_repr


class Asset:
    name_index = 0
    type_index = name_index + 1
    is_in_pci_dss_scope_index = type_index + 1
    has_iid_clients_index = is_in_pci_dss_scope_index + 1
    has_iid_employees_index = has_iid_clients_index + 1
    sensitive_data_description_index = has_iid_clients_index + 1
    business_owner_index = sensitive_data_description_index + 1
    purpose_index = business_owner_index + 1
    access_owner_index = purpose_index + 1
    comments_index = access_owner_index + 1

    def __init__(self, raw_asset: list[str | bool | None], survey: Survey):
        self.name: str = raw_asset[Asset.name_index].strip()
        self.type: str = raw_asset[Asset.type_index]
        self.is_in_pci_dss_scope: bool = True if raw_asset[Asset.is_in_pci_dss_scope_index].lower() == "true" else False
        self.has_iid_clients: bool = True if raw_asset[Asset.has_iid_clients_index].lower() == "true" else False
        self.has_iid_employees: bool = True if raw_asset[Asset.has_iid_employees_index].lower() == "true" else False
        self.sensitive_data_description: list[str] | str = list()
        self.business_owner: list[str] | str = list()
        self.purpose: list[str] | str = list()
        self.access_owner: list[str] | str = list()
        self.comments: list[str] | str = list()

        try:
            if raw_asset[Asset.sensitive_data_description_index]: self.sensitive_data_description.append(raw_asset[4])
        except IndexError:
            ""
        try:
            if raw_asset[Asset.business_owner_index]: self.business_owner.append(raw_asset[5])
        except IndexError:
            ""
        try:
            if raw_asset[Asset.purpose_index]: self.purpose.append(raw_asset[6])
        except IndexError:
            ""
        try:
            if raw_asset[Asset.access_owner_index]: self.access_owner.append(raw_asset[7])
        except IndexError:
            ""
        try:
            if raw_asset[Asset.comments_index]: self.comments.append(raw_asset[8])
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
                   f"{str(self.has_iid_clients).ljust(5)} | "
                   f"{str(self.has_iid_employees).ljust(5)} | "
                   f"{shorten_text_repr(self.sensitive_data_description, 25)} | "
                   f"{shorten_text_repr(self.business_owner, 25)} | "
                   f"{shorten_text_repr(self.purpose, 25)} | "
                   f"{shorten_text_repr(self.access_owner, 25)} | "
                   f"{shorten_text_repr(self.department, 25)} | "
                   f"{shorten_text_repr(self.unit, 25)} | "
                   f"{shorten_text_repr(self.department_and_unit, 30)} | "
                   f"{shorten_text_repr(self.comments, 25)} | ")
        return message
