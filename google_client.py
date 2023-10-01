import httplib2
import apiclient

from oauth2client.service_account import ServiceAccountCredentials


class GoogleClient:
    def __init__(self, credentials_path: str, table_id: str = ""):
        self.service = GoogleClient.build_service(credentials_path)
        self.main_table_id = table_id

    @staticmethod
    def build_service(credentials_path):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path,
                                                                       ['https://www.googleapis.com/auth/spreadsheets',
                                                                        'https://www.googleapis.com/auth/drive']
                                                                       )
        http_auth = credentials.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http=http_auth)
        return service

    def upload_values(self, values, range: str) -> None:
        body = {"values": values,
                "majorDimension": "ROWS"}

        upload_request = self.service.spreadsheets().values().update(spreadsheetId=self.main_table_id,
                                                                     range=range,
                                                                     valueInputOption="USER_ENTERED",
                                                                     body=body)
        upload_request.execute()

    def get_values(self, link: str, range: str) -> dict:
        get_request = self.service.spreadsheets().values().get(spreadsheetId=link,
                                                               range=range)
        return get_request.execute()


def main():
    pass


if __name__ == "__main__":
    main()