from odoo.addons.base.tests.common import BaseCommon


class TestInspectionFreetextSerial(BaseCommon):
    def test_search_by_serial_number(self):
        inspection_model = self.env["qc.inspection"]
        matching = inspection_model.create(
            {"name": "Inspection A", "serial_number": "SN-001"}
        )
        inspection_model.create({"name": "Inspection B", "serial_number": "SN-002"})
        found = inspection_model.search([("serial_number", "=", "SN-001")])
        self.assertEqual(found, matching)
