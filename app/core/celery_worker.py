import importlib
import string
from time import sleep
from gspread.exceptions import GSpreadException, APIError

from celery.utils.log import get_task_logger

from app.services.googlesheet_service import SpreadSheetService
from app.services.setup_service import SetupService
from app.exceptions.export_exceptions import CellLimitException
from .celery_app import celery_app

celery_log = get_task_logger(__name__)

setup_service = SetupService()

TEN_MILLIONS = 10000000


@celery_app.task(
    name='app.core.celery_worker.update_tab_task', 
    queue="report_tabs",
    max_retries=10,
    default_retry_delay=60
    )
def update_tab_task(cd_instance: int, cd_resource: int, repository: str, sheet_id='', tab='', lino: int = 0):
    # sleep is added to avoid the google spreadsheet request limit
    sleep(5)
    celery_log.info(f"Starting with with repository: {repository}")
    repo = importlib.import_module(f"app.repositories.{repository}")

    try:

        gsheet = SpreadSheetService(spreadsheet=sheet_id)
        worksheet = gsheet.spreadsheet.worksheet(tab)

        headers, rows = repo.gets(cd_resource, cd_instance)
        last_column = get_last_column(headers)
        last_row = len(rows)+1
    
        worksheet.clear()
        cell_list = worksheet.range(f'A1:{last_column}{last_row}')

        # write headers
        for header in range(len(headers)):
            cell_list[header].value = headers[header]

        pointer = header + 1

        # write values
        for row in rows:
            for cell in row:
                cell_list[pointer].value = str(cell)
                pointer = pointer + 1

        if len(cell_list) > TEN_MILLIONS:
            raise CellLimitException


        value_input_option = 'USER_ENTERED' if tab in ['rent', 'utility'] else 'RAW'
        worksheet.update_cells(cell_list, value_input_option=value_input_option)

    except CellLimitException as e:
        setup_service.write_error_message(lino, message=f"Errors: check notes")
        setup_service.write_error_note(lino,message=f"Exception: Tab {tab}, Cell limit of {TEN_MILLIONS} reached, cd_resource={cd_resource}, "
                        f"cd_instance={cd_instance}")
        celery_log.info(f"#GS-INTEGRATION-NOTIFICATION. Exception: Cell limit of {TEN_MILLIONS} reached, cd_resource={cd_resource}, "
                        f"cd_instance={cd_instance}, in tab {tab} , line nro: {lino}")

    except (GSpreadException, APIError, Exception) as e:
        setup_service.write_error_message(lino, message=f"Errors: check notes" )
        setup_service.write_error_note(lino,
                                          message=f"Exception: Tab {tab} can't be updated cd_resource={cd_resource}, "
                                                  f"cd_instance={cd_instance}: {e}")

        celery_log.info(f"#GS-INTEGRATION-NOTIFICATION. Tab {repository} can't be updated cd_resource={cd_resource}, "
                        f"cd_instance={cd_instance}, line nro: {lino}, {e}")

    


def get_last_column(headers):
    """
    # Based on headers return the set of letters for the last column
    :param headers: it is a list of headers
    :return: a set of letters
    """
    letters = ' ' + string.ascii_uppercase
    last_column = {}
    counter = 1
    for l in letters:
        for c in string.ascii_uppercase:
            last_column[counter] = l.strip() + c
            counter = counter + 1

    return last_column[len(headers)]
