import gspread
from oauth2client.service_account import ServiceAccountCredentials
from app.core.config import GOOGLE_TOKEN_FILENAME


class SpreadSheetService:

    def __init__(self, spreadsheet):
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_TOKEN_FILENAME, scope)
        self.client = gspread.authorize(credentials)
        self.spreadsheet = self.client.open_by_key(spreadsheet)


