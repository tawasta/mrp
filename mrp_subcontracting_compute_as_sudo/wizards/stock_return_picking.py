from odoo import fields, models


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    subcontract_location_id = fields.Many2one(compute_sudo=True)
