from odoo import models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def action_fill_answers(self):
        # Launch the simplified data entry view for the first line of the inspection
        self.ensure_one()
        lines = self.inspection_lines.sorted(lambda line: line.id)
        if not lines:
            return False
        return lines[0]._action_open_form()
