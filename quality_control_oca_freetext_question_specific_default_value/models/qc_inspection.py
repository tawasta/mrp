from odoo import models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def _prepare_inspection_line(self, test, line, fill=None):
        data = super()._prepare_inspection_line(test, line, fill=fill)
        if (
            fill
            and line.type == "freetext"
            and line.use_specific_default_freetext_value
        ):
            data["freetext_value"] = line.default_freetext_value
        return data
