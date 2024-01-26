from odoo import fields, models


class ProductMrpArea(models.Model):

    _inherit = "product.mrp.area"

    abc_classification_profile_id = fields.Many2one(
        related="product_id.abc_classification_profile_id"
    )
    abc_classification_level_id = fields.Many2one(
        related="product_id.abc_classification_level_id"
    )
