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

    def update_range(self, spreadsheet_id: str, range: str, body: dict) -> dict:
        request = self.service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                              range=range,
                                                              body=body,
                                                              valueInputOption="RAW")
        response = request.execute()
        return response

    def wipe_range(self, spreadsheet_id: str, range: str):
        request = self.service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id,
                                                             range=range)
        response = request.execute()
        return response

    def get_values(self, link: str, range: str) -> dict:
        get_request = self.service.spreadsheets().values().get(spreadsheetId=link,
                                                               range=range)
        return get_request.execute()

    def batch_update(self, spreadsheet_id: str, request: dict[str, list[dict[str, dict[str, dict[str, str]]]]]) -> dict:
        request = self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                                          body=request)

        response = request.execute()
        return response


def main():
    import os

    path = os.getenv("GOOGLE_TOKEN_PATH")

    google_service = GoogleClient(path)

    print(type(google_service.service))


if __name__ == "__main__":
    main()
