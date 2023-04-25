from odoo import fields, models


class MrpBom(models.Model):

    _inherit = "mrp.bom"

    type = fields.Selection(
        selection_add=[("consumption", "Consumable BOM")],
        ondelete={
            "consumption": lambda self: self.write({"type": "normal", "active": False})
        },
    )
