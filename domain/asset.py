from domain.survey import Survey
from domain.common import shorten_text_repr
from dataclasses import dataclass


@dataclass
class Asset:
    NAME_INDEX = 0
    TYPE_INDEX = 1
    IS_IN_PCI_DSS_SCOPE_INDEX = 2
    HAS_IID_CLIENTS_INDEX = 3
    HAS_IID_EMPLOYEES_INDEX = 4
    SENSITIVE_DATA_DESCRIPTION_INDEX = 5
    BUSINESS_OWNER_INDEX = 6
    PURPOSE_INDEX = 7
    ACCESS_OWNER_INDEX = 8
    COMMENTS_INDEX = 9

    name:                       str
    type:                       str
    is_in_pci_dss_scope:        bool
    has_iid_clients:            bool
    has_iid_employees:          bool
    sensitive_data_description: list[str] | str
    business_owner:             list[str] | str
    purpose:                    list[str] | str
    access_owner:               list[str] | str
    comments:                   list[str] | str
    department:                 str
    unit:                       str
    department_and_unit:        list[str] | str

    @staticmethod
    def make_from_survey(raw_asset: list[str | bool | None], survey: Survey):
        name:                str = raw_asset[Asset.NAME_INDEX].strip()
        type:                str = raw_asset[Asset.TYPE_INDEX]
        is_in_pci_dss_scope: bool = True if raw_asset[Asset.IS_IN_PCI_DSS_SCOPE_INDEX].lower() == "true" else False
        has_iid_clients:     bool = True if raw_asset[Asset.HAS_IID_CLIENTS_INDEX].lower() == "true" else False
        has_iid_employees:   bool = True if raw_asset[Asset.HAS_IID_EMPLOYEES_INDEX].lower() == "true" else False
        sensitive_data_description: list[str] | str = list()
        business_owner:      list[str] | str = list()
        purpose:             list[str] | str = list()
        access_owner:        list[str] | str = list()
        comments:            list[str] | str = list()
        department:          str = survey.department
        unit:                str = survey.unit
        department_and_unit: str = f"{survey.department} {survey.unit}"

        try:
            if raw_asset[Asset.SENSITIVE_DATA_DESCRIPTION_INDEX]:
                sensitive_data_description.append(raw_asset[Asset.SENSITIVE_DATA_DESCRIPTION_INDEX])
        except IndexError:
            ""
        try:
            if raw_asset[Asset.BUSINESS_OWNER_INDEX]:
                business_owner.append(raw_asset[Asset.BUSINESS_OWNER_INDEX])
        except IndexError:
            ""
        try:
            if raw_asset[Asset.PURPOSE_INDEX]:
                purpose.append(raw_asset[Asset.PURPOSE_INDEX])
        except IndexError:
            ""
        try:
            if raw_asset[Asset.ACCESS_OWNER_INDEX]:
                access_owner.append(raw_asset[Asset.ACCESS_OWNER_INDEX])
        except IndexError:
            ""
        try:
            if raw_asset[Asset.COMMENTS_INDEX]:
                comments.append(raw_asset[Asset.COMMENTS_INDEX])
        except IndexError:
            ""

        return Asset(name=name, type=type, is_in_pci_dss_scope=is_in_pci_dss_scope, has_iid_clients=has_iid_clients,
                     has_iid_employees=has_iid_employees, sensitive_data_description=sensitive_data_description,
                     business_owner=business_owner, purpose=purpose, access_owner=access_owner, comments=comments,
                     department=department, unit=unit, department_and_unit=department_and_unit)

    @staticmethod
    def make_from_loa_asset(loa_asset: list):
        name:                str = loa_asset[Asset.NAME_INDEX].strip()
        type:                str = loa_asset[Asset.TYPE_INDEX]
        is_in_pci_dss_scope: bool = True if loa_asset[Asset.IS_IN_PCI_DSS_SCOPE_INDEX].lower() == "true" else False
        has_iid_clients:     bool = True if loa_asset[Asset.HAS_IID_CLIENTS_INDEX].lower() == "true" else False
        has_iid_employees:   bool = True if loa_asset[Asset.HAS_IID_EMPLOYEES_INDEX].lower() == "true" else False
        sensitive_data_description: list[str] | str = loa_asset[Asset.SENSITIVE_DATA_DESCRIPTION_INDEX]
        business_owner:      list[str] | str = loa_asset[Asset.BUSINESS_OWNER_INDEX]
        purpose:             list[str] | str = loa_asset[Asset.PURPOSE_INDEX]
        access_owner:        list[str] | str = [loa_asset[Asset.ACCESS_OWNER_INDEX]] if isinstance(
            loa_asset[Asset.ACCESS_OWNER_INDEX], str) else loa_asset[Asset.ACCESS_OWNER_INDEX].split(", ")

        # NOT GOING INTO UPDATE PACK
        comments:            list[str] | str = loa_asset[Asset.COMMENTS_INDEX]
        department:          str = loa_asset[-3]
        unit:                str = loa_asset[-2]
        department_and_unit: list[str] = [x.strip() for x in loa_asset[-1].split("; ")]

        return Asset(name=name, type=type, is_in_pci_dss_scope=is_in_pci_dss_scope, has_iid_clients=has_iid_clients,
                     has_iid_employees=has_iid_employees, sensitive_data_description=sensitive_data_description,
                     business_owner=business_owner, purpose=purpose, access_owner=access_owner, comments=comments,
                     department=department, unit=unit, department_and_unit=department_and_unit)

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
                   f"{shorten_text_repr(str(self.sensitive_data_description), 25)} | "
                   f"{shorten_text_repr(str(self.business_owner), 25)} | "
                   f"{shorten_text_repr(str(self.purpose), 25)} | "
                   f"{shorten_text_repr(str(self.access_owner), 25)} | "
                   f"{shorten_text_repr(str(self.department), 25)} | "
                   f"{shorten_text_repr(str(self.unit), 25)} | "
                   f"{shorten_text_repr(str(self.department_and_unit), 30)} | "
                   f"{shorten_text_repr(str(self.comments), 25)} | ")
        return message


