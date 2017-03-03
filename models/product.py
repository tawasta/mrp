from openerp import api, fields, models


class Product(models.Model):

    _inherit = "product.template"

    bom_locked = fields.Boolean(string="Lock BOM", help="Locks all BOM's for this product")

