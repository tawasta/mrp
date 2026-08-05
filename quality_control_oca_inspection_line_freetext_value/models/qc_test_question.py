from odoo import fields, models


class QcTestQuestion(models.Model):
    _inherit = "qc.test.question"

    # When a new selection is added to an existing mandatory field, some kind of
    # ondelete needs to be set for the module to install. This fulfills that
    # requirement but is not really useful in real world use.
    type = fields.Selection(
        selection_add=[("freetext", "Freetext")],
        ondelete={"freetext": lambda recs: recs.write({"type": "qualitative"})},
    )
