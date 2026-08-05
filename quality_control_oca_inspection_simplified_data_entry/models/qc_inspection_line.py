from odoo import api, fields, models


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    answer_display = fields.Char(string="Answer", compute="_compute_answer_display")

    @api.depends(
        "question_type",
        "qualitative_value",
        "quantitative_value",
        "uom_id",
        "freetext_value",
    )
    def _compute_answer_display(self):
        # A helper field to visualize the answer value, regardless of its question
        # type
        for line in self:
            if line.question_type == "qualitative":
                line.answer_display = line.qualitative_value.name or ""
            elif line.question_type == "freetext":
                line.answer_display = line.freetext_value or ""
            else:
                value = "%g" % (line.quantitative_value or 0.0)
                uom = line.uom_id.name or ""
                line.answer_display = " ".join(filter(None, [value, uom]))

    def _sorted_siblings(self):
        self.ensure_one()
        return self.inspection_id.inspection_lines.sorted(lambda line: line.id)

    def _action_open_form(self):
        # Launches the simplified data entry row
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Enter your answer"),
            "res_model": "qc.inspection.line",
            "res_id": self.id,
            "view_mode": "form",
            "views": [
                (
                    self.env.ref(
                        "quality_control_oca_inspection_simplified_data_entry."
                        "qc_inspection_line_form_view_simplified_data_entry"
                    ).id,
                    "form",
                )
            ],
            "target": "new",
        }

    def action_save_and_next(self):
        # Save the qc.inspection.line and open the next line of the inspection,
        # or close the form and refresh if we were at the last qc.inspection line
        self.ensure_one()
        siblings = self._sorted_siblings()
        remaining = siblings.filtered(lambda line: line.id > self.id)
        if not remaining:
            return {"type": "ir.actions.client", "tag": "reload"}
        return remaining[0]._action_open_form()
