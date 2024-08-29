from unittest.mock import patch
from app.services.export_service import ExportService


class TestExportService:

    def setup_method(self):
        self.service = ExportService()

    def test_is_a_no_positive_integer(self):
        assert self.service.is_a_positive_integer(-1) == False

    def test_is_a_positive_integer(self):
        assert self.service.is_a_positive_integer(1) == True

    def test_sheet_valid(self):
        sheet = {
            "cd_resource": 1,
            "cd_instance": 15
        }
        assert self.service.sheet_is_valid(sheet) == True

    def test_sheet_no_valid(self):
        sheet = {
            "cd_resource": 1,
            "cd_instance": 'l1'
        }
        assert self.service.sheet_is_valid(sheet) == False

    @patch('app.repositories.resource_repository.get_type')
    def test_get_report_type_business(self, mock_get_type):
        mock_get_type.return_value = 1
        assert self.service.get_report_type(cd_resource=1) == "business"

    @patch('app.repositories.resource_repository.get_type')
    def test_get_report_type_individual(self, mock_get_type):
        mock_get_type.return_value = 2
        assert self.service.get_report_type(cd_resource=1) == "individual"
