from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    bom_locked = fields.Boolean(
        string="Lock BOMs",
        help="Locks all Bills of Materials for this product"
             "so that they cannot be modified.")
