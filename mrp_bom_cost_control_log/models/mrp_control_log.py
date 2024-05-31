from odoo import fields, models


class MrpControlLog(models.Model):

    _name = "mrp.control.log"
    _description = "MRP Control logs"

    name = fields.Char(string="Name", readonly=True)
    product_code = fields.Char(string="Product code", readonly=True)
    computed_date = fields.Date(string="Computed on", readonly=True)
    computed_cost = fields.Float(string="BoM cost", readonly=True)
    product_id = fields.Many2one("product.product", string="Product", readonly=True)
