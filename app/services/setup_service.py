from app.services.googlesheet_service import SpreadSheetService
from app.core.config import SETUP_SPREADSHEET


class SetupService:
    def __init__(self):
        self.setup_sheet = SpreadSheetService(spreadsheet=SETUP_SPREADSHEET)
        self.setup = self.setup_sheet.spreadsheet.worksheet("setup")

    def get_setup_tab(self):
        return self.setup_sheet.spreadsheet.worksheet("setup")

    def write_error_message(self, lino, message=''):
        self.setup.update(f"E{lino}", message)

    def write_error_note(self, lino, message=''):
        note = self.setup.get_note(f"E{lino}") + message
        self.setup.update_note (f"E{lino}", note)

    def clear_notes(self, lino):
        self.setup.update_note(f"E{lino}", '')

    def clear_errors(self, lino):
        self.write_error_message(lino, '')
        self.clear_notes(lino)