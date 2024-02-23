from odoo import models, fields
from odoo.addons import decimal_precision as dp


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    primary_vendor_id = fields.Many2one(
        comodel_name="res.partner",
        related="product_id.primary_vendor_id",
        string="Primary Vendor",
    )

    primary_vendor_code = fields.Char(
        related="product_id.primary_supplierinfo_id.product_code",
        string="Primary Vendor's Code",
    )

    primary_vendor_price = fields.Float(
        related="product_id.primary_supplierinfo_id.price",
        digits=dp.get_precision("Product Price"),
        string="Primary Vendor's Price",
    )

    primary_vendor_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="product_id.primary_supplierinfo_id.currency_id",
        string="Primary Vendor's Currency",
    )

    primary_vendor_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="product_id.primary_supplierinfo_id.product_uom",
        string="Primary Vendor's UoM",
    )
