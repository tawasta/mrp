from odoo import api, exceptions, fields, models


class QcTestQuestionValue(models.Model):
    _inherit = "qc.test.question.value"

    is_default_qualitative_value = fields.Boolean(
        string="Default pre-fill value",
        help=(
            "If enabled, this answer is used to pre-fill the question "
            "instead of the first correct answer found (requires "
            "'Pre-fill with correct values' to be enabled on the test)."
        ),
    )

    @api.constrains("is_default_qualitative_value", "ok")
    def _check_default_qualitative_value_is_correct(self):
        for value in self:
            if value.is_default_qualitative_value and not value.ok:
                raise exceptions.ValidationError(
                    self.env._(
                        "Only a correct answer can be set as the default "
                        "pre-fill value."
                    )
                )

    @api.constrains("is_default_qualitative_value")
    def _check_single_default_qualitative_value(self):
        for value in self:
            if not value.is_default_qualitative_value:
                continue
            siblings = (
                value.test_line.ql_values.filtered("is_default_qualitative_value")
                - value
            )
            if siblings:
                raise exceptions.ValidationError(
                    self.env._(
                        "Only one answer can be set as the default "
                        "pre-fill value per question."
                    )
                )
