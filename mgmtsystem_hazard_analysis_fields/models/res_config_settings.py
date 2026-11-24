from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hazard_supplier_company_id = fields.Many2one(
        related="company_id.hazard_supplier_company_id", readonly=False
    )
