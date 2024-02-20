from odoo import fields, models


class PurchaseRequest(models.Model):

    _inherit = "purchase.request"

    mrp_production_id = fields.Many2one(
        string="Manufacturing Order",
        comodel_name="mrp.production",
        help="""Manufacturing Order this Purchase Request originated from""",
    )
