from odoo import models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def _prepare_inspection_line(self, test, line, fill=None):
        data = super()._prepare_inspection_line(test, line, fill=fill)
        if fill and line.type == "quantitative" and line.use_specific_default_value:
            data["quantitative_value"] = line.default_quantitative_value
        return data
