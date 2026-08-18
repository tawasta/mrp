from odoo import fields, models


class QcTestQuestion(models.Model):
    _inherit = "qc.test.question"

    use_specific_default_freetext_value = fields.Boolean(
        string="Use specific pre-fill value",
        help=(
            "If enabled, the Default value below is used to pre-fill "
            "this question's answer instead of leaving it empty "
            "(requires 'Pre-fill with correct values' to be enabled "
            "on the test)."
        ),
    )
    default_freetext_value = fields.Text(
        help=(
            "Value used to pre-fill this question's answer when "
            "'Use specific pre-fill value' is enabled."
        ),
    )
