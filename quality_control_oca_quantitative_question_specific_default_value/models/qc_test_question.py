from odoo import fields, models


class QcTestQuestion(models.Model):
    _inherit = "qc.test.question"

    use_specific_default_value = fields.Boolean(
        string="Use specific pre-fill value",
        help=(
            "If enabled, the Default value below is used to pre-fill "
            "this question's answer instead of the midpoint of "
            "Min/Max (requires 'Pre-fill with correct values' to be "
            "enabled on the test)."
        ),
    )
    default_quantitative_value = fields.Float(
        digits="Quality Control",
        help=(
            "Value used to pre-fill this question's answer when "
            "'Use specific pre-fill value' is enabled."
        ),
    )
