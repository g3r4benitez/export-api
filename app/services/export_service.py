import gspread
import logging

from app.core.celery_worker import update_tab_task
from app.services.googlesheet_service import SpreadSheetService
from app.services.setup_service import SetupService
from app.repositories import resource_repository

INDIVIDUAL_TABS = {'demographics', 'questions', 'rent', 'utility', 'income', 'documents', 'landlord', 'manage'}
BUSINESS_TABS = {'business_questions_merged', 'business_manage', 'business_documents'}

setup_service = SetupService()


class ExportService:

    def __init__(self):
        self.gsheet = None

    def update_sheets(self):
        """Read the setup spreadsheet to start the reports creation"""

        sheets_to_create = self.get_sheets_from_gsuite()

        # validate sheets
        lino = 2
        for sheet in sheets_to_create:
            if self.sheet_is_valid(sheet):
                self.update_sheet(sheet['sheet_id'], sheet['cd_resource'], sheet['cd_instance'], lino=lino)
            else:
                setup_service.write_error_message(lino, 'Check if cd_resource or cd_instance is a number')

            lino = lino + 1

        return True

    def get_sheets_from_gsuite(self):
        """
        Reads a spreadsheet used as a setup where is defined the reports to create
        :param self:
        :return: a list of dictionaries whith cd_resource, cd_instance, and spreadsheet_id
        """

        tab = setup_service.get_setup_tab()
        lines = tab.get_all_records()
        return lines

    def sheet_is_valid(self, sheet):
        """Validate:
        cd_resource: is a positive integer
        cd_instance: is a positive integer
        """

        if not self.is_a_positive_integer(sheet['cd_resource']):
            return False

        if not self.is_a_positive_integer(sheet['cd_instance']):
            return False

        return True

    def is_a_positive_integer(self, number):
        try:
            val = int(number)
            if val < 1:
                return False
        except ValueError:
            return False
        return True

    def update_sheet(self, sheet_id, cd_resource, cd_instance, lino):
        setup_service.clear_errors(lino)
        setup_service.clear_notes(lino)

        try:
            print(f"working with cd_resource={cd_resource} and cd_instance={cd_instance}")
            report_type = self.get_report_type(cd_resource)

            tabs = INDIVIDUAL_TABS if report_type == "individual" else BUSINESS_TABS

            self.gsheet = SpreadSheetService(spreadsheet=sheet_id)
            sheets = [sheet.title for sheet in self.gsheet.spreadsheet.worksheets()]

            for tab in tabs:
                if tab not in sheets:
                    self.gsheet.spreadsheet.add_worksheet(title=tab, rows=500, cols=100)
                print(f"sending task '{tab}' to queue, cd_resource={cd_resource}, cd_instance={cd_instance} ")
                update_tab_task.delay(cd_instance, cd_resource, repository=f"{tab}_repository", sheet_id=sheet_id,
                                      tab=tab, lino=lino)

        except Exception as e:
            MESSAGE_GS_AVOID_TO_REPORT = "timed out"
            if e != MESSAGE_GS_AVOID_TO_REPORT:
                setup_service.write_error_message(lino, message="can't read the sheet id, check if the spreadsheet is share and the id value")
                setup_service.clear_notes(lino)
                setup_service.write_error_note(lino, f"the spreadsheet is not shared to write on it")
                print(f"#GS-INTEGRATION-NOTIFICATION. Spreadsheet not shared: cd_resource={cd_resource}, cd_instance={cd_instance}, line nro: {lino}")

        except TypeError:
            setup_service.write_error_message(lino, message="check if cd_resource and cd_instance are valid")
            print(f"#GS-INTEGRATION-NOTIFICATION. Check if cd_resource and cd_instance are valid: cd_resource={cd_resource}, cd_instance={cd_instance}, line nro: {lino}")

    def get_report_type(self, cd_resource):
        """Return report type based on cd_resource"""
        report_type = resource_repository.get_type(cd_resource=cd_resource)

        return "business" if report_type == 1 else "individual"
