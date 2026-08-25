from odoo import models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def _prepare_inspection_line(self, test, line, fill=None):
        data = super()._prepare_inspection_line(test, line, fill=fill)
        if fill and line.type == "qualitative":
            default_value = line.ql_values.filtered("is_default_qualitative_value")
            if default_value:
                data["qualitative_value"] = default_value.id
        return data
