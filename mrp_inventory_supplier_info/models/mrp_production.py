from odoo import fields, models


class MrpInventory(models.Model):

    _inherit = "mrp.inventory"

    supplier_name = fields.Char(
        string="Supplier Name",
        related="product_mrp_area_id.main_supplierinfo_id.name.name",
        store=True,
        readonly=True,
    )

    supplier_info = fields.Many2one(
        string="Supplier Info",
        related="product_mrp_area_id.main_supplierinfo_id",
    )
