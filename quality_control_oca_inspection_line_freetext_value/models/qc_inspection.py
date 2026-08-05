from odoo import exceptions, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def action_confirm(self):
        # The entire function needs to be overridden so that freetext answers don't
        # wrongly cause missing data exceptions
        for inspection in self:
            for line in inspection.inspection_lines:
                if line.question_type == "qualitative" and not line.qualitative_value:
                    raise exceptions.UserError(
                        self.env._(
                            "You should provide an answer for all "
                            "qualitative questions."
                        )
                    )
                if line.question_type == "quantitative" and not line.uom_id:
                    raise exceptions.UserError(
                        self.env._(
                            "You should provide a unit of measure for "
                            "quantitative questions."
                        )
                    )
            if inspection.success:
                inspection.state = "success"
            else:
                inspection.state = "waiting"
