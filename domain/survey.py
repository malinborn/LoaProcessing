from typing import NewType
from domain.common import shorten_text_repr


class Survey:
    def __init__(self, raw_survey_data: list[str]):
        if len(raw_survey_data) > 5:
            self.department: str = raw_survey_data[0]
            self.unit: str = raw_survey_data[1]
            self.leader: str = raw_survey_data[2]
            self.link: str = Survey._extract_link(raw_survey_data[3])
            self.expert: str = raw_survey_data[4]
            self.auditor: str = raw_survey_data[5]
            self.additional_expert: str | None = None
            self.additional_auditor: str | None = None

        if len(raw_survey_data) == 8:
            self.additional_expert: str | None = raw_survey_data[6]
            self.additional_auditor: str | None = raw_survey_data[7]

    def __repr__(self):
        return (f"| {shorten_text_repr(self.department, 25)} | "
                f"{shorten_text_repr(self.unit, 25)} | "
                f"{self.leader.ljust(30)} | "
                f"{self.link[0:10] + '...' + self.link[-10:]} | "
                f"{shorten_text_repr(self.expert, 25)} | "
                f"{shorten_text_repr(self.auditor, 25)} | "
                f"{shorten_text_repr(self.additional_expert, 25) if self.additional_expert is not None else ''} | "
                f"{shorten_text_repr(self.additional_auditor, 25) if self.additional_auditor is not None else ''} |")

    @staticmethod
    def _extract_link(raw_link: str) -> str:
        link = raw_link.split(r"/d/")[-1]
        if r"/" in link:
            link = link.split(r"/")[0]
        return link

    @staticmethod
    def fill_departments(main_table: list[NewType("Survey", object)]) -> None:
        last_seen_department: str = ""
        for survey in main_table:
            if survey.department != "":
                last_seen_department = survey.department
            else:
                survey.department = last_seen_department
